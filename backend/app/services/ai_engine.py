import google.generativeai as genai
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class AIEngine:
    """Gemini-powered AI engine for SmartReach AI."""
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None
            logger.warning("No Gemini API key configured. AI features will use fallback responses.")
    
    async def generate_campaign_plan(self, objective: str, customer_stats: dict) -> dict:
        """Generate a complete campaign plan from a natural language objective.
        
        Args:
            objective: The marketer's business objective in natural language
            customer_stats: Summary statistics about the customer base
                          (total_customers, avg_spend, etc.)
        
        Returns:
            Complete campaign plan with segment rules, messages, channel recommendation
        """
        prompt = f"""You are an expert marketing AI for a premium coffee brand called "Brewly".
You help marketers create targeted campaigns.

Customer Database Summary:
- Total customers: {customer_stats.get('total_customers', 100)}
- Average spend: ₹{customer_stats.get('avg_spend', 8500)}
- Average visits: {customer_stats.get('avg_visits', 12)}
- Customers with recent purchases (last 30 days): {customer_stats.get('recent_active', 45)}
- Inactive customers (no purchase in 60+ days): {customer_stats.get('inactive_60_days', 25)}
- High-value customers (spend > ₹15K): {customer_stats.get('high_value', 20)}

Available customer fields for segmentation:
- total_spend (float, in ₹)
- visit_count (integer)
- last_purchase_at (datetime - can use "older_than_days" or "within_days" operators)
- segment_tags (string - contains tags like: premium, loyal, frequent, lapsed, high-value, new, bargain, at-risk, one-time)

Available operators: greater_than, less_than, equals, not_equals, contains, older_than_days, within_days

The marketer's objective is:
"{objective}"

Generate a complete campaign plan as a JSON object with EXACTLY this structure:
{{
  "segment_name": "A short descriptive name for the audience segment",
  "segment_description": "A 1-2 sentence description of who this segment targets",
  "rules": {{
    "conditions": [
      {{"field": "field_name", "operator": "operator", "value": "value"}}
    ],
    "logic": "AND"
  }},
  "audience_reasoning": "2-3 sentences explaining WHY this audience was selected. Be specific about the marketing logic.",
  "confidence_score": 0.85,
  "messages": {{
    "whatsapp": "WhatsApp message with {{{{name}}}} placeholder. Keep under 160 chars. Use emojis.",
    "sms": "SMS message with {{{{name}}}} placeholder. Keep under 140 chars.",
    "email_subject": "Email subject line with {{{{name}}}} placeholder",
    "email_body": "Email body (2-3 short paragraphs) with {{{{name}}}} placeholder. Include a call to action.",
    "rcs": "RCS rich message with {{{{name}}}} placeholder. Can be longer, use emojis."
  }},
  "channel_recommendation": {{
    "channel": "whatsapp",
    "reasoning": "Why this channel is best for this audience and objective",
    "confidence": 0.88
  }},
  "campaign_name": "A catchy campaign name",
  "predicted_open_rate": 0.65,
  "predicted_click_rate": 0.12,
  "predicted_engagement_score": 0.78
}}

Respond with ONLY the JSON object, no other text."""

        if not self.model:
            return self._fallback_plan(objective)
        
        try:
            # Note: generate_content_async is run in executor if not supported, 
            # but standard SDK supports it async. Let's make sure it's correct.
            # Using generate_content inside run_in_executor or direct generate_content is also fine.
            # Let's call the API synchronously via executor to be 100% compatible and avoid any async sdk issues, 
            # or just call model.generate_content which is standard.
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
            text = response.text.strip()
            # Clean up potential markdown formatting
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
                text = text.rsplit('```', 1)[0]
                text = text.strip()
                if text.startswith('json'):
                    text = text.split('\n', 1)[1].strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_plan(objective)
    
    async def generate_insights(self, campaign_data: dict) -> dict:
        """Generate AI insights for a completed campaign."""
        prompt = f"""You are a marketing analytics AI. Analyze this campaign performance and provide insights.

Campaign: "{campaign_data.get('name', 'Campaign')}"
Objective: "{campaign_data.get('objective', 'N/A')}"
Channel: {campaign_data.get('channel', 'N/A')}

Performance Metrics:
- Total Sent: {campaign_data.get('total_sent', 0)}
- Delivered: {campaign_data.get('delivered', 0)} ({campaign_data.get('delivery_rate', 0):.1f}%)
- Failed: {campaign_data.get('failed', 0)}
- Opened: {campaign_data.get('opened', 0)} ({campaign_data.get('open_rate', 0):.1f}%)
- Read: {campaign_data.get('read', 0)}
- Clicked: {campaign_data.get('clicked', 0)} ({campaign_data.get('click_rate', 0):.1f}%)

Respond with a JSON object:
{{
  "summary": "A 2-3 sentence overall performance summary",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"],
  "performance_rating": "excellent|good|average|poor"
}}

Respond with ONLY the JSON object."""

        if not self.model:
            return self._fallback_insights(campaign_data)
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
            text = response.text.strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1]
                text = text.rsplit('```', 1)[0]
                text = text.strip()
                if text.startswith('json'):
                    text = text.split('\n', 1)[1].strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Gemini insights error: {e}")
            return self._fallback_insights(campaign_data)
    
    def _fallback_plan(self, objective: str) -> dict:
        """Fallback campaign plan when Gemini is unavailable."""
        objective_lower = objective.lower()
        
        # Detect intent and create appropriate fallback
        if any(w in objective_lower for w in ['lapsed', 'inactive', 'back', 'return', 'haven\'t purchased', 'not purchased', 'dormant', 're-engage', 'reengage', 'win back']):
            return {
                "segment_name": "Lapsed Customers",
                "segment_description": "Customers who haven't made a purchase in a significant period and need re-engagement.",
                "rules": {
                    "conditions": [
                        {"field": "last_purchase_at", "operator": "older_than_days", "value": 60},
                        {"field": "total_spend", "operator": "greater_than", "value": 1000}
                    ],
                    "logic": "AND"
                },
                "audience_reasoning": "Targeting customers who previously showed purchase intent (spent >₹1,000) but have gone silent for 60+ days. These shoppers already know and trust the brand, making them prime candidates for re-engagement at a fraction of new acquisition cost.",
                "confidence_score": 0.87,
                "messages": {
                    "whatsapp": "Hey {{name}}! ☕ We've missed you at Brewly. Here's 20% off your next order to welcome you back! 🎉",
                    "sms": "{{name}}, we miss you! Get 20% off your next Brewly order. Use code COMEBACK20.",
                    "email_subject": "We miss you, {{name}}! Here's a special treat ☕",
                    "email_body": "Hi {{name}},\n\nIt's been a while since your last visit to Brewly, and we've missed having you!\n\nAs a special welcome-back treat, we're offering you 20% off your next order. Whether it's your favorite Cold Brew or something new from our seasonal menu, we'd love to see you again.\n\nUse code COMEBACK20 at checkout.\n\nWarm regards,\nTeam Brewly ☕",
                    "rcs": "Hey {{name}}! ☕ We've noticed you haven't visited Brewly in a while. We have exciting new blends waiting for you! Here's an exclusive 20% off to welcome you back 🎉"
                },
                "channel_recommendation": {
                    "channel": "whatsapp",
                    "reasoning": "WhatsApp offers 98% open rates, making it ideal for re-engagement campaigns where grabbing attention is critical. The personal, conversational format helps rebuild the connection with lapsed customers.",
                    "confidence": 0.91
                },
                "campaign_name": "We Miss You — Win Back Campaign",
                "predicted_open_rate": 0.72,
                "predicted_click_rate": 0.15,
                "predicted_engagement_score": 0.68
            }
        elif any(w in objective_lower for w in ['premium', 'high-value', 'luxury', 'upsell', 'upgrade', 'coffee beans', 'beans']):
            return {
                "segment_name": "Premium Upsell Targets",
                "segment_description": "High-spending loyal customers who are primed for premium product upgrades.",
                "rules": {
                    "conditions": [
                        {"field": "total_spend", "operator": "greater_than", "value": 10000},
                        {"field": "visit_count", "operator": "greater_than", "value": 10}
                    ],
                    "logic": "AND"
                },
                "audience_reasoning": "These customers have demonstrated consistent spending above ₹10K and visit regularly (10+ times). They're already brand enthusiasts and are the most likely to respond positively to premium product launches or exclusive offerings.",
                "confidence_score": 0.92,
                "messages": {
                    "whatsapp": "{{name}}, as one of our most valued patrons ⭐ you get FIRST access to our new Single Origin Reserve collection! ☕✨",
                    "sms": "{{name}}, exclusive invite: Try our new Single Origin Reserve before anyone else. Limited stock!",
                    "email_subject": "{{name}}, you're invited to something exclusive ✨",
                    "email_body": "Dear {{name}},\n\nAs one of Brewly's most valued customers, we wanted you to be the first to know about our new Single Origin Reserve collection.\n\nSourced from the finest estates in Ethiopia and Colombia, these limited-edition beans are available exclusively to our top customers before the public launch.\n\nReserve your bag now and enjoy a complimentary tasting at your nearest Brewly store.\n\nExclusively yours,\nTeam Brewly",
                    "rcs": "✨ {{name}}, VIP Alert! As a top Brewly customer, you get exclusive early access to our Single Origin Reserve collection. Tap to reserve yours before it's gone! ☕"
                },
                "channel_recommendation": {
                    "channel": "email",
                    "reasoning": "Email allows for rich, detailed content that conveys the premium positioning of the product. High-value customers are more likely to engage with well-crafted email content that tells the story behind exclusive offerings.",
                    "confidence": 0.85
                },
                "campaign_name": "VIP First Access — Single Origin Reserve",
                "predicted_open_rate": 0.58,
                "predicted_click_rate": 0.22,
                "predicted_engagement_score": 0.82
            }
        else:
            # Generic fallback
            return {
                "segment_name": "Engaged Shoppers",
                "segment_description": "Active customers with recent purchase history who are likely to respond to campaigns.",
                "rules": {
                    "conditions": [
                        {"field": "last_purchase_at", "operator": "within_days", "value": 90},
                        {"field": "visit_count", "operator": "greater_than", "value": 2}
                    ],
                    "logic": "AND"
                },
                "audience_reasoning": "Targeting recently active customers (purchased within 90 days) with multiple visits. These engaged shoppers have the highest probability of converting on new campaigns, ensuring strong ROI.",
                "confidence_score": 0.80,
                "messages": {
                    "whatsapp": "Hey {{name}}! 🎉 Exciting news from Brewly — check out what's new for you this week! ☕",
                    "sms": "{{name}}, Brewly has something special for you! Visit us this week for exclusive offers.",
                    "email_subject": "{{name}}, something special is brewing at Brewly ☕",
                    "email_body": "Hi {{name}},\n\nWe've been brewing something special at Brewly and couldn't wait to share it with you!\n\nCheck out our latest offerings and exclusive deals available just for our loyal customers.\n\nVisit us today and discover what's new!\n\nCheers,\nTeam Brewly",
                    "rcs": "🎉 {{name}}! Brewly has exciting new offerings this week. Come discover our latest seasonal specials and exclusive deals! ☕✨"
                },
                "channel_recommendation": {
                    "channel": "whatsapp",
                    "reasoning": "WhatsApp provides the highest engagement rates across demographics, making it the safest choice for broad promotional campaigns with engaged customer segments.",
                    "confidence": 0.82
                },
                "campaign_name": "Weekly Brewly Highlights",
                "predicted_open_rate": 0.60,
                "predicted_click_rate": 0.10,
                "predicted_engagement_score": 0.65
            }
    
    def _fallback_insights(self, campaign_data: dict) -> dict:
        """Fallback insights when Gemini is unavailable."""
        delivery_rate = campaign_data.get('delivery_rate', 0.0)
        open_rate = campaign_data.get('open_rate', 0.0)
        click_rate = campaign_data.get('click_rate', 0.0)
        
        if open_rate > 50:
            rating = "excellent"
        elif open_rate > 30:
            rating = "good"
        elif open_rate > 15:
            rating = "average"
        else:
            rating = "poor"
        
        return {
            "summary": f"Campaign achieved a {delivery_rate:.1f}% delivery rate with {open_rate:.1f}% open rate and {click_rate:.1f}% click-through rate. {'Strong performance across all metrics.' if rating in ['excellent', 'good'] else 'There is room for improvement in engagement.'}",
            "key_findings": [
                f"Delivery rate of {delivery_rate:.1f}% {'exceeds' if delivery_rate > 85 else 'is below'} industry average of 85%",
                f"Open rate of {open_rate:.1f}% indicates {'strong' if open_rate > 30 else 'moderate'} audience interest",
                f"Click-through rate of {click_rate:.1f}% suggests {'compelling' if click_rate > 10 else 'room to improve'} call-to-action effectiveness"
            ],
            "recommendations": [
                "Consider A/B testing message content to optimize open rates",
                "Segment high-engagers for follow-up campaigns with stronger CTAs",
                "Test different send times to find the optimal engagement window"
            ],
            "performance_rating": rating
        }

# Singleton instance
ai_engine = AIEngine()

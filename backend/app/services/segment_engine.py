import json
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer

logger = logging.getLogger(__name__)

class SegmentEngine:
    """Translates segment rules into SQL queries and evaluates audience size."""
    
    OPERATOR_MAP = {
        "greater_than": lambda col, val: col > float(val),
        "less_than": lambda col, val: col < float(val),
        "equals": lambda col, val: col == val,
        "not_equals": lambda col, val: col != val,
        "contains": lambda col, val: col.contains(str(val)),
        "older_than_days": lambda col, val: col < datetime.utcnow() - timedelta(days=int(val)),
        "within_days": lambda col, val: col >= datetime.utcnow() - timedelta(days=int(val)),
    }
    
    FIELD_MAP = {
        "total_spend": Customer.total_spend,
        "visit_count": Customer.visit_count,
        "last_purchase_at": Customer.last_purchase_at,
        "segment_tags": Customer.segment_tags,
        "email": Customer.email,
        "name": Customer.name,
        "phone": Customer.phone,
    }
    
    def _coerce_rules_to_dict(self, rules) -> dict:
        if rules is None:
            return {}
        if hasattr(rules, "model_dump"):
            return rules.model_dump()
        elif hasattr(rules, "dict"):
            return rules.dict()
        elif isinstance(rules, str):
            try:
                return json.loads(rules)
            except Exception:
                return {}
        elif isinstance(rules, dict):
            return rules
        return {}
    
    def build_query(self, rules: dict):
        """Build SQLAlchemy filter conditions from rules dict."""
        rules = self._coerce_rules_to_dict(rules)
        conditions_data = rules.get("conditions", [])
        logic = rules.get("logic", "AND").upper()
        
        filters = []
        for cond in conditions_data:
            field_name = cond.get("field")
            operator = cond.get("operator")
            value = cond.get("value")
            
            if field_name not in self.FIELD_MAP:
                logger.warning(f"Unknown field: {field_name}")
                continue
            if operator not in self.OPERATOR_MAP:
                logger.warning(f"Unknown operator: {operator}")
                continue
            
            column = self.FIELD_MAP[field_name]
            filter_expr = self.OPERATOR_MAP[operator](column, value)
            filters.append(filter_expr)
        
        if not filters:
            return select(Customer)  # Return all if no valid filters
        
        if logic == "OR":
            return select(Customer).where(or_(*filters))
        return select(Customer).where(and_(*filters))
    
    async def calculate_audience_size(self, rules: dict, db: AsyncSession) -> int:
        """Count the number of customers matching the rules."""
        try:
            rules = self._coerce_rules_to_dict(rules)
            conditions_data = rules.get("conditions", [])
            logic = rules.get("logic", "AND").upper()
            
            filters = []
            for cond in conditions_data:
                field_name = cond.get("field")
                operator = cond.get("operator")
                value = cond.get("value")
                if field_name in self.FIELD_MAP and operator in self.OPERATOR_MAP:
                    column = self.FIELD_MAP[field_name]
                    filters.append(self.OPERATOR_MAP[operator](column, value))
            
            if not filters:
                count_query = select(func.count()).select_from(Customer)
            elif logic == "OR":
                count_query = select(func.count()).select_from(Customer).where(or_(*filters))
            else:
                count_query = select(func.count()).select_from(Customer).where(and_(*filters))
            
            result = await db.execute(count_query)
            return result.scalar() or 0
        except Exception as e:
            logger.error(f"Error calculating audience size: {e}")
            return 0
    
    async def get_audience(self, rules: dict, db: AsyncSession) -> list:
        """Get all customers matching the segment rules."""
        try:
            query = self.build_query(rules)
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching audience: {e}")
            return []

# Singleton
segment_engine = SegmentEngine()

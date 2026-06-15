import json
import random
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.customer import Customer
from app.models.order import Order

# Coffee menu items with typical prices in INR (₹)
COFFEE_PRODUCTS = [
    {"name": "Espresso", "price": 150.0},
    {"name": "Cappuccino", "price": 220.0},
    {"name": "Latte", "price": 240.0},
    {"name": "Cold Brew", "price": 190.0},
    {"name": "Mocha", "price": 260.0},
    {"name": "Premium Single Origin", "price": 450.0},
    {"name": "Ethiopian Blend", "price": 480.0},
    {"name": "Colombian Roast", "price": 420.0},
    {"name": "Coffee Beans (250g)", "price": 350.0},
    {"name": "Coffee Beans (500g)", "price": 650.0},
    {"name": "French Press", "price": 1200.0},
    {"name": "Pour Over Kit", "price": 1800.0},
    {"name": "Subscription Box", "price": 2500.0},
    {"name": "Gift Card", "price": 1000.0},
]

INDIAN_FIRST_NAMES = [
    "Rohan", "Aarav", "Arjun", "Rahul", "Vikram", "Aditya", "Kabir", "Dev", "Kunal", "Sameer",
    "Amit", "Gaurav", "Yash", "Siddharth", "Vivek", "Ajay", "Sanjay", "Sunil", "Anil", "Deepak",
    "Ananya", "Priya", "Neha", "Aisha", "Diya", "Pooja", "Aditi", "Riya", "Shruti", "Tanvi",
    "Sneha", "Divya", "Kavya", "Kiara", "Isha", "Shreya", "Meera", "Nikita", "Jyoti", "Rekha"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Mehta", "Patel", "Kapoor", "Gupta", "Joshi", "Sen", "Das", "Rao", "Nair",
    "Menon", "Roy", "Verma", "Mishra", "Bhat", "Reddy", "Choudhury", "Singh", "Prasad", "Kumar"
]

CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata"]
COFFEE_PREFERENCES = ["Espresso", "Cappuccino", "Latte", "Cold Brew", "Mocha", "Filter Coffee", "Black Coffee"]
SIGNUP_SOURCES = ["Instagram Ad", "Google Search", "Word of Mouth", "In-Store Flyer", "Referral"]

async def seed_database(db: AsyncSession) -> None:
    """Seed the database with a demo user, 100 customers, and 500+ orders."""
    # Check if data already exists
    customer_check = await db.execute(select(Customer).limit(1))
    if customer_check.scalar_one_or_none() is not None:
        print("Database already has customer data. Skipping seeding.")
        return

    random.seed(42)  # Set seed for reproducibility
    now = datetime.utcnow()

    # 1. Create Demo User
    demo_user = User(
        id=str(uuid4()),
        email="demo@smartreach.ai",
        name="Demo Marketer",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=256&h=256"
    )
    db.add(demo_user)
    await db.flush()

    # Create 100 Customers
    customers = []
    generated_emails = set()

    for i in range(100):
        # Generate unique name
        fname = random.choice(INDIAN_FIRST_NAMES)
        lname = random.choice(INDIAN_LAST_NAMES)
        full_name = f"{fname} {lname}"
        
        # Ensure email is unique
        email_prefix = f"{fname.lower()}.{lname.lower()}"
        email = f"{email_prefix}@gmail.com"
        counter = 1
        while email in generated_emails:
            email = f"{email_prefix}{counter}@gmail.com"
            counter += 1
        generated_emails.add(email)

        # Phone
        phone = f"+91 9{random.randint(100000000, 999999999)}"
        
        # Meta info
        pref = random.choice(COFFEE_PREFERENCES)
        city = random.choice(CITIES)
        source = random.choice(SIGNUP_SOURCES)
        meta = {
            "city": city,
            "preference": pref,
            "signup_source": source
        }

        # Decide persona and parameters
        # Indices 0-14 (15): Premium Loyalists
        # Indices 15-34 (20): Regular Buyers
        # Indices 35-49 (15): Bargain Hunters
        # Indices 50-69 (20): Lapsed Customers
        # Indices 70-79 (10): New Customers
        # Indices 80-89 (10): High-Value At Risk
        # Indices 90-99 (10): One-Time Buyers
        if i < 15:
            persona = "premium_loyalist"
            tags = "premium,loyal,frequent"
            min_orders, max_orders = 15, 25
            min_amt, max_amt = 400.0, 1800.0
            order_span_days = 90
            last_order_within_days = 7
        elif i < 35:
            persona = "regular_buyer"
            tags = "regular,active"
            min_orders, max_orders = 6, 12
            min_amt, max_amt = 250.0, 800.0
            order_span_days = 120
            last_order_within_days = 30
        elif i < 50:
            persona = "bargain_hunter"
            tags = "bargain,discount-seeker,active"
            min_orders, max_orders = 8, 15
            min_amt, max_amt = 100.0, 300.0
            order_span_days = 90
            last_order_within_days = 14
        elif i < 70:
            persona = "lapsed_customer"
            tags = "lapsed,inactive"
            min_orders, max_orders = 4, 10
            min_amt, max_amt = 300.0, 1000.0
            order_span_days = 200
            # Last purchase was between 60 and 180 days ago
            last_order_within_days = random.randint(60, 180)
        elif i < 80:
            persona = "new_customer"
            tags = "new,active"
            min_orders, max_orders = 1, 3
            min_amt, max_amt = 200.0, 600.0
            order_span_days = 21
            last_order_within_days = 21
        elif i < 90:
            persona = "high_value_at_risk"
            tags = "high-value,at-risk"
            min_orders, max_orders = 12, 22
            min_amt, max_amt = 800.0, 3000.0
            order_span_days = 150
            # Last purchase was between 30 and 90 days ago
            last_order_within_days = random.randint(30, 90)
        else:
            persona = "one_time_buyer"
            tags = "one-time,inactive"
            min_orders, max_orders = 1, 1
            min_amt, max_amt = 500.0, 2000.0
            order_span_days = 365
            # Last purchase was between 100 and 365 days ago
            last_order_within_days = random.randint(100, 365)

        customer = Customer(
            id=str(uuid4()),
            email=email,
            name=full_name,
            phone=phone,
            segment_tags=tags,
            metadata_json=json.dumps(meta),
            total_spend=0.0,
            visit_count=0,
            last_purchase_at=None,
            created_at=now - timedelta(days=random.randint(180, 400))
        )
        customers.append((customer, persona, min_orders, max_orders, min_amt, max_amt, order_span_days, last_order_within_days))
        db.add(customer)

    await db.flush()

    # Generate Orders for each customer
    all_orders = []
    for customer, persona, min_orders, max_orders, min_amt, max_amt, order_span_days, last_order_within_days in customers:
        num_orders = random.randint(min_orders, max_orders)
        
        # Calculate order dates
        # The last order must be within the specified last_order_within_days
        last_order_date = now - timedelta(days=random.uniform(0.1, last_order_within_days))
        
        order_dates = [last_order_date]
        for _ in range(num_orders - 1):
            # Other orders are spaced back in time from the last order date
            days_ago = random.uniform(2, order_span_days)
            order_dates.append(last_order_date - timedelta(days=days_ago))
        
        order_dates.sort()  # Chronological order

        total_spend = 0.0
        visit_count = 0
        last_purchase_at = None

        for o_date in order_dates:
            # Generate random order items
            items_count = random.randint(1, 3)
            order_items = random.sample(COFFEE_PRODUCTS, items_count)
            # Adjust price based on target spending parameters for this persona
            # We scale the item prices to hit the target total amount
            target_amount = random.uniform(min_amt, max_amt)
            actual_items = []
            current_sum = sum(x["price"] for x in order_items)
            
            scale = target_amount / current_sum
            for item in order_items:
                actual_items.append({
                    "name": item["name"],
                    "price": round(item["price"] * scale, 2),
                    "quantity": 1
                })
            
            order_amount = round(sum(x["price"] for x in actual_items), 2)
            
            order = Order(
                id=str(uuid4()),
                customer_id=customer.id,
                amount=order_amount,
                status="completed",
                items=json.dumps(actual_items),
                order_date=o_date,
                created_at=o_date + timedelta(minutes=5)
            )
            db.add(order)
            all_orders.append(order)

            total_spend += order_amount
            visit_count += 1
            last_purchase_at = o_date

        # Update customer aggregates
        customer.total_spend = round(total_spend, 2)
        customer.visit_count = visit_count
        customer.last_purchase_at = last_purchase_at

    await db.commit()
    print(f"Seeding completed: Created 1 demo user, {len(customers)} customers, and {len(all_orders)} orders.")

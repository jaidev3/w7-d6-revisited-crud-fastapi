from datetime import datetime, timedelta
from models import SessionLocal, create_tables
from schemas import ExpenseCreate
import crud

def create_sample_data():
    """Create sample expense data for testing"""
    create_tables()
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_expenses = crud.get_expenses(db, limit=1)
        if existing_expenses:
            print("Sample data already exists. Skipping initialization.")
            return
        
        # Sample expenses data
        sample_expenses = [
            {
                "title": "Grocery Shopping",
                "amount": 85.50,
                "category": "Groceries",
                "description": "Weekly grocery shopping at supermarket",
                "date": datetime.now() - timedelta(days=1)
            },
            {
                "title": "Gas Station",
                "amount": 45.00,
                "category": "Transportation",
                "description": "Fuel for car",
                "date": datetime.now() - timedelta(days=2)
            },
            {
                "title": "Restaurant Dinner",
                "amount": 67.80,
                "category": "Food & Dining",
                "description": "Dinner at Italian restaurant",
                "date": datetime.now() - timedelta(days=3)
            },
            {
                "title": "Movie Tickets",
                "amount": 28.00,
                "category": "Entertainment",
                "description": "Movie tickets for two",
                "date": datetime.now() - timedelta(days=4)
            },
            {
                "title": "Electricity Bill",
                "amount": 120.35,
                "category": "Bills & Utilities",
                "description": "Monthly electricity bill",
                "date": datetime.now() - timedelta(days=5)
            },
            {
                "title": "Coffee Shop",
                "amount": 12.50,
                "category": "Food & Dining",
                "description": "Morning coffee and pastry",
                "date": datetime.now() - timedelta(days=6)
            },
            {
                "title": "Online Course",
                "amount": 99.99,
                "category": "Education",
                "description": "Python programming course",
                "date": datetime.now() - timedelta(days=7)
            },
            {
                "title": "Pharmacy",
                "amount": 23.75,
                "category": "Healthcare",
                "description": "Prescription medication",
                "date": datetime.now() - timedelta(days=8)
            },
            {
                "title": "Uber Ride",
                "amount": 18.20,
                "category": "Transportation",
                "description": "Ride to downtown",
                "date": datetime.now() - timedelta(days=9)
            },
            {
                "title": "New Shoes",
                "amount": 129.99,
                "category": "Shopping",
                "description": "Running shoes",
                "date": datetime.now() - timedelta(days=10)
            },
            {
                "title": "Gym Membership",
                "amount": 49.99,
                "category": "Personal Care",
                "description": "Monthly gym membership",
                "date": datetime.now() - timedelta(days=15)
            },
            {
                "title": "Home Depot",
                "amount": 87.45,
                "category": "Home & Garden",
                "description": "Hardware supplies for home repair",
                "date": datetime.now() - timedelta(days=20)
            },
            {
                "title": "Birthday Gift",
                "amount": 65.00,
                "category": "Gifts & Donations",
                "description": "Birthday gift for friend",
                "date": datetime.now() - timedelta(days=25)
            },
            {
                "title": "Car Insurance",
                "amount": 156.80,
                "category": "Insurance",
                "description": "Monthly car insurance premium",
                "date": datetime.now() - timedelta(days=30)
            },
            {
                "title": "Business Lunch",
                "amount": 42.30,
                "category": "Business",
                "description": "Client meeting lunch",
                "date": datetime.now() - timedelta(days=35)
            }
        ]
        
        # Create expenses
        created_count = 0
        for expense_data in sample_expenses:
            try:
                expense = ExpenseCreate(**expense_data)
                crud.create_expense(db=db, expense=expense)
                created_count += 1
            except Exception as e:
                print(f"Error creating expense '{expense_data['title']}': {e}")
        
        print(f"Successfully created {created_count} sample expenses!")
        
        # Print summary
        total_data = crud.get_total_expenses(db=db)
        print(f"Total expenses: ${total_data['total_amount']:.2f}")
        print(f"Total count: {total_data['total_count']}")
        print("Category breakdown:")
        for category, amount in total_data['category_breakdown'].items():
            print(f"  {category}: ${amount:.2f}")
    
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data() 
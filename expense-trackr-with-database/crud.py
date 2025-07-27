from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from models import Expense
from schemas import ExpenseCreate, ExpenseUpdate
from datetime import datetime, date
from typing import Optional, List

def create_expense(db: Session, expense: ExpenseCreate) -> Expense:
    """Create a new expense"""
    expense_data = expense.dict()
    if expense_data.get('date') is None:
        expense_data['date'] = datetime.utcnow()
    
    db_expense = Expense(**expense_data)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expense(db: Session, expense_id: int) -> Optional[Expense]:
    """Get a single expense by ID"""
    return db.query(Expense).filter(Expense.id == expense_id).first()

def get_expenses(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Expense]:
    """Get expenses with optional filtering"""
    query = db.query(Expense)
    
    # Apply filters
    if category:
        query = query.filter(Expense.category == category)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        # Include the entire end date by adding 1 day
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(Expense.date <= end_datetime)
    
    return query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()

def get_expenses_count(
    db: Session,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> int:
    """Get count of expenses with optional filtering"""
    query = db.query(Expense)
    
    if category:
        query = query.filter(Expense.category == category)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(Expense.date <= end_datetime)
    
    return query.count()

def update_expense(db: Session, expense_id: int, expense_update: ExpenseUpdate) -> Optional[Expense]:
    """Update an existing expense"""
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return None
    
    update_data = expense_update.dict(exclude_unset=True)
    if update_data:
        update_data['updated_at'] = datetime.utcnow()
        for field, value in update_data.items():
            setattr(db_expense, field, value)
        
        db.commit()
        db.refresh(db_expense)
    
    return db_expense

def delete_expense(db: Session, expense_id: int) -> bool:
    """Delete an expense"""
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        return False
    
    db.delete(db_expense)
    db.commit()
    return True

def get_expenses_by_category(db: Session, category: str) -> List[Expense]:
    """Get all expenses for a specific category"""
    return db.query(Expense).filter(Expense.category == category).order_by(Expense.date.desc()).all()

def get_total_expenses(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> dict:
    """Get total expenses and breakdown by category"""
    query = db.query(Expense)
    
    # Apply date filters
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(Expense.date <= end_datetime)
    
    # Get total amount and count
    total_result = query.with_entities(
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('total_count')
    ).first()
    
    total_amount = float(total_result.total_amount or 0)
    total_count = int(total_result.total_count or 0)
    
    # Get category breakdown
    category_breakdown = {}
    category_results = query.with_entities(
        Expense.category,
        func.sum(Expense.amount).label('category_total')
    ).group_by(Expense.category).all()
    
    for category, amount in category_results:
        category_breakdown[category] = float(amount or 0)
    
    return {
        "total_amount": total_amount,
        "total_count": total_count,
        "category_breakdown": category_breakdown
    } 
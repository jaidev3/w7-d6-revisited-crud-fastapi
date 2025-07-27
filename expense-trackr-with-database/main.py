from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional, List
import uvicorn

from models import create_tables, get_db, EXPENSE_CATEGORIES
from schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseTotal, ExpensesResponse
import crud

# Create FastAPI app
app = FastAPI(
    title="Expense Tracker API",
    description="A comprehensive expense tracking API with database integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    print("Database tables created successfully!")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to the Expense Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "GET /expenses": "Fetch all expenses",
            "POST /expenses": "Create a new expense",
            "PUT /expenses/{expense_id}": "Update an existing expense",
            "DELETE /expenses/{expense_id}": "Delete an expense",
            "GET /expenses/category/{category}": "Filter expenses by category",
            "GET /expenses/total": "Get total expenses and breakdown by category"
        }
    }

@app.get("/categories", response_model=List[str], tags=["Categories"])
async def get_categories():
    """Get all available expense categories"""
    return EXPENSE_CATEGORIES

@app.get("/expenses", response_model=ExpensesResponse, tags=["Expenses"])
async def get_expenses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Fetch all expenses with optional filtering"""
    try:
        # Validate category if provided
        if category and category not in EXPENSE_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(EXPENSE_CATEGORIES)}"
            )
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before or equal to end_date"
            )
        
        expenses = crud.get_expenses(
            db=db,
            skip=skip,
            limit=limit,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        total_count = crud.get_expenses_count(
            db=db,
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculate filtered total
        filtered_total = sum(expense.amount for expense in expenses)
        
        return ExpensesResponse(
            expenses=expenses,
            total_count=total_count,
            filtered_total=filtered_total
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/expenses", response_model=ExpenseResponse, tags=["Expenses"])
async def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """Create a new expense"""
    try:
        db_expense = crud.create_expense(db=db, expense=expense)
        return db_expense
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/expenses/{expense_id}", response_model=ExpenseResponse, tags=["Expenses"])
async def get_expense(expense_id: int, db: Session = Depends(get_db)):
    """Get a specific expense by ID"""
    db_expense = crud.get_expense(db=db, expense_id=expense_id)
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense

@app.put("/expenses/{expense_id}", response_model=ExpenseResponse, tags=["Expenses"])
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing expense"""
    try:
        db_expense = crud.update_expense(db=db, expense_id=expense_id, expense_update=expense_update)
        if not db_expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        return db_expense
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/expenses/{expense_id}", tags=["Expenses"])
async def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    """Delete an expense"""
    success = crud.delete_expense(db=db, expense_id=expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}

@app.get("/expenses/category/{category}", response_model=List[ExpenseResponse], tags=["Expenses"])
async def get_expenses_by_category(category: str, db: Session = Depends(get_db)):
    """Filter expenses by category"""
    if category not in EXPENSE_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(EXPENSE_CATEGORIES)}"
        )
    
    expenses = crud.get_expenses_by_category(db=db, category=category)
    return expenses

@app.get("/expenses/total", response_model=ExpenseTotal, tags=["Expenses"])
async def get_total_expenses(
    start_date: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get total expenses and breakdown by category"""
    try:
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before or equal to end_date"
            )
        
        total_data = crud.get_total_expenses(
            db=db,
            start_date=start_date,
            end_date=end_date
        )
        
        return ExpenseTotal(**total_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
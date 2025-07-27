from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from models import EXPENSE_CATEGORIES

class ExpenseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Expense title")
    amount: float = Field(..., gt=0, description="Expense amount (must be positive)")
    category: str = Field(..., description="Expense category")
    description: Optional[str] = Field(None, max_length=500, description="Optional description")
    date: Optional[datetime] = Field(None, description="Expense date")
    
    @validator('category')
    def validate_category(cls, v):
        if v not in EXPENSE_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(EXPENSE_CATEGORIES)}')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None
    
    @validator('category')
    def validate_category(cls, v):
        if v is not None and v not in EXPENSE_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(EXPENSE_CATEGORIES)}')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Amount must be positive')
            return round(v, 2)
        return v

class ExpenseResponse(ExpenseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ExpenseTotal(BaseModel):
    total_amount: float
    total_count: int
    category_breakdown: dict[str, float]

class ExpensesResponse(BaseModel):
    expenses: list[ExpenseResponse]
    total_count: int
    filtered_total: float 
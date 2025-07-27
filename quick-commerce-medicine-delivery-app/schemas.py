from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import UserRole, OrderStatus, PrescriptionStatus, DeliveryUrgency

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    phone_number: str
    full_name: str
    date_of_birth: Optional[datetime] = None
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(UserBase):
    id: int
    phone_verified: bool
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    medical_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

class PhoneVerification(BaseModel):
    phone_number: str
    verification_code: str

# Medicine Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Medicine Schemas
class MedicineBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    description: Optional[str] = None
    category_id: int
    price: float = Field(..., gt=0)
    discount_percentage: float = Field(default=0.0, ge=0, le=100)
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    pack_size: Optional[str] = None
    manufacturer: Optional[str] = None
    prescription_required: bool = False
    age_restrictions: Optional[Dict[str, Any]] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    delivery_time_minutes: int = Field(default=30, ge=10, le=120)
    is_available_for_quick_delivery: bool = True
    tags: Optional[List[str]] = None

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = Field(None, gt=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    pack_size: Optional[str] = None
    manufacturer: Optional[str] = None
    prescription_required: Optional[bool] = None
    age_restrictions: Optional[Dict[str, Any]] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    delivery_time_minutes: Optional[int] = Field(None, ge=10, le=120)
    is_available_for_quick_delivery: Optional[bool] = None
    tags: Optional[List[str]] = None

class MedicineResponse(MedicineBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse
    discounted_price: Optional[float] = None
    is_in_stock: bool
    
    class Config:
        from_attributes = True

class MedicineStock(BaseModel):
    stock_quantity: int = Field(..., ge=0)

class MedicineSearch(BaseModel):
    q: Optional[str] = None
    category_id: Optional[int] = None
    prescription_required: Optional[bool] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    in_stock_only: bool = True
    quick_delivery_only: bool = False

# Prescription Schemas
class PrescriptionBase(BaseModel):
    doctor_name: str
    doctor_license: Optional[str] = None
    hospital_clinic: Optional[str] = None
    prescription_date: datetime

class PrescriptionCreate(PrescriptionBase):
    valid_until: Optional[datetime] = None

class PrescriptionResponse(PrescriptionBase):
    id: int
    user_id: int
    image_path: Optional[str] = None
    status: PrescriptionStatus
    verified_by_pharmacist_id: Optional[int] = None
    verification_notes: Optional[str] = None
    verified_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PrescriptionVerification(BaseModel):
    status: PrescriptionStatus
    verification_notes: Optional[str] = None

class PrescriptionItemCreate(BaseModel):
    medicine_id: int
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity_prescribed: Optional[int] = None

class PrescriptionItemResponse(BaseModel):
    id: int
    prescription_id: int
    medicine: MedicineResponse
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity_prescribed: Optional[int] = None
    
    class Config:
        from_attributes = True

# Cart Schemas
class CartItemBase(BaseModel):
    medicine_id: int
    quantity: int = Field(..., gt=0)
    prescription_id: Optional[int] = None

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    medicine: MedicineResponse
    subtotal: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    estimated_delivery_time: int  # minutes
    prescription_required_items: List[CartItemResponse]

class CartValidation(BaseModel):
    is_valid: bool
    invalid_items: List[Dict[str, Any]]
    prescription_warnings: List[Dict[str, Any]]

# Order Schemas
class OrderCreate(BaseModel):
    delivery_address: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_urgency: DeliveryUrgency = DeliveryUrgency.STANDARD
    special_instructions: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    medicine: MedicineResponse
    quantity: int
    unit_price: float
    total_price: float
    prescription_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    subtotal: float
    delivery_fee: float
    discount_amount: float
    total_amount: float
    delivery_address: str
    delivery_urgency: DeliveryUrgency
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    status: OrderStatus
    delivery_partner_id: Optional[int] = None
    delivery_tracking_id: Optional[str] = None
    special_instructions: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None

class OrderTracking(BaseModel):
    order_id: int
    order_number: str
    status: OrderStatus
    estimated_delivery_time: Optional[datetime] = None
    current_location: Optional[Dict[str, float]] = None  # lat, lng
    delivery_partner_name: Optional[str] = None
    delivery_partner_phone: Optional[str] = None
    timeline: List[Dict[str, Any]]

# Delivery Schemas
class DeliveryEstimate(BaseModel):
    estimated_time_minutes: int
    delivery_fee: float
    available_urgency_options: List[DeliveryUrgency]

class DeliveryPartnerResponse(BaseModel):
    id: int
    name: str
    rating: float
    distance_km: float
    estimated_arrival_minutes: int
    
class EmergencyDeliveryRequest(BaseModel):
    medicine_id: int
    quantity: int
    prescription_id: Optional[int] = None
    delivery_address: str
    emergency_reason: str
    contact_phone: str

class NearbyPharmacy(BaseModel):
    id: int
    name: str
    address: str
    distance_km: float
    phone_number: str
    is_open: bool
    has_stock: bool
    estimated_delivery_minutes: int

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserProfile

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None

# Response Schemas
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    success: bool = False

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int 
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, timedelta
import json

from database import SessionLocal, engine, get_db
from models import Base, UserRole, OrderStatus, PrescriptionStatus, DeliveryUrgency
import models
import schemas
import crud
from auth import (
    get_current_user, get_current_active_user, get_pharmacy_admin_user,
    get_pharmacist_user, get_delivery_partner_user, get_admin_user
)
from security import (
    verify_password, create_access_token, generate_verification_code,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quick Commerce Medicine Delivery API",
    description="A comprehensive medicine delivery platform with quick commerce features",
    version="1.0.0"
)

# Authentication endpoints
@app.post("/auth/register", response_model=schemas.Token)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with medical profile."""
    # Check if user already exists
    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if crud.get_user_by_phone(db, phone_number=user.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create user
    db_user = crud.create_user(db=db, user=user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id}
    )
    
    # Convert user to profile format
    user_profile = schemas.UserProfile.from_orm(db_user)
    if db_user.medical_conditions:
        user_profile.medical_conditions = json.loads(db_user.medical_conditions)
    if db_user.allergies:
        user_profile.allergies = json.loads(db_user.allergies)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_profile
    }

@app.post("/auth/login", response_model=schemas.Token)
async def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """User login."""
    user = crud.get_user_by_email(db, email=user_credentials.email)
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Convert user to profile format
    user_profile = schemas.UserProfile.from_orm(user)
    if user.medical_conditions:
        user_profile.medical_conditions = json.loads(user.medical_conditions)
    if user.allergies:
        user_profile.allergies = json.loads(user.allergies)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user_profile
    }

@app.get("/auth/me", response_model=schemas.UserProfile)
async def get_current_user_profile(current_user: models.User = Depends(get_current_active_user)):
    """Get current user profile."""
    user_profile = schemas.UserProfile.from_orm(current_user)
    if current_user.medical_conditions:
        user_profile.medical_conditions = json.loads(current_user.medical_conditions)
    if current_user.allergies:
        user_profile.allergies = json.loads(current_user.allergies)
    return user_profile

@app.put("/auth/profile", response_model=schemas.UserProfile)
async def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile and delivery address."""
    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_profile = schemas.UserProfile.from_orm(updated_user)
    if updated_user.medical_conditions:
        user_profile.medical_conditions = json.loads(updated_user.medical_conditions)
    if updated_user.allergies:
        user_profile.allergies = json.loads(updated_user.allergies)
    return user_profile

@app.post("/auth/verify-phone", response_model=schemas.MessageResponse)
async def verify_phone_number(
    verification: schemas.PhoneVerification,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify phone number for delivery."""
    # In production, you would verify the actual code sent via SMS
    # For demo purposes, we'll accept any 6-digit code
    if len(verification.verification_code) == 6 and verification.verification_code.isdigit():
        crud.verify_user_phone(db, current_user.id)
        return {"message": "Phone number verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

# Medicine Categories endpoints
@app.get("/categories", response_model=List[schemas.CategoryResponse])
async def get_medicine_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all medicine categories."""
    return crud.get_categories(db, skip=skip, limit=limit)

@app.post("/categories", response_model=schemas.CategoryResponse)
async def create_medicine_category(
    category: schemas.CategoryCreate,
    current_user: models.User = Depends(get_pharmacy_admin_user),
    db: Session = Depends(get_db)
):
    """Create new category (pharmacy admin only)."""
    return crud.create_category(db=db, category=category)

@app.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def update_medicine_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    current_user: models.User = Depends(get_pharmacy_admin_user),
    db: Session = Depends(get_db)
):
    """Update category (pharmacy admin only)."""
    updated_category = crud.update_category(db, category_id, category_update)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@app.delete("/categories/{category_id}", response_model=schemas.MessageResponse)
async def delete_medicine_category(
    category_id: int,
    current_user: models.User = Depends(get_pharmacy_admin_user),
    db: Session = Depends(get_db)
):
    """Delete category (pharmacy admin only)."""
    if crud.delete_category(db, category_id):
        return {"message": "Category deleted successfully"}
    raise HTTPException(status_code=404, detail="Category not found")

# Medicine endpoints
@app.get("/medicines", response_model=List[schemas.MedicineResponse])
async def get_medicines(
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    prescription_required: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    in_stock_only: bool = Query(True),
    quick_delivery_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all medicines with availability and pricing."""
    search_params = schemas.MedicineSearch(
        q=q,
        category_id=category_id,
        prescription_required=prescription_required,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        quick_delivery_only=quick_delivery_only
    )
    
    medicines = crud.get_medicines(db, skip=skip, limit=limit, search=search_params)
    
    # Add computed fields
    result = []
    for medicine in medicines:
        medicine_dict = schemas.MedicineResponse.from_orm(medicine).dict()
        medicine_dict['discounted_price'] = medicine.price * (1 - medicine.discount_percentage / 100)
        medicine_dict['is_in_stock'] = medicine.stock_quantity > 0
        result.append(schemas.MedicineResponse(**medicine_dict))
    
    return result

@app.post("/medicines", response_model=schemas.MedicineResponse)
async def create_medicine(
    medicine: schemas.MedicineCreate,
    current_user: models.User = Depends(get_pharmacy_admin_user),
    db: Session = Depends(get_db)
):
    """Add new medicine (pharmacy admin only)."""
    db_medicine = crud.create_medicine(db=db, medicine=medicine)
    medicine_dict = schemas.MedicineResponse.from_orm(db_medicine).dict()
    medicine_dict['discounted_price'] = db_medicine.price * (1 - db_medicine.discount_percentage / 100)
    medicine_dict['is_in_stock'] = db_medicine.stock_quantity > 0
    return schemas.MedicineResponse(**medicine_dict)

@app.put("/medicines/{medicine_id}", response_model=schemas.MedicineResponse)
async def update_medicine(
    medicine_id: int,
    medicine_update: schemas.MedicineUpdate,
    current_user: models.User = Depends(get_pharmacy_admin_user),
    db: Session = Depends(get_db)
):
    """Update medicine details (pharmacy admin only)."""
    updated_medicine = crud.update_medicine(db, medicine_id, medicine_update)
    if not updated_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    medicine_dict = schemas.MedicineResponse.from_orm(updated_medicine).dict()
    medicine_dict['discounted_price'] = updated_medicine.price * (1 - updated_medicine.discount_percentage / 100)
    medicine_dict['is_in_stock'] = updated_medicine.stock_quantity > 0
    return schemas.MedicineResponse(**medicine_dict)

@app.delete("/medicines/{medicine_id}", response_model=schemas.MessageResponse)
async def delete_medicine(
    medicine_id: int,
    current_user: models.User = Depends(get_pharmacy_admin_user),
    db: Session = Depends(get_db)
):
    """Remove medicine (pharmacy admin only)."""
    if crud.delete_medicine(db, medicine_id):
        return {"message": "Medicine deleted successfully"}
    raise HTTPException(status_code=404, detail="Medicine not found")

@app.get("/medicines/{medicine_id}/alternatives", response_model=List[schemas.MedicineResponse])
async def get_medicine_alternatives(
    medicine_id: int,
    db: Session = Depends(get_db)
):
    """Get alternative medicines for the same condition."""
    alternatives = crud.get_medicine_alternatives(db, medicine_id)
    
    result = []
    for medicine in alternatives:
        medicine_dict = schemas.MedicineResponse.from_orm(medicine).dict()
        medicine_dict['discounted_price'] = medicine.price * (1 - medicine.discount_percentage / 100)
        medicine_dict['is_in_stock'] = medicine.stock_quantity > 0
        result.append(schemas.MedicineResponse(**medicine_dict))
    
    return result

@app.patch("/medicines/{medicine_id}/stock", response_model=schemas.MedicineResponse)
async def update_medicine_stock(
    medicine_id: int,
    stock_update: schemas.MedicineStock,
    current_user: models.User = Depends(get_pharmacy_admin_user),
    db: Session = Depends(get_db)
):
    """Update medicine stock levels."""
    updated_medicine = crud.update_medicine_stock(db, medicine_id, stock_update)
    if not updated_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    medicine_dict = schemas.MedicineResponse.from_orm(updated_medicine).dict()
    medicine_dict['discounted_price'] = updated_medicine.price * (1 - updated_medicine.discount_percentage / 100)
    medicine_dict['is_in_stock'] = updated_medicine.stock_quantity > 0
    return schemas.MedicineResponse(**medicine_dict)

# Prescription endpoints
@app.post("/prescriptions/upload", response_model=schemas.PrescriptionResponse)
async def upload_prescription(
    file: UploadFile = File(...),
    doctor_name: str = Query(...),
    doctor_license: Optional[str] = Query(None),
    hospital_clinic: Optional[str] = Query(None),
    prescription_date: datetime = Query(...),
    valid_until: Optional[datetime] = Query(None),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload prescription image."""
    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/prescriptions"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = f"{upload_dir}/{current_user.id}_{int(datetime.now().timestamp())}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create prescription record
    prescription_data = schemas.PrescriptionCreate(
        doctor_name=doctor_name,
        doctor_license=doctor_license,
        hospital_clinic=hospital_clinic,
        prescription_date=prescription_date,
        valid_until=valid_until
    )
    
    db_prescription = crud.create_prescription(db, current_user.id, prescription_data)
    db_prescription.image_path = file_path
    db.commit()
    db.refresh(db_prescription)
    
    return db_prescription

@app.get("/prescriptions", response_model=List[schemas.PrescriptionResponse])
async def get_user_prescriptions(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's prescriptions."""
    return crud.get_user_prescriptions(db, current_user.id, skip=skip, limit=limit)

@app.get("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionResponse)
async def get_prescription_details(
    prescription_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific prescription details."""
    prescription = crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Check if user owns this prescription or is a pharmacist
    if prescription.user_id != current_user.id and current_user.role not in [UserRole.PHARMACIST, UserRole.PHARMACY_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to view this prescription")
    
    return prescription

@app.put("/prescriptions/{prescription_id}/verify", response_model=schemas.PrescriptionResponse)
async def verify_prescription(
    prescription_id: int,
    verification: schemas.PrescriptionVerification,
    current_user: models.User = Depends(get_pharmacist_user),
    db: Session = Depends(get_db)
):
    """Verify prescription (pharmacist only)."""
    verified_prescription = crud.verify_prescription(db, prescription_id, current_user.id, verification)
    if not verified_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return verified_prescription

@app.get("/prescriptions/{prescription_id}/medicines", response_model=List[schemas.PrescriptionItemResponse])
async def get_prescription_medicines(
    prescription_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get medicines from prescription."""
    prescription = crud.get_prescription(db, prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    
    # Check if user owns this prescription or is a pharmacist
    if prescription.user_id != current_user.id and current_user.role not in [UserRole.PHARMACIST, UserRole.PHARMACY_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to view this prescription")
    
    return crud.get_prescription_medicines(db, prescription_id)

# Shopping Cart endpoints
@app.get("/cart", response_model=schemas.CartResponse)
async def get_user_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's cart with prescription validation."""
    cart_items = crud.get_user_cart(db, current_user.id)
    
    # Convert to response format
    cart_item_responses = []
    prescription_required_items = []
    total_items = 0
    subtotal = 0.0
    estimated_delivery_time = 30  # Default
    
    for item in cart_items:
        unit_price = item.medicine.price * (1 - item.medicine.discount_percentage / 100)
        item_subtotal = unit_price * item.quantity
        
        cart_item_response = schemas.CartItemResponse(
            id=item.id,
            user_id=item.user_id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            prescription_id=item.prescription_id,
            medicine=schemas.MedicineResponse.from_orm(item.medicine),
            subtotal=item_subtotal,
            created_at=item.created_at
        )
        
        cart_item_responses.append(cart_item_response)
        
        if item.medicine.prescription_required:
            prescription_required_items.append(cart_item_response)
        
        total_items += item.quantity
        subtotal += item_subtotal
        
        # Update estimated delivery time to maximum of all items
        estimated_delivery_time = max(estimated_delivery_time, item.medicine.delivery_time_minutes)
    
    return schemas.CartResponse(
        items=cart_item_responses,
        total_items=total_items,
        subtotal=subtotal,
        estimated_delivery_time=estimated_delivery_time,
        prescription_required_items=prescription_required_items
    )

@app.post("/cart/items", response_model=schemas.CartItemResponse)
async def add_medicine_to_cart(
    cart_item: schemas.CartItemCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add medicine to cart."""
    # Verify medicine exists and is in stock
    medicine = crud.get_medicine(db, cart_item.medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    
    if medicine.stock_quantity < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # If prescription required, verify prescription
    if medicine.prescription_required and not cart_item.prescription_id:
        raise HTTPException(status_code=400, detail="Prescription required for this medicine")
    
    db_cart_item = crud.add_to_cart(db, current_user.id, cart_item)
    
    unit_price = medicine.price * (1 - medicine.discount_percentage / 100)
    return schemas.CartItemResponse(
        id=db_cart_item.id,
        user_id=db_cart_item.user_id,
        medicine_id=db_cart_item.medicine_id,
        quantity=db_cart_item.quantity,
        prescription_id=db_cart_item.prescription_id,
        medicine=schemas.MedicineResponse.from_orm(medicine),
        subtotal=unit_price * db_cart_item.quantity,
        created_at=db_cart_item.created_at
    )

@app.put("/cart/items/{cart_item_id}", response_model=schemas.CartItemResponse)
async def update_cart_item_quantity(
    cart_item_id: int,
    cart_update: schemas.CartItemUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity."""
    updated_item = crud.update_cart_item(db, cart_item_id, current_user.id, cart_update)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Get medicine for response
    medicine = crud.get_medicine(db, updated_item.medicine_id)
    unit_price = medicine.price * (1 - medicine.discount_percentage / 100)
    
    return schemas.CartItemResponse(
        id=updated_item.id,
        user_id=updated_item.user_id,
        medicine_id=updated_item.medicine_id,
        quantity=updated_item.quantity,
        prescription_id=updated_item.prescription_id,
        medicine=schemas.MedicineResponse.from_orm(medicine),
        subtotal=unit_price * updated_item.quantity,
        created_at=updated_item.created_at
    )

@app.delete("/cart/items/{cart_item_id}", response_model=schemas.MessageResponse)
async def remove_medicine_from_cart(
    cart_item_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove medicine from cart."""
    if crud.remove_from_cart(db, cart_item_id, current_user.id):
        return {"message": "Item removed from cart"}
    raise HTTPException(status_code=404, detail="Cart item not found")

@app.delete("/cart", response_model=schemas.MessageResponse)
async def clear_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear entire cart."""
    crud.clear_user_cart(db, current_user.id)
    return {"message": "Cart cleared successfully"}

# Order endpoints
@app.post("/orders", response_model=schemas.OrderResponse)
async def create_order(
    order_data: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create order from cart with delivery details."""
    try:
        db_order = crud.create_order(db, current_user.id, order_data)
        
        # Calculate estimated delivery time
        estimate = crud.calculate_delivery_estimate(order_data.delivery_urgency)
        db_order.estimated_delivery_time = datetime.utcnow() + timedelta(minutes=estimate["time"])
        db.commit()
        db.refresh(db_order)
        
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/orders", response_model=List[schemas.OrderResponse])
async def get_user_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's orders with delivery status."""
    return crud.get_user_orders(db, current_user.id, skip=skip, limit=limit)

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
async def get_order_details(
    order_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific order details."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order or has appropriate role
    if order.user_id != current_user.id and current_user.role not in [UserRole.PHARMACY_ADMIN, UserRole.DELIVERY_PARTNER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order

@app.patch("/orders/{order_id}/status", response_model=schemas.OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update order status (pharmacy/delivery partner)."""
    # Check permissions
    if current_user.role not in [UserRole.PHARMACY_ADMIN, UserRole.DELIVERY_PARTNER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to update order status")
    
    updated_order = crud.update_order_status(db, order_id, status_update)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return updated_order

# Quick Delivery Features
@app.get("/delivery/estimate", response_model=schemas.DeliveryEstimate)
async def get_delivery_estimate(
    urgency: DeliveryUrgency = Query(DeliveryUrgency.STANDARD),
):
    """Get delivery time estimate."""
    estimate = crud.calculate_delivery_estimate(urgency)
    return schemas.DeliveryEstimate(
        estimated_time_minutes=estimate["time"],
        delivery_fee=estimate["fee"],
        available_urgency_options=[DeliveryUrgency.STANDARD, DeliveryUrgency.EXPRESS, DeliveryUrgency.EMERGENCY]
    )

@app.get("/nearby-pharmacies", response_model=List[schemas.NearbyPharmacy])
async def find_nearby_pharmacies(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(10.0),
    db: Session = Depends(get_db)
):
    """Find nearby pharmacies with stock."""
    pharmacies = crud.get_nearby_pharmacies(db, latitude, longitude, radius_km)
    
    result = []
    for pharmacy in pharmacies:
        # Simple distance calculation (replace with proper geospatial calculation in production)
        distance = ((pharmacy.latitude - latitude) ** 2 + (pharmacy.longitude - longitude) ** 2) ** 0.5 * 111  # Approximate km
        
        result.append(schemas.NearbyPharmacy(
            id=pharmacy.id,
            name=pharmacy.name,
            address=pharmacy.address,
            distance_km=round(distance, 2),
            phone_number=pharmacy.phone_number,
            is_open=pharmacy.is_24_hours or True,  # Simplified logic
            has_stock=True,  # Simplified - would check actual stock
            estimated_delivery_minutes=max(10, int(distance * 3))  # 3 minutes per km
        ))
    
    return sorted(result, key=lambda x: x.distance_km)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
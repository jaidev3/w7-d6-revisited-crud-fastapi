from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta

from models import (
    User, UserRole, MedicineCategory, Medicine, MedicineAlternative,
    Prescription, PrescriptionItem, CartItem, Order, OrderItem, OrderStatus,
    DeliveryPartner, Pharmacy, PrescriptionStatus, DeliveryUrgency
)
import schemas
from security import get_password_hash, generate_order_number, generate_tracking_id

# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()

def create_user(db: Session, user: schemas.UserCreate) -> User:
    # Convert lists to JSON strings for storage
    medical_conditions = json.dumps(user.medical_conditions) if hasattr(user, 'medical_conditions') and user.medical_conditions else None
    allergies = json.dumps(user.allergies) if hasattr(user, 'allergies') and user.allergies else None
    
    db_user = User(
        email=user.email,
        phone_number=user.phone_number,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        date_of_birth=user.date_of_birth,
        role=user.role,
        medical_conditions=medical_conditions,
        allergies=allergies
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Handle JSON fields
    if 'medical_conditions' in update_data:
        update_data['medical_conditions'] = json.dumps(update_data['medical_conditions'])
    if 'allergies' in update_data:
        update_data['allergies'] = json.dumps(update_data['allergies'])
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_phone(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if db_user:
        db_user.phone_verified = True
        db.commit()
        db.refresh(db_user)
    return db_user

# Medicine Category CRUD operations
def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[MedicineCategory]:
    return db.query(MedicineCategory).filter(MedicineCategory.is_active == True).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int) -> Optional[MedicineCategory]:
    return db.query(MedicineCategory).filter(MedicineCategory.id == category_id).first()

def create_category(db: Session, category: schemas.CategoryCreate) -> MedicineCategory:
    db_category = MedicineCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate) -> Optional[MedicineCategory]:
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if db_category:
        db_category.is_active = False
        db.commit()
        return True
    return False

# Medicine CRUD operations
def get_medicines(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[schemas.MedicineSearch] = None
) -> List[Medicine]:
    query = db.query(Medicine).options(joinedload(Medicine.category)).filter(Medicine.is_active == True)
    
    if search:
        if search.q:
            query = query.filter(
                or_(
                    Medicine.name.ilike(f"%{search.q}%"),
                    Medicine.generic_name.ilike(f"%{search.q}%"),
                    Medicine.brand_name.ilike(f"%{search.q}%"),
                    Medicine.description.ilike(f"%{search.q}%")
                )
            )
        
        if search.category_id:
            query = query.filter(Medicine.category_id == search.category_id)
        
        if search.prescription_required is not None:
            query = query.filter(Medicine.prescription_required == search.prescription_required)
        
        if search.min_price is not None:
            query = query.filter(Medicine.price >= search.min_price)
        
        if search.max_price is not None:
            query = query.filter(Medicine.price <= search.max_price)
        
        if search.in_stock_only:
            query = query.filter(Medicine.stock_quantity > 0)
        
        if search.quick_delivery_only:
            query = query.filter(Medicine.is_available_for_quick_delivery == True)
    
    return query.offset(skip).limit(limit).all()

def get_medicine(db: Session, medicine_id: int) -> Optional[Medicine]:
    return db.query(Medicine).options(joinedload(Medicine.category)).filter(Medicine.id == medicine_id).first()

def create_medicine(db: Session, medicine: schemas.MedicineCreate) -> Medicine:
    # Convert lists to JSON strings for storage
    age_restrictions = json.dumps(medicine.age_restrictions) if medicine.age_restrictions else None
    tags = json.dumps(medicine.tags) if medicine.tags else None
    
    db_medicine = Medicine(
        **medicine.dict(exclude={'age_restrictions', 'tags'}),
        age_restrictions=age_restrictions,
        tags=tags
    )
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine_update: schemas.MedicineUpdate) -> Optional[Medicine]:
    db_medicine = get_medicine(db, medicine_id)
    if not db_medicine:
        return None
    
    update_data = medicine_update.dict(exclude_unset=True)
    
    # Handle JSON fields
    if 'age_restrictions' in update_data:
        update_data['age_restrictions'] = json.dumps(update_data['age_restrictions'])
    if 'tags' in update_data:
        update_data['tags'] = json.dumps(update_data['tags'])
    
    for field, value in update_data.items():
        setattr(db_medicine, field, value)
    
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine_stock(db: Session, medicine_id: int, stock_update: schemas.MedicineStock) -> Optional[Medicine]:
    db_medicine = get_medicine(db, medicine_id)
    if db_medicine:
        db_medicine.stock_quantity = stock_update.stock_quantity
        db.commit()
        db.refresh(db_medicine)
    return db_medicine

def delete_medicine(db: Session, medicine_id: int) -> bool:
    db_medicine = get_medicine(db, medicine_id)
    if db_medicine:
        db_medicine.is_active = False
        db.commit()
        return True
    return False

def get_medicine_alternatives(db: Session, medicine_id: int) -> List[Medicine]:
    alternatives = db.query(MedicineAlternative).filter(
        MedicineAlternative.medicine_id == medicine_id
    ).all()
    
    alternative_ids = [alt.alternative_medicine_id for alt in alternatives]
    return db.query(Medicine).filter(Medicine.id.in_(alternative_ids)).all()

# Prescription CRUD operations
def get_user_prescriptions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Prescription]:
    return db.query(Prescription).filter(
        and_(Prescription.user_id == user_id, Prescription.is_active == True)
    ).offset(skip).limit(limit).all()

def get_prescription(db: Session, prescription_id: int) -> Optional[Prescription]:
    return db.query(Prescription).options(
        joinedload(Prescription.items).joinedload(PrescriptionItem.medicine)
    ).filter(Prescription.id == prescription_id).first()

def create_prescription(db: Session, user_id: int, prescription: schemas.PrescriptionCreate) -> Prescription:
    db_prescription = Prescription(
        user_id=user_id,
        **prescription.dict()
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def verify_prescription(
    db: Session, 
    prescription_id: int, 
    pharmacist_id: int, 
    verification: schemas.PrescriptionVerification
) -> Optional[Prescription]:
    db_prescription = get_prescription(db, prescription_id)
    if not db_prescription:
        return None
    
    db_prescription.status = verification.status
    db_prescription.verification_notes = verification.verification_notes
    db_prescription.verified_by_pharmacist_id = pharmacist_id
    db_prescription.verified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def get_prescription_medicines(db: Session, prescription_id: int) -> List[PrescriptionItem]:
    return db.query(PrescriptionItem).options(
        joinedload(PrescriptionItem.medicine)
    ).filter(PrescriptionItem.prescription_id == prescription_id).all()

# Cart CRUD operations
def get_user_cart(db: Session, user_id: int) -> List[CartItem]:
    return db.query(CartItem).options(
        joinedload(CartItem.medicine).joinedload(Medicine.category)
    ).filter(CartItem.user_id == user_id).all()

def add_to_cart(db: Session, user_id: int, cart_item: schemas.CartItemCreate) -> CartItem:
    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        and_(
            CartItem.user_id == user_id,
            CartItem.medicine_id == cart_item.medicine_id,
            CartItem.prescription_id == cart_item.prescription_id
        )
    ).first()
    
    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        db_cart_item = CartItem(
            user_id=user_id,
            **cart_item.dict()
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

def update_cart_item(db: Session, cart_item_id: int, user_id: int, update: schemas.CartItemUpdate) -> Optional[CartItem]:
    db_cart_item = db.query(CartItem).filter(
        and_(CartItem.id == cart_item_id, CartItem.user_id == user_id)
    ).first()
    
    if db_cart_item:
        db_cart_item.quantity = update.quantity
        db.commit()
        db.refresh(db_cart_item)
    
    return db_cart_item

def remove_from_cart(db: Session, cart_item_id: int, user_id: int) -> bool:
    db_cart_item = db.query(CartItem).filter(
        and_(CartItem.id == cart_item_id, CartItem.user_id == user_id)
    ).first()
    
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
        return True
    return False

def clear_user_cart(db: Session, user_id: int) -> bool:
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    return True

# Order CRUD operations
def create_order(db: Session, user_id: int, order_data: schemas.OrderCreate) -> Order:
    # Get cart items
    cart_items = get_user_cart(db, user_id)
    if not cart_items:
        raise ValueError("Cart is empty")
    
    # Calculate totals
    subtotal = sum(item.quantity * item.medicine.price * (1 - item.medicine.discount_percentage / 100) for item in cart_items)
    
    # Calculate delivery fee based on urgency
    delivery_fee = 0.0
    if order_data.delivery_urgency == DeliveryUrgency.EXPRESS:
        delivery_fee = 50.0
    elif order_data.delivery_urgency == DeliveryUrgency.EMERGENCY:
        delivery_fee = 150.0
    
    total_amount = subtotal + delivery_fee
    
    # Create order
    db_order = Order(
        user_id=user_id,
        order_number=generate_order_number(),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        delivery_tracking_id=generate_tracking_id(),
        **order_data.dict()
    )
    db.add(db_order)
    db.flush()  # Get the order ID
    
    # Create order items
    for cart_item in cart_items:
        unit_price = cart_item.medicine.price * (1 - cart_item.medicine.discount_percentage / 100)
        db_order_item = OrderItem(
            order_id=db_order.id,
            medicine_id=cart_item.medicine_id,
            quantity=cart_item.quantity,
            unit_price=unit_price,
            total_price=unit_price * cart_item.quantity,
            prescription_id=cart_item.prescription_id
        )
        db.add(db_order_item)
        
        # Update medicine stock
        cart_item.medicine.stock_quantity -= cart_item.quantity
    
    # Clear cart
    clear_user_cart(db, user_id)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.medicine)
    ).filter(Order.user_id == user_id).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()

def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.medicine).joinedload(Medicine.category)
    ).filter(Order.id == order_id).first()

def update_order_status(db: Session, order_id: int, status_update: schemas.OrderStatusUpdate) -> Optional[Order]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db_order.status = status_update.status
    
    if status_update.status == OrderStatus.DELIVERED:
        db_order.actual_delivery_time = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    return db_order

# Delivery and location operations
def get_nearby_pharmacies(db: Session, latitude: float, longitude: float, radius_km: float = 10.0) -> List[Pharmacy]:
    # Simple distance calculation (for production, use PostGIS or similar)
    return db.query(Pharmacy).filter(
        and_(
            Pharmacy.is_active == True,
            func.abs(Pharmacy.latitude - latitude) < 0.01 * radius_km,  # Approximate
            func.abs(Pharmacy.longitude - longitude) < 0.01 * radius_km
        )
    ).all()

def get_available_delivery_partners(db: Session, latitude: float, longitude: float, radius_km: float = 10.0) -> List[DeliveryPartner]:
    return db.query(DeliveryPartner).join(User).filter(
        and_(
            DeliveryPartner.is_available == True,
            User.is_active == True,
            func.abs(DeliveryPartner.current_latitude - latitude) < 0.01 * radius_km,
            func.abs(DeliveryPartner.current_longitude - longitude) < 0.01 * radius_km
        )
    ).all()

def calculate_delivery_estimate(urgency: DeliveryUrgency) -> Dict[str, Any]:
    estimates = {
        DeliveryUrgency.STANDARD: {"time": 30, "fee": 0.0},
        DeliveryUrgency.EXPRESS: {"time": 15, "fee": 50.0},
        DeliveryUrgency.EMERGENCY: {"time": 10, "fee": 150.0}
    }
    return estimates.get(urgency, estimates[DeliveryUrgency.STANDARD]) 
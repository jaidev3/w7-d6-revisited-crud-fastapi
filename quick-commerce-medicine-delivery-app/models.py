from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    PHARMACY_ADMIN = "pharmacy_admin"
    PHARMACIST = "pharmacist"
    DELIVERY_PARTNER = "delivery_partner"
    ADMIN = "admin"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PrescriptionStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class DeliveryUrgency(str, enum.Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    EMERGENCY = "emergency"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    phone_verified = Column(Boolean, default=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    
    # Address information
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Medical profile
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    medical_conditions = Column(Text, nullable=True)  # JSON string
    allergies = Column(Text, nullable=True)  # JSON string
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    prescriptions = relationship("Prescription", back_populates="user")
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")

class MedicineCategory(Base):
    __tablename__ = "medicine_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)  # Icon name or URL
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    medicines = relationship("Medicine", back_populates="category")

class Medicine(Base):
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    generic_name = Column(String, nullable=True)
    brand_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    category_id = Column(Integer, ForeignKey("medicine_categories.id"))
    
    # Pricing and stock
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0.0)
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    
    # Medicine specifications
    dosage_form = Column(String, nullable=True)  # tablet, capsule, syrup, etc.
    strength = Column(String, nullable=True)  # 500mg, 10ml, etc.
    pack_size = Column(String, nullable=True)  # 10 tablets, 100ml bottle
    manufacturer = Column(String, nullable=True)
    
    # Prescription and safety
    prescription_required = Column(Boolean, default=False)
    age_restrictions = Column(String, nullable=True)  # JSON string
    contraindications = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    
    # Quick commerce features
    delivery_time_minutes = Column(Integer, default=30)
    is_available_for_quick_delivery = Column(Boolean, default=True)
    
    # SEO and search
    tags = Column(Text, nullable=True)  # JSON string for search tags
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("MedicineCategory", back_populates="medicines")
    alternatives = relationship("MedicineAlternative", foreign_keys="MedicineAlternative.medicine_id", back_populates="medicine")
    prescription_items = relationship("PrescriptionItem", back_populates="medicine")
    cart_items = relationship("CartItem", back_populates="medicine")
    order_items = relationship("OrderItem", back_populates="medicine")

class MedicineAlternative(Base):
    __tablename__ = "medicine_alternatives"
    
    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    alternative_medicine_id = Column(Integer, ForeignKey("medicines.id"))
    reason = Column(String, nullable=True)  # same_generic, same_category, etc.
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    medicine = relationship("Medicine", foreign_keys=[medicine_id])
    alternative = relationship("Medicine", foreign_keys=[alternative_medicine_id])

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Prescription details
    doctor_name = Column(String, nullable=False)
    doctor_license = Column(String, nullable=True)
    hospital_clinic = Column(String, nullable=True)
    prescription_date = Column(DateTime, nullable=False)
    
    # Image and verification
    image_path = Column(String, nullable=True)
    status = Column(Enum(PrescriptionStatus), default=PrescriptionStatus.PENDING)
    verified_by_pharmacist_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Validity
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="prescriptions")
    verified_by = relationship("User", foreign_keys=[verified_by_pharmacist_id])
    items = relationship("PrescriptionItem", back_populates="prescription")

class PrescriptionItem(Base):
    __tablename__ = "prescription_items"
    
    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    
    dosage = Column(String, nullable=True)
    frequency = Column(String, nullable=True)  # twice daily, once at night, etc.
    duration = Column(String, nullable=True)  # 7 days, 2 weeks, etc.
    quantity_prescribed = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    prescription = relationship("Prescription", back_populates="items")
    medicine = relationship("Medicine", back_populates="prescription_items")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    
    quantity = Column(Integer, nullable=False, default=1)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    medicine = relationship("Medicine", back_populates="cart_items")
    prescription = relationship("Prescription")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_number = Column(String, unique=True, nullable=False)
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Delivery details
    delivery_address = Column(Text, nullable=False)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    delivery_urgency = Column(Enum(DeliveryUrgency), default=DeliveryUrgency.STANDARD)
    estimated_delivery_time = Column(DateTime, nullable=True)
    actual_delivery_time = Column(DateTime, nullable=True)
    
    # Status and tracking
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    delivery_partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    delivery_tracking_id = Column(String, nullable=True)
    delivery_proof_image = Column(String, nullable=True)
    
    # Notes
    special_instructions = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="orders")
    delivery_partner = relationship("User", foreign_keys=[delivery_partner_id])
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    medicine = relationship("Medicine", back_populates="order_items")
    prescription = relationship("Prescription")

class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Partner details
    license_number = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)  # bike, car, etc.
    vehicle_number = Column(String, nullable=True)
    
    # Location and availability
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    is_available = Column(Boolean, default=True)
    max_delivery_radius_km = Column(Float, default=10.0)
    
    # Ratings and performance
    rating = Column(Float, default=5.0)
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")

class Pharmacy(Base):
    __tablename__ = "pharmacies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    
    # Address
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Contact
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    
    # Operating hours
    opening_time = Column(String, nullable=True)  # "09:00"
    closing_time = Column(String, nullable=True)  # "22:00"
    is_24_hours = Column(Boolean, default=False)
    
    # Features
    has_quick_delivery = Column(Boolean, default=True)
    delivery_radius_km = Column(Float, default=5.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now()) 
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, UserRole, MedicineCategory, Medicine, Pharmacy, DeliveryPartner
from security import get_password_hash
import json

# Create tables
Base.metadata.create_all(bind=engine)

def create_sample_data():
    """Create sample data for testing the application."""
    db = SessionLocal()
    
    try:
        # Create sample categories
        categories_data = [
            {"name": "Pain Relief", "description": "Medicines for pain management", "icon": "🩹"},
            {"name": "Antibiotics", "description": "Antibacterial medications", "icon": "💊"},
            {"name": "Vitamins & Supplements", "description": "Health supplements and vitamins", "icon": "🌟"},
            {"name": "Cold & Flu", "description": "Medicines for cold and flu symptoms", "icon": "🤧"},
            {"name": "Digestive Health", "description": "Medicines for digestive issues", "icon": "🍽️"},
            {"name": "Heart & Blood Pressure", "description": "Cardiovascular medications", "icon": "❤️"},
            {"name": "Diabetes Care", "description": "Diabetes management medicines", "icon": "🩸"},
            {"name": "Skin Care", "description": "Dermatological medications", "icon": "🧴"},
            {"name": "Baby Care", "description": "Medicines for infants and children", "icon": "👶"},
            {"name": "Women's Health", "description": "Women's healthcare products", "icon": "👩‍⚕️"}
        ]
        
        categories = []
        for cat_data in categories_data:
            category = MedicineCategory(**cat_data)
            db.add(category)
            categories.append(category)
        
        db.commit()
        
        # Create sample medicines
        medicines_data = [
            # Pain Relief
            {
                "name": "Paracetamol",
                "generic_name": "Acetaminophen",
                "brand_name": "Crocin",
                "description": "Effective pain relief and fever reducer",
                "category_id": 1,
                "price": 25.50,
                "stock_quantity": 500,
                "dosage_form": "Tablet",
                "strength": "500mg",
                "pack_size": "10 tablets",
                "manufacturer": "GSK",
                "prescription_required": False,
                "delivery_time_minutes": 15,
                "tags": json.dumps(["fever", "headache", "pain", "common"])
            },
            {
                "name": "Ibuprofen",
                "generic_name": "Ibuprofen",
                "brand_name": "Brufen",
                "description": "Anti-inflammatory pain reliever",
                "category_id": 1,
                "price": 45.00,
                "stock_quantity": 300,
                "dosage_form": "Tablet",
                "strength": "400mg",
                "pack_size": "20 tablets",
                "manufacturer": "Abbott",
                "prescription_required": False,
                "delivery_time_minutes": 15,
                "tags": json.dumps(["inflammation", "pain", "arthritis"])
            },
            
            # Antibiotics
            {
                "name": "Amoxicillin",
                "generic_name": "Amoxicillin",
                "brand_name": "Moxikind",
                "description": "Broad-spectrum antibiotic",
                "category_id": 2,
                "price": 120.00,
                "stock_quantity": 150,
                "dosage_form": "Capsule",
                "strength": "500mg",
                "pack_size": "10 capsules",
                "manufacturer": "Mankind",
                "prescription_required": True,
                "delivery_time_minutes": 20,
                "contraindications": "Penicillin allergy",
                "tags": json.dumps(["infection", "bacteria", "prescription"])
            },
            {
                "name": "Azithromycin",
                "generic_name": "Azithromycin",
                "brand_name": "Azee",
                "description": "Macrolide antibiotic for infections",
                "category_id": 2,
                "price": 95.00,
                "stock_quantity": 100,
                "dosage_form": "Tablet",
                "strength": "500mg",
                "pack_size": "3 tablets",
                "manufacturer": "Cipla",
                "prescription_required": True,
                "delivery_time_minutes": 20,
                "tags": json.dumps(["respiratory", "infection", "prescription"])
            },
            
            # Vitamins
            {
                "name": "Vitamin D3",
                "generic_name": "Cholecalciferol",
                "brand_name": "Calcirol",
                "description": "Vitamin D supplement for bone health",
                "category_id": 3,
                "price": 180.00,
                "discount_percentage": 10.0,
                "stock_quantity": 200,
                "dosage_form": "Granules",
                "strength": "60000 IU",
                "pack_size": "4 sachets",
                "manufacturer": "Cadila",
                "prescription_required": False,
                "delivery_time_minutes": 25,
                "tags": json.dumps(["vitamin", "bones", "immunity"])
            },
            {
                "name": "Multivitamin",
                "generic_name": "Multivitamin",
                "brand_name": "Revital",
                "description": "Complete multivitamin supplement",
                "category_id": 3,
                "price": 350.00,
                "discount_percentage": 15.0,
                "stock_quantity": 150,
                "dosage_form": "Capsule",
                "strength": "Mixed",
                "pack_size": "30 capsules",
                "manufacturer": "Ranbaxy",
                "prescription_required": False,
                "delivery_time_minutes": 25,
                "tags": json.dumps(["multivitamin", "energy", "health"])
            },
            
            # Cold & Flu
            {
                "name": "Cetirizine",
                "generic_name": "Cetirizine",
                "brand_name": "Zyrtec",
                "description": "Antihistamine for allergies and cold",
                "category_id": 4,
                "price": 35.00,
                "stock_quantity": 400,
                "dosage_form": "Tablet",
                "strength": "10mg",
                "pack_size": "10 tablets",
                "manufacturer": "UCB",
                "prescription_required": False,
                "delivery_time_minutes": 15,
                "side_effects": "May cause drowsiness",
                "tags": json.dumps(["allergy", "cold", "antihistamine"])
            },
            {
                "name": "Cough Syrup",
                "generic_name": "Dextromethorphan",
                "brand_name": "Benadryl",
                "description": "Effective cough suppressant",
                "category_id": 4,
                "price": 85.00,
                "stock_quantity": 250,
                "dosage_form": "Syrup",
                "strength": "100ml",
                "pack_size": "100ml bottle",
                "manufacturer": "Johnson & Johnson",
                "prescription_required": False,
                "delivery_time_minutes": 20,
                "tags": json.dumps(["cough", "syrup", "cold"])
            },
            
            # Digestive Health
            {
                "name": "Omeprazole",
                "generic_name": "Omeprazole",
                "brand_name": "Prilosec",
                "description": "Proton pump inhibitor for acidity",
                "category_id": 5,
                "price": 75.00,
                "stock_quantity": 180,
                "dosage_form": "Capsule",
                "strength": "20mg",
                "pack_size": "14 capsules",
                "manufacturer": "Dr. Reddy's",
                "prescription_required": False,
                "delivery_time_minutes": 20,
                "tags": json.dumps(["acidity", "heartburn", "stomach"])
            },
            {
                "name": "Probiotic",
                "generic_name": "Lactobacillus",
                "brand_name": "Enterogermina",
                "description": "Probiotic for digestive health",
                "category_id": 5,
                "price": 140.00,
                "stock_quantity": 120,
                "dosage_form": "Vial",
                "strength": "2 billion CFU",
                "pack_size": "10 vials",
                "manufacturer": "Sanofi",
                "prescription_required": False,
                "delivery_time_minutes": 25,
                "tags": json.dumps(["probiotic", "digestion", "gut health"])
            },
            
            # Heart & Blood Pressure
            {
                "name": "Amlodipine",
                "generic_name": "Amlodipine",
                "brand_name": "Norvasc",
                "description": "Calcium channel blocker for hypertension",
                "category_id": 6,
                "price": 65.00,
                "stock_quantity": 200,
                "dosage_form": "Tablet",
                "strength": "5mg",
                "pack_size": "30 tablets",
                "manufacturer": "Pfizer",
                "prescription_required": True,
                "delivery_time_minutes": 20,
                "contraindications": "Severe heart failure",
                "tags": json.dumps(["blood pressure", "hypertension", "prescription"])
            },
            
            # Diabetes Care
            {
                "name": "Metformin",
                "generic_name": "Metformin",
                "brand_name": "Glucophage",
                "description": "Blood sugar control medication",
                "category_id": 7,
                "price": 45.00,
                "stock_quantity": 300,
                "dosage_form": "Tablet",
                "strength": "500mg",
                "pack_size": "20 tablets",
                "manufacturer": "Sun Pharma",
                "prescription_required": True,
                "delivery_time_minutes": 20,
                "tags": json.dumps(["diabetes", "blood sugar", "prescription"])
            }
        ]
        
        for med_data in medicines_data:
            medicine = Medicine(**med_data)
            db.add(medicine)
        
        db.commit()
        
        # Create sample users
        users_data = [
            {
                "email": "customer@example.com",
                "phone_number": "+91 9876543210",
                "password_hash": get_password_hash("password123"),
                "full_name": "John Customer",
                "role": UserRole.CUSTOMER,
                "address_line1": "123 Health Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "phone_verified": True,
                "medical_conditions": json.dumps(["Hypertension"]),
                "allergies": json.dumps(["Penicillin"])
            },
            {
                "email": "pharmacist@example.com",
                "phone_number": "+91 9876543211",
                "password_hash": get_password_hash("pharmacist123"),
                "full_name": "Dr. Sarah Pharmacist",
                "role": UserRole.PHARMACIST,
                "phone_verified": True
            },
            {
                "email": "admin@example.com",
                "phone_number": "+91 9876543212",
                "password_hash": get_password_hash("admin123"),
                "full_name": "Admin User",
                "role": UserRole.PHARMACY_ADMIN,
                "phone_verified": True
            },
            {
                "email": "delivery@example.com",
                "phone_number": "+91 9876543213",
                "password_hash": get_password_hash("delivery123"),
                "full_name": "Raj Delivery",
                "role": UserRole.DELIVERY_PARTNER,
                "phone_verified": True
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
            users.append(user)
        
        db.commit()
        
        # Create sample pharmacies
        pharmacies_data = [
            {
                "name": "MedPlus Pharmacy",
                "license_number": "MH-PHM-2023-001",
                "address": "Shop 15, Health Complex, Andheri West, Mumbai - 400058",
                "latitude": 19.1367,
                "longitude": 72.8258,
                "phone_number": "+91 22 26742000",
                "email": "andheri@medplus.in",
                "opening_time": "08:00",
                "closing_time": "22:00",
                "has_quick_delivery": True,
                "delivery_radius_km": 8.0
            },
            {
                "name": "Apollo Pharmacy",
                "license_number": "MH-PHM-2023-002",
                "address": "Ground Floor, Linking Road, Bandra West, Mumbai - 400050",
                "latitude": 19.0596,
                "longitude": 72.8295,
                "phone_number": "+91 22 26430000",
                "email": "bandra@apollopharmacy.in",
                "is_24_hours": True,
                "has_quick_delivery": True,
                "delivery_radius_km": 10.0
            },
            {
                "name": "NetMeds QuickRx",
                "license_number": "MH-PHM-2023-003",
                "address": "Unit 3, Medical Plaza, Powai, Mumbai - 400076",
                "latitude": 19.1197,
                "longitude": 72.9095,
                "phone_number": "+91 22 67890000",
                "email": "powai@netmeds.com",
                "opening_time": "07:00",
                "closing_time": "23:00",
                "has_quick_delivery": True,
                "delivery_radius_km": 12.0
            }
        ]
        
        for pharmacy_data in pharmacies_data:
            pharmacy = Pharmacy(**pharmacy_data)
            db.add(pharmacy)
        
        db.commit()
        
        # Create sample delivery partners
        delivery_partners_data = [
            {
                "user_id": users[3].id,  # Delivery user
                "license_number": "DL-2023-001",
                "vehicle_type": "Motorcycle",
                "vehicle_number": "MH-01-AB-1234",
                "current_latitude": 19.0760,
                "current_longitude": 72.8777,
                "is_available": True,
                "max_delivery_radius_km": 15.0,
                "rating": 4.8,
                "total_deliveries": 245,
                "successful_deliveries": 238
            }
        ]
        
        for dp_data in delivery_partners_data:
            delivery_partner = DeliveryPartner(**dp_data)
            db.add(delivery_partner)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print("\n📋 Test Accounts:")
        print("👤 Customer: customer@example.com / password123")
        print("💊 Pharmacist: pharmacist@example.com / pharmacist123")
        print("🏥 Admin: admin@example.com / admin123")
        print("🚚 Delivery: delivery@example.com / delivery123")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data() 
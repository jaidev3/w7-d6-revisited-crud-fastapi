# 💊 QuickMed - Medicine Delivery Platform

A comprehensive quick commerce medicine delivery application built with FastAPI backend and Streamlit frontend, featuring user authentication, medicine catalog management, prescription handling, and rapid delivery functionality.

## 🌟 Features

### 🔐 Authentication & User Management
- User registration with medical profiles
- Role-based access control (Customer, Pharmacist, Admin, Delivery Partner)
- Phone number verification for delivery
- Profile management with delivery addresses
- Medical conditions and allergy tracking

### 💊 Medicine Catalog
- Comprehensive medicine database with categories
- Advanced search and filtering
- Stock management and pricing
- Alternative medicine suggestions
- Prescription requirement validation
- Quick delivery availability tracking

### 📋 Prescription Management
- Prescription image upload
- Pharmacist verification system
- Valid prescription tracking
- Prescription-based medicine ordering

### 🛒 Shopping Cart & Orders
- Smart cart with prescription validation
- Multiple delivery urgency options (Standard/Express/Emergency)
- Real-time order tracking
- Delivery partner assignment
- Order history and management

### 🚚 Quick Commerce Features
- **10-30 minute delivery promise**
- Real-time inventory tracking
- Dynamic pricing based on urgency
- Location-based medicine availability
- Emergency delivery requests
- Nearby pharmacy finder

### ♿ Accessibility Features
- High contrast mode
- Large text support
- Screen reader compatibility
- Elderly-friendly interface
- Voice guidance support

## 🏗️ Architecture

### Backend (FastAPI)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with role-based access
- **Security**: Password hashing, input validation
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend (Streamlit)
- **Modern UI**: Responsive design with accessibility features
- **Real-time Updates**: Live order tracking and cart updates
- **Maps Integration**: Delivery tracking with Folium
- **File Upload**: Prescription image handling

## 📁 Project Structure

```
quick-commerce-medicine-delivery-app/
├── main.py                 # FastAPI application with all endpoints
├── streamlit_app.py        # Streamlit UI application
├── models.py              # Database models (SQLAlchemy)
├── schemas.py             # Pydantic schemas for API
├── crud.py                # Database operations
├── auth.py                # Authentication dependencies
├── security.py            # Security utilities (JWT, hashing)
├── database.py            # Database configuration
├── sample_data.py         # Sample data creation script
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── uploads/              # Prescription image uploads (created automatically)
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd quick-commerce-medicine-delivery-app

# Activate virtual environment (if using venv)
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create sample data (or run the setup script)
python sample_data.py
# OR run the automated setup script:
python setup.py
```

### 3. Run the Application

```bash
# Make sure virtual environment is activated
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate

# Terminal 1: Start FastAPI backend
python main.py
# API will be available at http://localhost:8000
# API docs at http://localhost:8000/docs

# Terminal 2: Start Streamlit frontend (in new terminal with venv activated)
streamlit run streamlit_app.py
# UI will be available at http://localhost:8501
```

## 👥 Test Accounts

After running `sample_data.py`, you can use these test accounts:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| **Customer** | customer@example.com | password123 | Regular user account |
| **Pharmacist** | pharmacist@example.com | pharmacist123 | Can verify prescriptions |
| **Admin** | admin@example.com | admin123 | Pharmacy admin with full access |
| **Delivery** | delivery@example.com | delivery123 | Delivery partner account |

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile
- `PUT /auth/profile` - Update user profile
- `POST /auth/verify-phone` - Verify phone number

### Medicine Management
- `GET /medicines` - Browse medicines with search/filter
- `POST /medicines` - Add new medicine (admin only)
- `PUT /medicines/{id}` - Update medicine (admin only)
- `DELETE /medicines/{id}` - Remove medicine (admin only)
- `GET /medicines/{id}/alternatives` - Get alternative medicines
- `PATCH /medicines/{id}/stock` - Update stock levels

### Categories
- `GET /categories` - Get all categories
- `POST /categories` - Create category (admin only)
- `PUT /categories/{id}` - Update category (admin only)
- `DELETE /categories/{id}` - Delete category (admin only)

### Prescriptions
- `POST /prescriptions/upload` - Upload prescription image
- `GET /prescriptions` - Get user's prescriptions
- `GET /prescriptions/{id}` - Get prescription details
- `PUT /prescriptions/{id}/verify` - Verify prescription (pharmacist only)
- `GET /prescriptions/{id}/medicines` - Get prescription medicines

### Shopping Cart
- `GET /cart` - Get user's cart
- `POST /cart/items` - Add medicine to cart
- `PUT /cart/items/{id}` - Update cart item quantity
- `DELETE /cart/items/{id}` - Remove from cart
- `DELETE /cart` - Clear entire cart

### Orders & Delivery
- `POST /orders` - Create order from cart
- `GET /orders` - Get user's orders
- `GET /orders/{id}` - Get order details
- `PATCH /orders/{id}/status` - Update order status
- `GET /delivery/estimate` - Get delivery estimate
- `GET /nearby-pharmacies` - Find nearby pharmacies

## 🎯 Key Features Walkthrough

### 1. Quick Commerce Shopping Experience
1. **Browse Medicines**: Search by name, category, or condition
2. **Smart Filtering**: Filter by prescription requirement, price, delivery time
3. **Add to Cart**: Automatic prescription validation
4. **Quick Checkout**: Choose delivery urgency (10-30 mins)
5. **Real-time Tracking**: Live order and delivery tracking

### 2. Prescription Management
1. **Upload Prescription**: Take photo of doctor's prescription
2. **Pharmacist Verification**: Licensed pharmacist reviews and approves
3. **Smart Cart Integration**: Prescription medicines auto-linked to cart
4. **Validity Tracking**: Monitor prescription expiration dates

### 3. Emergency Delivery
1. **Emergency Mode**: 10-minute delivery for urgent needs
2. **Priority Processing**: Fast-track through pharmacy preparation
3. **Dedicated Partners**: Emergency delivery partner network
4. **Real-time Communication**: Direct contact with delivery partner

### 4. Accessibility Features
1. **Visual Aids**: High contrast mode, large text options
2. **Navigation**: Keyboard-friendly interface
3. **Clear Communication**: Simple language, clear instructions
4. **Emergency Support**: Quick access to emergency contacts

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production deployment:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./medicine_delivery.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
API_BASE_URL=http://localhost:8000
```

### Database Configuration
The application uses SQLite by default. For production, update `database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost/dbname"
# or
DATABASE_URL = "mysql://user:password@localhost/dbname"
```

## 📱 Mobile Responsiveness

The Streamlit interface is optimized for mobile devices with:
- Touch-friendly buttons and controls
- Responsive grid layouts
- Mobile-optimized forms
- Swipe-friendly navigation

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Role-based Access**: Different permissions for different user types
- **Input Validation**: Comprehensive data validation
- **File Upload Security**: Secure prescription image handling

## 🚀 Deployment

### Docker Deployment (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "python main.py & streamlit run streamlit_app.py --server.address=0.0.0.0"]
```

### Cloud Deployment
- **Backend**: Deploy FastAPI on Heroku, AWS, or Google Cloud
- **Frontend**: Deploy Streamlit on Streamlit Cloud or any cloud provider
- **Database**: Use PostgreSQL or MySQL for production

## 🧪 Testing

### API Testing
Access the interactive API documentation at `http://localhost:8000/docs` to test all endpoints.

### Sample Workflows

1. **Customer Journey**:
   - Register → Verify Phone → Upload Prescription → Browse Medicines → Add to Cart → Place Order → Track Delivery

2. **Pharmacist Workflow**:
   - Login → Review Prescriptions → Verify/Reject → Update Stock → Monitor Orders

3. **Admin Tasks**:
   - Manage Medicine Catalog → Add Categories → Update Pricing → Monitor System

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact: support@quickmed.com
- Emergency: +91 9876543210

## 🌟 Acknowledgments

- Built with FastAPI and Streamlit
- Icons from Unicode Emoji
- Maps powered by Folium
- Designed for accessibility and ease of use

---

**Made with ❤️ for better healthcare accessibility** 
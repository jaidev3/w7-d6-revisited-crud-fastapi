# Quick Commerce Medicine Delivery API

A comprehensive FastAPI-based medicine delivery platform with quick commerce features, user authentication, prescription management, and real-time order tracking.

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd quick-commerce-medicine-delivery-app
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```

3. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Admin Dashboard: `streamlit run streamlit_app.py`

### Production Deployment

This application is configured for easy deployment to **Render**. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

#### Quick Deploy to Render
1. Push code to GitHub
2. Connect repository to Render
3. Use the included `render.yaml` for automatic deployment
4. Set required environment variables

## 📋 Features

### Core Functionality
- **User Management**: Registration, authentication, profile management
- **Medicine Catalog**: Browse, search, and filter medicines
- **Prescription Handling**: Upload and manage prescriptions
- **Order Management**: Place orders, track delivery, payment processing
- **Real-time Tracking**: Live order and delivery tracking
- **Multi-user Roles**: Customers, pharmacists, delivery partners, admins

### Technical Features
- **FastAPI Framework**: High-performance async API
- **SQLAlchemy ORM**: Database abstraction and migrations
- **JWT Authentication**: Secure token-based authentication
- **File Upload**: Prescription image handling
- **Geolocation**: Distance calculation and routing
- **Health Monitoring**: Built-in health checks

## 🛠 Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT tokens with bcrypt hashing
- **File Storage**: Local filesystem with upload management
- **Frontend**: Streamlit admin dashboard
- **Deployment**: Render with automatic scaling

## 📁 Project Structure

```
quick-commerce-medicine-delivery-app/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic data validation schemas
├── crud.py              # Database operations
├── auth.py              # Authentication logic
├── security.py          # Security utilities
├── database.py          # Database configuration
├── sample_data.py       # Sample data for testing
├── streamlit_app.py     # Admin dashboard
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
├── Procfile            # Alternative deployment config
├── runtime.txt         # Python version specification
├── migrate_db.py       # Database migration script
├── env.example         # Environment variables template
├── DEPLOYMENT.md       # Deployment guide
└── uploads/            # File upload directory
    └── prescriptions/  # Prescription images
```

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Required for production
ENVIRONMENT=production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional
ACCESS_TOKEN_EXPIRE_MINUTES=1440
MAX_FILE_SIZE=10485760
```

### Database Setup

**Development (SQLite)**:
```bash
python sample_data.py  # Create sample data
```

**Production (PostgreSQL)**:
```bash
python migrate_db.py   # Run migrations
python sample_data.py  # Optional: Load sample data
```

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token

### User Management
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update profile
- `POST /users/medical-profile` - Add medical info

### Medicine & Pharmacy
- `GET /medicines` - Browse medicines
- `GET /pharmacies` - Find pharmacies
- `GET /inventory` - Check medicine availability

### Orders & Delivery
- `POST /orders` - Place order
- `GET /orders/{id}` - Track order
- `POST /prescriptions` - Upload prescription
- `GET /deliveries/{id}` - Track delivery

### Admin Functions
- `GET /admin/dashboard` - Admin overview
- `GET /admin/users` - Manage users
- `GET /admin/orders` - Manage orders

## 🧪 Testing

### API Testing
```bash
# Run test script
python test_api.py

# Manual testing with curl
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/docs"
```

### Load Testing
```bash
# Install testing tools
pip install pytest httpx

# Run tests
pytest test_*.py
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for password security
- **Role-based Access**: Different permissions per user type
- **Input Validation**: Pydantic schema validation
- **File Upload Security**: Type and size validation
- **CORS Configuration**: Configurable cross-origin requests

## 📈 Monitoring & Maintenance

### Health Checks
- `GET /health` - Application health status
- Database connection monitoring
- Automatic error logging

### Performance
- Gunicorn with multiple workers
- Database connection pooling
- Async request handling
- Optimized query patterns

## 🚀 Production Deployment

### Render (Recommended)
1. Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide
2. Use included `render.yaml` configuration
3. Set environment variables
4. Deploy with one click

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python migrate_db.py

# Start application
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check `/docs` endpoint for API documentation
- **Issues**: Create GitHub issues for bugs or feature requests
- **Deployment Help**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guides

## 🔄 Recent Updates

- ✅ Production deployment configuration
- ✅ PostgreSQL support for production
- ✅ Environment variable configuration
- ✅ Health monitoring endpoints
- ✅ Automated database migrations
- ✅ Render deployment templates

---

**Ready to deploy?** Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide for step-by-step deployment instructions.

---

**Made with ❤️ for better healthcare accessibility** 
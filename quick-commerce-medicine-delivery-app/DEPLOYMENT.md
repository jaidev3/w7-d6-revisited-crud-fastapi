# Medicine Delivery API - Render Deployment Guide

## Prerequisites

1. **GitHub Repository**: Ensure your code is pushed to a GitHub repository
2. **Render Account**: Create a free account at [render.com](https://render.com)
3. **PostgreSQL Database**: Render will provide this automatically

## Deployment Steps

### 1. Database Setup (Automatic with render.yaml)

The `render.yaml` file will automatically create a PostgreSQL database for you. Alternatively, you can create it manually:

1. Go to Render Dashboard
2. Click "New" → "PostgreSQL"
3. Configure:
   - Name: `medicine-delivery-db`
   - Database Name: `medicine_delivery`
   - User: `medicine_user`
   - Plan: `Starter` (free tier)

### 2. Web Service Deployment

#### Option A: Using render.yaml (Recommended)

1. Ensure `render.yaml` is in your repository root
2. Connect your GitHub repository to Render
3. Render will automatically detect and deploy both database and web service

#### Option B: Manual Setup

1. Go to Render Dashboard
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `medicine-delivery-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### 3. Environment Variables

Set the following environment variables in Render:

#### Required Variables
```
ENVIRONMENT=production
SECRET_KEY=[Generate a secure 32+ character string]
DATABASE_URL=[Automatically provided by Render PostgreSQL]
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

#### How to Set Environment Variables
1. Go to your web service dashboard
2. Click "Environment" tab
3. Add each variable using "Add Environment Variable"

#### Generate SECRET_KEY
Use one of these methods:
```bash
# Method 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -hex 32
```

### 4. Database Migration

After deployment, your database tables will be created automatically when the application starts (thanks to `Base.metadata.create_all(bind=engine)` in main.py).

To populate with sample data, you can:
1. Access your app's shell via Render dashboard
2. Run: `python sample_data.py`

### 5. Deployment Verification

1. Check deployment status in Render dashboard
2. Visit your app URL (provided by Render)
3. Test endpoints:
   - `GET /` - Root endpoint
   - `GET /health` - Health check
   - `GET /docs` - API documentation

### 6. Monitoring and Maintenance

#### Health Checks
- Render automatically monitors `/health` endpoint
- Application logs available in Render dashboard

#### Performance Monitoring
- Monitor response times in Render dashboard
- Set up alerts for downtime

#### Scaling
- Upgrade to paid plan for:
  - Multiple instances
  - Custom domains
  - Advanced monitoring

## Production Considerations

### Security
- [ ] SECRET_KEY is properly generated and set
- [ ] Database credentials are secure
- [ ] CORS origins are properly configured
- [ ] File upload limits are set

### Performance
- [ ] Database connection pooling enabled
- [ ] Gunicorn worker count optimized
- [ ] Static file serving configured (if needed)

### Monitoring
- [ ] Health check endpoint working
- [ ] Error logging configured
- [ ] Performance monitoring setup

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL service is running
   - Verify database credentials

2. **Import Errors**
   - Check all dependencies in requirements.txt
   - Verify Python version compatibility

3. **Authentication Issues**
   - Verify SECRET_KEY is set
   - Check token expiration settings

4. **File Upload Issues**
   - Ensure uploads directory exists
   - Check file size limits
   - Verify permissions

### Support Resources
- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `ENVIRONMENT` | Yes | Deployment environment | `production` |
| `SECRET_KEY` | Yes | JWT signing key | `your-32-char-secret` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiration time | `1440` (24 hours) |

## Post-Deployment Checklist

- [ ] Application starts successfully
- [ ] Database tables created
- [ ] Health check endpoint responds
- [ ] API documentation accessible at `/docs`
- [ ] Authentication flow works
- [ ] Sample data loaded (optional)
- [ ] Error logging working
- [ ] Performance metrics available 
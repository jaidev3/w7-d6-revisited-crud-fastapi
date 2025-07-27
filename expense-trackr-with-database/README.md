# 💰 Expense Tracker with Database

A comprehensive expense tracking application built with FastAPI and SQLite database integration, featuring a modern Streamlit UI with advanced analytics.

## 🌟 Features

### Backend API Features
- **Complete CRUD Operations**: Create, read, update, and delete expenses
- **Advanced Filtering**: Filter by category, date range, and pagination
- **Data Validation**: Robust input validation with positive amounts and predefined categories
- **Database Integration**: SQLite database with SQLAlchemy ORM
- **Automatic Schema**: Database tables created automatically on startup
- **Error Handling**: Comprehensive error handling with meaningful messages
- **API Documentation**: Interactive Swagger/OpenAPI documentation

### Frontend UI Features
- **Modern Interface**: Beautiful and responsive Streamlit UI
- **Dashboard**: Overview with metrics, charts, and recent expenses
- **Expense Management**: Easy form-based expense creation and management
- **Advanced Filtering**: Filter expenses by category, date range
- **Data Visualization**: Interactive charts and graphs using Plotly
- **Analytics**: Monthly trends, category analysis, and insights
- **Real-time Updates**: Live data synchronization between UI and API

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint with API information |
| `GET` | `/categories` | Get all available expense categories |
| `GET` | `/expenses` | Fetch all expenses with optional filtering |
| `POST` | `/expenses` | Create a new expense |
| `GET` | `/expenses/{expense_id}` | Get a specific expense by ID |
| `PUT` | `/expenses/{expense_id}` | Update an existing expense |
| `DELETE` | `/expenses/{expense_id}` | Delete an expense |
| `GET` | `/expenses/category/{category}` | Filter expenses by category |
| `GET` | `/expenses/total` | Get total expenses and breakdown by category |

### Query Parameters

#### GET /expenses
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)
- `category`: Filter by category
- `start_date`: Filter from date (YYYY-MM-DD format)
- `end_date`: Filter to date (YYYY-MM-DD format)

#### GET /expenses/total
- `start_date`: Filter from date (YYYY-MM-DD format)
- `end_date`: Filter to date (YYYY-MM-DD format)

## 🗂️ Database Schema

### Expense Model
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY,
    title VARCHAR NOT NULL,
    amount FLOAT NOT NULL,
    category VARCHAR NOT NULL,
    description VARCHAR,
    date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Predefined Categories
- Food & Dining
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Travel
- Education
- Personal Care
- Home & Garden
- Groceries
- Insurance
- Gifts & Donations
- Business
- Other

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone and Setup
```bash
# Navigate to the project directory
cd expense-trackr-with-database

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Initialize Database with Sample Data (Optional)
```bash
# Run the sample data script to populate the database
python sample_data.py
```

### Step 3: Start the FastAPI Server
```bash
# Start the API server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

### Step 4: Launch the Streamlit UI
```bash
# In a new terminal, start the Streamlit app
streamlit run streamlit_app.py
```

The UI will be available at: `http://localhost:8501`

## 📖 Usage Guide

### Using the API

#### Create a New Expense
```bash
curl -X POST "http://localhost:8000/expenses" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Grocery Shopping",
       "amount": 85.50,
       "category": "Groceries",
       "description": "Weekly shopping",
       "date": "2025-01-15"
     }'
```

#### Get All Expenses
```bash
curl "http://localhost:8000/expenses"
```

#### Filter Expenses by Category
```bash
curl "http://localhost:8000/expenses?category=Food%20%26%20Dining"
```

#### Filter Expenses by Date Range
```bash
curl "http://localhost:8000/expenses?start_date=2025-01-01&end_date=2025-01-31"
```

#### Get Total Expenses and Category Breakdown
```bash
curl "http://localhost:8000/expenses/total"
```

#### Update an Expense
```bash
curl -X PUT "http://localhost:8000/expenses/1" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Updated Title",
       "amount": 100.00
     }'
```

#### Delete an Expense
```bash
curl -X DELETE "http://localhost:8000/expenses/1"
```

### Using the Streamlit UI

1. **Dashboard**: View overview metrics, charts, and recent expenses
2. **Add Expense**: Use the form to create new expenses with validation
3. **View Expenses**: Browse, filter, and delete expenses
4. **Analytics**: Explore spending patterns with interactive charts

## 🔧 Advanced Features

### Data Validation
- **Amount Validation**: Ensures amounts are positive numbers
- **Category Validation**: Restricts categories to predefined list
- **Date Validation**: Validates date formats and ranges
- **Required Fields**: Enforces required fields (title, amount, category)

### Error Handling
- **404 Errors**: Clear messages for non-existent resources
- **400 Errors**: Detailed validation error messages
- **500 Errors**: Graceful handling of server errors

### Database Features
- **Automatic Timestamps**: Created and updated timestamps
- **Session Management**: Proper database session handling
- **Connection Pooling**: Efficient database connections
- **Data Integrity**: Foreign key constraints and data validation

## 🛠️ Development

### Project Structure
```
expense-trackr-with-database/
├── main.py              # FastAPI application and endpoints
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── crud.py              # Database CRUD operations
├── sample_data.py       # Sample data initialization
├── streamlit_app.py     # Streamlit UI application
├── requirements.txt     # Python dependencies
└── README.md           # This documentation
```

### Running Tests
```bash
# Test the API endpoints
curl -X GET "http://localhost:8000/docs"  # Access Swagger documentation
```

### Database Management
```bash
# The SQLite database file is created automatically as 'expenses.db'
# You can view it using any SQLite browser or command line tools

# Reset database (delete the file and restart the application)
rm expenses.db
python main.py
```

## 🔍 API Documentation

Once the server is running, you can access:
- **Interactive API Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🎯 Example Use Cases

1. **Personal Expense Tracking**: Track daily expenses with categorization
2. **Budget Analysis**: Analyze spending patterns by category and time
3. **Monthly Reports**: Generate monthly expense reports and insights
4. **Receipt Management**: Store expense details with descriptions
5. **Financial Planning**: Understand spending habits for better budgeting

## 📈 Analytics Features

The application provides comprehensive analytics including:
- **Monthly Spending Trends**: Track how spending changes over time
- **Category Analysis**: Understand which categories consume the most budget
- **Expense Frequency**: See how often you spend in different categories
- **Key Insights**: Automatic insights like highest expense and daily averages
- **Visual Charts**: Interactive pie charts, bar charts, and line graphs

## 🔒 Security Considerations

- **Input Validation**: All inputs are validated on both client and server side
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection attacks
- **Error Messages**: Detailed error messages without exposing sensitive information
- **CORS Configuration**: Properly configured for cross-origin requests

## 🚀 Future Enhancements

Potential improvements for future versions:
- **User Authentication**: Multi-user support with authentication
- **Budget Limits**: Set and track budget limits by category
- **Recurring Expenses**: Support for recurring/scheduled expenses
- **Export Features**: Export data to CSV, PDF formats
- **Mobile App**: React Native or Flutter mobile application
- **Email Notifications**: Budget alerts and monthly reports
- **Multi-Currency**: Support for different currencies
- **Receipt Photos**: Upload and store receipt images

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the error messages in the response
3. Verify all required fields are provided
4. Ensure the FastAPI server is running before starting the UI

## 📄 License

This project is available for educational and personal use. 
# 🎫 Ticket Booking System with Database Relationships

A comprehensive FastAPI-based ticket booking system that demonstrates advanced database relationships, CRUD operations, and real-world business logic with a beautiful Streamlit UI.

## 🌟 Features

### Core Functionality
- **Venue Management**: Create and manage event venues with capacity tracking
- **Event Management**: Schedule events with date/time and ticket limits
- **Ticket Types**: Define different ticket categories (VIP, Standard, Economy) with pricing
- **Booking System**: Complete booking workflow with automatic price calculation
- **Real-time Availability**: Track and enforce ticket availability limits
- **Booking Status Management**: Handle pending, confirmed, and cancelled bookings

### Database Relationships
- **One-to-Many**: Venues → Events, Events → Bookings, TicketTypes → Bookings
- **Many-to-One**: Bookings → Event, Events → Venue, Bookings → TicketType
- **Foreign Key Constraints**: Ensures data integrity across related entities
- **Cascade Operations**: Proper handling of entity deletions
- **Join Operations**: Efficient queries with related data

### Advanced Features
- **Search & Filtering**: Multi-criteria booking search
- **Analytics Dashboard**: Revenue tracking, occupancy rates, booking statistics
- **Capacity Management**: Automatic enforcement of venue and event limits
- **Booking Codes**: Unique confirmation codes for each booking
- **Revenue Reporting**: Detailed financial analytics per event/venue
- **Real-time Statistics**: Live dashboard with key metrics

## 🏗️ Architecture

### Backend (FastAPI)
- **models.py**: SQLAlchemy ORM models with relationships
- **schemas.py**: Pydantic models for request/response validation
- **database.py**: Database configuration and session management
- **crud.py**: Database operations and business logic
- **main.py**: FastAPI application with all API endpoints

### Frontend (Streamlit)
- **streamlit_app.py**: Interactive web interface with multiple sections
- **Dashboard**: System overview with key metrics
- **Management Interfaces**: CRUD operations for all entities
- **Search Interface**: Advanced booking search functionality
- **Analytics**: Comprehensive reporting with charts and graphs

## 📡 API Endpoints

### Venues
```
POST   /venues                    - Create new venue
GET    /venues                    - Get all venues
GET    /venues/{venue_id}/events  - Get venue events
GET    /venues/{venue_id}/occupancy - Get occupancy stats
```

### Events
```
POST   /events                           - Create new event
GET    /events                           - Get all events
GET    /events/{event_id}/bookings       - Get event bookings
GET    /events/{event_id}/available-tickets - Get ticket availability
GET    /events/{event_id}/revenue        - Get event revenue
```

### Ticket Types
```
POST   /ticket-types                     - Create ticket type
GET    /ticket-types                     - Get all ticket types
GET    /ticket-types/{type_id}/bookings  - Get ticket type bookings
```

### Bookings
```
POST   /bookings                         - Create new booking
GET    /bookings                         - Get all bookings
PUT    /bookings/{booking_id}            - Update booking
DELETE /bookings/{booking_id}            - Cancel booking
PATCH  /bookings/{booking_id}/status     - Update booking status
```

### Advanced Queries
```
GET    /bookings/search                  - Search bookings (event, venue, ticket type)
GET    /booking-system/stats             - System statistics
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone or navigate to the project directory**
```bash
cd ticket-booking-system-withdatabase
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the FastAPI server**
```bash
python main.py
```
The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

4. **Start the Streamlit UI** (in a new terminal)
```bash
streamlit run streamlit_app.py
```
The UI will be available at `http://localhost:8501`

## 🎯 Usage Guide

### 1. Setup Basic Data
1. **Add Venues**: Create venues with names, addresses, and capacities
2. **Add Ticket Types**: Define pricing tiers (e.g., VIP $100, Standard $50, Economy $25)
3. **Add Events**: Schedule events at venues with ticket limits

### 2. Booking Workflow
1. **Create Bookings**: Select event, venue, ticket type, and quantity
2. **Automatic Validation**: System checks availability and calculates prices
3. **Booking Confirmation**: Unique booking codes generated
4. **Status Management**: Update bookings to confirmed/cancelled

### 3. Analytics & Reporting
1. **Dashboard**: View system overview and key metrics
2. **Revenue Tracking**: Monitor earnings by event and venue
3. **Occupancy Analysis**: Track venue utilization rates
4. **Search & Filter**: Find specific bookings with multiple criteria

## 📊 Key Business Logic

### Capacity Management
- Venues have maximum capacity limits
- Events have configurable ticket limits (can be less than venue capacity)
- Real-time availability tracking prevents overbooking
- Cancelled bookings free up capacity automatically

### Pricing Logic
- Each ticket type has a base price
- Total booking cost = ticket price × quantity
- Automatic price calculation during booking creation
- Revenue tracking for confirmed bookings only

### Booking Status Flow
```
PENDING → CONFIRMED (payment processed)
PENDING → CANCELLED (customer cancellation)
CONFIRMED → CANCELLED (refund processed)
```

## 🗄️ Database Schema

### Relationships Overview
```
Venue (1) ←→ (Many) Event
Event (1) ←→ (Many) Booking
TicketType (1) ←→ (Many) Booking
Venue (1) ←→ (Many) Booking (through Event)
```

### Key Tables
- **venues**: Basic venue information and capacity
- **events**: Event details linked to venues
- **ticket_types**: Pricing categories for tickets
- **bookings**: Individual customer bookings with all relationships

## 🔧 Configuration

### Database
- Default: SQLite (`ticket_booking.db`)
- Easily configurable for PostgreSQL, MySQL, etc.
- Automatic table creation on startup

### API Settings
- Default port: 8000
- Configurable through `main.py`
- CORS enabled for frontend integration

## 🧪 Testing

### Manual Testing via UI
1. Use the Streamlit interface for end-to-end testing
2. Create venues, events, and ticket types
3. Make bookings and verify availability updates
4. Test search and analytics features

### API Testing
1. Access FastAPI docs at `/docs`
2. Use the interactive API explorer
3. Test all endpoints with sample data

## 🎨 UI Features

### Navigation
- **Dashboard**: System overview and statistics
- **Venues**: Venue management with occupancy tracking
- **Events**: Event scheduling with availability monitoring
- **Ticket Types**: Pricing tier management
- **Bookings**: Complete booking workflow and management
- **Search**: Advanced booking search capabilities
- **Analytics**: Comprehensive reporting dashboard

### Interactive Elements
- **Real-time Data**: Live updates of availability and statistics
- **Visual Analytics**: Charts and graphs for insights
- **Status Management**: One-click booking status updates
- **Responsive Design**: Clean, modern interface

## 🚀 Advanced Features

### Revenue Analytics
- Track total revenue by event, venue, and time period
- Identify top-performing events and venues
- Monitor booking trends over time

### Occupancy Management
- Calculate venue utilization rates
- Track upcoming events per venue
- Optimize venue scheduling

### Search Capabilities
- Multi-criteria search across events, venues, and ticket types
- Real-time filtering of booking results
- Export capabilities for reporting

## 📈 Business Insights

### Key Metrics Tracked
- Total bookings and revenue
- Booking status distribution
- Venue occupancy rates
- Event performance analytics
- Ticket type popularity

### Reporting Features
- Revenue by event and venue
- Occupancy trends and forecasting
- Customer booking patterns
- Ticket type performance analysis

## 🛠️ Technical Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite (configurable)
- **Frontend**: Streamlit, Plotly, Pandas
- **Authentication**: Ready for extension
- **API Documentation**: Automatic with FastAPI

## 📝 Future Enhancements

- **User Authentication**: Customer and admin portals
- **Payment Integration**: Stripe/PayPal integration
- **Email Notifications**: Booking confirmations and reminders
- **Mobile App**: React Native or Flutter frontend
- **Advanced Analytics**: ML-based demand forecasting
- **Multi-tenancy**: Support for multiple organizations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is available for educational and commercial use.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Streamlit** 
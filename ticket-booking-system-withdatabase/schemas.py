from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

# Venue Schemas
class VenueBase(BaseModel):
    name: str
    address: Optional[str] = None
    capacity: int
    city: Optional[str] = None

class VenueCreate(VenueBase):
    pass

class VenueResponse(VenueBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class VenueWithEvents(VenueResponse):
    events: List['EventResponse'] = []

# TicketType Schemas
class TicketTypeBase(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketTypeResponse(TicketTypeBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Event Schemas
class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    event_date: datetime
    venue_id: int
    max_tickets: int

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    created_at: datetime
    venue: Optional[VenueResponse] = None
    
    class Config:
        from_attributes = True

class EventWithBookings(EventResponse):
    bookings: List['BookingResponse'] = []

# Booking Schemas
class BookingBase(BaseModel):
    event_id: int
    venue_id: int
    ticket_type_id: int
    customer_name: str
    customer_email: EmailStr
    quantity: int = 1

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    quantity: Optional[int] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class BookingResponse(BookingBase):
    id: int
    total_price: float
    booking_code: str
    status: BookingStatus
    created_at: datetime
    event: Optional[EventResponse] = None
    venue: Optional[VenueResponse] = None
    ticket_type: Optional[TicketTypeResponse] = None
    
    class Config:
        from_attributes = True

# Statistics Schemas
class BookingStats(BaseModel):
    total_bookings: int
    total_events: int
    total_venues: int
    total_revenue: float
    confirmed_bookings: int
    pending_bookings: int
    cancelled_bookings: int

class EventRevenue(BaseModel):
    event_id: int
    event_name: str
    total_revenue: float
    total_bookings: int
    confirmed_bookings: int

class VenueOccupancy(BaseModel):
    venue_id: int
    venue_name: str
    capacity: int
    total_bookings: int
    occupancy_rate: float
    upcoming_events: int

# Available Tickets Schema
class AvailableTickets(BaseModel):
    event_id: int
    event_name: str
    max_tickets: int
    booked_tickets: int
    available_tickets: int

# Forward references for nested models
VenueWithEvents.model_rebuild()
EventWithBookings.model_rebuild() 
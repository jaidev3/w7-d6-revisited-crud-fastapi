from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import Optional, List
import secrets
import string
from datetime import datetime

import models
import schemas

# Helper function to generate booking codes
def generate_booking_code() -> str:
    import random
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Venue CRUD
def create_venue(db: Session, venue: schemas.VenueCreate):
    db_venue = models.Venue(**venue.model_dump())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

def get_venues(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Venue).offset(skip).limit(limit).all()

def get_venue(db: Session, venue_id: int):
    return db.query(models.Venue).filter(models.Venue.id == venue_id).first()

def get_venue_events(db: Session, venue_id: int):
    return db.query(models.Event).filter(models.Event.venue_id == venue_id).all()

# TicketType CRUD
def create_ticket_type(db: Session, ticket_type: schemas.TicketTypeCreate):
    db_ticket_type = models.TicketType(**ticket_type.model_dump())
    db.add(db_ticket_type)
    db.commit()
    db.refresh(db_ticket_type)
    return db_ticket_type

def get_ticket_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TicketType).offset(skip).limit(limit).all()

def get_ticket_type(db: Session, ticket_type_id: int):
    return db.query(models.TicketType).filter(models.TicketType.id == ticket_type_id).first()

def get_ticket_type_bookings(db: Session, ticket_type_id: int):
    return db.query(models.Booking).filter(models.Booking.ticket_type_id == ticket_type_id).all()

# Event CRUD
def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Event).options(joinedload(models.Event.venue)).offset(skip).limit(limit).all()

def get_event(db: Session, event_id: int):
    return db.query(models.Event).options(joinedload(models.Event.venue)).filter(models.Event.id == event_id).first()

def get_event_bookings(db: Session, event_id: int):
    return db.query(models.Booking).options(
        joinedload(models.Booking.event),
        joinedload(models.Booking.venue),
        joinedload(models.Booking.ticket_type)
    ).filter(models.Booking.event_id == event_id).all()

def get_event_available_tickets(db: Session, event_id: int):
    event = get_event(db, event_id)
    if not event:
        return None
    
    booked_count = db.query(func.sum(models.Booking.quantity)).filter(
        and_(
            models.Booking.event_id == event_id,
            models.Booking.status != models.BookingStatus.CANCELLED
        )
    ).scalar() or 0
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "max_tickets": event.max_tickets,
        "booked_tickets": booked_count,
        "available_tickets": event.max_tickets - booked_count
    }

# Booking CRUD
def create_booking(db: Session, booking: schemas.BookingCreate):
    # Check if event exists and has available tickets
    event = get_event(db, booking.event_id)
    if not event:
        raise ValueError("Event not found")
    
    # Check venue exists
    venue = get_venue(db, booking.venue_id)
    if not venue:
        raise ValueError("Venue not found")
    
    # Check ticket type exists
    ticket_type = get_ticket_type(db, booking.ticket_type_id)
    if not ticket_type:
        raise ValueError("Ticket type not found")
    
    # Check ticket availability
    available_info = get_event_available_tickets(db, booking.event_id)
    if available_info["available_tickets"] < booking.quantity:
        raise ValueError("Not enough tickets available")
    
    # Calculate total price
    total_price = ticket_type.price * booking.quantity
    
    # Generate unique booking code
    booking_code = generate_booking_code()
    while db.query(models.Booking).filter(models.Booking.booking_code == booking_code).first():
        booking_code = generate_booking_code()
    
    db_booking = models.Booking(
        **booking.model_dump(),
        total_price=total_price,
        booking_code=booking_code
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Booking).options(
        joinedload(models.Booking.event),
        joinedload(models.Booking.venue),
        joinedload(models.Booking.ticket_type)
    ).offset(skip).limit(limit).all()

def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).options(
        joinedload(models.Booking.event),
        joinedload(models.Booking.venue),
        joinedload(models.Booking.ticket_type)
    ).filter(models.Booking.id == booking_id).first()

def update_booking(db: Session, booking_id: int, booking_update: schemas.BookingUpdate):
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return None
    
    update_data = booking_update.model_dump(exclude_unset=True)
    
    # If quantity is being updated, recalculate total price
    if "quantity" in update_data:
        ticket_type = get_ticket_type(db, db_booking.ticket_type_id)
        update_data["total_price"] = ticket_type.price * update_data["quantity"]
    
    for field, value in update_data.items():
        setattr(db_booking, field, value)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking

def update_booking_status(db: Session, booking_id: int, status_update: schemas.BookingStatusUpdate):
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return None
    
    db_booking.status = status_update.status
    db.commit()
    db.refresh(db_booking)
    return db_booking

def delete_booking(db: Session, booking_id: int):
    db_booking = get_booking(db, booking_id)
    if not db_booking:
        return None
    
    db.delete(db_booking)
    db.commit()
    return db_booking

# Search and Analytics
def search_bookings(
    db: Session, 
    event_name: Optional[str] = None,
    venue_name: Optional[str] = None,
    ticket_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(models.Booking).options(
        joinedload(models.Booking.event),
        joinedload(models.Booking.venue),
        joinedload(models.Booking.ticket_type)
    )
    
    if event_name:
        query = query.join(models.Event).filter(models.Event.name.ilike(f"%{event_name}%"))
    
    if venue_name:
        query = query.join(models.Venue).filter(models.Venue.name.ilike(f"%{venue_name}%"))
    
    if ticket_type:
        query = query.join(models.TicketType).filter(models.TicketType.name.ilike(f"%{ticket_type}%"))
    
    return query.offset(skip).limit(limit).all()

def get_booking_stats(db: Session):
    total_bookings = db.query(models.Booking).count()
    total_events = db.query(models.Event).count()
    total_venues = db.query(models.Venue).count()
    
    total_revenue = db.query(func.sum(models.Booking.total_price)).filter(
        models.Booking.status == models.BookingStatus.CONFIRMED
    ).scalar() or 0
    
    confirmed_bookings = db.query(models.Booking).filter(
        models.Booking.status == models.BookingStatus.CONFIRMED
    ).count()
    
    pending_bookings = db.query(models.Booking).filter(
        models.Booking.status == models.BookingStatus.PENDING
    ).count()
    
    cancelled_bookings = db.query(models.Booking).filter(
        models.Booking.status == models.BookingStatus.CANCELLED
    ).count()
    
    return {
        "total_bookings": total_bookings,
        "total_events": total_events,
        "total_venues": total_venues,
        "total_revenue": total_revenue,
        "confirmed_bookings": confirmed_bookings,
        "pending_bookings": pending_bookings,
        "cancelled_bookings": cancelled_bookings
    }

def get_event_revenue(db: Session, event_id: int):
    event = get_event(db, event_id)
    if not event:
        return None
    
    revenue_data = db.query(
        func.sum(models.Booking.total_price).label("total_revenue"),
        func.count(models.Booking.id).label("total_bookings")
    ).filter(
        and_(
            models.Booking.event_id == event_id,
            models.Booking.status == models.BookingStatus.CONFIRMED
        )
    ).first()
    
    confirmed_bookings = db.query(models.Booking).filter(
        and_(
            models.Booking.event_id == event_id,
            models.Booking.status == models.BookingStatus.CONFIRMED
        )
    ).count()
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "total_revenue": revenue_data.total_revenue or 0,
        "total_bookings": revenue_data.total_bookings or 0,
        "confirmed_bookings": confirmed_bookings
    }

def get_venue_occupancy(db: Session, venue_id: int):
    venue = get_venue(db, venue_id)
    if not venue:
        return None
    
    total_bookings = db.query(func.sum(models.Booking.quantity)).join(
        models.Event
    ).filter(
        and_(
            models.Event.venue_id == venue_id,
            models.Booking.status != models.BookingStatus.CANCELLED
        )
    ).scalar() or 0
    
    upcoming_events = db.query(models.Event).filter(
        and_(
            models.Event.venue_id == venue_id,
            models.Event.event_date > datetime.utcnow()
        )
    ).count()
    
    occupancy_rate = (total_bookings / venue.capacity) * 100 if venue.capacity > 0 else 0
    
    return {
        "venue_id": venue_id,
        "venue_name": venue.name,
        "capacity": venue.capacity,
        "total_bookings": total_bookings,
        "occupancy_rate": round(occupancy_rate, 2),
        "upcoming_events": upcoming_events
    } 
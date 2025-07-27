from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import SessionLocal, engine
from models import Base
import crud
import schemas

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ticket Booking System",
    description="A comprehensive ticket booking system with database relationships",
    version="1.0.0"
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Venues Endpoints
@app.post("/venues", response_model=schemas.VenueResponse)
def create_venue(venue: schemas.VenueCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_venue(db=db, venue=venue)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/venues", response_model=List[schemas.VenueResponse])
def read_venues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    venues = crud.get_venues(db, skip=skip, limit=limit)
    return venues

@app.get("/venues/{venue_id}/events", response_model=List[schemas.EventResponse])
def read_venue_events(venue_id: int, db: Session = Depends(get_db)):
    venue = crud.get_venue(db, venue_id=venue_id)
    if venue is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    return crud.get_venue_events(db=db, venue_id=venue_id)

# Ticket Types Endpoints
@app.post("/ticket-types", response_model=schemas.TicketTypeResponse)
def create_ticket_type(ticket_type: schemas.TicketTypeCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_ticket_type(db=db, ticket_type=ticket_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ticket-types", response_model=List[schemas.TicketTypeResponse])
def read_ticket_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ticket_types = crud.get_ticket_types(db, skip=skip, limit=limit)
    return ticket_types

@app.get("/ticket-types/{type_id}/bookings", response_model=List[schemas.BookingResponse])
def read_ticket_type_bookings(type_id: int, db: Session = Depends(get_db)):
    ticket_type = crud.get_ticket_type(db, ticket_type_id=type_id)
    if ticket_type is None:
        raise HTTPException(status_code=404, detail="Ticket type not found")
    return crud.get_ticket_type_bookings(db=db, ticket_type_id=type_id)

# Events Endpoints
@app.post("/events", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_event(db=db, event=event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events", response_model=List[schemas.EventResponse])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events

@app.get("/events/{event_id}/bookings", response_model=List[schemas.BookingResponse])
def read_event_bookings(event_id: int, db: Session = Depends(get_db)):
    event = crud.get_event(db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return crud.get_event_bookings(db=db, event_id=event_id)

@app.get("/events/{event_id}/available-tickets", response_model=schemas.AvailableTickets)
def read_event_available_tickets(event_id: int, db: Session = Depends(get_db)):
    available_tickets = crud.get_event_available_tickets(db=db, event_id=event_id)
    if available_tickets is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return available_tickets

@app.get("/events/{event_id}/revenue", response_model=schemas.EventRevenue)
def read_event_revenue(event_id: int, db: Session = Depends(get_db)):
    revenue = crud.get_event_revenue(db=db, event_id=event_id)
    if revenue is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return revenue

# Bookings Endpoints
@app.post("/bookings", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_booking(db=db, booking=booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings", response_model=List[schemas.BookingResponse])
def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = crud.get_bookings(db, skip=skip, limit=limit)
    return bookings

@app.put("/bookings/{booking_id}", response_model=schemas.BookingResponse)
def update_booking(booking_id: int, booking_update: schemas.BookingUpdate, db: Session = Depends(get_db)):
    booking = crud.update_booking(db=db, booking_id=booking_id, booking_update=booking_update)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.delete("/bookings/{booking_id}", response_model=schemas.BookingResponse)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = crud.delete_booking(db=db, booking_id=booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.patch("/bookings/{booking_id}/status", response_model=schemas.BookingResponse)
def update_booking_status(booking_id: int, status_update: schemas.BookingStatusUpdate, db: Session = Depends(get_db)):
    booking = crud.update_booking_status(db=db, booking_id=booking_id, status_update=status_update)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

# Advanced Queries
@app.get("/bookings/search", response_model=List[schemas.BookingResponse])
def search_bookings(
    event: Optional[str] = Query(None, description="Event name to search for"),
    venue: Optional[str] = Query(None, description="Venue name to search for"),
    ticket_type: Optional[str] = Query(None, description="Ticket type to search for"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.search_bookings(
        db=db,
        event_name=event,
        venue_name=venue,
        ticket_type=ticket_type,
        skip=skip,
        limit=limit
    )

@app.get("/booking-system/stats", response_model=schemas.BookingStats)
def read_booking_stats(db: Session = Depends(get_db)):
    return crud.get_booking_stats(db=db)

@app.get("/venues/{venue_id}/occupancy", response_model=schemas.VenueOccupancy)
def read_venue_occupancy(venue_id: int, db: Session = Depends(get_db)):
    occupancy = crud.get_venue_occupancy(db=db, venue_id=venue_id)
    if occupancy is None:
        raise HTTPException(status_code=404, detail="Venue not found")
    return occupancy

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Ticket Booking System API", "status": "active"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
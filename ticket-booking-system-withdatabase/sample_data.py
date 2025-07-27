"""
Sample data script to populate the ticket booking system with test data.
Run this script after starting the FastAPI server to add sample venues, events, ticket types, and bookings.
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000"

def create_sample_data():
    """Create comprehensive sample data for the ticket booking system"""
    
    print("🎫 Creating sample data for Ticket Booking System...")
    
    # Sample Venues
    venues = [
        {
            "name": "Madison Square Garden",
            "address": "4 Pennsylvania Plaza, New York, NY 10001",
            "capacity": 20000,
            "city": "New York"
        },
        {
            "name": "Hollywood Bowl",
            "address": "2301 Highland Ave, Los Angeles, CA 90068",
            "capacity": 17500,
            "city": "Los Angeles"
        },
        {
            "name": "Red Rocks Amphitheatre",
            "address": "18300 W Alameda Pkwy, Morrison, CO 80465",
            "capacity": 9525,
            "city": "Morrison"
        },
        {
            "name": "Royal Albert Hall",
            "address": "Kensington Gore, South Kensington, London SW7 2AP",
            "capacity": 5272,
            "city": "London"
        },
        {
            "name": "Sydney Opera House",
            "address": "Bennelong Point, Sydney NSW 2000, Australia",
            "capacity": 2679,
            "city": "Sydney"
        }
    ]
    
    # Sample Ticket Types
    ticket_types = [
        {
            "name": "VIP",
            "price": 150.00,
            "description": "Premium seating with exclusive amenities, complimentary drinks, and meet & greet opportunities"
        },
        {
            "name": "Standard",
            "price": 75.00,
            "description": "Regular seating with good views and standard venue amenities"
        },
        {
            "name": "Economy",
            "price": 35.00,
            "description": "Budget-friendly seating with basic amenities"
        },
        {
            "name": "Student",
            "price": 25.00,
            "description": "Discounted tickets for students with valid ID"
        },
        {
            "name": "Senior",
            "price": 30.00,
            "description": "Special pricing for senior citizens (65+)"
        }
    ]
    
    print("🏢 Creating venues...")
    venue_ids = []
    for venue in venues:
        try:
            response = requests.post(f"{API_BASE_URL}/venues", json=venue)
            if response.status_code == 200:
                venue_data = response.json()
                venue_ids.append(venue_data['id'])
                print(f"  ✅ Created venue: {venue['name']}")
            else:
                print(f"  ❌ Failed to create venue: {venue['name']} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating venue {venue['name']}: {str(e)}")
    
    print("🎟️ Creating ticket types...")
    ticket_type_ids = []
    for ticket_type in ticket_types:
        try:
            response = requests.post(f"{API_BASE_URL}/ticket-types", json=ticket_type)
            if response.status_code == 200:
                ticket_data = response.json()
                ticket_type_ids.append(ticket_data['id'])
                print(f"  ✅ Created ticket type: {ticket_type['name']}")
            else:
                print(f"  ❌ Failed to create ticket type: {ticket_type['name']} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating ticket type {ticket_type['name']}: {str(e)}")
    
    # Sample Events (using created venue IDs)
    base_date = datetime.now() + timedelta(days=7)
    events = [
        {
            "name": "Rock Concert - The Electric Thunder",
            "description": "High-energy rock concert featuring The Electric Thunder band with special guests",
            "event_date": (base_date + timedelta(days=0)).isoformat(),
            "venue_id": venue_ids[0] if venue_ids else 1,  # Madison Square Garden
            "max_tickets": 15000
        },
        {
            "name": "Classical Symphony Night",
            "description": "An evening of beautiful classical music performed by the City Symphony Orchestra",
            "event_date": (base_date + timedelta(days=3)).isoformat(),
            "venue_id": venue_ids[3] if len(venue_ids) > 3 else 1,  # Royal Albert Hall
            "max_tickets": 4000
        },
        {
            "name": "Comedy Show - Laugh Out Loud",
            "description": "Stand-up comedy show featuring top comedians from around the world",
            "event_date": (base_date + timedelta(days=5)).isoformat(),
            "venue_id": venue_ids[1] if len(venue_ids) > 1 else 1,  # Hollywood Bowl
            "max_tickets": 12000
        },
        {
            "name": "Jazz Festival Opening Night",
            "description": "Opening night of the annual jazz festival with renowned jazz musicians",
            "event_date": (base_date + timedelta(days=7)).isoformat(),
            "venue_id": venue_ids[2] if len(venue_ids) > 2 else 1,  # Red Rocks
            "max_tickets": 8000
        },
        {
            "name": "Pop Star World Tour",
            "description": "Exclusive concert as part of the global world tour by international pop sensation",
            "event_date": (base_date + timedelta(days=10)).isoformat(),
            "venue_id": venue_ids[4] if len(venue_ids) > 4 else 1,  # Sydney Opera House
            "max_tickets": 2500
        },
        {
            "name": "Alternative Rock Festival",
            "description": "Three-day alternative rock festival featuring multiple bands and artists",
            "event_date": (base_date + timedelta(days=14)).isoformat(),
            "venue_id": venue_ids[0] if venue_ids else 1,  # Madison Square Garden
            "max_tickets": 18000
        },
        {
            "name": "Broadway Musical Gala",
            "description": "Special gala performance featuring songs from the most popular Broadway musicals",
            "event_date": (base_date + timedelta(days=17)).isoformat(),
            "venue_id": venue_ids[3] if len(venue_ids) > 3 else 1,  # Royal Albert Hall
            "max_tickets": 5000
        },
        {
            "name": "Electronic Dance Music Night",
            "description": "High-energy EDM event with top DJs and spectacular light shows",
            "event_date": (base_date + timedelta(days=21)).isoformat(),
            "venue_id": venue_ids[1] if len(venue_ids) > 1 else 1,  # Hollywood Bowl
            "max_tickets": 16000
        }
    ]
    
    print("📅 Creating events...")
    event_ids = []
    for event in events:
        try:
            response = requests.post(f"{API_BASE_URL}/events", json=event)
            if response.status_code == 200:
                event_data = response.json()
                event_ids.append(event_data['id'])
                print(f"  ✅ Created event: {event['name']}")
            else:
                print(f"  ❌ Failed to create event: {event['name']} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating event {event['name']}: {str(e)}")
    
    # Sample Bookings
    sample_customers = [
        {"name": "John Smith", "email": "john.smith@email.com"},
        {"name": "Sarah Johnson", "email": "sarah.johnson@email.com"},
        {"name": "Michael Brown", "email": "michael.brown@email.com"},
        {"name": "Emily Davis", "email": "emily.davis@email.com"},
        {"name": "David Wilson", "email": "david.wilson@email.com"},
        {"name": "Lisa Anderson", "email": "lisa.anderson@email.com"},
        {"name": "Robert Taylor", "email": "robert.taylor@email.com"},
        {"name": "Jessica Miller", "email": "jessica.miller@email.com"},
        {"name": "Christopher Lee", "email": "christopher.lee@email.com"},
        {"name": "Amanda White", "email": "amanda.white@email.com"},
        {"name": "Daniel Garcia", "email": "daniel.garcia@email.com"},
        {"name": "Michelle Martinez", "email": "michelle.martinez@email.com"},
        {"name": "Ryan Thompson", "email": "ryan.thompson@email.com"},
        {"name": "Jennifer Clark", "email": "jennifer.clark@email.com"},
        {"name": "Kevin Rodriguez", "email": "kevin.rodriguez@email.com"}
    ]
    
    print("📖 Creating sample bookings...")
    booking_count = 0
    
    # Create bookings for each event
    for i, event_id in enumerate(event_ids):
        # Get the corresponding venue_id for this event
        event_venue_id = venue_ids[i % len(venue_ids)] if venue_ids else 1
        
        # Create 3-5 bookings per event
        import random
        num_bookings = random.randint(3, 5)
        
        for j in range(num_bookings):
            customer = sample_customers[booking_count % len(sample_customers)]
            ticket_type_id = ticket_type_ids[random.randint(0, len(ticket_type_ids)-1)] if ticket_type_ids else 1
            quantity = random.randint(1, 4)
            
            booking = {
                "event_id": event_id,
                "venue_id": event_venue_id,
                "ticket_type_id": ticket_type_id,
                "customer_name": customer["name"],
                "customer_email": customer["email"],
                "quantity": quantity
            }
            
            try:
                response = requests.post(f"{API_BASE_URL}/bookings", json=booking)
                if response.status_code == 200:
                    booking_data = response.json()
                    booking_count += 1
                    print(f"  ✅ Created booking: {booking_data['booking_code']} for {customer['name']}")
                    
                    # Confirm some bookings randomly
                    if random.random() > 0.3:  # 70% chance to confirm
                        confirm_response = requests.patch(
                            f"{API_BASE_URL}/bookings/{booking_data['id']}/status",
                            json={"status": "confirmed"}
                        )
                        if confirm_response.status_code == 200:
                            print(f"    ✅ Confirmed booking: {booking_data['booking_code']}")
                    
                    # Cancel some bookings randomly
                    elif random.random() > 0.8:  # 10% chance to cancel (of remaining 30%)
                        cancel_response = requests.patch(
                            f"{API_BASE_URL}/bookings/{booking_data['id']}/status",
                            json={"status": "cancelled"}
                        )
                        if cancel_response.status_code == 200:
                            print(f"    ❌ Cancelled booking: {booking_data['booking_code']}")
                            
                else:
                    print(f"  ❌ Failed to create booking for {customer['name']}: {response.text}")
            except Exception as e:
                print(f"  ❌ Error creating booking for {customer['name']}: {str(e)}")
    
    print(f"\n🎉 Sample data creation completed!")
    print(f"📊 Summary:")
    print(f"  - Venues created: {len(venue_ids)}")
    print(f"  - Ticket types created: {len(ticket_type_ids)}")
    print(f"  - Events created: {len(event_ids)}")
    print(f"  - Bookings created: {booking_count}")
    print(f"\n🚀 You can now explore the system using the Streamlit UI at http://localhost:8501")
    print(f"📚 Or check the API documentation at http://localhost:8000/docs")

def main():
    """Main function to run sample data creation"""
    print("🔗 Checking API connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("  ✅ API is running and accessible")
            create_sample_data()
        else:
            print(f"  ❌ API responded with status {response.status_code}")
            print("     Please make sure the FastAPI server is running on http://localhost:8000")
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to API")
        print("     Please make sure the FastAPI server is running:")
        print("     python main.py")
    except Exception as e:
        print(f"  ❌ Error connecting to API: {str(e)}")

if __name__ == "__main__":
    main() 
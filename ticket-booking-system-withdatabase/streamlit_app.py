import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time
from streamlit_option_menu import option_menu
import json

# Configure the page
st.set_page_config(
    page_title="Ticket Booking System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .section-header {
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_request(method, endpoint, data=None, params=None):
    """Make HTTP request to the API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        elif method == "PATCH":
            response = requests.patch(url, json=data)
        
        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {str(e)}"

def get_venues():
    """Get all venues"""
    data, error = make_request("GET", "/venues")
    return data if data else []

def get_events():
    """Get all events"""
    data, error = make_request("GET", "/events")
    return data if data else []

def get_ticket_types():
    """Get all ticket types"""
    data, error = make_request("GET", "/ticket-types")
    return data if data else []

def get_bookings():
    """Get all bookings"""
    data, error = make_request("GET", "/bookings")
    return data if data else []

# Main title
st.markdown('<h1 class="main-header">🎫 Ticket Booking System</h1>', unsafe_allow_html=True)

# Navigation menu
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Venues", "Events", "Ticket Types", "Bookings", "Search", "Analytics"],
    icons=["house", "building", "calendar-event", "ticket", "book", "search", "graph-up"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa"},
        "icon": {"color": "#1f77b4", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px"},
        "nav-link-selected": {"background-color": "#1f77b4"},
    }
)

# Dashboard
if selected == "Dashboard":
    st.markdown('<h2 class="section-header">📊 System Overview</h2>', unsafe_allow_html=True)
    
    # Get statistics
    stats_data, stats_error = make_request("GET", "/booking-system/stats")
    
    if stats_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Bookings", stats_data.get("total_bookings", 0))
        with col2:
            st.metric("Total Events", stats_data.get("total_events", 0))
        with col3:
            st.metric("Total Venues", stats_data.get("total_venues", 0))
        with col4:
            st.metric("Total Revenue", f"${stats_data.get('total_revenue', 0):,.2f}")
        
        # Booking status breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            # Booking status pie chart
            status_data = {
                "Confirmed": stats_data.get("confirmed_bookings", 0),
                "Pending": stats_data.get("pending_bookings", 0),
                "Cancelled": stats_data.get("cancelled_bookings", 0)
            }
            
            if sum(status_data.values()) > 0:
                fig_pie = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    title="Booking Status Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Recent bookings
            bookings = get_bookings()
            if bookings:
                df_bookings = pd.DataFrame(bookings)
                df_bookings['created_at'] = pd.to_datetime(df_bookings['created_at'])
                recent_bookings = df_bookings.head(10)
                
                st.subheader("Recent Bookings")
                for _, booking in recent_bookings.iterrows():
                    with st.expander(f"Booking {booking['booking_code']} - {booking['customer_name']}"):
                        st.write(f"**Event:** {booking.get('event', {}).get('name', 'N/A')}")
                        st.write(f"**Status:** {booking['status']}")
                        st.write(f"**Total:** ${booking['total_price']}")
    else:
        st.error("Unable to fetch statistics")

# Venues Section
elif selected == "Venues":
    st.markdown('<h2 class="section-header">🏢 Venue Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add Venue", "View Venues"])
    
    with tab1:
        st.subheader("Add New Venue")
        
        with st.form("venue_form"):
            venue_name = st.text_input("Venue Name*")
            venue_address = st.text_area("Address")
            venue_capacity = st.number_input("Capacity*", min_value=1, value=100)
            venue_city = st.text_input("City")
            
            if st.form_submit_button("Add Venue"):
                if venue_name and venue_capacity:
                    venue_data = {
                        "name": venue_name,
                        "address": venue_address if venue_address else None,
                        "capacity": venue_capacity,
                        "city": venue_city if venue_city else None
                    }
                    
                    result, error = make_request("POST", "/venues", venue_data)
                    if result:
                        st.success(f"Venue '{venue_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add venue: {error}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab2:
        st.subheader("All Venues")
        venues = get_venues()
        
        if venues:
            for venue in venues:
                with st.expander(f"{venue['name']} (Capacity: {venue['capacity']})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**ID:** {venue['id']}")
                        st.write(f"**City:** {venue.get('city', 'N/A')}")
                    with col2:
                        st.write(f"**Address:** {venue.get('address', 'N/A')}")
                    with col3:
                        # Get venue occupancy
                        occupancy_data, _ = make_request("GET", f"/venues/{venue['id']}/occupancy")
                        if occupancy_data:
                            st.write(f"**Occupancy Rate:** {occupancy_data['occupancy_rate']}%")
                            st.write(f"**Upcoming Events:** {occupancy_data['upcoming_events']}")
        else:
            st.info("No venues found. Add some venues to get started!")

# Events Section
elif selected == "Events":
    st.markdown('<h2 class="section-header">📅 Event Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add Event", "View Events"])
    
    with tab1:
        st.subheader("Add New Event")
        
        venues = get_venues()
        venue_options = {venue['name']: venue['id'] for venue in venues}
        
        if not venues:
            st.warning("Please add venues first before creating events.")
        else:
            with st.form("event_form"):
                event_name = st.text_input("Event Name*")
                event_description = st.text_area("Description")
                venue_selection = st.selectbox("Select Venue*", options=list(venue_options.keys()))
                event_date = st.date_input("Event Date*", min_value=date.today())
                event_time = st.time_input("Event Time*", value=time(19, 0))
                max_tickets = st.number_input("Maximum Tickets*", min_value=1, value=100)
                
                if st.form_submit_button("Add Event"):
                    if event_name and venue_selection and max_tickets:
                        event_datetime = datetime.combine(event_date, event_time)
                        
                        event_data = {
                            "name": event_name,
                            "description": event_description if event_description else None,
                            "event_date": event_datetime.isoformat(),
                            "venue_id": venue_options[venue_selection],
                            "max_tickets": max_tickets
                        }
                        
                        result, error = make_request("POST", "/events", event_data)
                        if result:
                            st.success(f"Event '{event_name}' added successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to add event: {error}")
                    else:
                        st.error("Please fill in all required fields")
    
    with tab2:
        st.subheader("All Events")
        events = get_events()
        
        if events:
            for event in events:
                with st.expander(f"{event['name']} - {event['event_date'][:10]}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Date:** {event['event_date'][:10]}")
                        st.write(f"**Venue:** {event.get('venue', {}).get('name', 'N/A')}")
                    with col2:
                        st.write(f"**Max Tickets:** {event['max_tickets']}")
                        # Get available tickets
                        tickets_data, _ = make_request("GET", f"/events/{event['id']}/available-tickets")
                        if tickets_data:
                            st.write(f"**Available:** {tickets_data['available_tickets']}")
                    with col3:
                        # Get revenue
                        revenue_data, _ = make_request("GET", f"/events/{event['id']}/revenue")
                        if revenue_data:
                            st.write(f"**Revenue:** ${revenue_data['total_revenue']:,.2f}")
                            st.write(f"**Confirmed Bookings:** {revenue_data['confirmed_bookings']}")
        else:
            st.info("No events found. Add some events to get started!")

# Ticket Types Section
elif selected == "Ticket Types":
    st.markdown('<h2 class="section-header">🎟️ Ticket Type Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add Ticket Type", "View Ticket Types"])
    
    with tab1:
        st.subheader("Add New Ticket Type")
        
        with st.form("ticket_type_form"):
            ticket_name = st.text_input("Ticket Type Name*")
            ticket_price = st.number_input("Price*", min_value=0.01, value=50.00, step=0.01)
            ticket_description = st.text_area("Description")
            
            if st.form_submit_button("Add Ticket Type"):
                if ticket_name and ticket_price:
                    ticket_data = {
                        "name": ticket_name,
                        "price": ticket_price,
                        "description": ticket_description if ticket_description else None
                    }
                    
                    result, error = make_request("POST", "/ticket-types", ticket_data)
                    if result:
                        st.success(f"Ticket type '{ticket_name}' added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add ticket type: {error}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab2:
        st.subheader("All Ticket Types")
        ticket_types = get_ticket_types()
        
        if ticket_types:
            for ticket_type in ticket_types:
                with st.expander(f"{ticket_type['name']} - ${ticket_type['price']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Price:** ${ticket_type['price']}")
                        st.write(f"**Description:** {ticket_type.get('description', 'N/A')}")
                    with col2:
                        # Get bookings count
                        bookings_data, _ = make_request("GET", f"/ticket-types/{ticket_type['id']}/bookings")
                        if bookings_data:
                            st.write(f"**Total Bookings:** {len(bookings_data)}")
        else:
            st.info("No ticket types found. Add some ticket types to get started!")

# Bookings Section
elif selected == "Bookings":
    st.markdown('<h2 class="section-header">📖 Booking Management</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Create Booking", "View Bookings"])
    
    with tab1:
        st.subheader("Create New Booking")
        
        events = get_events()
        venues = get_venues()
        ticket_types = get_ticket_types()
        
        event_options = {f"{event['name']} ({event['event_date'][:10]})": event['id'] for event in events}
        venue_options = {venue['name']: venue['id'] for venue in venues}
        ticket_type_options = {f"{tt['name']} (${tt['price']})": tt['id'] for tt in ticket_types}
        
        if not events or not venues or not ticket_types:
            st.warning("Please add events, venues, and ticket types first before creating bookings.")
        else:
            with st.form("booking_form"):
                customer_name = st.text_input("Customer Name*")
                customer_email = st.text_input("Customer Email*")
                event_selection = st.selectbox("Select Event*", options=list(event_options.keys()))
                venue_selection = st.selectbox("Select Venue*", options=list(venue_options.keys()))
                ticket_type_selection = st.selectbox("Select Ticket Type*", options=list(ticket_type_options.keys()))
                quantity = st.number_input("Quantity*", min_value=1, value=1)
                
                if st.form_submit_button("Create Booking"):
                    if customer_name and customer_email and event_selection and venue_selection and ticket_type_selection:
                        booking_data = {
                            "customer_name": customer_name,
                            "customer_email": customer_email,
                            "event_id": event_options[event_selection],
                            "venue_id": venue_options[venue_selection],
                            "ticket_type_id": ticket_type_options[ticket_type_selection],
                            "quantity": quantity
                        }
                        
                        result, error = make_request("POST", "/bookings", booking_data)
                        if result:
                            st.success(f"Booking created successfully! Booking Code: {result['booking_code']}")
                            st.rerun()
                        else:
                            st.error(f"Failed to create booking: {error}")
                    else:
                        st.error("Please fill in all required fields")
    
    with tab2:
        st.subheader("All Bookings")
        bookings = get_bookings()
        
        if bookings:
            # Create a DataFrame for better display
            df_bookings = pd.DataFrame(bookings)
            
            # Display summary
            st.write(f"**Total Bookings:** {len(bookings)}")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "pending", "confirmed", "cancelled"])
            with col2:
                if len(bookings) > 0:
                    events_in_bookings = list(set([b.get('event', {}).get('name', 'N/A') for b in bookings]))
                    event_filter = st.selectbox("Filter by Event", ["All"] + events_in_bookings)
            with col3:
                show_details = st.checkbox("Show Details")
            
            # Apply filters
            filtered_bookings = bookings
            if status_filter != "All":
                filtered_bookings = [b for b in filtered_bookings if b['status'] == status_filter]
            if 'event_filter' in locals() and event_filter != "All":
                filtered_bookings = [b for b in filtered_bookings if b.get('event', {}).get('name') == event_filter]
            
            # Display bookings
            for booking in filtered_bookings:
                status_color = {"pending": "🟡", "confirmed": "🟢", "cancelled": "🔴"}
                status_icon = status_color.get(booking['status'], "⚪")
                
                with st.expander(f"{status_icon} {booking['booking_code']} - {booking['customer_name']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Customer:** {booking['customer_name']}")
                        st.write(f"**Email:** {booking['customer_email']}")
                        st.write(f"**Quantity:** {booking['quantity']}")
                    with col2:
                        st.write(f"**Event:** {booking.get('event', {}).get('name', 'N/A')}")
                        st.write(f"**Venue:** {booking.get('venue', {}).get('name', 'N/A')}")
                        st.write(f"**Ticket Type:** {booking.get('ticket_type', {}).get('name', 'N/A')}")
                    with col3:
                        st.write(f"**Total Price:** ${booking['total_price']}")
                        st.write(f"**Status:** {booking['status']}")
                        st.write(f"**Created:** {booking['created_at'][:10]}")
                    
                    # Status update buttons
                    if booking['status'] != 'confirmed':
                        if st.button(f"Confirm Booking {booking['booking_code']}", key=f"confirm_{booking['id']}"):
                            result, error = make_request("PATCH", f"/bookings/{booking['id']}/status", {"status": "confirmed"})
                            if result:
                                st.success("Booking confirmed!")
                                st.rerun()
                            else:
                                st.error(f"Failed to confirm booking: {error}")
                    
                    if booking['status'] != 'cancelled':
                        if st.button(f"Cancel Booking {booking['booking_code']}", key=f"cancel_{booking['id']}"):
                            result, error = make_request("PATCH", f"/bookings/{booking['id']}/status", {"status": "cancelled"})
                            if result:
                                st.success("Booking cancelled!")
                                st.rerun()
                            else:
                                st.error(f"Failed to cancel booking: {error}")
        else:
            st.info("No bookings found. Create some bookings to get started!")

# Search Section
elif selected == "Search":
    st.markdown('<h2 class="section-header">🔍 Search Bookings</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        event_search = st.text_input("Event Name")
    with col2:
        venue_search = st.text_input("Venue Name")
    with col3:
        ticket_type_search = st.text_input("Ticket Type")
    
    if st.button("Search"):
        params = {}
        if event_search:
            params['event'] = event_search
        if venue_search:
            params['venue'] = venue_search
        if ticket_type_search:
            params['ticket_type'] = ticket_type_search
        
        search_results, error = make_request("GET", "/bookings/search", params=params)
        
        if search_results:
            st.write(f"Found {len(search_results)} booking(s)")
            
            for booking in search_results:
                with st.expander(f"{booking['booking_code']} - {booking['customer_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Event:** {booking.get('event', {}).get('name', 'N/A')}")
                        st.write(f"**Venue:** {booking.get('venue', {}).get('name', 'N/A')}")
                        st.write(f"**Ticket Type:** {booking.get('ticket_type', {}).get('name', 'N/A')}")
                    with col2:
                        st.write(f"**Customer:** {booking['customer_name']}")
                        st.write(f"**Status:** {booking['status']}")
                        st.write(f"**Total:** ${booking['total_price']}")
        elif error:
            st.error(f"Search failed: {error}")
        else:
            st.info("No bookings found matching your search criteria.")

# Analytics Section
elif selected == "Analytics":
    st.markdown('<h2 class="section-header">📈 Analytics Dashboard</h2>', unsafe_allow_html=True)
    
    # Get all data
    stats_data, _ = make_request("GET", "/booking-system/stats")
    bookings = get_bookings()
    events = get_events()
    venues = get_venues()
    
    if stats_data and bookings:
        # Revenue by event
        st.subheader("Revenue by Event")
        event_revenues = []
        for event in events:
            revenue_data, _ = make_request("GET", f"/events/{event['id']}/revenue")
            if revenue_data:
                event_revenues.append(revenue_data)
        
        if event_revenues:
            df_revenue = pd.DataFrame(event_revenues)
            fig_revenue = px.bar(df_revenue, x='event_name', y='total_revenue', 
                               title="Revenue by Event")
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Venue occupancy
        st.subheader("Venue Occupancy Rates")
        venue_occupancy = []
        for venue in venues:
            occupancy_data, _ = make_request("GET", f"/venues/{venue['id']}/occupancy")
            if occupancy_data:
                venue_occupancy.append(occupancy_data)
        
        if venue_occupancy:
            df_occupancy = pd.DataFrame(venue_occupancy)
            fig_occupancy = px.bar(df_occupancy, x='venue_name', y='occupancy_rate',
                                 title="Venue Occupancy Rates (%)")
            st.plotly_chart(fig_occupancy, use_container_width=True)
        
        # Bookings over time
        if bookings:
            df_bookings = pd.DataFrame(bookings)
            df_bookings['created_at'] = pd.to_datetime(df_bookings['created_at'])
            df_bookings['date'] = df_bookings['created_at'].dt.date
            
            bookings_by_date = df_bookings.groupby('date').size().reset_index(name='count')
            
            fig_timeline = px.line(bookings_by_date, x='date', y='count',
                                 title="Bookings Over Time")
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Revenue by ticket type
        if bookings:
            ticket_revenue = df_bookings.groupby('ticket_type').agg({
                'total_price': 'sum',
                'quantity': 'sum'
            }).reset_index()
            
            # Extract ticket type names
            ticket_revenue['ticket_type_name'] = ticket_revenue['ticket_type'].apply(
                lambda x: x.get('name', 'Unknown') if isinstance(x, dict) else 'Unknown'
            )
            
            col1, col2 = st.columns(2)
            with col1:
                fig_ticket_revenue = px.pie(ticket_revenue, values='total_price', 
                                          names='ticket_type_name',
                                          title="Revenue by Ticket Type")
                st.plotly_chart(fig_ticket_revenue, use_container_width=True)
            
            with col2:
                fig_ticket_quantity = px.pie(ticket_revenue, values='quantity',
                                           names='ticket_type_name', 
                                           title="Tickets Sold by Type")
                st.plotly_chart(fig_ticket_quantity, use_container_width=True)
    else:
        st.info("No data available for analytics. Add some bookings to see analytics.")

# Footer
st.markdown("---")
st.markdown("**Ticket Booking System** - Built with FastAPI, SQLAlchemy, and Streamlit") 
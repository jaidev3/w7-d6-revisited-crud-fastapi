import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
import base64
from io import BytesIO
import folium
from streamlit_folium import st_folium

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="QuickMed - Medicine Delivery",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design and accessibility
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50 0%, #2196F3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .medicine-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    
    .cart-summary {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    
    .order-status {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    
    .status-pending { background-color: #ffc107; }
    .status-confirmed { background-color: #17a2b8; }
    .status-preparing { background-color: #fd7e14; }
    .status-out-for-delivery { background-color: #007bff; }
    .status-delivered { background-color: #28a745; }
    .status-cancelled { background-color: #dc3545; }
    
    .emergency-banner {
        background: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }
    
    .accessibility-button {
        font-size: 18px;
        padding: 12px 24px;
        border-radius: 8px;
        border: 2px solid;
        margin: 5px;
    }
    
    /* High contrast mode */
    .high-contrast {
        filter: contrast(150%);
    }
    
    /* Large text mode */
    .large-text {
        font-size: 120% !important;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'accessibility_mode' not in st.session_state:
    st.session_state.accessibility_mode = 'normal'

# Helper functions
def make_request(method: str, endpoint: str, data: dict = None, files: dict = None, params: dict = None) -> Optional[Dict]:
    """Make API request with authentication."""
    headers = {}
    if st.session_state.token:
        headers['Authorization'] = f"Bearer {st.session_state.token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files, data=data)
            else:
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            headers['Content-Type'] = 'application/json'
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        elif method == "PATCH":
            headers['Content-Type'] = 'application/json'
            response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def login_user(email: str, password: str) -> bool:
    """Login user and store token."""
    data = {"email": email, "password": password}
    response = make_request("POST", "/auth/login", data=data)
    
    if response:
        st.session_state.token = response['access_token']
        st.session_state.user = response['user']
        return True
    return False

def register_user(user_data: dict) -> bool:
    """Register new user."""
    response = make_request("POST", "/auth/register", data=user_data)
    
    if response:
        st.session_state.token = response['access_token']
        st.session_state.user = response['user']
        return True
    return False

def logout_user():
    """Logout user and clear session."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.cart = []
    st.rerun()

def format_currency(amount: float) -> str:
    """Format currency for display."""
    return f"₹{amount:.2f}"

def get_order_status_class(status: str) -> str:
    """Get CSS class for order status."""
    return f"status-{status.lower().replace('_', '-')}"

# Accessibility features
def render_accessibility_controls():
    """Render accessibility controls in sidebar."""
    st.sidebar.markdown("### ♿ Accessibility")
    
    accessibility_mode = st.sidebar.selectbox(
        "Display Mode",
        ["Normal", "High Contrast", "Large Text"],
        index=0 if st.session_state.accessibility_mode == 'normal' else 
              1 if st.session_state.accessibility_mode == 'high_contrast' else 2
    )
    
    if accessibility_mode == "High Contrast":
        st.session_state.accessibility_mode = 'high_contrast'
        st.markdown('<div class="high-contrast">', unsafe_allow_html=True)
    elif accessibility_mode == "Large Text":
        st.session_state.accessibility_mode = 'large_text'
        st.markdown('<div class="large-text">', unsafe_allow_html=True)
    else:
        st.session_state.accessibility_mode = 'normal'
    
    if st.sidebar.button("🔊 Read Page Aloud", help="Screen reader support"):
        st.sidebar.info("Screen reader: Page content available for audio reading")

# Main app header
def render_header():
    """Render main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>💊 QuickMed - Medicine Delivery</h1>
        <p>Your health, delivered in 10-30 minutes</p>
    </div>
    """, unsafe_allow_html=True)

# Authentication pages
def render_login_page():
    """Render login page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🔐 Login to QuickMed")
        
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Login", use_container_width=True):
                    if email and password:
                        if login_user(email, password):
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
                    else:
                        st.error("Please fill in all fields")
            
            with col2:
                if st.form_submit_button("Register", use_container_width=True):
                    st.session_state.show_register = True
                    st.rerun()

def render_register_page():
    """Render registration page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 📝 Register for QuickMed")
        
        with st.form("register_form"):
            # Basic information
            st.markdown("### Basic Information")
            full_name = st.text_input("Full Name*", placeholder="John Doe")
            email = st.text_input("Email Address*", placeholder="john@example.com")
            phone = st.text_input("Phone Number*", placeholder="+91 9876543210")
            password = st.text_input("Password*", type="password", help="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password*", type="password")
            
            # Medical information
            st.markdown("### Medical Profile (Optional)")
            dob = st.date_input("Date of Birth", value=None)
            
            col1, col2 = st.columns(2)
            with col1:
                emergency_contact_name = st.text_input("Emergency Contact Name")
            with col2:
                emergency_contact_phone = st.text_input("Emergency Contact Phone")
            
            medical_conditions = st.text_area("Medical Conditions", 
                                            placeholder="Diabetes, Hypertension, etc. (comma-separated)")
            allergies = st.text_area("Allergies", 
                                    placeholder="Penicillin, Sulfa drugs, etc. (comma-separated)")
            
            # Address information
            st.markdown("### Delivery Address")
            address_line1 = st.text_input("Address Line 1")
            address_line2 = st.text_input("Address Line 2")
            col1, col2, col3 = st.columns(3)
            with col1:
                city = st.text_input("City")
            with col2:
                state = st.text_input("State")
            with col3:
                pincode = st.text_input("PIN Code")
            
            # Terms and conditions
            agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy*")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Register", use_container_width=True):
                    if not all([full_name, email, phone, password, confirm_password, agree_terms]):
                        st.error("Please fill in all required fields and agree to terms")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        user_data = {
                            "full_name": full_name,
                            "email": email,
                            "phone_number": phone,
                            "password": password,
                            "date_of_birth": dob.isoformat() if dob else None,
                            "emergency_contact_name": emergency_contact_name or None,
                            "emergency_contact_phone": emergency_contact_phone or None,
                            "medical_conditions": [cond.strip() for cond in medical_conditions.split(",") if cond.strip()] if medical_conditions else None,
                            "allergies": [allergy.strip() for allergy in allergies.split(",") if allergy.strip()] if allergies else None,
                            "address_line1": address_line1 or None,
                            "address_line2": address_line2 or None,
                            "city": city or None,
                            "state": state or None,
                            "pincode": pincode or None
                        }
                        
                        if register_user(user_data):
                            st.success("Registration successful! Welcome to QuickMed!")
                            st.rerun()
                        else:
                            st.error("Registration failed. Please try again.")
            
            with col2:
                if st.form_submit_button("Back to Login", use_container_width=True):
                    st.session_state.show_register = False
                    st.rerun()

# Medicine browsing and search
def render_medicine_catalog():
    """Render medicine catalog with search and filters."""
    st.markdown("## 💊 Medicine Catalog")
    
    # Search and filters
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search medicines", placeholder="Search by name, generic name, or condition")
    
    with col2:
        # Get categories
        categories_response = make_request("GET", "/categories")
        categories = categories_response if categories_response else []
        category_options = ["All Categories"] + [cat['name'] for cat in categories]
        selected_category = st.selectbox("Category", category_options)
    
    with col3:
        prescription_filter = st.selectbox("Prescription", ["All", "Prescription Required", "Over the Counter"])
    
    with col4:
        sort_by = st.selectbox("Sort by", ["Name", "Price (Low to High)", "Price (High to Low)", "Delivery Time"])
    
    # Emergency delivery banner
    if st.checkbox("🚨 Emergency Delivery (10 mins)", help="For urgent medical needs"):
        st.markdown("""
        <div class="emergency-banner">
            🚨 EMERGENCY DELIVERY MODE ACTIVATED<br>
            Medicines will be delivered within 10 minutes | Additional charges apply
        </div>
        """, unsafe_allow_html=True)
    
    # Build search parameters
    params = {}
    if search_query:
        params['q'] = search_query
    if selected_category != "All Categories":
        # Find category ID
        category_id = next((cat['id'] for cat in categories if cat['name'] == selected_category), None)
        if category_id:
            params['category_id'] = category_id
    if prescription_filter == "Prescription Required":
        params['prescription_required'] = True
    elif prescription_filter == "Over the Counter":
        params['prescription_required'] = False
    
    # Get medicines
    medicines_response = make_request("GET", "/medicines", params=params)
    medicines = medicines_response if medicines_response else []
    
    # Display medicines
    if medicines:
        for medicine in medicines:
            render_medicine_card(medicine)
    else:
        st.info("No medicines found matching your criteria.")

def render_medicine_card(medicine: dict):
    """Render individual medicine card."""
    with st.container():
        st.markdown(f"""
        <div class="medicine-card">
            <div style="display: flex; justify-content: between; align-items: start;">
                <div style="flex: 1;">
                    <h3>{medicine['name']}</h3>
                    <p><strong>Generic:</strong> {medicine.get('generic_name', 'N/A')}</p>
                    <p><strong>Category:</strong> {medicine['category']['name']}</p>
                    <p><strong>Manufacturer:</strong> {medicine.get('manufacturer', 'N/A')}</p>
                    <p><strong>Strength:</strong> {medicine.get('strength', 'N/A')}</p>
                </div>
                <div style="text-align: right; min-width: 200px;">
                    <h4 style="color: #4CAF50;">{format_currency(medicine.get('discounted_price', medicine['price']))}</h4>
                    {f"<s>{format_currency(medicine['price'])}</s>" if medicine.get('discount_percentage', 0) > 0 else ""}
                    <p><strong>Stock:</strong> {medicine['stock_quantity']}</p>
                    <p><strong>Delivery:</strong> {medicine['delivery_time_minutes']} mins</p>
                    {"<span style='color: #ff6b6b;'>⚠️ Prescription Required</span>" if medicine['prescription_required'] else "<span style='color: #4CAF50;'>✓ Over the Counter</span>"}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            quantity = st.number_input(f"Qty", min_value=1, max_value=medicine['stock_quantity'], 
                                     value=1, key=f"qty_{medicine['id']}")
        
        with col2:
            if st.button("🛒 Add to Cart", key=f"add_{medicine['id']}", 
                        disabled=medicine['stock_quantity'] == 0):
                add_to_cart(medicine['id'], quantity, medicine['prescription_required'])
        
        with col3:
            if st.button("📋 Details", key=f"details_{medicine['id']}"):
                show_medicine_details(medicine)
        
        with col4:
            if medicine.get('alternatives'):
                if st.button("🔄 View Alternatives", key=f"alt_{medicine['id']}"):
                    show_alternatives(medicine['id'])

def add_to_cart(medicine_id: int, quantity: int, prescription_required: bool):
    """Add medicine to cart."""
    cart_item = {
        "medicine_id": medicine_id,
        "quantity": quantity
    }
    
    # If prescription required, check if user has valid prescriptions
    if prescription_required:
        prescriptions_response = make_request("GET", "/prescriptions")
        if prescriptions_response:
            valid_prescriptions = [p for p in prescriptions_response if p['status'] == 'verified']
            if valid_prescriptions:
                # For demo, use the first valid prescription
                cart_item["prescription_id"] = valid_prescriptions[0]['id']
            else:
                st.error("This medicine requires a verified prescription. Please upload and verify your prescription first.")
                return
        else:
            st.error("Unable to verify prescriptions. Please try again.")
            return
    
    response = make_request("POST", "/cart/items", data=cart_item)
    if response:
        st.success(f"Added {quantity} item(s) to cart!")
        st.rerun()

# Shopping cart
def render_cart_page():
    """Render shopping cart page."""
    st.markdown("## 🛒 Shopping Cart")
    
    cart_response = make_request("GET", "/cart")
    if not cart_response or not cart_response['items']:
        st.info("Your cart is empty. Browse medicines to add items.")
        if st.button("🔍 Browse Medicines"):
            st.session_state.page = 'catalog'
            st.rerun()
        return
    
    cart = cart_response
    
    # Cart items
    for item in cart['items']:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{item['medicine']['name']}**")
                st.markdown(f"*{item['medicine']['category']['name']}*")
                if item['medicine']['prescription_required']:
                    st.markdown("⚠️ *Prescription item*")
            
            with col2:
                st.markdown(f"**{format_currency(item['medicine']['price'])}**")
            
            with col3:
                new_quantity = st.number_input("Qty", min_value=1, value=item['quantity'], 
                                             key=f"cart_qty_{item['id']}")
                if new_quantity != item['quantity']:
                    update_cart_item(item['id'], new_quantity)
            
            with col4:
                st.markdown(f"**{format_currency(item['subtotal'])}**")
            
            with col5:
                if st.button("🗑️", key=f"remove_{item['id']}", help="Remove from cart"):
                    remove_from_cart(item['id'])
    
    # Cart summary
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="cart-summary">
            <h4>Cart Summary</h4>
            <p><strong>Items:</strong> {cart['total_items']}</p>
            <p><strong>Subtotal:</strong> {format_currency(cart['subtotal'])}</p>
            <p><strong>Estimated Delivery:</strong> {cart['estimated_delivery_time']} mins</p>
            <hr>
            <h4><strong>Total: {format_currency(cart['subtotal'])}</strong></h4>
        </div>
        """, unsafe_allow_html=True)
        
        if cart['prescription_required_items']:
            st.warning(f"⚠️ {len(cart['prescription_required_items'])} prescription items in cart")
        
        if st.button("🚀 Proceed to Checkout", use_container_width=True):
            st.session_state.page = 'checkout'
            st.rerun()

def update_cart_item(cart_item_id: int, quantity: int):
    """Update cart item quantity."""
    response = make_request("PUT", f"/cart/items/{cart_item_id}", data={"quantity": quantity})
    if response:
        st.rerun()

def remove_from_cart(cart_item_id: int):
    """Remove item from cart."""
    response = make_request("DELETE", f"/cart/items/{cart_item_id}")
    if response:
        st.success("Item removed from cart")
        st.rerun()

# Checkout and orders
def render_checkout_page():
    """Render checkout page."""
    st.markdown("## 🚀 Checkout")
    
    # Get cart
    cart_response = make_request("GET", "/cart")
    if not cart_response or not cart_response['items']:
        st.error("Your cart is empty!")
        return
    
    cart = cart_response
    
    # Delivery details
    st.markdown("### 📍 Delivery Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        delivery_address = st.text_area("Delivery Address*", 
                                       value=f"{st.session_state.user.get('address_line1', '')}\n{st.session_state.user.get('address_line2', '')}\n{st.session_state.user.get('city', '')}, {st.session_state.user.get('state', '')} - {st.session_state.user.get('pincode', '')}")
        
        special_instructions = st.text_area("Special Instructions", 
                                          placeholder="Any specific delivery instructions...")
    
    with col2:
        delivery_urgency = st.selectbox("Delivery Speed", [
            ("STANDARD", "Standard (30 mins) - Free"),
            ("EXPRESS", "Express (15 mins) - ₹50"),
            ("EMERGENCY", "Emergency (10 mins) - ₹150")
        ], format_func=lambda x: x[1])
        
        # Show delivery estimate
        estimate_response = make_request("GET", "/delivery/estimate", 
                                       params={"urgency": delivery_urgency[0]})
        if estimate_response:
            st.info(f"⏱️ Estimated delivery: {estimate_response['estimated_time_minutes']} minutes")
            delivery_fee = estimate_response['delivery_fee']
        else:
            delivery_fee = 0
    
    # Order summary
    st.markdown("### 📋 Order Summary")
    
    total_amount = cart['subtotal'] + delivery_fee
    
    st.markdown(f"""
    <div class="cart-summary">
        <p><strong>Items ({cart['total_items']}):</strong> {format_currency(cart['subtotal'])}</p>
        <p><strong>Delivery Fee:</strong> {format_currency(delivery_fee)}</p>
        <hr>
        <h4><strong>Total Amount: {format_currency(total_amount)}</strong></h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Payment and place order
    st.markdown("### 💳 Payment")
    
    payment_method = st.selectbox("Payment Method", [
        "Cash on Delivery",
        "UPI",
        "Credit/Debit Card",
        "Digital Wallet"
    ])
    
    if payment_method != "Cash on Delivery":
        st.info("💡 For demo purposes, all payments are simulated as successful.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Place Order", use_container_width=True):
            place_order(delivery_address, delivery_urgency[0], special_instructions)
    
    with col2:
        if st.button("⬅️ Back to Cart", use_container_width=True):
            st.session_state.page = 'cart'
            st.rerun()

def place_order(delivery_address: str, delivery_urgency: str, special_instructions: str):
    """Place the order."""
    order_data = {
        "delivery_address": delivery_address,
        "delivery_urgency": delivery_urgency,
        "special_instructions": special_instructions
    }
    
    response = make_request("POST", "/orders", data=order_data)
    if response:
        st.success("🎉 Order placed successfully!")
        st.balloons()
        
        # Show order details
        st.markdown(f"""
        ### Order Confirmation
        **Order Number:** {response['order_number']}  
        **Total Amount:** {format_currency(response['total_amount'])}  
        **Estimated Delivery:** {response.get('estimated_delivery_time', 'TBD')}  
        **Status:** {response['status'].title()}
        """)
        
        if st.button("📱 Track Order"):
            st.session_state.page = 'orders'
            st.rerun()

# Orders and tracking
def render_orders_page():
    """Render orders page with tracking."""
    st.markdown("## 📦 My Orders")
    
    orders_response = make_request("GET", "/orders")
    if not orders_response:
        st.info("You have no orders yet.")
        return
    
    orders = orders_response
    
    # Order filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", 
                                   ["All", "Pending", "Confirmed", "Preparing", "Out for Delivery", "Delivered", "Cancelled"])
    
    # Display orders
    for order in orders:
        if status_filter != "All" and order['status'].title() != status_filter:
            continue
            
        with st.expander(f"Order #{order['order_number']} - {format_currency(order['total_amount'])}", 
                        expanded=order['status'] in ['confirmed', 'preparing', 'out_for_delivery']):
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**Order Date:** {order['created_at'][:10]}")
                st.markdown(f"**Items:** {len(order['items'])}")
                st.markdown(f"**Delivery:** {order['delivery_urgency'].title()}")
            
            with col2:
                st.markdown(f"**Total:** {format_currency(order['total_amount'])}")
                st.markdown(f"**Delivery Fee:** {format_currency(order['delivery_fee'])}")
                if order.get('estimated_delivery_time'):
                    st.markdown(f"**ETA:** {order['estimated_delivery_time'][:16]}")
            
            with col3:
                status_class = get_order_status_class(order['status'])
                st.markdown(f"""
                <div class="order-status {status_class}">
                    {order['status'].replace('_', ' ').title()}
                </div>
                """, unsafe_allow_html=True)
            
            # Order items
            st.markdown("**Items:**")
            for item in order['items']:
                st.markdown(f"- {item['medicine']['name']} × {item['quantity']} = {format_currency(item['total_price'])}")
            
            # Delivery address
            st.markdown(f"**Delivery Address:** {order['delivery_address']}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if order['status'] in ['confirmed', 'preparing', 'out_for_delivery']:
                    if st.button("📍 Track Live", key=f"track_{order['id']}"):
                        show_order_tracking(order)
            
            with col2:
                if order['status'] == 'pending':
                    if st.button("❌ Cancel", key=f"cancel_{order['id']}"):
                        cancel_order(order['id'])
            
            with col3:
                if st.button("📄 Receipt", key=f"receipt_{order['id']}"):
                    show_receipt(order)

def show_order_tracking(order: dict):
    """Show real-time order tracking."""
    st.markdown(f"### 📍 Tracking Order #{order['order_number']}")
    
    # Simulated tracking data
    tracking_steps = [
        {"status": "Order Placed", "time": order['created_at'], "completed": True},
        {"status": "Order Confirmed", "time": order['created_at'], "completed": order['status'] in ['confirmed', 'preparing', 'out_for_delivery', 'delivered']},
        {"status": "Preparing", "time": "", "completed": order['status'] in ['preparing', 'out_for_delivery', 'delivered']},
        {"status": "Out for Delivery", "time": "", "completed": order['status'] in ['out_for_delivery', 'delivered']},
        {"status": "Delivered", "time": order.get('actual_delivery_time', ''), "completed": order['status'] == 'delivered'},
    ]
    
    # Progress bar
    progress = sum(1 for step in tracking_steps if step['completed']) / len(tracking_steps)
    st.progress(progress)
    
    # Tracking timeline
    for i, step in enumerate(tracking_steps):
        icon = "✅" if step['completed'] else "⏳" if i == sum(1 for s in tracking_steps if s['completed']) else "⭕"
        st.markdown(f"{icon} **{step['status']}** {step['time']}")
    
    # Delivery map (simulated)
    if order['status'] == 'out_for_delivery':
        st.markdown("### 🗺️ Live Location")
        
        # Create a simple map (you would use real coordinates in production)
        map_center = [28.6139, 77.2090]  # Delhi coordinates as example
        delivery_map = folium.Map(location=map_center, zoom_start=12)
        
        # Add markers
        folium.Marker(map_center, popup="Delivery Partner", icon=folium.Icon(color='blue')).add_to(delivery_map)
        folium.Marker([28.6239, 77.2190], popup="Delivery Address", icon=folium.Icon(color='green')).add_to(delivery_map)
        
        st_folium(delivery_map, width=700, height=400)
        
        st.info("🚴‍♂️ Your delivery partner is on the way! ETA: 8 minutes")

# Prescription management
def render_prescriptions_page():
    """Render prescription management page."""
    st.markdown("## 📋 My Prescriptions")
    
    tab1, tab2 = st.tabs(["📤 Upload New", "📋 My Prescriptions"])
    
    with tab1:
        st.markdown("### Upload Prescription")
        
        with st.form("prescription_upload"):
            col1, col2 = st.columns(2)
            
            with col1:
                doctor_name = st.text_input("Doctor Name*")
                doctor_license = st.text_input("Doctor License Number")
                hospital_clinic = st.text_input("Hospital/Clinic Name")
            
            with col2:
                prescription_date = st.date_input("Prescription Date*", value=datetime.now().date())
                valid_until = st.date_input("Valid Until", value=datetime.now().date() + timedelta(days=30))
            
            uploaded_file = st.file_uploader("Upload Prescription Image*", 
                                           type=['jpg', 'jpeg', 'png', 'pdf'],
                                           help="Clear image of your prescription")
            
            if st.form_submit_button("📤 Upload Prescription"):
                if uploaded_file and doctor_name and prescription_date:
                    upload_prescription(uploaded_file, doctor_name, doctor_license, 
                                      hospital_clinic, prescription_date, valid_until)
                else:
                    st.error("Please fill in all required fields and upload an image")
    
    with tab2:
        prescriptions_response = make_request("GET", "/prescriptions")
        if prescriptions_response:
            for prescription in prescriptions_response:
                render_prescription_card(prescription)
        else:
            st.info("No prescriptions uploaded yet.")

def upload_prescription(uploaded_file, doctor_name: str, doctor_license: str, 
                       hospital_clinic: str, prescription_date, valid_until):
    """Upload prescription file."""
    files = {"file": uploaded_file.getvalue()}
    data = {
        "doctor_name": doctor_name,
        "doctor_license": doctor_license,
        "hospital_clinic": hospital_clinic,
        "prescription_date": prescription_date.isoformat(),
        "valid_until": valid_until.isoformat()
    }
    
    response = make_request("POST", "/prescriptions/upload", data=data, files={"file": uploaded_file})
    if response:
        st.success("Prescription uploaded successfully! It will be verified by our pharmacist.")
        st.rerun()

def render_prescription_card(prescription: dict):
    """Render prescription card."""
    status_color = {
        'pending': '#ffc107',
        'verified': '#28a745',
        'rejected': '#dc3545'
    }
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Dr. {prescription['doctor_name']}**")
            st.markdown(f"*{prescription.get('hospital_clinic', 'N/A')}*")
            st.markdown(f"Date: {prescription['prescription_date'][:10]}")
        
        with col2:
            st.markdown(f"**Status:** <span style='color: {status_color.get(prescription['status'], '#666')}'>{prescription['status'].title()}</span>", 
                       unsafe_allow_html=True)
            if prescription.get('valid_until'):
                st.markdown(f"Valid until: {prescription['valid_until'][:10]}")
        
        with col3:
            if prescription['status'] == 'verified':
                if st.button("🛒 Shop Medicines", key=f"shop_{prescription['id']}"):
                    st.session_state.page = 'catalog'
                    st.rerun()
        
        if prescription.get('verification_notes'):
            st.markdown(f"**Notes:** {prescription['verification_notes']}")

# Profile management
def render_profile_page():
    """Render user profile page."""
    st.markdown("## 👤 My Profile")
    
    user = st.session_state.user
    
    tab1, tab2, tab3 = st.tabs(["📝 Personal Info", "📍 Address", "🏥 Medical Profile"])
    
    with tab1:
        with st.form("personal_info"):
            st.markdown("### Personal Information")
            
            full_name = st.text_input("Full Name", value=user.get('full_name', ''))
            email = st.text_input("Email", value=user.get('email', ''), disabled=True)
            phone = st.text_input("Phone", value=user.get('phone_number', ''), disabled=True)
            
            if user.get('date_of_birth'):
                dob = st.date_input("Date of Birth", value=datetime.fromisoformat(user['date_of_birth']).date())
            else:
                dob = st.date_input("Date of Birth")
            
            col1, col2 = st.columns(2)
            with col1:
                emergency_name = st.text_input("Emergency Contact Name", 
                                             value=user.get('emergency_contact_name', ''))
            with col2:
                emergency_phone = st.text_input("Emergency Contact Phone", 
                                               value=user.get('emergency_contact_phone', ''))
            
            if st.form_submit_button("💾 Update Personal Info"):
                update_profile({
                    "full_name": full_name,
                    "date_of_birth": dob.isoformat() if dob else None,
                    "emergency_contact_name": emergency_name,
                    "emergency_contact_phone": emergency_phone
                })
    
    with tab2:
        with st.form("address_info"):
            st.markdown("### Delivery Address")
            
            address_line1 = st.text_input("Address Line 1", value=user.get('address_line1', ''))
            address_line2 = st.text_input("Address Line 2", value=user.get('address_line2', ''))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                city = st.text_input("City", value=user.get('city', ''))
            with col2:
                state = st.text_input("State", value=user.get('state', ''))
            with col3:
                pincode = st.text_input("PIN Code", value=user.get('pincode', ''))
            
            if st.form_submit_button("💾 Update Address"):
                update_profile({
                    "address_line1": address_line1,
                    "address_line2": address_line2,
                    "city": city,
                    "state": state,
                    "pincode": pincode
                })
    
    with tab3:
        with st.form("medical_info"):
            st.markdown("### Medical Profile")
            
            conditions_text = ", ".join(user.get('medical_conditions', [])) if user.get('medical_conditions') else ""
            medical_conditions = st.text_area("Medical Conditions", value=conditions_text,
                                            placeholder="Diabetes, Hypertension, etc. (comma-separated)")
            
            allergies_text = ", ".join(user.get('allergies', [])) if user.get('allergies') else ""
            allergies = st.text_area("Allergies", value=allergies_text,
                                    placeholder="Penicillin, Sulfa drugs, etc. (comma-separated)")
            
            if st.form_submit_button("💾 Update Medical Profile"):
                update_profile({
                    "medical_conditions": [cond.strip() for cond in medical_conditions.split(",") if cond.strip()] if medical_conditions else [],
                    "allergies": [allergy.strip() for allergy in allergies.split(",") if allergy.strip()] if allergies else []
                })

def update_profile(data: dict):
    """Update user profile."""
    response = make_request("PUT", "/auth/profile", data=data)
    if response:
        st.session_state.user = response
        st.success("Profile updated successfully!")
        st.rerun()

# Main navigation
def render_navigation():
    """Render main navigation."""
    if st.session_state.user:
        # Logged in navigation
        st.sidebar.markdown(f"### Welcome, {st.session_state.user['full_name'].split()[0]}! 👋")
        
        # Quick stats
        cart_response = make_request("GET", "/cart")
        cart_count = len(cart_response['items']) if cart_response else 0
        
        if cart_count > 0:
            st.sidebar.success(f"🛒 Cart: {cart_count} items")
        
        # Navigation menu
        pages = {
            "🏠 Home": "home",
            "💊 Browse Medicines": "catalog", 
            f"🛒 Cart ({cart_count})": "cart",
            "📦 My Orders": "orders",
            "📋 Prescriptions": "prescriptions",
            "👤 Profile": "profile"
        }
        
        selected_page = st.sidebar.selectbox("Navigate", list(pages.keys()))
        st.session_state.page = pages[selected_page]
        
        # Emergency contact
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🚨 Emergency")
        if st.sidebar.button("🚑 Emergency Delivery", use_container_width=True):
            st.sidebar.error("Emergency feature would contact nearest pharmacy for urgent medication needs.")
        
        # Logout
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            logout_user()
    
    # Accessibility controls
    render_accessibility_controls()

# Main app logic
def main():
    """Main application logic."""
    render_header()
    
    # Handle authentication
    if not st.session_state.token:
        if st.session_state.get('show_register', False):
            render_register_page()
        else:
            render_login_page()
        return
    
    # Render navigation
    render_navigation()
    
    # Route to appropriate page
    page = st.session_state.get('page', 'home')
    
    if page == 'home':
        render_home_page()
    elif page == 'catalog':
        render_medicine_catalog()
    elif page == 'cart':
        render_cart_page()
    elif page == 'checkout':
        render_checkout_page()
    elif page == 'orders':
        render_orders_page()
    elif page == 'prescriptions':
        render_prescriptions_page()
    elif page == 'profile':
        render_profile_page()

def render_home_page():
    """Render home page dashboard."""
    st.markdown("## 🏠 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Quick stats
    with col1:
        cart_response = make_request("GET", "/cart")
        cart_count = len(cart_response['items']) if cart_response else 0
        st.metric("🛒 Cart Items", cart_count)
    
    with col2:
        orders_response = make_request("GET", "/orders")
        orders_count = len(orders_response) if orders_response else 0
        st.metric("📦 Total Orders", orders_count)
    
    with col3:
        prescriptions_response = make_request("GET", "/prescriptions")
        prescriptions_count = len(prescriptions_response) if prescriptions_response else 0
        st.metric("📋 Prescriptions", prescriptions_count)
    
    with col4:
        if orders_response:
            active_orders = [o for o in orders_response if o['status'] in ['confirmed', 'preparing', 'out_for_delivery']]
            st.metric("🚚 Active Orders", len(active_orders))
        else:
            st.metric("🚚 Active Orders", 0)
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💊 Browse Medicines", use_container_width=True):
            st.session_state.page = 'catalog'
            st.rerun()
    
    with col2:
        if st.button("📋 Upload Prescription", use_container_width=True):
            st.session_state.page = 'prescriptions'
            st.rerun()
    
    with col3:
        if st.button("📦 Track Orders", use_container_width=True):
            st.session_state.page = 'orders'
            st.rerun()
    
    with col4:
        if st.button("🚨 Emergency Order", use_container_width=True):
            st.error("Emergency delivery would be initiated for urgent medical needs.")
    
    # Recent activity
    st.markdown("### 📊 Recent Activity")
    
    if orders_response:
        recent_orders = orders_response[:3]  # Show last 3 orders
        for order in recent_orders:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Order #{order['order_number']}**")
                with col2:
                    st.markdown(f"{format_currency(order['total_amount'])}")
                with col3:
                    status_class = get_order_status_class(order['status'])
                    st.markdown(f"<span class='order-status {status_class}'>{order['status'].title()}</span>", 
                               unsafe_allow_html=True)
    else:
        st.info("No recent orders. Start by browsing our medicine catalog!")

if __name__ == "__main__":
    main() 
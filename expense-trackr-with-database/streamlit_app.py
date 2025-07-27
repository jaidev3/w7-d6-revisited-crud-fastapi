import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e40af;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
    }
    .category-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .expense-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    .success-message {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #a7f3d0;
    }
    .error-message {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #fca5a5;
    }
</style>
""", unsafe_allow_html=True)

def get_categories():
    """Fetch available categories from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/categories")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return ["Food & Dining", "Transportation", "Shopping", "Entertainment", 
                "Bills & Utilities", "Healthcare", "Travel", "Education", 
                "Personal Care", "Home & Garden", "Groceries", "Insurance", 
                "Gifts & Donations", "Business", "Other"]

def create_expense(expense_data):
    """Create a new expense via API"""
    try:
        response = requests.post(f"{API_BASE_URL}/expenses", json=expense_data)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def get_expenses(category=None, start_date=None, end_date=None, limit=1000):
    """Fetch expenses from API with optional filters"""
    try:
        params = {"limit": limit}
        if category:
            params["category"] = category
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")
        
        response = requests.get(f"{API_BASE_URL}/expenses", params=params)
        if response.status_code == 200:
            return response.json()
        return {"expenses": [], "total_count": 0, "filtered_total": 0}
    except:
        return {"expenses": [], "total_count": 0, "filtered_total": 0}

def delete_expense(expense_id):
    """Delete an expense via API"""
    try:
        response = requests.delete(f"{API_BASE_URL}/expenses/{expense_id}")
        return response.status_code == 200
    except:
        return False

def get_total_expenses(start_date=None, end_date=None):
    """Get total expenses and category breakdown"""
    try:
        params = {}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")
        
        response = requests.get(f"{API_BASE_URL}/expenses/total", params=params)
        if response.status_code == 200:
            return response.json()
        return {"total_amount": 0, "total_count": 0, "category_breakdown": {}}
    except:
        return {"total_amount": 0, "total_count": 0, "category_breakdown": {}}

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_date(date_str):
    """Format date string for display"""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except:
        return date_str

# Main app
def main():
    st.markdown('<h1 class="main-header">💰 Expense Tracker</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Add Expense", "View Expenses", "Analytics"])
    
    # Initialize session state
    if 'refresh_data' not in st.session_state:
        st.session_state.refresh_data = False
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Add Expense":
        show_add_expense()
    elif page == "View Expenses":
        show_view_expenses()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    """Dashboard with overview metrics and charts"""
    st.header("📊 Dashboard")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    # Get total data
    total_data = get_total_expenses(start_date, end_date)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Expenses", format_currency(total_data["total_amount"]))
    with col2:
        st.metric("Number of Expenses", total_data["total_count"])
    with col3:
        avg_expense = total_data["total_amount"] / max(total_data["total_count"], 1)
        st.metric("Average Expense", format_currency(avg_expense))
    
    if total_data["category_breakdown"]:
        # Category breakdown chart
        st.subheader("📈 Spending by Category")
        
        categories = list(total_data["category_breakdown"].keys())
        amounts = list(total_data["category_breakdown"].values())
        
        # Pie chart
        fig_pie = px.pie(
            values=amounts,
            names=categories,
            title="Expense Distribution by Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar chart
        fig_bar = px.bar(
            x=categories,
            y=amounts,
            title="Spending by Category",
            labels={"x": "Category", "y": "Amount ($)"},
            color=amounts,
            color_continuous_scale="viridis"
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent expenses
    st.subheader("📝 Recent Expenses")
    expenses_data = get_expenses(limit=5)
    if expenses_data["expenses"]:
        for expense in expenses_data["expenses"]:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{expense['title']}**")
                    st.write(expense['description'] or "No description")
                with col2:
                    st.write(f"**{format_currency(expense['amount'])}**")
                with col3:
                    st.write(expense['category'])
                with col4:
                    st.write(format_date(expense['date']))
                st.divider()
    else:
        st.info("No expenses found. Add some expenses to see them here!")

def show_add_expense():
    """Form to add new expenses"""
    st.header("➕ Add New Expense")
    
    categories = get_categories()
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Expense Title*", placeholder="e.g., Grocery Shopping")
            amount = st.number_input("Amount ($)*", min_value=0.01, step=0.01, format="%.2f")
            category = st.selectbox("Category*", categories)
        
        with col2:
            description = st.text_area("Description", placeholder="Optional description")
            expense_date = st.date_input("Date", value=date.today())
        
        submit_button = st.form_submit_button("💾 Add Expense", use_container_width=True)
        
        if submit_button:
            if not title.strip():
                st.error("Please enter a title for the expense.")
            elif amount <= 0:
                st.error("Please enter a valid amount greater than 0.")
            else:
                expense_data = {
                    "title": title.strip(),
                    "amount": float(amount),
                    "category": category,
                    "description": description.strip() if description.strip() else None,
                    "date": expense_date.isoformat()
                }
                
                success, result = create_expense(expense_data)
                if success:
                    st.success("✅ Expense added successfully!")
                    st.session_state.refresh_data = True
                    st.balloons()
                else:
                    st.error(f"❌ Error adding expense: {result}")

def show_view_expenses():
    """View and manage expenses with filtering"""
    st.header("📋 View Expenses")
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    categories = get_categories()
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All Categories"] + categories)
        filter_category = None if filter_category == "All Categories" else filter_category
    
    with col2:
        filter_start_date = st.date_input("From Date", value=None)
    
    with col3:
        filter_end_date = st.date_input("To Date", value=None)
    
    # Get filtered expenses
    expenses_data = get_expenses(
        category=filter_category,
        start_date=filter_start_date,
        end_date=filter_end_date
    )
    
    # Summary
    st.subheader("📊 Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Expenses", expenses_data["total_count"])
    with col2:
        st.metric("Filtered Total", format_currency(expenses_data["filtered_total"]))
    with col3:
        if expenses_data["total_count"] > 0:
            avg = expenses_data["filtered_total"] / expenses_data["total_count"]
            st.metric("Average", format_currency(avg))
        else:
            st.metric("Average", "$0.00")
    
    # Expenses list
    if expenses_data["expenses"]:
        st.subheader("💳 Expenses")
        
        for expense in expenses_data["expenses"]:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    st.write(f"**{expense['title']}**")
                    if expense['description']:
                        st.write(f"*{expense['description']}*")
                
                with col2:
                    st.write(f"**{format_currency(expense['amount'])}**")
                
                with col3:
                    st.write(f"📁 {expense['category']}")
                
                with col4:
                    st.write(f"📅 {format_date(expense['date'])}")
                
                with col5:
                    if st.button("🗑️", key=f"delete_{expense['id']}", help="Delete expense"):
                        if delete_expense(expense['id']):
                            st.success("Expense deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete expense")
                
                st.divider()
    else:
        st.info("No expenses found matching your filters.")

def show_analytics():
    """Advanced analytics and insights"""
    st.header("📈 Analytics & Insights")
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Analysis Start Date", value=date.today() - timedelta(days=90))
    with col2:
        end_date = st.date_input("Analysis End Date", value=date.today())
    
    # Get data
    total_data = get_total_expenses(start_date, end_date)
    expenses_data = get_expenses(start_date=start_date, end_date=end_date, limit=1000)
    
    if not expenses_data["expenses"]:
        st.info("No data available for the selected date range.")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(expenses_data["expenses"])
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    
    # Monthly spending trend
    st.subheader("📊 Monthly Spending Trend")
    monthly_spending = df.groupby('month')['amount'].sum()
    
    fig_trend = px.line(
        x=monthly_spending.index.astype(str),
        y=monthly_spending.values,
        title="Monthly Spending Trend",
        labels={"x": "Month", "y": "Amount ($)"}
    )
    fig_trend.update_traces(line_color='#1f77b4', line_width=3)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Category analysis
    st.subheader("🏷️ Category Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top categories by amount
        category_totals = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        fig_top_cat = px.bar(
            x=category_totals.head(10).values,
            y=category_totals.head(10).index,
            orientation='h',
            title="Top 10 Categories by Amount",
            labels={"x": "Amount ($)", "y": "Category"}
        )
        st.plotly_chart(fig_top_cat, use_container_width=True)
    
    with col2:
        # Expense frequency by category
        category_counts = df['category'].value_counts()
        fig_freq = px.bar(
            x=category_counts.head(10).index,
            y=category_counts.head(10).values,
            title="Expense Frequency by Category",
            labels={"x": "Category", "y": "Number of Expenses"}
        )
        fig_freq.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_freq, use_container_width=True)
    
    # Insights
    st.subheader("💡 Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        highest_expense = df.loc[df['amount'].idxmax()]
        st.info(f"**Highest Expense:** {highest_expense['title']} - {format_currency(highest_expense['amount'])}")
    
    with col2:
        most_frequent_category = df['category'].mode().iloc[0]
        st.info(f"**Most Frequent Category:** {most_frequent_category}")
    
    with col3:
        daily_avg = df['amount'].sum() / max((end_date - start_date).days, 1)
        st.info(f"**Daily Average:** {format_currency(daily_avg)}")

if __name__ == "__main__":
    main() 
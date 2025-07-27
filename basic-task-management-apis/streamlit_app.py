import streamlit as st
import requests
import json
from datetime import datetime
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Task Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .task-card {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #ffffff;
    }
    .task-completed {
        background-color: #f8f9fa;
        border-color: #28a745;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .stat-card {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Make API request to FastAPI backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code in [200, 201]:
            return response.json() if response.content else {}
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return {}
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the API. Make sure the FastAPI server is running on http://localhost:8000")
        return {}
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {}

def get_tasks() -> List[Dict[Any, Any]]:
    """Fetch all tasks from API"""
    return make_api_request("GET", "/tasks") or []

def create_task(title: str, description: str = "") -> Dict[Any, Any]:
    """Create a new task"""
    data = {"title": title, "description": description}
    return make_api_request("POST", "/tasks", data)

def update_task(task_id: int, **kwargs) -> Dict[Any, Any]:
    """Update a task"""
    return make_api_request("PUT", f"/tasks/{task_id}", kwargs)

def delete_task(task_id: int) -> Dict[Any, Any]:
    """Delete a task"""
    return make_api_request("DELETE", f"/tasks/{task_id}")

def format_datetime(dt_string: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_string

def main():
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📋 Task Management System")
    st.markdown("Manage your tasks efficiently with this simple interface")
    st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar for adding new tasks
    with st.sidebar:
        st.header("➕ Add New Task")
        
        with st.form("add_task_form"):
            title = st.text_input("Task Title*", placeholder="Enter task title")
            description = st.text_area("Description", placeholder="Enter task description (optional)")
            submitted = st.form_submit_button("Add Task", use_container_width=True)
            
            if submitted:
                if title.strip():
                    result = create_task(title.strip(), description.strip())
                    if result:
                        st.success("✅ Task added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add task")
                else:
                    st.error("❌ Task title is required")

    # Main content area
    tasks = get_tasks()
    
    if tasks:
        # Statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get('completed', False)])
        pending_tasks = total_tasks - completed_tasks
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tasks", total_tasks)
        with col2:
            st.metric("Completed", completed_tasks)
        with col3:
            st.metric("Pending", pending_tasks)
        
        st.divider()
        
        # Filter options
        st.subheader("📝 Your Tasks")
        filter_option = st.selectbox(
            "Filter tasks:",
            ["All Tasks", "Pending Tasks", "Completed Tasks"]
        )
        
        # Filter tasks based on selection
        if filter_option == "Pending Tasks":
            filtered_tasks = [t for t in tasks if not t.get('completed', False)]
        elif filter_option == "Completed Tasks":
            filtered_tasks = [t for t in tasks if t.get('completed', False)]
        else:
            filtered_tasks = tasks
        
        # Sort tasks by creation date (newest first)
        filtered_tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Display tasks
        for task in filtered_tasks:
            task_id = task.get('id')
            title = task.get('title', 'Untitled')
            description = task.get('description', '')
            completed = task.get('completed', False)
            created_at = task.get('created_at', '')
            
            # Task container
            with st.container():
                col1, col2, col3, col4 = st.columns([0.1, 0.6, 0.2, 0.1])
                
                with col1:
                    # Completion checkbox
                    new_status = st.checkbox(
                        "✓",
                        value=completed,
                        key=f"checkbox_{task_id}",
                        help="Mark as complete/incomplete"
                    )
                    if new_status != completed:
                        result = update_task(task_id, completed=new_status)
                        if result:
                            st.rerun()
                
                with col2:
                    # Task details
                    if completed:
                        st.markdown(f"~~**{title}**~~")
                        if description:
                            st.markdown(f"~~{description}~~")
                    else:
                        st.markdown(f"**{title}**")
                        if description:
                            st.markdown(description)
                    
                    if created_at:
                        st.caption(f"Created: {format_datetime(created_at)}")
                
                with col3:
                    # Status badge
                    if completed:
                        st.success("✅ Completed")
                    else:
                        st.info("⏳ Pending")
                
                with col4:
                    # Delete button
                    if st.button("🗑️", key=f"delete_{task_id}", help="Delete task"):
                        result = delete_task(task_id)
                        if result:
                            st.success("Task deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete task")
                
                st.divider()
    
    else:
        # Empty state
        st.info("🎉 No tasks yet! Add your first task using the sidebar.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "💡 **Tip:** Make sure the FastAPI server is running on `http://localhost:8000` for the app to work properly."
    )

if __name__ == "__main__":
    main() 
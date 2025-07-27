# Basic Task Management API

A simple task management system built with FastAPI backend and Streamlit frontend. This application provides a clean interface to manage your daily tasks with full CRUD functionality.

## Features

- ✅ Create new tasks with title and optional description
- ✅ View all tasks with filtering options (All, Pending, Completed)
- ✅ Mark tasks as complete/incomplete
- ✅ Delete tasks
- ✅ Real-time task statistics
- ✅ Modern and responsive Streamlit UI
- ✅ RESTful API with proper HTTP status codes

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **Frontend**: Streamlit (Interactive web apps)
- **Storage**: In-memory (Python list)
- **API Client**: Requests library

## Project Structure

```
basic-task-management-apis/
├── main.py              # FastAPI backend server
├── streamlit_app.py     # Streamlit frontend application
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Installation & Setup

### 1. Install Dependencies

```bash
cd basic-task-management-apis
pip install -r requirements.txt
```

### 2. Run the Application

You need to run both the backend and frontend separately:

#### Start the FastAPI Backend (Terminal 1)
```bash
python main.py
```
Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

#### Start the Streamlit Frontend (Terminal 2)
```bash
streamlit run streamlit_app.py
```

The Streamlit app will open automatically in your browser at: `http://localhost:8501`

## API Endpoints

The FastAPI backend provides the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | Fetch all tasks |
| POST | `/tasks` | Create a new task |
| PUT | `/tasks/{task_id}` | Update an existing task |
| DELETE | `/tasks/{task_id}` | Delete a task |

### API Documentation

Once the FastAPI server is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative docs**: `http://localhost:8000/redoc`

## Usage

### Using the Streamlit Interface

1. **Adding Tasks**: Use the sidebar form to add new tasks with title and optional description
2. **Viewing Tasks**: All tasks are displayed in the main area with statistics at the top
3. **Filtering**: Use the dropdown to filter between All, Pending, or Completed tasks
4. **Completing Tasks**: Click the checkbox next to any task to mark it as complete/incomplete
5. **Deleting Tasks**: Click the 🗑️ button to delete any task

### Using the API Directly

#### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks" \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

#### Get All Tasks
```bash
curl -X GET "http://localhost:8000/tasks"
```

#### Update a Task
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
     -H "Content-Type: application/json" \
     -d '{"completed": true}'
```

#### Delete a Task
```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

## Data Model

### Task Object
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Optional description",
  "completed": false,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

## Notes

- **In-Memory Storage**: All data is stored in memory and will be lost when the server restarts
- **Task IDs**: Auto-generated incrementing integers starting from 1
- **Error Handling**: Proper HTTP status codes (200, 201, 404) and error messages
- **CORS**: Not configured - add if needed for cross-origin requests

## Development

### Adding Features

Some potential enhancements:
- Persistent storage (SQLite, PostgreSQL)
- User authentication
- Task categories/tags
- Due dates and reminders
- Task priority levels
- Search functionality

### Testing

You can test the API endpoints using:
- The interactive Swagger UI at `http://localhost:8000/docs`
- curl commands (examples above)
- Postman or similar API testing tools

## Troubleshooting

1. **Connection Error**: Make sure the FastAPI server is running on port 8000
2. **Port Conflicts**: Change ports in the configuration if 8000 or 8501 are in use
3. **Module Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

## License

This project is for educational purposes. Feel free to modify and use as needed. 
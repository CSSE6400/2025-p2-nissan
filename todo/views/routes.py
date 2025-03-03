from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta, UTC
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    """Return the list of todo items"""
    # Start with base query
    query = Todo.query

    # Filter by completion status if specified
    completed = request.args.get('completed')
    if completed is not None:
        is_completed = completed.lower() == 'true'
        query = query.filter_by(completed=is_completed)

    # Filter by time window if specified
    window = request.args.get('window')
    if window is not None:
        window = int(window)
        future_date = datetime.now(UTC) + timedelta(days=window)
        query = query.filter(Todo.deadline_at <= future_date)

    # Execute query and format results
    todos = query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Return the details of a todo item"""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@api.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo item and return the created item"""
    # Validate no extra fields are present
    allowed_fields = {'title', 'description', 'completed', 'deadline_at'}
    if not set(request.json.keys()).issubset(allowed_fields):
        return jsonify({'error': 'Invalid fields in request'}), 400

    # Validate required fields
    if 'title' not in request.json:
        return jsonify({'error': 'Title is required'}), 400

    todo = Todo(
        title = request.json.get('title'),
        description = request.json.get('description'),
        completed = request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))
    
    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    
    # Commits the changes to the database.
    # This must be called for the changes to be saved
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    # Validate no extra fields are present
    allowed_fields = {'title', 'description', 'completed', 'deadline_at'}
    if not set(request.json.keys()).issubset(allowed_fields):
        return jsonify({'error': 'Invalid fields in request'}), 400

    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    if 'title' in request.json:
        todo.title = request.json['title']
    if 'description' in request.json:
        todo.description = request.json['description']
    if 'completed' in request.json:
        todo.completed = request.json['completed']
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json['deadline_at'])
    
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({}, 200)
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict(), 200)
 

from flask import request, render_template
from . import app, db
from .models import User, Task
from .auth import basic_auth, token_auth


# Define a route
@app.route("/")
def index():
    return 'hello world'

# User Endpoints

# Create New User
@app.route('/users', methods=['POST'])
def create_user():
    # Check to make sure that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json

    # Validate that the data has all the required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    # Pull the individual data from the body
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check to see if any current users already have that username and/or email
    check_user = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_user:
        return {'error': "A user with that username and/or email already exists"}, 400

    # Create a new instance of user with the data from the request
    new_user = User(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)

    return new_user.to_dict(), 201

@app.route("/token")
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()

# task Endpoints

# Get All tasks
@app.route('/tasks')
def get_tasks():
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))
    # Get the tasks from database
    tasks = db.session.execute(select_stmt).scalars().all()
    return [p.to_dict() for p in tasks]


# Get a Single task By ID
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    # Get the tasks from database by id
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        # If we loop through all the tasks without returning, the task with that ID does not exist
        return {'error': f"task with an ID of {task_id} does not exist"}, 404


# Create a task
@app.route('/tasks', methods=['POST'])
@token_auth.login_required
def create_task():
    # Check to see if the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate the incoming data
    required_fields = ['title', 'description']
    missing_fields = []
    # For each of the required fields
    for field in required_fields:
        # If the field is not in the request body dictionary
        if field not in data:
            # Add that field to the list of missing fields
            missing_fields.append(field)
    # If there are any missing fields, return 400 status code with the missing fields listed
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Get data values
    title = data.get('title')
    description = data.get('description')

    current_user = token_auth.current_user()

    # Create a new task instance with data (and hard-code user_id for time being)
    new_task = Task(title=title, description=description, user_id=current_user.id)

    # Return the newly created task dictionary with a 201 Created Status Code
    return new_task.to_dict(), 201

# update task end poitn
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def edit_tasks(task_id):
    # check to see that they have a json body
    if not request.is_json:
        return {"error": "your content type must be application/json"}, 400
    # find the task in the db
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f"task with id #{task_id} does not exist"}, 404
    # get current user based on token
    current_user = token_auth.current_user()
    # check if the current use is the author of the task
    if current_user is not task.author:
        return {'error': "this is not your task. you do not have permission to edit"}, 403
    
    # get data from request
    data = request.json
    # pass the data into the task
    task.update(**data)
    return task.to_dict()

# Delete a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@token_auth.login_required
def delete_task(task_id):
    # based on the task id parameter check to see if the task exists
    task = db.session.get(Task, task_id)

    if task is None:
        return {'Error': f'task with {task_id} does not exist'}, 404
    
    # make sure user trying to delete task is the owner
    current_user = token_auth.current_user()
    if task.author is not current_user:
        return {'error': "you do not have permisson to delete this task"}, 403
    
    # delete the task
    task.delete()
    return {"Success": f'{task.title} was successfully deleted'}, 200



@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def edit_users(user_id):
    # check to see that they have a json body
    if not request.is_json:
        return {"error": "your content type must be application/json"}, 400
    # find the user in the db
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f"user with id #{user_id} does not exist"}, 404
    # get current user based on token
    current_user = token_auth.current_user()
    # check if the current use is the id of the user
    if not current_user:
        return {'error': "this is not your user. you do not have permission to edit"}, 403
    
    # get data from request
    data = request.json
    # pass the data into the user
    user.update(**data)
    return user.to_dict()


# Delete a user
@app.route("/users/<int:user_id>", methods=["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    # based on the user id parameter check to see if the user exists
    user = db.session.get(User, user_id)

    if user is None:
        return {'Error': f'user with {user_id} does not exist'}, 404
    
    # make sure user trying to delete user is the owner
    current_user = token_auth.current_user()
    if not current_user:
        return {'error': "you do not have permisson to delete this user"}, 403
    
    # delete the user
    user.delete()
    return {"Success": f'{user.id} was successfully deleted'}, 200

# Get a Single user By ID
@app.route('/users/<int:user_id>')
def get_task(task_id):
    # Get the user from database by id
    task = db.session.get(User, user_id)
    if task:
        return user.to_dict()
    else:
        # If we loop through all the users without returning, the task with that ID does not exist
        return {'error': f"user with an ID of {user_id} does not exist"}, 404
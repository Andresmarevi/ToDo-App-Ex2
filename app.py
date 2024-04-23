from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson.objectid import ObjectId
import bcrypt


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize MongoDB connection
import os

# Initialize MongoDB connection
app.config['MONGO_URI'] = f"mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@db:27017/db"

mongo = PyMongo(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


# User model
class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(username):
    user = mongo.db.users.find_one({'username': username})
    if not user:
        return None
    return User(user['username'], user['password'])


# Routes

# Route to show every toDo in the index page
@app.route('/')
def index():
    if current_user.is_authenticated:
        todos = mongo.db.todos.find({'user_id': current_user.get_id()})
        return render_template('index.html', todos=todos)
    else:
        return redirect(url_for('login'))

# Route to create a new toDo
@app.route('/add', methods=['POST'])
@login_required
def add_todo():
    todo_content = request.form['content']
    mongo.db.todos.insert_one({'content': todo_content, 'done': False, 'user_id': current_user.get_id()})
    return redirect(url_for('index'))

# Route to mark as done a toDo
@app.route('/done/<string:todo_id>')
@login_required
def mark_done(todo_id):
    mongo.db.todos.update_one({'_id': ObjectId(todo_id)}, {'$set': {'done': True}})
    return redirect(url_for('index'))

# Route to delete a toDo
@app.route('/delete/<string:todo_id>')
@login_required
def delete_todo(todo_id):
    mongo.db.todos.delete_one({'_id': ObjectId(todo_id)})
    return redirect(url_for('index'))
    
    
# Route to log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = mongo.db.users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            user_obj = User(username, user['password'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Route to log out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Route to register a new user into the db
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store user in the database
        mongo.db.users.insert_one({'username': username, 'password': hashed_password})
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
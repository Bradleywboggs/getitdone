from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://getitdone:getitdone@localhost:8889/getitdone'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'F(*3FbNjen^3hfsmck{|f'
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.name = name
        self.completed = False
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['get_login', 'post_login', 'get_register', 'post_register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login')
def get_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def post_login():
    email = request.form.get('email')
    password = request.form.get('pw')
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        session['email'] = email
        flash('Login Successful!', category='success')
        return redirect('/')
    else:
        flash('Incorrect username or password.', category='error')
        return redirect('/login')

@app.route('/register')
def get_register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def post_register():
    email = request.form['email']
    password = request.form['pw']
    verifypw = request.form['verifypw']
    existing_user = User.query.filter_by(email=email).first()

    email_error = ''
    password_error = ''
    verifypw_error = ''
    duplicate_user_error = ''
    # Regex pattern looks for alphanumeric characters - minimum 3, no max; '@' symbol, 
    # at least one alphanumeric, ''.'', at least 2 alphas(case insensitive)
    email_pattern = re.compile(r'[\w]{3,}[@][\w]+[.][a-zA-Z]{2,}')
    email_matched = email_pattern.match(email)
    # Regex pattern checks for non-white space characters - minimum 8, maximum 20
    pw_pattern = re.compile(r'[^\s]{8,20}')
    pw_matched = pw_pattern.match(password)
    
    #verify email
    if not email_matched:
        email_error =  'error'
        flash('This email is not valid', 'error')
    else:
        email = email
        if existing_user:
            duplicate_user_error = 'error'
            flash('User already exists.', 'error')
        else:

    # validate password
            if password == '':
                password_error = 'error'
                flash('Please enter a password', 'error')
                password = ''
                verifypw = ''      
            elif not pw_matched:
                password_error = 'error'
                flash('This password is not valid', 'error')
                password = ''
                verifypw = ''    
        # verify both passwords match
            elif password != verifypw:
                verifypw_error = 'error'
                flash('Passwords do not match.', 'error')
                password = ''
                verifypw = ''
            else:
                password = password
                verifypw = verifypw   

    if not email_error and not password_error and not verifypw_error and not duplicate_user_error:
        new_user = User(email, password)
        db.session.add(new_user)
        db.session.commit()
        session['email'] = email
        flash('Registration successful!', category='success')
        return redirect('/')
    #TODO: Determine if re-rendering template is needed. 
    else:
        return render_template('register.html', 
        password_error=password_error, email_error=email_error, verifypw_error=verifypw_error,duplicate_user_error=duplicate_user_error,
        password='', verifypw='', email=email)

@app.route('/logout')
def log_out():
    del session['email']
    return redirect('/login')

@app.route('/', methods = ['POST', 'GET'])
def index():
    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()
    
    tasks = Task.query.filter_by(completed=False, owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True).all()

    return render_template('todos.html', title='Get It Done!', tasks=tasks,
        completed_tasks=completed_tasks)

@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')

if __name__ == '__main__':
    app.run()

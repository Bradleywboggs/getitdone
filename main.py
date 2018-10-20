from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://getitdone:getitdone@localhost:8889/getitdone'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)

    def __init__(self, name):
        self.name = name
        self.completed = False

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@app.route("/")
@app.route("/login")
def get_login():
    return render_template("/login")

@app.route("/" methods=['POST'])
@app.route("/login" methods=['POST'])
def post_login()

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/", methods=['POST'])
def validate_signup():
    username = request.form["username"]
    password = request.form["pw"]
    verifypw = request.form["verifypw"]
    email = request.form["email"]

    username_error = ''
    password_error = ''
    email_error = ''
    verifypw_error = ''

#validate username
    if username == '':
        username_error = "This field is required."
        username = ''
    elif len(username) < 3:
        username_error = "Username is not valid."
    elif len(username) > 20:
        username_error = "Username is not valid."
        username = ''
    elif username[0] == " ":
        username_error = "Username is not valid."
        username = ''
    else:
        username = username
        username_error = ''
    
# validate password
    if password == '':
        password_error = "This field is required."
        password = ''
        verifypw = ''      
    elif len(password) < 3:
        password_error = "Password is not valid."
        password = ''
        verifypw = ''
    elif len(password) > 20:
        password_error = "Password is not valid."
        password = ''
        verifypw = ''     
# verify both passwords match
    elif password != verifypw:
        verifypw_error = "Passwords do not match."
        password = ''
        verifypw = ''
    else:
        username = username
        password = password
        verifypw = verifypw
 
        
    
# validate email
    if email == '':
        email_error = ''
        email = email
    elif " " in email:
        email_error = "Email is not valid."
        email = ''
    elif "." not in email:
        email_error = "Email is not valid."
        email = ''
    elif "@" not in email:
        email_error = "Email is not valid."
        email = ''
    elif len(email) < 3:
        email_error = "Email is not valid."
        email = ''
    elif len(email) > 24:
        email_error = "Email is not valid."
        email = ''
    else:
        email_error = ''
        email = email

    if not username_error and not password_error and not email_error and not verifypw_error:
        return redirect(f"/todos")
    #render the page again with error descriptions
    else:
        return render_template("signup_form.html", username_error=username_error, 
        password_error=password_error, email_error=email_error, verifypw_error=verifypw_error, username=username,
        password='', verifypw='', email=email)
@app.route('/todos', methods = ['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name)
        db.session.add(new_task)
        db.session.commit()
    
    tasks = Task.query.filter_by(completed=False).all()
    completed_tasks = Task.query.order_by(desc(pub_date)).all()

    return render_template('todos.html', title="Get It Done!", tasks=tasks,
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

from flask import Flask,render_template,request,redirect,url_for,jsonify,flash,session
from flask_sqlalchemy import SQLAlchemy
from random import choice
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.sql import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jeremy@jeremy90k:AstraH07@jeremy90k.postgres.database.azure.com:5432/postgres'
app.secret_key = '8UjaMYHyGC_abrueAGwmQDH7yf7rhSH8E-GuWKd_5D4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    password = db.Column(db.String(300), nullable=False)
    todo = db.relationship('Todo', backref='user',lazy=True)
    

    def __init__(self, username, password,email):
        self.username = username
        self.email = email
        self.password = password

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    user_no = db.Column(db.Integer, db.ForeignKey('user.id'))
    color_me = db.Column(db.String(100))
    
    def __init__(self, content,color_me,user_no):
        self.content = content
        self.user_no = user_no
        self.color_me = color_me

    def serialize(self):
        return{
            'id':self.id,
            'content': self.content,
            'color_me': self.color_me,
            'created_at':self.created_at
        }


    def __repr__(self):
        return self.content
# Create Database Tables
db.create_all()


#===============User Auth===================#
# Route to create a new post for a user
@app.route('/register', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password=password_hash)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

#protected
@app.route('/')
def dashboard():
    if 'username' in session:
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
    
# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = user.username
            flash('Login successful')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))
#===============End of User Auth===================#

@app.route('/admin')
def RetrieveDataList():
    if session['username'] =='admin':
        tasks = Todo.query.order_by(Todo.id.desc()).all()
        return render_template('tasklist.html',tasks = tasks)
    else:
        return render_template('admin.html')
#api get
@app.route('/api/tasks', methods=['GET'])
def get_api_data():
    tasks = Todo.query.order_by(Todo.id.desc()).all()
    serialized_tasks = [task.serialize() for task in tasks]
    return jsonify(serialized_tasks),200

@app.route('/home',methods=['POST','GET'])
def home():
    data_list = ['danger','info','primary','secondary','success','dark','warning']
    colors = choice(data_list)
    user = session['username']
    users = User.query.filter_by(username=user).first()
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content,color_me=colors,user_no=users.id)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            flash('There was an error while adding the task try again')
    else:
        tasks =  Todo.query.filter_by(user_no=users.id).all()
        return render_template("index.html",tasks=tasks)
         
#post api
@app.route('/api/tasks', methods=['POST'])
def create_tasks():
    data_list = ['danger','info','primary','secondary','success','dark','warning']
    colors = choice(data_list)
    data = request.get_json()
    content = data.get('content')
    
    new_tasks = Todo(content=content,color_me=colors)

    db.session.add(new_tasks)
    db.session.commit()

    return jsonify(new_tasks.serialize()),201
#webpage delete
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an error deleting this task'
    
#delete api
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_tasks(task_id):
    task = Todo.query.filter_by(id=task_id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted'})
    return jsonify({'message': 'Task not found'}), 404
#webpage Update
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue while updating that task'

    else:
        return render_template('update.html', task=task)

#api update   
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_tasks(task_id):
    task = Todo.query.filter_by(id=task_id).first()
    if task:
        data = request.get_json()
        content = data.get('content')
        color_me =data.get('color_me')

        task.content = content
        task.color_me = color_me

        db.session.commit()

        return jsonify(task.serialize())
    return jsonify({'message': 'Task not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
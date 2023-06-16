from flask import Flask,render_template,request,redirect,url_for,jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from random import choice
app = Flask(__name__)
from sqlalchemy.sql import func
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1990@localhost/sample_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    color_me = db.Column(db.String(100))
    
    def __init__(self, content,color_me):
        self.content = content
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


@app.route('/data/')
def RetrieveDataList():
    tasks = Todo.query.order_by(Todo.id.desc()).all()
    return render_template('tasklist.html',tasks = tasks)
#api get
@app.route('/api/tasks', methods=['GET'])
def get_api_data():
    tasks = Todo.query.order_by(Todo.id.desc()).all()
    serialized_tasks = [task.serialize() for task in tasks]
    return jsonify(serialized_tasks),200

@app.route('/',methods=['POST','GET'])
def home():
    data_list = ['danger','info','primary','secondary','success','dark','warning']
    colors = choice(data_list)
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content,color_me=colors)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error while adding the task try again'
    else:
        tasks = Todo.query.order_by(Todo.id.desc()).all()
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
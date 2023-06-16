from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
from sqlalchemy.sql import func
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1990@localhost/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    
    def __init__(self, content):
        self.content = content


    def __repr__(self):
        return self.content
# Create Database Tables
db.create_all()

@app.route('/data/')
def RetrieveDataList():
    tasks = Todo.query.all()
    return render_template('tasklist.html',tasks = tasks)

@app.route('/',methods=['POST','GET'])
def home():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error while adding the task try again'
    else:
        tasks = Todo.query.all()
        return render_template("index.html",tasks=tasks)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an error deleting this task'

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

if __name__ == '__main__':
    app.run(debug=True)
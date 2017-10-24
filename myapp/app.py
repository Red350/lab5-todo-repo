from flask import Flask
from flask import render_template
from flask_mysqldb import MySQL
from flask_prometheus import monitor 
from slackclient import SlackClient
mysql = MySQL()
app = Flask(__name__)
# table: todolist(id, todo)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'p@ssword'
app.config['MYSQL_DB'] = 'todo'
app.config['MYSQL_HOST'] = '35.195.110.246'
mysql.init_app(app)
slack_token = "REDACTED"

@app.route('/')
def statichtml(name=None):
    return render_template('index.html', name=name)

@app.route("/list")
def list():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM todolist''')
    rv = cur.fetchall()
    return render_template('index.html', name=str(rv))

@app.route("/add/<item>")
def add(item=None):
    cur= mysql.connection.cursor()
    insert_stmt = (
                 "INSERT INTO todolist (todo) "
                 "VALUES (%s)")
    data=(item,)
    cur.execute(insert_stmt, data)
    mysql.connection.commit()
    send_slack_message(str(item))
    return render_template('index.html', name="New Record is added to the database")  

@app.route("/update/<todo_id>/<item>")
def update(todo_id=None, item=None):
    cur=mysql.connection.cursor()
    update_stmt = (
        "UPDATE todolist SET todo = %s " 
        "WHERE id = %s")
    data=(item,todo_id)
    cur.execute(update_stmt, data)
    mysql.connection.commit()
    return render_template('index.html', name="Todo item updated")

@app.route("/delete/<todo_id>")
def delete(todo_id=None):
    cur=mysql.connection.cursor()
    delstatmt = "DELETE FROM todolist WHERE id = {}".format(todo_id)
    cur.execute(delstatmt)
    mysql.connection.commit()
    return render_template('index.html', name="Todo item deleted")

def send_slack_message(item):
    sc = SlackClient(slack_token)
    sc.api_call(
            "chat.postMessage",
            channel="""#todo""",
            text = "Padraig added a new task: " + item
)

if __name__ == "__main__":
        monitor(app, port=8000)
        app.run(host='0.0.0.0', port='5000')

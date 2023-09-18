# import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# create the Flask app
from flask import Flask, render_template, request, redirect, session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug import security
from flask_login import UserMixin

app = Flask(__name__)

login_manager= LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

app.secret_key = 'any'

# select the database filename
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///todo.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set up a 'model' for the data you want to store
from db_schema import db, User, List, ListItem, dbinit

# init the database so it can connect with our app
db.init_app(app)

# change this to False to avoid resetting the database every time this app is restarted
resetdb = True
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
        dbinit()

# store the passwords in a database.
password_database = {
    'manpreet':security.generate_password_hash("them")
}

#route to the index
@app.route('/')
def index():
    items = ListItem.query.all()
    lists = List.query.all()
    return render_template('index.html', lists=lists, items=items)

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method== 'POST':
        username = request.form["username"]
        print(username)
        password = request.form['password']
        print(password)
        user = User(username=username, password=password)
        
        db.session.add(user)
        db.session.commit()
        print(request.form.get("username"))
        print(request.form.get("password"))
        return render_template('categoriesLab2.html')
    return render_template('register.html')



@app.route('/list', methods = ['GET', 'POST'])
def list():
    return render_template('list.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        username = request.args.get(username)
        password = request.args.get(password)

        user_id=User.query.filter_by(username=username).first().id

        hashed_password = password_database[username] 
        print(user_id)
        print(hashed_password)
        if security.check_password_hash( password, hashed_password ): 
            print("adding user id")
            return redirect('loginLab2.html')
        
        login_user(user_id)
        return redirect('categories.html')
    return render_template('loginLab2.html')


@app.route('/logout')
def logout():
    session.pop('userid', None)
    return render_template('logout.html')

@app.route('/categories')
def categories():
    manpreet_id = User.query.filter_by(username="Manpreet").first().id
    # userid = session.get('userid')
    
    manpreet = User.query.filter_by(id=3).first().id
    manpreetLists = List.query.filter_by(user_id = manpreet)
    manpreetListItems = ListItem.query.filter_by(id = 3)
    userIdLists= List.query.filter_by(id=session['user_id'])
    userIdItems = ListItem.query.filter_by(id=session['user_id'])
    return render_template('categoriesLab2.html', manpreetLists=manpreetLists, manpreetListItems=manpreetListItems, userIdItems=userIdItems, userIdLists=userIdLists)


@app.route('/newList', methods = ['POST', 'GET'])

def newList():
    if request.method== 'POST':
        taskname = request.form['newCategory']
        print(taskname)
        db.session.add(ListItem(taskname, 3)) #3 is the list id i think 
        db.session.commit()
   ##else : #GET
        ##taskname=request.args.get('taskname')
    # user_id=User.query.filter_by(username= request.form.get("username")).first().id
    #user_id = User.query.filter_by(username=username).first().id
    # user_id = request.args.get(user_id)
    user_id = User.query.filter_by(username=current_user.user_username).first().id
    userId= current_user.user_id
    userLists = List.query.filter_by(user_id=user_id)
    items = ListItem.query.filter_by(id=userLists)
    print(request.form.get("newCategory"))
    return render_template('newList.html', items= items, userLists=userLists, user_id=user_id)
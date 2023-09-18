# import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# create the Flask app
from flask import Flask, render_template, request, redirect, session,jsonify,url_for
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug import security
from sqlalchemy import text 
from markupsafe import escape, Markup

app = Flask(__name__)

login_manager= LoginManager()
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_id=User.query.filter_by(username=username).first().id

        hashed_password = password_database[username] if username in password_database else None

        if not hashed_password and security.check_password_hash(hashed_password, password ): 
            session['user_id'] = user_id
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
    manpreet = User.query.filter_by(id=3).first().id
    manpreetLists = List.query.filter_by(user_id = manpreet)
    manpreetListItems = ListItem.query.filter_by(id = 3)
    return render_template('categoriesLab2.html', manpreetLists=manpreetLists, manpreetListItems=manpreetListItems)


@app.route('/newList', methods = ['POST', 'GET'])

# def newList():
#     if request.method== 'POST':
#         taskname = request.form['newCategory']
#         safe_string = Markup(taskname).striptags()
#         db.session.add(ListItem(safe_string, 3)) #3 is the list id i think 
#         db.session.commit()
#     items=ListItem.query.filter_by(list_id=3)
#     print(request.form.get("newCategory"))
#     item_name = request.form['item_name']
#     checked = request.form['checked']
#     taskname.completed = True
#     db.session.commit()
#     return jsonify({'success': True})

#     return render_template('newList.html', manpreetListItems= items)

# @app.route('/newList', methods=['POST', 'GET'])
# def newList():
#     print(request.method)
#     if request.method == 'POST':
#         print("goodmes")
#         taskname = request.form['newCategory']
#         safe_string = Markup(taskname).striptags()
#         db.session.add(ListItem(safe_string, 3)) # 3 is the list id
#         db.session.commit()
        
    
#         print(request.form)
#         if 'newCategory' in request.form:
#             print("idk")
#             newCategory = request.form['newCategory']
#             item = ListItem.query.get(newCategory)
#             # item.completed = True
#             # db.session.commit()
#             return jsonify({'success': True})

#     items = ListItem.query.filter_by(list_id=3).all()
#     return render_template('newList.html', manpreetListItems=items)



def newList():
    if request.method== 'POST':
        taskname = request.form['newCategory']
        safe_string = Markup(taskname).striptags()
        print(taskname)
        db.session.add(ListItem(safe_string, 3)) #3 is the list id i think 
        db.session.commit()
    items=ListItem.query.filter_by(list_id=3)
    print(request.form.get("newCategory"))
    return render_template('newList.html', manpreetListItems= items, taskname=taskname)


@app.route('/completedItems', methods = ['POST', 'GET'])
def completedItems():
    items=ListItem.query.filter_by(list_id=3)
    return render_template('completedItems.html', manpreetListItems=items)

@app.route('/query')
def query():
    name = "Shopping"
    value1 = List.query.filter_by(name=name).first().id

    qry = ListItem.query.filter_by(list_id = value1)
    

    vals = qry.all()
    ret = "No values<br>"

    if len(vals)>0:
        ret = f"<br>{qry}"
        for x in vals:
            ret+=f"<br>{x.name} something {x.id}"

    return ret

@app.route('/ajax')
def ajax():
    return render_template('ajax.html')
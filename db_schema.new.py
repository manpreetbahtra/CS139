from flask_sqlalchemy import SQLAlchemy

# create the database interface
db = SQLAlchemy()

# a model of a user for the database
class User(db.Model):
    __tablename__='users'
    fullname = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(25)) 

    def __init__(self, fullname, email):  
        self.fullname=fullname
        self.email=email
        self.username=username
        self.password_hash=password_hash

class List(db.Model):
    __tablename__='lists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    username = db.Column(db.String(20)  # this ought to be a "foreign key"

    def __init__(self, name, username):
        self.name=name
        self.username = username


# a model of a list item for the database
# it refers to a list
class ListItem(db.Model):
    __tablename__='items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    list_id = db.Column(db.Integer)  # this ought to be a "foreign key"

    def __init__(self, name, list_id):
        self.name=name
        self.list_id=list_id

# put some data into the tables
def dbinit():
    user_list = [
        User("Felicia"), 
        User("Petra")
        ]
    db.session.add_all(user_list)

    # find the id of the user Felicia
    felicia_id = User.query.filter_by(username="Felicia").first().id

    all_lists = [
        List("Shopping",felicia_id), 
        List("Chores",felicia_id)
        ]
    db.session.add_all(all_lists)

    # find the ids of the lists Chores and Shopping

    chores_id = List.query.filter_by(name="Chores").first().id
    shopping_id= List.query.filter_by(name="Shopping").first().id

    all_items = [
        ListItem("Potatoes",shopping_id), 
        ListItem("Shampoo", shopping_id),
        ListItem("Wash up",chores_id), 
        ListItem("Vacuum bedroom",chores_id)
        ]
    db.session.add_all(all_items)

    # commit all the changes to the database file
    db.session.commit()

@app.route('/create')
def create_db():
    db.create_all()
    return "tables created"
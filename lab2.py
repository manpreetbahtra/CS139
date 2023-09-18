from flask import Flask, render_template
app = Flask(__name__)

#route to the index
@app.route('/')
def index():
    items = ListItem.query.all()
    lists = List.query.all()
    return render_template('indexLab2.html', lists=lists, items=items)

@app.route('/register')
def register():
    return render_template('registerLab2.html')

@app.route('/list', methods = ['GET', 'POST'])
def list():
    return render_template('list.html')

@app.route('/login')
def login():
    return render_template('loginLab2.html')

@app.route('/categories')
def categories():
    return render_template('categoriesLab2.html')

@app.route('/work')
def work():
    return render_template('workLab2.html')

@app.route('/home')
def home():
    return render_template('homeLab2.html')


@app.route('/layout')
def layout():
    return render_template('layout.html')

@app.route('/listLab2')
def layout():
    return render_template('listLab2.html')

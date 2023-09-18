# create the Flask app
from flask import Flask, render_template, redirect, request
from markupsafe import escape #for escaping bad input

app = Flask(__name__)
# turn off WTForms security : don't do this normally
app.config['WTF_CSRF_ENABLED'] = False

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired



#using Flask-WTF to make simple form
class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])

#route to the index
@app.route('/')
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = MyForm()
    if form.validate_on_submit():
        scriptcmd = "<script>alert('Ha ha.. I am a hacker');</script>"
        scriptcmd2 = '<script>window.location.replace("http://www.w3schools.com");</script>'

        ##safe_string = escape(scriptcmd)
        ##will run when you put scriptcmd wont run if you use safe_string

        xss = form.name.data
        return render_template('markup.html', xss=xss,
         scriptcmd=scriptcmd,
          scriptcmd2=scriptcmd2)
    return render_template('form.html', form=form)




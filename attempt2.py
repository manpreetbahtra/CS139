from flask import flask
app = Flask(__name__)

class User :
    fullname ="unset"
    password ="unset"
    email = "unset"

    def getFullname(self):
        return self.fullname;

    def setFullname(self, newFullname):
        self.fullname = newFullname;

@app.route('/user')
def user():
    myself = User()
    myself.setFullname("Manpreet")
    return myself.getFullname()
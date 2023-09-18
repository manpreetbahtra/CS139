from flask import Flask, render_template, request, redirect, session, jsonify, url_for, flash, make_response, Markup, send_file
from flask_mail import Mail  #for email verification
import secrets, string,sqlite3,os, random, io, datetime, barcode, base64
from io import BytesIO
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from itsdangerous import URLSafeTimedSerializer
from barcode import Code128, get_barcode_class, Code39
from barcode.writer import ImageWriter, SVGWriter
from markupsafe import Markup


#library that allows to serialise strings using secret key with URLSAFETIMEDSERIALIZER the output of the serialiser can be taken and put it in the url
#timed means a time limit can be put on it specifying after how long  the code/link to expire


#instantiate the app
app = Flask(__name__)
app.config['MAIL_SUPPRESS_SEND'] = False 
# set to False
mailSender = Mail(app) #instantiate the mail part

login_manager= LoginManager(app)
login_manager.init_app(app)
login_manager.login_view='login'


# select the database filename
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///ticket.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# set up a 'model' for the data that needs to be stored
from db_schema import db, UserAttendee, UserOrganiser, Event, Ticket, dbinit

# init the database so it can connect with app
db.init_app(app)
db.create_all()


# drop everything, create all the tables, then put some data into the tables
resetdb = True
if resetdb:
    with app.app_context():
        SECRET_KEY = os.urandom(32)
        app.config["SECRET_KEY"] = SECRET_KEY
        login_manager.init_app(app)
        db.create_all()

#instantiate the serialiser- used for verify email
serialiser= URLSafeTimedSerializer(app.config["SECRET_KEY"])

#route to the index
@app.route('/')
def index():
    with open('README.md') as readme:
      with open('requirements.txt') as req:
        return render_template('index.html', README=readme.read(), requirements=req.read())



@login_manager.user_loader
def load_user(user_id):
    try:
        attendee = UserAttendee.query.get(int(user_id))
        if attendee is not None: #an attendee is trying to log in
            return attendee
        else:
            organiser = UserOrganiser.query.get(int(user_id)) #otherwise an organiser is loggin in, so checks organiser table and retreives the user id, which is the primary key hence is unique.
            return organiser
    except:
        return None

    
# ------------------------------------------------------------REGISTER----------------------------------------------------------

""" I used a try catch statement because without it if the username or email entered is not unique, it displays sqlite Integrity error which is not user friendly. so if the username is unique, the successful message appears 
otherwise error message appears notifying users registration was unsuccessful. depending on if they were an attendee or user, they are objects of different class and are stored in different tables. """

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if current_user.is_authenticated: 
        return redirect('/')
    
    if request.method== 'POST': #-registration form is filled - data is retrieved. 
        username = Markup(request.form["username"]).striptags()
        password = Markup(request.form['password']).striptags() #filtering the input by removing html tags-for security purposes, i.e. to protect against XSS attacks. 
        confirm_password = Markup(request.form["confirm_password"]).striptags()
        registration_code = request.form["registration-code"]
        password_hash = generate_password_hash(password)
        email= request.form['email']
        userType=Markup(request.form['user-type']).striptags()

        ## validate the form data
        if(password != confirm_password ):
            flash("Password does not match confirmation") #using flash to display error messages. 
            return render_template('register.html')
        
        if (userType == 'organiser' and registration_code != 'Dc5_G1gz') :
            flash("Invalid registration code.")
            return render_template('register.html')
      
            
        try:
        # create new user object and add to the database
            if userType == "attendee":
                user = UserAttendee(username=username, password_hash=password_hash, email=email, userType=userType)
            else:
               user = UserOrganiser(username=username, password_hash=password_hash, email=email, userType=userType) 
            db.session.add(user)
            db.session.commit()
            session['userid'] = user.id

            login_user(user) #authenticate the user
            return redirect('/validEmail')

        except IntegrityError: #sqlalchemy can throw this error if the username/email entered already exists in the database since in the dbschema I use unique=true for these fields 
            db.session.rollback()
            return jsonify({'message': 'Registration failed: Username/Email already exists'}), 400 #return a json response with response- bad request. 
        
    return render_template('register.html')



# ------------------------------------------------------------EMAIL VALIDATION ----------------------------------------------------------
@app.route('/validEmail', methods=['GET', 'POST'])
def validEmail():
    flash ('Registration successful!')

    # get request is made when the page initially loads so then it should display the field to enter the email. 
    if request.method == 'GET' :
        return '<form action = "/validEmail" method="POST"><input name = "email">Enter your email to validate<input type = "submit"></form>'
    
    # here request.method = post, which will be the case when you hit the submit button. 
    email = request.form['email']
    token = serialiser.dumps(email)     #generate a token, dumps-s for string
    confirmation_link = url_for('tokenHandler', token=token, _external=True) #token is used to create a confirmation link

    sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
    mailSender.send_message(sender=("NOREPLY",sender),subject="Subject-Confirm Email",body=f'You are being registered on Giginator. {request.host_url} {confirmation_link}',recipients=[email])
    return redirect(url_for('login'))
    #confirmation link along with the host url (127.0.0.1:myuserid) is sent in the message then sends them to login page. 


#route that handles the token/confirms the email. It takes in a variable that is the token
@app.route('/tokenHandler/<token>')
def tokenHandler(token):
    #doing try catch using signature expired so that when the token expires the error message is user friendly.
    try:
        email = serialiser.loads(token, max_age=30) #reverse the dumps, max_age-when the link will expire
        user = UserAttendee.query.filter_by(email=email).first() #checks if the user is attendee then organiser 
        if user ==None :
           user = UserOrganiser.query.filter_by(email=email).first()
           if user ==None:             #    no attendee and no organiser exists with that email
               flash('Invalid')
        user.confirmed = True                #otherwise user is found. set his confirmed attribute to true, then commit the change to the database. 
        db.session.commit()
        flash('Your email has been confirmed. You can now log in.')
        return redirect(url_for('login'))
    except : #token expired
        flash('The confirmation link is invalid, has expired or new link needed .')
        print('The confirmation link is invalid, has expired or new link needed .') 
        return redirect(url_for('validEmail'))
    return redirect(url_for('login'))
#i  email the above link to whoever typed in the email

#for flask mail
if __name__ == '__main' :
    app.run(debug=True)

# ---------------------------------------------------LOGIN AND LOGOUT-------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')                                              #retrieve the details
        password = request.form.get('password')
        userType = request.form.get('user-type')

        if userType == "attendee":                                                               #match the user 
            user = UserAttendee.query.filter_by(username=username).first()
        else:
            user = UserOrganiser.query.filter_by(username=username).first()

        #if not user - no user was found with that username
        if not user or not check_password_hash(user.password_hash, password):
            flash("Login details incorrect. Please check your login details and try again.")
            return redirect(url_for('login'))
        elif user.confirmed == False:                                               #only confirmed users can use the main system
            flash('Please confirm your email address to login successfully.')
            return redirect('/login')
        else:
            #this creates the cookie and the session
            flash('Login successful!')
            login_user(user)
            session['userid'] = user.id 
            session['usertype'] = userType
            session['username']=username
            return redirect(url_for('homePage'))
    else :                                                      #here method = get so displays the form fields as in the html template 
        return render_template('login.html')



@app.route('/logout')
@login_required #users who are not logged in should not be able to logout
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------------------------------------HOMEPAGE-------------------------------------------

@app.route('/homePage')
@login_required
def homePage():
    events = Event.query.all()             # query all events to display them. 
    usertype = current_user.userType      #needed because according to usertype, users shouldbe able/unable to perform actions such as cancel events.
    now = datetime.datetime.now()         # needed for starttime attribute of an event in case an event is created/cancelled
    username=session['username']

    return render_template('base.html', events=events, usertype=usertype, now=now, username=username)



# ---------------------------------------------CREATE EVENT --------------------------------------------------------------

@app.route('/createEvent', methods = ['POST', 'GET'])
@login_required
def createEvent():
    if request.method== 'POST':
        title = Markup(request.form["title"]).striptags()                   #security feature- filter input- remove any HTML tags and prevent XSS attacks.
        description = Markup(request.form['description']).striptags()
        start_time = datetime.datetime.strptime(request.form["start_time"], "%Y-%m-%dT%H:%M")
        location = Markup(request.form["location"]).striptags()
        organiser_id = current_user.id
        userType = session['usertype']
        capacity=Markup(request.form["capacity"]).striptags()
        duration= Markup(request.form["duration"]).striptags()

        # create new event object and add to the database
        if userType == "organiser": 
            # when the event is created its capacity-that is total number of people it can accomodate is the same as its available tickets- no need to get input twice. --better user experience  
            event=Event(title=title, description=description, start_time=start_time, location=location, organiser_id=organiser_id, availableTickets=capacity, capacity=capacity, is_cancelled=False, duration=duration)
            db.session.add(event)
            db.session.commit()
            return render_template('succes.html')
        else :                                                #if user is an attendee, they are not able to create events. 
            return render_template('failed.html')
    return render_template('createEvent.html')


# ------------------------------------------------------------- PROMOTE ATTENDEE TO ORGANISER -------------------------------------


@app.route('/promoteAttendeeToOrganiser', methods = ['POST', 'GET'])
@login_required
def promoteAttendeeToOrganiser():
    if request.method == 'POST':
        username = Markup(request.form["username"]).striptags()                         #security feature- filter input- remove any HTML tags and prevent XSS attacks.
        userType = session['usertype']

        if userType == "organiser":                                                     #If not an organiser, they are not able to promote.                                         
            match = UserAttendee.query.filter_by(username=username).first()             # query the database to find details of the attendee who needs to be promoted
            if not match :                                              #if there is not a match, either the person they entered is already an organiser or not an attendee
                return render_template ('failedAgain.html')
            
            detailsPassword = match.password_hash     
            detailsEmail = match.email
            newOrganiser = UserOrganiser(username=username, password_hash=detailsPassword, email = detailsEmail, userType = "organiser")
            db.session.delete(match)                                                    #now i must delete this person from attendee's table/database
            db.session.add(newOrganiser) 
            db.session.commit()
            return render_template('successAgain.html')
        else :
            return render_template('failedAgain.html')                                #usertype not an organiser
            
    return render_template('promoteAttendeeToOrganiser.html')                          #here request.method==get

# ------------------------------------- BUY TICKETS -----------------------------

@app.route('/buyTickets/<int:event_id>', methods = ['GET', 'POST'])
@login_required
def buyTickets(event_id):
    event= Event.query.filter_by(id=event_id).first() # retrieves the corresponding Event from the database
    username=session.get('username')
    email=current_user.email
    
    if event.is_cancelled: #checks whether the event has been cancelled- cant buy tickets for cancelled events.
        flash('Sorry, this event has been cancelled.')
        return redirect(url_for('homePage'))
    
    now = datetime.datetime.now() #checks whether the event has already started. 
    if event.start_time <= now:
        flash("You can not buy tickets for past events")
        return redirect(url_for('homePage'))

    if request.method== 'POST':                                             #retrieves the number of tickets the user wants to buy and creates a Ticket object 
        ticketsBought = int(request.form["ticketsBought"])                  #cast it to int because in the form it was a drop down
        match = UserAttendee.query.filter_by(username=username).first()     #find the current user in the database

        if match != None:
            username=match.username
            detailsEmail = match.email
            ticket = Ticket(event_id=event_id, username=username, usernameO=None,email=detailsEmail, ticketsBought=ticketsBought) #create a ticket once user found in the db. 
        else:
            match = UserOrganiser.query.filter_by(username=username).first()
            detailsEmail = match.email
            usernameO=match.username
            ticket = Ticket(event_id=event_id, username=None,usernameO=usernameO, email=detailsEmail, ticketsBought=ticketsBought)
        db.session.add(ticket)
        event.availableTickets -= ticketsBought                                 #reduce the number of available tickets. 
        db.session.commit()
        flash("Ticket request successful!")

        # EMAIL ALL ORGANISERS THAT EVENT IS NEAR CAPACITY. 
        if event.availableTickets < 3:
            organisers = UserOrganiser.query.all()
            for organiser in organisers:
                detailsEmail = organiser.email
                sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
                mailSender.send_message(sender=("NOREPLY",sender),subject="Event near capacity",body=f'The event {event.title} is near capacity.',recipients=[detailsEmail])
            return redirect(url_for('homePage'))

        return redirect(url_for('homePage'))

    # get request recieved 
    return render_template('buyTickets.html', event=event, event_id=event_id)


# ----------------------------------------------CANCEL TICKETS-----------------------------------

@app.route('/cancelTicket/<int:event_id>', methods=['GET', "POST"])
@login_required
def cancelTicket(event_id):
    currentEvent= Event.query.filter_by(id=event_id).first()
    if not currentEvent:                              #this should never be executed because a button corresponds to each event which means that events exists- included as a sanity check. 
        flash ("Incorrect event id or event doesn't exist")
        return render_template('cancelTicket.html')
    
    if currentEvent.is_cancelled:   #if the event has been cancelled, then you should not be able to cancel tickets for it. 
        flash('Sorry, this event has been cancelled.')
        return redirect(url_for('homePage'))
    
    now = datetime.datetime.now()    # if the event has already started, then you should not be able to cancel tickets for it. 
    if currentEvent.start_time <= now:
        flash("You can only cancel tickets for future events")
        return render_template('cancelTicket.html')
    
    
    username=session.get('username')
    match = UserAttendee.query.filter_by(username=username).first()

    if match: #find user in database
        email=match.email
    else:
        match = UserOrganiser.query.filter_by(username=username).first()
        email=match.email
    
        
    hasTicket =Ticket.query.filter_by(email=email, event_id=currentEvent.id).first() #checking if that user even has a ticket for the event they are requesting to cancel the tickets for

    if hasTicket !=None :
        #i want to increase the no of available tickets by the amount that was cancelled
        ticketsBought=hasTicket.ticketsBought
        currentEventAvailability = currentEvent.availableTickets
        currentEventAvailability+=ticketsBought
        currentEvent.availableTickets = currentEventAvailability
        db.session.delete(hasTicket) #removes the tickets from the database
        db.session.commit()
        flash("Successfully cancelled tickets")
        return render_template('cancelTicket.html')
    else:
        flash("you have not bought tickets for this event, hence can't cancel them")
        return render_template('cancelTicket.html')
    
    
    return redirect(url_for('homePage')) 
    return render_template('cancelTicket.html', currentEvent=currentEvent)



# ------------------------------------------------------------------------CANCEL EVENTS--------------------------------------------------------------

@app.route('/cancelEvent/<int:event_id>', methods=['GET', "POST"])
@login_required
def cancelEvent(event_id):
    if request.method == 'POST':
        currentEvent= Event.query.filter_by(id=event_id).first()
        username=session.get('username')
        organiser_id = current_user.id
        userType = session['usertype']

        if currentEvent.is_cancelled:                       #you can not cancel an already cancelled event
            flash('Sorry, this event has been cancelled.')
            return redirect(url_for('homePage'))

        if userType == 'organiser':                          #only organisers can cancel future events.
            now = datetime.datetime.now()
            if currentEvent.start_time <= now:
                flash("You can only cancel future events- the event you are attempting to cancel is a past event")
                return render_template('cancelEvent.html', currentEvent=currentEvent, userType=userType)
            else :
                currentEvent.is_cancelled = True            #user is an organiser and they are attempting to cancel a future event- therefore cancel it. 
                db.session.commit()
                #i want to get all the tickets for that event. get each of their emails. send them email. 
                attendeesOfCancelledEvent = Ticket.query.filter_by(event_id=event_id).all()
                for attendee in attendeesOfCancelledEvent:
                    sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
                    mailSender.send_message(sender=("NOREPLY",sender),subject="Event cancellation notification",body=f'We regret to inform you that the event {currentEvent.title} has been cancelled.',recipients=[attendee.email])
                return redirect(url_for('homePage')) 
        else:
            flash("Not an organiser, hence can not cancel event")
            return redirect(url_for('homePage'))

    userType = session['usertype']
    return render_template('cancelEvent.html', currentEvent=currentEvent, userType=userType)


# ----------------------------------------------------------MY TICKETS------------------------------------------------------------------


@app.route('/myTickets', methods=['GET', 'POST'])
@login_required
def myTickets():
    #get current user's info. match it to the user database. match it to tickets. then a for loop 
    usertype = session['usertype']
    username=session['username']
    if usertype == "attendee":
        user= UserAttendee.query.filter_by(username=username).first() # queries the  user table and Ticket table to find the user's tickets.
        ticketsOfUser = Ticket.query.filter_by(username=username).all()
    else :
        user= UserOrganiser.query.filter_by(username=username).first()
        ticketsOfUser = Ticket.query.filter_by(usernameO=username).all()

    
    return render_template('myTickets.html', ticketsOfUser=ticketsOfUser)




#--------------------------------------------------------BARCODE--------------------------------------------------------------------------------------
EAN = barcode.get_barcode_class('Code39')
@app.route('/barcode/<value>')
def barcode(value):
    randomNumber = random.randint(100000000, 999999999) #   generate a random number to include in the barcode and concatanate it value(ticket id)
    uniqueBarcode = str(value)+ str(randomNumber)
    barcode = Code39(uniqueBarcode, writer=SVGWriter())

    barcodeBytes = BytesIO()
    barcode.write(barcodeBytes)         #generate a barcode file for it
    barcodeBytes.seek(0)

    return send_file(barcodeBytes, mimetype='image/svg+xml')


from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import AddUserForm, UserForm
from models import connect_db, db, User, Feedback
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///29.5-hashing-and-log-in"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "begdhfcjn823453edf"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

#################################

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def show_register():
    form = AddUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please choose a different username.')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        return redirect('/secret')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def show_login():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f'/user/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username')
    flash('logged out', 'info')
    return redirect('/')

@app.route('/secret', methods=['GET'])
def show_secret():
    if 'username' not in session:
        flash('must log in or register to view')
        return redirect('/login')
    else:
        return render_template('secret.html')

@app.route('/user/<username>', methods=['GET'])
def show_user_details(username):
    if 'username' not in session or username != session['username']:
        flash('must log in or register to view')
        return redirect('/login')
    curr_user = User.query.get(username)
    print(f'{curr_user}')
    if curr_user.username == session['username']:
        return render_template('users/user.html', user=curr_user)

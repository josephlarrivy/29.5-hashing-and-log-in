from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from forms import AddUserForm, FeedbackForm, UserForm
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
    return redirect('/login')

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
        return redirect('/login')
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
    if curr_user.username == session['username']:
        return render_template('users/user.html', user=curr_user, username=username)

@app.route('/feedback/<username>/feedback', methods=['GET', 'POST'])
def feedback_form(username):
    if 'username' not in session or username != session['username']:
        flash('must log in or register to view')
        return redirect('/login')
    
    form = FeedbackForm()

    if form.validate_on_submit():
        title=form.title.data
        content=form.content.data

        fb=Feedback(title=title, content=content, username=username)
        db.session.add(fb)
        db.session.commit()

        return redirect(f'/user/{username}')

    return render_template('/feedback/feedback_form.html', form=form, username=username)

@app.route('/feedback/<username>/<int:feedback_id>/feedback_edit', methods=['GET', 'POST'])
def edit_feedback(feedback_id, username):

    if 'username' not in session or username != session['username']:
        flash('must log in or register to view')
        return redirect('/login')
    
    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get(username)

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect('/feedback/<username>/feedback')
    
    return render_template('/feedback/feedback_edit.html', form=form, feedback=feedback, user=user, username=username, feedback_id=feedback_id)

@app.route('/users/<username>/delete', methods=['GET', 'POST'])
def delete_user(username):
    if 'username' not in session or username != session['username']:
        flash('must log in or register to view')
        return redirect('/login')
    
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    return redirect('/register')

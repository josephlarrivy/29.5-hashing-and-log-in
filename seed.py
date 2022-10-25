from app import app
from models import db, User, Feedback

db.drop_all()
db.create_all()

#######################

u1 = User(
    username = 'john_doe',
    password = 'password1',
    email = 'john_doe@test.com',
    first_name = 'John',
    last_name = 'Doe'
    )

u2 = User(
    username = 'jane_doe',
    password = 'password2',
    email = 'jane_doe@test.com',
    first_name = 'Jane',
    last_name = 'Doe'
    )

f1 = Feedback(
    title = 'feedback1',
    content = 'feedback1 content',
    username = 'john_doe'
    )

f2 = Feedback(
    title='feedback2',
    content='feedback2 content',
    username='jane_doe'
)

db.session.add_all([u1, u2])
db.session.commit()

db.session.add_all([f1, f2])
db.session.commit()
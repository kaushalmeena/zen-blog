# dummyrecords.py
"""Python script for inserting dummyrecords in database."""

from app.database.setup import session, USER, POST, COMMENT
from app.helpers.helper import make_password_hash


# Create dummy user
password_hash = make_password_hash('admin', '123')
user1 = USER(username='admin',
             password_hash=password_hash,
             name='Admin',
             email='admin@example.com')
session.add(user1)
session.commit()

# Create posts
post1 = POST(
    user_id=user1.id,
    subject='ABC 1',
    content='This is sample content 1'
)
session.add(post1)
session.commit()

post2 = POST(
    user_id=user1.id,
    subject='ABC 2',
    content='This is sample content 2'
)
session.add(post1)
session.commit()

post3 = POST(
    user_id=user1.id,
    subject='ABC 2',
    content='This is sample content 2'
)
session.add(post1)
session.commit()

# Create comments
comment1 = COMMENT(
    user_id=user1.id,
    post_id=post1.id,
    name='Sample Name 1',
    email='sample@example.com',
    content="This is sample comment 1")
session.add(comment1)
session.commit()

comment2 = COMMENT(
    user_id=user1.id,
    post_id=post2.id,
    name='Sample Name 2',
    email='sample@example.com',
    content="This is sample comment 2")
session.add(comment2)
session.commit()

print("Dummy content added to database!")

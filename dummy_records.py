"""Inserts dummy records in database."""


from blog.models import COMMENT, POST, USER, db
from blog.utils import make_password_hash


# Create dummy user
password_hash = make_password_hash("admin", "123")
user1 = USER(
    username="admin",
    password_hash=password_hash,
    name="Admin",
    email="admin@example.com",
)
db.session.add(user1)
db.session.commit()

# Create postss
post1 = POST(user_id=user1.id, subject="ABC 1", content="This is sample content 1")
db.session.add(post1)
db.session.commit()

post2 = POST(user_id=user1.id, subject="ABC 2", content="This is sample content 2")
db.session.add(post2)
db.session.commit()

post3 = POST(user_id=user1.id, subject="ABC 3", content="This is sample content 3")
db.session.add(post3)
db.session.commit()

# Create comments
comment1 = COMMENT(
    user_id=user1.id,
    post_id=post1.id,
    name="Sample Name 1",
    email="sample@example.com",
    content="This is sample comment 1",
)
db.session.add(comment1)
db.session.commit()

comment2 = COMMENT(
    user_id=user1.id,
    post_id=post2.id,
    name="Sample Name 2",
    email="sample@example.com",
    content="This is sample comment 2",
)
db.session.add(comment2)
db.session.commit()

# Create Likes
user1.liked_posts.append(post1)
user1.liked_posts.append(post2)
db.session.add(user1)
db.session.commit()

print("Dummy content added to database!")

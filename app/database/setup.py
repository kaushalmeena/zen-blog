# setup.py
"""Python script for creating the database."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy import create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

from app.database.config import get_database_uri

engine = create_engine(get_database_uri())

Base = declarative_base()

# Bind the engine to the metadata of the Base class
Base.metadata.bind = engine

# Create DBSession from engine
DBSession = sessionmaker(bind=engine)

# Create instance of DBSession
session = DBSession()

# Like association table
likes = Table('likes',
              Base.metadata,
              Column('user_id', Integer, ForeignKey('user.id')),
              Column('post_id', Integer, ForeignKey('post.id')))


class USER(Base):
    """Provides way to store blog's user related information."""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(256), nullable=False)
    password_hash = Column(String(256), nullable=False)
    name = Column(String(256), nullable=True)
    email = Column(String(256), nullable=True)
    liked_posts = relationship('POST', secondary=likes, backref='liked_by')

    # # @classmethod
    # # def by_id(cls, user_id):
    # #     """Returns a list of USER entities which have id same as
    # #        passed parameter."""
    # #     return session.query(USER).filter_by(id=user_id).first()

    # # @classmethod
    # # def by_username(cls, username):
    # #     """Returns a list of USER entities which have username same
    # #        as passed parameter."""
    # #     return session.query(USER).filter_by(username=username)

    # # @classmethod
    # # def register(cls, username, password, name=None, email=None):
    # #     """Create a new USER entitity using passed parameters."""
    # #     password_hash = make_password_hash(username, password)

    # #     return USER(username=username,
    # #                 password_hash=password_hash,
    # #                 name=name,
    # #                 email=email)

    # @classmethod
    # def login(cls, username, password):
    #     """Validates the user login information."""
    #     user = cls.by_username(username)

    #     if user and validate_password(username,
    #                                   password,
    #                                   user.password_hash):
    #         return user


class POST(Base):
    """Provides way to store blog's post related information."""
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    subject = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    comments = relationship('COMMENT', backref='post')
    created = Column(DateTime, server_default=func.now())

    # @classmethod
    # def by_id(cls, post_id):
    #     """Returns a list of POST entities which have post_id same
    #        as passed parameter."""
    #     return session.query(POST).filter_by(id=post_id).first()

    # @classmethod
    # def by_user_id(cls, user_id):
    #     """Returns a list of POST entities which have user_id same
    #        as passed parameter."""
    #     return session.query(POST).filter_by(user_id=user_id)

    # @classmethod
    # def create_post(cls, user_id, subject, content):
    #     """Creates a new POST entitiy using passed parameters."""
    #     return POST(user_id=user_id,
    #                 subject=subject,
    #                 content=content)


class COMMENT(Base):
    """Provides way to store blog's comment related information."""
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    post_id = Column(Integer, ForeignKey('post.id'))
    name = Column(String(256), nullable=True)
    email = Column(String(256), nullable=True)
    content = Column(Text, nullable=False)
    created = Column(DateTime, server_default=func.now())

    # @classmethod
    # def by_id(cls, comment_id):
    #     """Returns a list of COMMENT entities which have comment_id
    #     same as passed parameter."""
    #     return session.query(POST).filter_by(id=comment_id).first()
    # @classmethod
    # def by_post_id(cls, post_id):
    #     """Returns a list of COMMENT entities which have comment_id
    #     same as passed parameter."""
    #     return session.query(POST).filter_by(post_id=post_id)
    # @classmethod
    # def by_user_id(cls, user_id):
    #     """Returns a list of COMMENT entities which have user_id
    #        same as passed parameter."""
    #     return session.query(POST).filter_by(user_id=user_id)
    # @classmethod
    # def create_comment(cls, user_id, post_id, name, email, content):
    #     """Creates a new COMMENT entitiy using passed parameters."""
    #     return COMMENT(user_id=user_id,
    #                    post_id=post_id,
    #                    name=name,
    #                    email=email,
    #                    content=content)


# Create all tables
Base.metadata.create_all(engine)

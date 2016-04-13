#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from os import listdir
import unittest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.sqlite'
db = SQLAlchemy(app)

# many:1 user : thread
# many:1 user : comments
# 1:many thread : comments
# 1:1 thread : image
# 1:many image: tags

# A user owns threads and comments
# A thread owns a list of comments, and an image


# user.threads.append(thread_t)
# => user.threads.all() => [thread_t]
# => thread_t.user => user
# => thread_t.p_user => user

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)

    # user col not actually necessary, as the user can be referenced by thread.p_user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    # comments = db.Column(db.Integer, db.ForeignKey('user.id'))

    comments = db.relationship('Comment', backref='thread')   # 1:many  map with comments

    c_time = db.Column(db.DateTime) # when the thread was created
    m_time = db.Column(db.DateTime) # when the thread was last modified

    def __init__(self, title, body, user, image):
        self.title = title
        self.body = body
        self.user = user
        self.image = image

        user.threads.append(self)
    def __repr__(self):
        return "Thread\nTitle: %s\nBody: %s\nOP: %s" % (self.title, self.body, self.user.username)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imagelink = db.Column(db.String(100))
    thread = db.relationship('Thread', backref='image')   # 1:1 map with an image
    tags = db.relationship('Tag', backref='image')
    def __init__(self, imagelink):
        self.imagelink = imagelink

    def __repr__(self):
        text = ""
        for tag in self.tags:
            text += tag.name + "|"
        return 'Image: %s\nTags: %s' (self.imagelink, self.text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.Text)
    role = db.Column(db.String(10))
    comments = db.relationship('Comment', backref='user')
    threads = db.relationship('Thread', backref='user')   # 1 user writes many threads
                                                            # t.p_user => gets (parent) user
    
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role
    def __repr__(self):
        return "User: %s ; Pass: %s" % (self.username, self.password)
        
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
    body = db.Column(db.Text)
    c_time = db.Column(db.DateTime) # when the comment was created
    m_time = db.Column(db.DateTime) # when the comment was last modified
    # would ideally have recursive comments; comments reply to comments
    # children = db.Column([Comments]) kind of thing
    # parent = db.Column(Comment)

    def __init__(self, thread, user, body):
        self.thread = thread
        self.user = user
        self.body = body
        thread.comments.append(self)
        user.comments.append(self)
        # db.session.add(thread)
        # db.session.add(user)
    def __repr__(self):
        return "Thread Title: %s\nPoster: %s\nText: %s\n" % (self.thread.title, self.user.username, self.body)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    name = db.Column(db.String(15))

    def __init__(self, image, name):
        self.image = image
        self.name = name
        image.tags.append(self)
    def __repre__(self):
        return 'Image: %s\n Tag: %s' % (self.image.imagelink, self.name)

def newthread(title, body, imagelink, user, tags):
    """ adds a new thread to the DB; returns a thread object and an image object """

    taglist = list()
    i = Image(imagelink)
    for tag in tags:
        tag = Tag(i, tag)
        db.session.add(tag)
        taglist.append(taglist)
    t = Thread(title, body, user, i)
    # note: if you try to use bulk_save_objects instead of add, it silently fucks up.
    db.session.add(i)
    db.session.add(t)
    db.session.commit()
    # tag shit
    return t, i
    
def newcomment(thread, user, body):
    """ Commits a new comment; returns the comment object"""
    c = Comment(thread, user, body)
    db.session.add(c)
    db.session.commit()
    return c

def newuser(username, password, role):   
    """ Adds a new user; Returns -1 if username was taken; Returns the committed user object otherwise """
    # this would be the point to hash the pass
    # and do a try/catch to validate username uniqueness
    u = User(username, password, role)
    db.session.add(u)
    db.session.commit()
    return u

def addtags(image, taglist):
    pass

def getuserbyname(username):
    return User.query.filter_by(username=username).first()
def getthreadbyimagename(imagelink):
    return Image.query.filter_by(imagelink=imagelink).first().thread[0]
def getlast20images():
    return Image.query.limit(20).all()
def getallimageswithtag(tagname):
    return Image.query.filter_by(tags=tagname).all()


# population functions
bugpath = 'imgs/bugs/'
def getalltestusers():
    names = ['brandon', 'neil', 'zubin', 'alfredo']
    return map(getuserbyname, names)
def getalltestthreads():
    imagenames = list(listdir('static/' + bugpath))
    return map(getthreadbyimagename, imagenames) 

def makeusers():
    names = ['brandon', 'neil', 'zubin', 'alfredo']
    passw = 'password'
    roles = ['admin'  , 'admin','user' , 'user']
    for name, roles in zip(names, roles):
        newuser(name, passw, roles)
def makethreads():
    imagenames = list(listdir('static/' + bugpath))
    users = getalltestusers()
    for i, imagename in enumerate(imagenames):
        title = 'title %s' % i
        body = 'body-text %s' % i
        tags = ['ladybug', 'praying mantis']
        newthread(title, body, imagename, users[i%4], tags)
def makecomments():
    threads = getalltestthreads()
    users = getalltestusers()
    for i, thread in enumerate(threads):
        c = newcomment(thread, users[i%4], 'body text %s' % i)
        
def makeall():
    makeusers()
    makethreads()
    makecomments()

    
# u = newuser('neil', 'pass', 'admin')
# u2 = newuser('alfredo', 'pass', 'user')
# t, i = newthread('title', 'body', 'file.jpg', u, None)
# c = newcomment(t, u, 'bodytext')
# addtags(i, ['ladybug', 'enemy-of-the-state')


# from script import User, Image, Comment, Thread, db; u = User('neil', 'password'); u2 = User('nathan', 'password'); i = Image('image.jpg'); t = Thread("title", "body text", u, i); c1 = Comment(t, u, "body text1"); c2 = Comment(t, u2, "body text 2");db.session.add(u);db.session.add(u2);db.session.add(t);db.session.add(c1);db.session.add(c2);db.session.add(i);db.commit();
db.drop_all()
db.create_all()
makeall()

#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
import shutil
import unittest
import exifread

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))

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
    imagename = db.Column(db.String(100))
    geoloc = db.Column(db.String(25))
    thread = db.relationship('Thread', backref='image')   # 1:1 map with an image
    tags = db.relationship('Tag', backref='image')

    def __init__(self, imagename, geoloc=None):
        self.imagename = imagename
        self.geoloc = geoloc

    def __repr__(self):
        text = ""
        for tag in self.tags:
            text += tag.name + "|"
        return 'Image: %s\nTags: %s' % (self.imagename, text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(160))
    role = db.Column(db.String(10))
    comments = db.relationship('Comment', backref='user')
    threads = db.relationship('Thread', backref='user')   # 1 user writes many threads
                                                            # t.p_user => gets (parent) user
    def check_pass(self, password):
        return check_password_hash(self.password, password)
    
    def __init__(self, username, password, role):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

    def __repr__(self):
        return "User: %s ; Pass: %s" % (self.username, self.password)
        
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    parent = db.relationship("Comment",
                                backref="children",
                                remote_side=[id])

    body = db.Column(db.Text)
    c_time = db.Column(db.DateTime) # when the comment was created
    m_time = db.Column(db.DateTime) # when the comment was last modified

    def __init__(self, thread, user, body, parent=None):
        self.thread = thread
        self.user = user
        self.body = body
        if parent:
            self.parent = parent 
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
        return 'Image: %s\n Tag: %s' % (self.image.imagename, self.name)

def newthread(title, body, imagename, userobj, tags, geoloc=None):
    """ adds a new thread to the DB; returns a thread object and an image object """

    i = Image(imagename, geoloc)
    for tag in tags:
        tg = Tag(i, tag)
        db.session.add(tg)
    t = Thread(title, body, userobj, i)
    # note: if you try to use bulk_save_objects instead of add, it silently fucks up.
    db.session.add(i)
    db.session.add(t)
    db.session.commit()
    # tag shit
    return t, i
    
def newcomment(threadobj, user, body, parent=None):
    """ Commits a new comment; returns the comment object"""
    c = Comment(threadobj, user, body, parent)
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

def addtags(imagename, taglist):
    image = Imagequery.filter_by(imagename=imagename).first()
    if image:
        for tag in taglist:
            tag = Tag(image, tag)
            db.session.add(Tag)
        db.session.commit()
    pass

# this should really be in a seperate helper module
def getgeoloc(filepath):
    extension = filepath.rsplit('.', 1)[1]

    geoloc = None
    if extension in ['jpg', 'jpeg']:  # then get exif data
        try:
            exif = exifread.process_file(open(filepath, 'rb'), details=False)
            #'GPS GPSLatitude': (0x0002) Ratio=[46, 3803/100, 0] @ 850
            #'GPS GPSLongitude': (0x0004) Ratio=[13, 2429/100, 0] @ 874,
            if 'GPS GPSLatitude' in exif and 'GPS GPSLongitude' in exif:
                print exif
                lat = exif['GPS GPSLatitude'].values #[46, 3803/100, 0]
                lon = exif['GPS GPSLongitude'].values #[13, 2429/100, 0]
                
                # degree + minutes + seconds to decimal
                lat = map(lambda x: x.num * 1. / x.den, lat)
                lon = map(lambda x: x.num * 1. / x.den, lon)

                lat = lat[0] + (lat[1]*1. /60) + (lat[2]*1. /3600)
                lon = lon[0] + (lon[1]*1. /60) + (lon[2]*1. /3600)
                lat = round(lat, 6)
                lon = round(lon, 6)

                # Longitude (E): +  Latitude (N): +
                # Longitude (W): -  Latitude (S): -

                if 'GPS GPSLatitudeRef' in exif:
                    latref = exif['GPS GPSLatitudeRef'].values
                    if latref == 'S':
                        lat *= -1
                if 'GPS GPSLongitudeRef' in exif:
                    lonref = exif['GPS GPSLongitudeRef'].values
                    if lonref == 'W':
                        lon *= -1

                geoloc = "%s,%s" % (lat, lon)
                # then store lat/long in format for gmaps, in the image table
                # and inject into html on image loading, for js gmaps 
        except UnicodeEncodeError:
            return None
    return geoloc

def getuserbyname(username):
    return User.query.filter_by(username=username).first()
def getthreadbyimagename(imagename):
    return Image.query.filter_by(imagename=imagename).first().thread[0]
def getlast20images():
    return Image.query.limit(20).all()
def getallimageswithtag(tagname):
    images = Image.query.all()
    return [i for i in images if tagname in [t.name for t in i.tags]]
    #return Image.query.filter_by(tags=tagname).all()
def isvalidlogin(username, password):
    user = getuserbyname(username)
    if user.check_pass(password):
        return True, user
    return False, None


# population functions
bugpath = 'static/imgs/bugs/'
def getalltestusers():
    names = ['brandon', 'neil', 'zubin', 'alfredo']
    return map(getuserbyname, names)
def getalltestthreads():
    imagenames = list(os.listdir(bugpath))
    return map(getthreadbyimagename, imagenames) 

def makeusers():
    names = ['brandon', 'neil', 'zubin', 'alfredo']
    passw = 'password'
    roles = ['admin', 'admin', 'user', 'user']
    for name, roles in zip(names, roles):
        newuser(name, passw, roles)
def makethreads():
    # remove production folder, and replace with copy of dummy
    # so we can start from scratch
    dummy = 'static/imgs/dummyimgs/'
    if os.path.isdir(bugpath):
        shutil.rmtree(bugpath)
    shutil.copytree(dummy, bugpath)

    imagenames = list(os.listdir(bugpath))
    users = getalltestusers()
    ts = ['ladybug', 'praying mantis']
    for i, imagename in enumerate(imagenames):
        title = 'title %s' % i
        body = 'body-text %s' % i
        tags = [ts[i%2]]
        print bugpath + imagename
        geoloc = getgeoloc(bugpath + imagename)
        newthread(title, body, imagename, users[i%4], tags, geoloc)
def makecomments():
    threads = getalltestthreads()
    users = getalltestusers()
    for i, thread in enumerate(threads):
        c = newcomment(thread, users[i%4], 'body text %s' % i)
        c = newcomment(thread, users[(i+1)%4], 'body text %s' % (i+1,), c)
        c = newcomment(thread, users[(i+2)%4], 'body text %s' % (i+2,), c)
        c = newcomment(thread, users[(i+3)%4], 'body text %s' % (i+3,))
        
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

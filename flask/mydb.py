#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
import shutil
import unittest
import exifread

import requests
import re

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://master:leech@64.131.111.27/newdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

master = SQLAlchemy.create_engine("mysql+pymysql://master:leech@64.131.111.27/newdatabase")
slave = SQLAlchemy.create_engine("mysql+pymysql://master:leech@64.131.111.26/newdatabase")
Session = SQLAlchemy.scoped_session(SQLAlchemy.sessionmaker(bind=master))

def with_slave(fn):
    def go(*arg, **kw):
        s = Session()
        oldbind = s.bind
        s.bind = slave
        try:
            return fn(*arg, **kw)
        finally:
            s.bind = oldbind
    return go


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
    """ 
    Thread Table 
    
    ============= ======
    Relationships Tables
    ============= ======
    many:1        user:thread
    1:many        thread:comments
    1:1           thread:image
    ============= ======

    :param int id: unique id
    :param str title: thread title
    :param str body: OP's body text
    :param User user: parent user object (1:many thread:user)
    :param Image image: image object (1:1 image:thread)
    :param Comment comments: list of children comment objects (1:many thrad: comments)
    """

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
    """ 
    Image Table

    ============= ======
    Relationships Tables
    ============= ======
    1:1           thread:image
    many:1        tags:image 
    ============= ======

    :param str imagename: The name of the image, stored on disk
    :param str geoloc: The X,Y coordinates for Google maps. May be *null*
    :param Tag tags: list of children tag objects
    """

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
    """ 
    User Table

    ============= ======
    Relationships Tables
    ============= ======
    1:many        user:thread
    1:many        user:comments
    ============= ======

    :param str username: User's username
    :param str password: User's hashed + salted password
    :param str role: User's role ['user', 'admin']
    :param Comment comments: list of comments the user has made
    :param Thread thread: list of threads the user has made
    """

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
    """ 
    Comments table

    ============= ======
    Relationships Tables
    ============= ======
    1:many        user:comments
    1:many        thread:comments
    ============= ======

    :param User user: The user that created this comment
    :param Thread thread: The thread this comment lives in
    :param Comment parent: If this comment is a reply, this is set to the parent comment. Otherwise, None
    :param str body: The body text of the comment
    """

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
    """ 
    Tag table

    ============= ======
    Relationships Tables
    ============= ======
    many:1        tags:image
    ============= ======

    :param Image image: The image this tag is associated with
    :param str name: The text of this tag
    """
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
    """ 
    adds a new thread to the DB and commits
    
    :param str title: title of the thread
    :param str body: body text for the OP
    :param str imagename: name of the image stored on disk
    :param User userobj: the user making the thread
    :param Tag tags: list of tags associated with the image
    :param str geoloc: geoloc for the image, if available. Otherwise None

    :return: (Thread, Image) tuple. The Thread and Image objects created.
    """

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
    """ 
    Commits a new comment

    :param Thread threadobj: the thread owning this comment
    :param User user: the user posting this comment
    :param str body: the body text
    :param Comment parent: the comment this comment replies to, if relevant. Otherwise, None

    :return: the Comment object"""
    c = Comment(threadobj, user, body, parent)
    db.session.add(c)
    db.session.commit()
    return c

def newuser(username, password, role):   
    """ 
    Adds a new user
    :param str username:
    :param str password: plaintext password
    :param str role: user's role from ['user', 'admin']

    :return: -1 if username was taken
    :return: Otherwise, the User object.
    """
    # this would be the point to hash the pass
    # and do a try/catch to validate username uniqueness
    u = User(username, password, role)
    db.session.add(u)
    db.session.commit()
    return u

def addtags(imagename, taglist):
    """
    Appends tags to the given image

    :param str imagename: name of image stored on disk
    :param [Tag] taglist: list of tags to be appended
    :return: Nothing
    """
    image = Imagequery.filter_by(imagename=imagename).first()
    if image:
        for tag in taglist:
            tag = Tag(image, tag)
            db.session.add(Tag)
        db.session.commit()
    pass

# this should really be in a seperate helper module
def getgeoloc(filepath):
    """
    Finds the geolocation for the given file, by reading the EXIF data. Only useful for jpg files.

    :param str filepath: full filepath for the target image
    
    :return: geolocation (str) if found
    :return: None otherwise
    """
    extension = filepath.rsplit('.', 1)[1]

    geoloc = None
    if extension in ['jpg', 'jpeg']:  # then get exif data
        try:
            exif = exifread.process_file(open(filepath, 'rb'), details=False)
            #'GPS GPSLatitude': (0x0002) Ratio=[46, 3803/100, 0] @ 850
            #'GPS GPSLongitude': (0x0004) Ratio=[13, 2429/100, 0] @ 874,
            if 'GPS GPSLatitude' in exif and 'GPS GPSLongitude' in exif:
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

@with_slave
def getuserbyname(username):
    """ 
    :param str username:
    :return: the user object affiliated with the username """
    return User.query.filter_by(username=username).first()

@with_slave
def getthreadbyimagename(imagename):
    """ 
    :param str imagename:
    :return: an image object affiliated with the image name """
    try:
        val = Image.query.filter_by(imagename=imagename).first().thread[0]
    except AttributeError:
        val = None
    return val

@with_slave
def getlast20images():
    """ :return: a list of image objects"""
    return Image.query.limit(20).all()

@with_slave
def getallimageswithtag(tagname):
    """ 
    :param str tagname:
    :return: a list of image objects associated with the tag """
    images = Image.query.all()
    return [i for i in images if tagname in [t.name for t in i.tags]]

@with_slave
def isvalidlogin(username, password):
    """ 
    :param str username:
    :param str password: plaintext password
    :return: True, user-object if login succeeded
    :return: True, user-object if iit-login succeeded; creates new user(name, pass, role="iit")
    :return: False, None otherwise """
    # try to validate through our db
    user = getuserbyname(username)
    success = False
    if user and user.check_pass(password):
        success = True
    # try to validate through iit
    if not user:
        r = requests.get('http://my.iit.edu/cp/home/login?pass=%s&user=%s' % (password, username))
        ok = re.compile('loginok.html', re.MULTILINE)
        if re.search(ok, r.text):
            success = True
            user = newuser(username, password, 'iit')

    if success:
        return True, user
    else: 
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
        c = newcomment(thread, users[i%4], 'body text HELP %s' % i)
        c = newcomment(thread, users[(i+1)%4], 'body text HELP2 %s' % (i+1,), c)
        c = newcomment(thread, users[(i+2)%4], 'body text %s' % (i+2,), c)
        c = newcomment(thread, users[(i+3)%4], 'body text %s' % (i+3,))
        
def makeall():
    """ Autogenerates dummy data """
    makeusers()
    makethreads()
    makecomments()

    
""" Dumps the DB, rebuilds it, and inserts dummy data """ 
def rebuilddb():
    db.drop_all()
    db.create_all()
    makeall()




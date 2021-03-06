#!/usr/bin/env python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from flask import Flask
import os
import shutil
import unittest
import exifread

import requests
import re
import subprocess

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://master:leech@64.131.111.94/newdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

master = create_engine("mysql+pymysql://master:leech@64.131.111.94/newdatabase")
slave = create_engine("mysql+pymysql://slave:leech@64.131.111.95/newdatabase")
Session = scoped_session(sessionmaker(bind=master))

def with_slave(fn):
    """
    Decorator

    Forces the decorated function to use the slave session, instead of the master.

    Returns the session to the master at the end of the function.
    """
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
        self.user = user
        self.body = body
        if parent:
            self.parent = parent 
        else: # thread should only refer to root nodes
            self.thread = thread
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

def makethread1(users):
    imagename = 'QK2CXrHybdE2oz25y7dfknpOQ2RcchvZlmQQayNFzkE.jpg'
    tags = ['colorful', 'desert']
    op = users[0]
    title = 'Who\'s this cool looking bug? [Tucson, AZ]'
    body = 'LOOK AT ALL THESE DESERT BUGS!'
    geoloc = getgeoloc(bugpath + imagename)
    thread, _ = newthread(title, body, imagename, op, tags, geoloc)

    c1 = newcomment(thread, users[1],
            """An iron cross blister beetle, Tegrodera sp""")
    c2 = newcomment(thread, users[2],
            """Also, do not touch it. You can get painful blisters. And do not eat it, the same chemical that causes the blisters is poisonous to us, and can be fatal.""",
            c1)
    c3 = newcomment(thread, users[1],
            """The coloring is definitely a sign.""",
            c2)
    c4 = newcomment(thread, users[3],
            """citation?""",
            c2)
    c5 = newcomment(thread, users[2],
            """\"It has drawn a lot of attention due to its toxicity to humans and the painful/fatal diseases it inflicts upon certain livestock. This chemical, C10H12O4, causes severe skin blisters (dermatosis) to humans within hours of exposure to it; it is not known how much of this substance it takes to cause a skin blister. The insect secretes this substance as a defense mechanism, or it can happen if it is crushed and comes in contact with skin. (Ghoneim, Karem S.)\"
            http://en.m.wikipedia.org/wiki/Iron_Cross_Beetle""",
            c4)
    return None

def makethread2(users):
    imagename = '3d67e9b8e32e4e5e984b4413db2407f3.jpeg'
    tags = ['centipede', 'upside-down']
    op = users[3]
    title = '[Southwestern US] Centipede'
    body = 'Found in reddit\'s r/creepy'
    geoloc = getgeoloc(bugpath + imagename)
    thread, _ = newthread(title, body, imagename, op, tags, geoloc)

    c1 = newcomment(thread, users[0],
            """I\'m not sure how useful a belly shot is to others who may have more experience with centipedes than me, but it looks like something in Scolopendra, maybe a common desert centipede or something approximating that. Not one you\'d want to fondle.""")
    c2 = newcomment(thread, users[3],
            """Okay thanks!""",
            c1)
    c3 = newcomment(thread, users[2],
            """I think I\'d die right on the spot if I saw that in person!""")
    return None

def makethread3(users):
    imagename = 'Ot_rXXcnnNtBPm2NeDBtSzNy5f7WA-H90-KKuGPfNAA.jpg'
    tags = ['SPIDERS', 'EVERYWHERE']
    op = users[1]
    title = """Everywhere! Spiders !!!"""
    body = """Hey, these spiders are everywhere in my house and I started freaking myself out that it is a Brown Recluse.. I need to know the type of spider!!!! What do you guys think??"""
    geoloc = getgeoloc(bugpath + imagename)
    thread, _ = newthread(title, body, imagename, op, tags, geoloc)

    c1 = newcomment(thread, users[2],
            """Fairly sure it\'s Tegenaria domestica, the barn funnel weaver/eruopean house spider. Very common all across North America. Harmless and common.""")
    c2 = newcomment(thread, users[3],
            """You got it. Those overlapping pentagons are usually diagnostic.""",
            c1)
    c3 = newcomment(thread, users[0],
            """You might have better luck posting this guy over at /r/spiders!
            I can promise it's not a brown recluse though, they're smaller and have much lighter bodies. There really aren\'t any spiders in that area that you need to be super worried about as far as danger goes, but I can\'t give you a confident ID! Sorry!""")
    c4 = newcomment(thread, users[1],
            """Thank you that\'s honestly all I needed. I\'m considering burning the fucking place. I swear I kill at least three of these huge assholes every day and it\'s disgusting.""",
            c3)
    c5 = newcomment(thread, users[2],
            """For the most part, most of the breeds of spiders in North America aren\'t dangerous to humans, with the exception of Black Widows and Brown Recluses, and even then if you can get a positive ID and medical attention quickly enough you\'ll be fine.""",
            c4)
    c6 = newcomment(thread, users[3],
            """Fine kill the spiders. Have fun with the swarms of small pests theyve been keeping at bay.""",
            c4)
    return None

def makethread4(users):
    imagename = '20160428_090635.jpg'
    tags = ['wasp', 'hornet', 'scary', 'florida', 'winged']
    op = users[2]
    title = '[Florida US] Wasp or Hornet?'
    body = 'Saw this out by my shed! Wasp or Hornet? How do I get rid of the nest!?'
    geoloc = getgeoloc(bugpath + imagename)
    thread, _ = newthread(title, body, imagename, op, tags, geoloc)

    c1 = newcomment(thread, users[3],
            """Looks like a hornet to me!""")
    c2 = newcomment(thread, users[0],
            """Actually its a umbrella wasp...very common in places like Florida""",
            c1)
    c3 = newcomment(thread, users[1],
            """Keep your kids away from there!""")
    return None

def makethread5(users):
    imagename = '20160428_090810.jpg'
    tags = ['gross', 'cockroach', 'brown', 'hairy legs', 'florida']
    op = users[1]
    title = '[Florida US] Cockroach?'
    body = 'Is this a cockroach? I cant tell!'
    geoloc = getgeoloc(bugpath + imagename)
    thread, _ = newthread(title, body, imagename, op, tags, geoloc)

    c1 = newcomment(thread, users[3],
            """Those are a pain to get rid of if they get in your house!""")
    c2 = newcomment(thread, users[0],
            """Looks like a cockroach to me...""")
    return None

def makethread6(users):
    imagename = '20160428_094037.jpg'
    tags = ['dragonfly', 'black', 'florida', 'winged']
    op = users[0]
    title = '[Florida US] Dragonfly'
    body = 'This dragonfly is cool! What kind is it?'
    geoloc = getgeoloc(bugpath + imagename)
    thread, _ = newthread(title, body, imagename, op, tags, geoloc)

    c1 = newcomment(thread, users[2],
            """Calopteryx maculata""")
    c2 = newcomment(thread, users[1],
            """adult Calopteryx maculata, a damselfly. The species is in the family Calopterygidae""")
    c3 = newcomment(thread, users[3],
            """adult damselfly from the family Coenagrionidae""")
    return None

def makethread7(users):
    imagename = '20160428_090755.jpg'
    tags = ['beetle', 'brown', 'florida']
    op = users[3]
    title = '[Florida US] beetle'
    body = 'found this beetle under a rock'
    geoloc = getgeoloc(bugpath + imagename)
    thread, _ = newthread(title, body, imagename, op, tags, geoloc)

    c1 = newcomment(thread, users[0],
            """small and cute!""")
    c2 = newcomment(thread, users[1],
            """i think it may be a hister beetle""")
    c3 = newcomment(thread, users[2],
            """those don't normally live under rocks though""", c2) 
    c4 = newcomment(thread, users[1],
            """oh okay my bad""", c3)
    return None

def makethreads_real():
    dummy = 'static/imgs/real_dummyimgs/'
    if os.path.isdir(bugpath):
        shutil.rmtree(bugpath)
    shutil.copytree(dummy, bugpath)

    users = getalltestusers()
    makethread1(users)
    makethread2(users)
    makethread3(users)
    makethread4(users)
    makethread5(users)
    makethread6(users)
    makethread7(users)

def makeall_real():
    """ Autogenerates dummy data based on reddit threads """
    makeusers()
    makethreads_real()


    
""" Dumps the DB, rebuilds it, and inserts dummy data """ 
def rebuilddb():
    db.drop_all()
    db.create_all()
    #makeall()
    makeall_real()



def dumpdb():
    """ retores the database, returns text to give back to the user """
    command = "python manage.py dump create".split(" ")
    try:
        output = subprocess.check_output(command).strip()
    except subprocess.CalledProcessError:
        return ["We broke!"]
    return [o[4:] for o in output.split('\n')]

def getids():
    """ Returns a list of (backup_ids, full_text) """
    command = "python manage.py dump history".split(" ")
    try:
        output = subprocess.check_output(command).strip().split("\n")
    except subprocess.CalledProcessError:
        return None
    output = [o[4:] for o in output if "ID" in o][::-1]
    backupids = map(lambda x: re.search('ID: (\d+?) ', x).group(1), output)
    return zip(output, backupids)

def restoredb(num):
    """ restores the database; returns text to give back to the user """
    command = "python manage.py dump restore -d %s" % str(num)
    command = command.split(" ")
    try:
        output = subprocess.check_output(command).strip().split("\n")
    except subprocess.CalledProcessError:
        return ["we broke it!"]
    output = map(lambda x: re.search('-(.*\.gz.*)', x).group(1), output)
    return output

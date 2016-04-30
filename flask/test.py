import mydb
import os
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for, flash, redirect, session
from flask import send_from_directory
from flask_recaptcha import ReCaptcha
from os import listdir
from werkzeug import secure_filename

gmaps_key = 'AIzaSyBB3o_tLwpc9tvBuoFF0S-bdv934mrmhv4'

import exifread
app = Flask(__name__)
recaptcha = ReCaptcha(app=app)

bugpath = "imgs/bugs/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = 'static/' + bugpath


## This thing is supposed to be secret	
## ~~ nyaa ~~
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
@app.route('/',methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    images = mydb.getlast20images()
    imgnames = [i.imagename for i in images]
    entries = [(dict(imagepath=bugpath+name, link="bug/"+name)) for name in imgnames]
    return render_template('index.html',entries=entries, index=True)

def ishuman():
    human = True
    if human not in session or (human in session and not session['human']):
        human = False
        for i in xrange(3):
            if recaptcha.verify():
                session['human'] = True
                human = True
        
    return human

@app.route('/login', methods=['POST'])
def login():
    error = None
    message = "" 
    username, password  = request.form['username'], request.form['password']

    if username and password:
        valid, user = mydb.isvalidlogin(username, password)
        if valid:
            session['username'] = user.username
            session['role'] = user.role
            session['logged_in'] = True
    return redirect(url_for('index'))
        
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('human', None)
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        if 'logged_in' in session and not session['logged_in']:
            return redirect(url_for('index'))
            # errormsg = 'You must be logged in to post'
            # return redirect(url_for('403.html'))
        return render_template('signup.html')
    if ishuman():
        username = request.form['username']
        password = request.form['password']


        role = 'user'
        user = mydb.newuser(username, password, role)
        session['username'] = username
        session['role'] = user.role
        session['logged_in'] = True
        return redirect(url_for('index'))

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', about=True)

def allowed_file(filename):
    # this checks if the file extension is valid
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # if request is GET, load the upload form-page
    if request.method == 'GET':
        return render_template('upload.html')

    # if POST read the file and form data
    image = request.files['file']
    title = request.form['title']
    body = request.form['body']
    tags = request.form['tags'] 
    tags = tags.split(',')

    
    # The log-in check *should* be in the 'GET' side of things
    # So the user doesn't do all the work, and then get informed he can't post
    if 'logged_in' not in session:
        errormsg = 'You must be logged in to post'
        return redirect(url_for('403.html'))
        #return redirect(url_for('error', error=errormsg))

    # we should probably redirect back to the 'GET' side, with the forms still filled out.
    if not image or not allowed_file(image.filename):
        errormsg = 'file not allowed'
        return redirect(url_for('index')) 
        #return redirect(url_for('error', error=errormsg))
        #return render_template('index.html', error=errormsg)

	#user = session['username']
    user = mydb.getuserbyname(session['username'])


    # setting the object imagename to the secure file  	
    imagename = secure_filename(image.filename)
    # saving the file to the upload folder static/imgs/bugs
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], imagename)
    image.save(filepath)
    geoloc = mydb.getgeoloc(filepath)
    
    # make a new thread
    thread,image = mydb.newthread(title, body, imagename, user, tags, geoloc)
    # and then send the user to it
    
    # imagename should be the name of the image itself, without any filepath
    # ie 'bug-img.jpg'
    return redirect(url_for('bug', path=image.imagename)) 

@app.route('/profile')
def profile():
	return render_template('profile.html')
	##TODO
	pass

@app.route('/bug/<path:path>', methods=['GET', 'POST'])
def bug(path):
    thread = mydb.getthreadbyimagename(path)
    # thread doesn't exist; throw error at user
    if not thread:
        return redirect(url_for('index')) 
        #return redirect(url_for('error', error=errormsg))

    bug_image = bugpath + thread.image.imagename

    return render_template('bug.html',
            thread=thread,
            bug_image = bug_image)

@app.route('/bug/<path:path>/postcomment', methods=['GET', 'POST'])
def postcomment(path):
    body = request.form['cbody']
    print request.form
    if body.strip():
        user = mydb.getuserbyname(session['username'])
        thread = mydb.getthreadbyimagename(path)
        c = mydb.newcomment(thread, user, body)
    return redirect(url_for('bug', path=path))

#selected tag
@app.route('/tags/<path:path>', methods=['GET', 'POST'])
def tags(path):
    imageobjs = mydb.getallimageswithtag(path)
    imagenames = [i.imagename for i in imageobjs]
    images = [(dict(imagepath=bugpath+name, link=name)) for name in imagenames]
    # get all bugs with tagname
    # pass it to the template
    return render_template('tags.html',tags=True, tag=path, images=images)
    ## TODO
    pass

#direct to tags
@app.route('/tags', methods=['GET', 'POST'])
def tag():
    # this page needs to do a word cloud or whatever
    # instead of displaying images of bugs with the given tag
    tags = mydb.Tag.query.all()
    tags = sorted(set([t.name for t in tags]))
    return render_template('tags.html', tags=True, taglist=tags)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500 

if __name__ == "__main__":
    mydb.rebuilddb()
    app.run(host='0.0.0.0', debug=True)

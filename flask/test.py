import mydb
import os
from flask import Flask
from flask import render_template
from flask import request
from flask import url_for, flash, redirect, session
from flask import send_from_directory
from os import listdir
from werkzeug import secure_filename


import exifread
app = Flask(__name__)
 
bugpath = "imgs/bugs/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = 'static/' + bugpath

## This thing is supposed to be secret	
## ~~ nyaa ~~
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
@app.route('/',methods=['GET'])
@app.route('/index', methods=['GET'])
#def process_form():
def index():
    images = mydb.getlast20images()
    imgnames = [i.imagename for i in images]
    entries = [(dict(imagepath=bugpath+name, link="bug/"+name)) for name in imgnames]
    return render_template('index.html',entries=entries, index=True)

@app.route('/login', methods=['POST'])
def login():
    error = None
    message = "" 
    valid, user = mydb.isvalidlogin(request.form['username'], request.form['password'])
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
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

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
        return redirect(url_for('index'))
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
    extension = image.filename.rsplit('.', 1)[1]

    if extension in ['jpg', 'jpeg']:  # then get exif data
        exif = exifread.process_file(open(filepath, 'rb'), details=False)
        #'GPS GPSLatitude': (0x0002) Ratio=[46, 3803/100, 0] @ 850
        #'GPS GPSLongitude': (0x0004) Ratio=[13, 2429/100, 0] @ 874,
        if 'GPS GPSLatitude' in exif and 'GPS GPSLongitude' in exif:
            lat = exif['GPS GPSLatitude'].values() #[46, 3803/100, 0]
            lon = exif['GPS GPSLongitude'].values() #[13, 2429/100, 0]
            # then store lat/long in format for gmaps, in the image table
            # and inject into html on image loading, for js gmaps
    
    # make a new thread
    thread = mydb.newthread(title, body, imagename, user, tags)
    # and then send the user to it
    
    # imagename should be the name of the image itself, without any filepath
    # ie 'bug-img.jpg'
    return redirect(url_for('bug', path=imagename)) 

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

    question = thread.title
    bug_image = bugpath + thread.image.imagename
    tags = [tag.name for tag in thread.image.tags]
    body = thread.body

    comments = thread.comments
    
    #tags = ['ladybug', 'beetle', 'spotted']
    #question = "What bug is this??"
    #bug_image = bugpath+path
    #tags = bugs[path]

    return render_template('bug.html',
            user = thread.user.username,
            tags = tags,
            question = question,
            bug_image = bug_image,
            description = body,
            comments = comments)
		

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

if __name__ == "__main__":
   app.run(host='0.0.0.0', debug=True)

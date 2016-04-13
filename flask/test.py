from flask import Flask
from flask import render_template
from flask import request
from flask import url_for, flash, redirect, session
from os import listdir
import mydb

app = Flask(__name__)
 
bugpath = "imgs/bugs/"

## This thing is supposed to be secret
## ~~ nyaa ~~
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
@app.route('/',methods=['GET'])
@app.route('/index', methods=['GET'])
#def process_form():
def index():
    #imgnames = list(listdir('static/' + bugpath))
    images = mydb.getlast20images()
    imgnames = [i.imagelink for i in images]
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
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        username = request.form['username']
        password = request.form['password']
        role = 'user'
        newuser(username, password, role)
        session['username'] = username
        session['role'] = user.role
        session['logged_in'] = True
        return redirect(url_for('login'))
    ##TODO
    pass

@app.route('/about', methods=['GET', 'POST'])
def about():
    # About.html doesn't exist
    return render_template('about.html', about=True)
    ## TODO
    pass
@app.route('/upload', methods=['POST'])
def upload():
    # get everything necessary for a new thread
    # save the image to bugpath =>
    # 'static/' + bugpath + imgname
    # make a new thread
    user = getuserbyusername(session['username'])
    imagename = None # this should be the name of the image itself, without any filepath
                     # ie 'bug-img.jpg'
    title = request.form['title']
    body = request.form['body']
    # tags needs to be a list of strings.
    # if tags comes in as a comma seperated list, then do 
    # tags = tags.split(',')
    tags = request.form['tags'] 
    thread = newthread(title, body, imagename, user, tags)
    return redirect(url_for('bug'), path=thread.image.imagelink)
    #  


	# return render_template('upload.html')
	# ##TODO
	# pass

@app.route('/profile')
def profile():
	return render_template('profile.html')
	##TODO
	pass

bugs={
"140602.png" : ['ladybug', 'beetle', 'spotted'],
"Dore-Justice.jpg" : ['parasites', 'anthill'],
"Dore-Portrait-of-Dante.jpg" : ['mantis', 'machine'],
"Dore-Rose.jpg": ['Borer', 'Mining'],
"Dore-Woe's-me.jpg": ["dampwood", "drywood", "varieties"],
"Dore-Wretched-Hands.jpg": [],
"Dore-Writhing.jpg": [],
"General_Winter.jpg": [],
"akagi-3928579.jpg": [],
"escher-babel.jpg":[]
}


@app.route('/bug/<path:path>', methods=['GET', 'POST'])
def bug(path):
    thread = mydb.getthreadbyimagename(path)
    question = thread.title
    bug_image = bugpath + thread.image.imagelink
    tags = [tag.name for tag in thread.image.tags]
    body = thread.body
    
    #tags = ['ladybug', 'beetle', 'spotted']
    #question = "What bug is this??"
    #bug_image = bugpath+path
    #tags = bugs[path]

    return render_template('bug.html',
            tags = tags,
            question = question,
            bug_image = bug_image,
            description = body)
    # [tags]
    # question
    # bug_image (the name of it)

    ## TODO
    pass

#selected tag
@app.route('/tags/<path:path>', methods=['GET', 'POST'])
def tags(path):
    print path
    # get all bugs with tagname
    # pass it to the template
    return render_template('tags.html', tags=True)
    ## TODO
    pass

#direct to tags
@app.route('/tags', methods=['GET', 'POST'])
def tag():

    # this page needs to do a word cloud or whatever
    # instead of displaying images of bugs with the given tag
    return render_template('tag.html', tags=True)
    ##TODO
    pass




if __name__ == "__main__":
   app.run(host='0.0.0.0', debug=True)

from flask import Flask
from flask import render_template
from flask import request
from flask import url_for, flash, redirect, session
from os import listdir

app = Flask(__name__)

bugpath = "imgs/bugs/"

## This thing is supposed to be secret
## ~~ nyaa ~~
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
@app.route('/',methods=['GET'])
#def process_form():
def index():
    imgnames = list(listdir('static/' + bugpath))
    entries = [(dict(imagepath=bugpath+name, link="bug/"+name)) for name in imgnames]

    return render_template('index.html',entries=entries)

@app.route('/login', methods=['POST'])
def login():
    error = None
    message = "" 
    if request.form['username'] != 'admin':
        message = 'Invalid username'
    elif request.form['password'] != 'leech':
        message = 'Invalid password'
    else:
        session['username'] = request.form['username']
        session['logged_in'] = True
        flash('login succeeded')
    return redirect(url_for('index'))
        
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')
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
    tags = ['ladybug', 'beetle', 'spotted']
    question = "What bug is this??"
    bug_image = bugpath+path
    tags = bugs[path]

    return render_template('bug.html',
            tags = tags,
            question = question,
            bug_image = bug_image)
    # [tags]
    # question
    # bug_image (the name of it)

    ## TODO
    pass


if __name__ == '__main__':
   app.run(debug=True)

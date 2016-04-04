from flask import Flask
from flask import render_template
from flask import request
from flask import url_for, flash, redirect, session
from os import listdir

app = Flask(__name__)

## This thing is supposed to be secret
## ~~ nyaa ~~
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
@app.route('/',methods=['GET'])
#def process_form():
def index():
    imgnames = list(listdir('static/imgs'))
    entries = [(dict(imagepath="imgs/"+name, link='#')) for name in imgnames]

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
        
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')
    ##TODO
    pass


@app.route('/bug', methods=['GET', 'POST'])
def bug():
    # [tags]
    # question
    ## TODO
    pass

if __name__ == '__main__':
   app.run(debug=True)

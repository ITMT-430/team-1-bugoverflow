from flask import Flask
from flask import render_template
from flask import request
from os import listdir

app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def process_form():
    if request.method == 'POST':
       form_input = request.form['name']
       return render_template('index.html',name=form_input)
    else:
       imgnames = list(listdir('static/imgs'))
       entries = [(dict(imagepath="imgs/"+name, link='#')) for name in imgnames]

       return render_template('index.html',entries=entries)

@app.route('/signup', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin':
            error = 'Invalid username'
        elif request.form['password'] != 'leech':
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('signup.html', error=error)
if __name__ == '__main__':
   app.run(debug=True)

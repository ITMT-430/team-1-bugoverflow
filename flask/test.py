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

if __name__ == '__main__':
   app.run(debug=True)

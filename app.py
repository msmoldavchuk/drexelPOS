from flask import Flask
from flask import render_template
from flask import request
import requests
app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/Plan')
def plan():
    return render_template('plan.html')

@app.route('/POS')
def pos():
    return render_template('pos.html')
@app.route('/temp', methods=['GET', 'POST'])
def temp():
    if request.method == 'POST':
        if request.form.get('name'):
            return render_template('temp.html', name="hello")
    return render_template('temp.html')
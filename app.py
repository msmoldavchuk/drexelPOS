from flask import Flask
from flask import render_template
from flask import request
import requests
from flask import json
from flask import jsonify
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
    return render_template('courseinput.html')
#reroutes to POS pages
@app.route('/POS/CS')
def poscs():
    if request.method == 'POST':
        return render_template('POS/CS.html')
#API endpoints
@app.route('/api/POS', methods=['GET', 'POST'])
def api_pos():
    if request.method == 'POST':
        if request.form.get('major'):
            return redirect(url_for('POS/CS'))
@app.route('/api/POS/CS', methods=['GET', 'POST'])
def api_poscs():
    #this takes the form data from the CS POS page and runs it through the API
    #returns the data as a json object
    #method()
    return jsonify({'place': 'holder'})


#test routes
#does not use for anything except testing
@app.route('/test', methods=['GET', 'POST'])
def testfn():
    # GET request
    if request.method == 'GET':
        message = {'greeting':'Hello from Flask!'}
        return jsonify(message)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        print(request.get_json())  # parse as JSON
        return 'Sucesss', 200


@app.route('/test/data', methods=['GET', 'POST'])
def testfn2():
    if request.method == 'POST':
        
        print(request.get_data(as_text=True))
        message = request.get_data(as_text=True)
        return jsonify(message)

@app.route('/temp', methods=['GET', 'POST'])
def temp():
    if request.method == 'POST':
        if request.form.get('name'):
            return render_template('temp.html', name="hi")
    return render_template('temp.html')
            

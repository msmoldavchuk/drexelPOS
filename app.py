from flask import Flask
from flask import render_template
from flask import request
import requests
from flask import json
from flask import jsonify
from werkzeug.datastructures import ImmutableMultiDict
import scrapper
app = Flask(__name__)


#core webpage routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/Plan')
def plan():
    return render_template('plan.html')

#routes for CS pos generation 
@app.route('/csPOS/data', methods=['GET', 'POST'])
def csPOS():
    if request.method == 'POST':
        print(request.mimetype)
        data = request.get_json()
        data = scrapper.getPlanOfStudy(NAME=data.get('major'),CONCENTRATION1= data.get('concentration1'), CONCENTRATION2= data.get('concentration2'),SPRINGSUMMERCOOP=data.get('coop'),SEQUENCELOCK=data.get('sequence'))
        return jsonify(data)

   
@app.route('/CS', methods=['GET', 'POST'])
def cs():
    return render_template('CS.html')


#test routes
#does not use for anything except testing

@app.route('/temp2', methods=['GET', 'POST'])
def temp2():
    return render_template('temp2.html')
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


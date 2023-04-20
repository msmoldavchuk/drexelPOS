from flask import Flask
from flask import render_template
from flask import request
import requests
from flask import json
from flask import jsonify
from werkzeug.datastructures import ImmutableMultiDict
import scrapper
app = Flask(__name__)
if __name__ == "__main__":
    app.run()

#core webpage routes
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/allmajors')
def allmajors():
    return render_template('allmajors.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/Plan')
def plan():
    return render_template('plan.html')
@app.route('/allmajor')
def allmajor():
    return render_template('allmajor.html')
#routes for CS pos generation 
@app.route('/csPOS/data', methods=['GET', 'POST'])
def csPOS():
    if request.method == 'POST':
        print(request.mimetype)
        data = request.get_json()
        hardCodeDictoanary = {"Algorithms and Theory":["CS 457","MATH 300","MATH 305"],"Artificial Intelligence and Machine Learning":["DSCI 351","CS 383","CS 380"],"Computer Systems & Architecture":["CS 314","CS 361","CS 370"],"Software Engineering":["CS 375","SE 320","SE 410"]}
        conc1 = data.get('concentration1')
        conc2 = data.get('concentration2')
        concentrationArray = [[conc1, hardCodeDictoanary.get(conc1)], [conc2, hardCodeDictoanary.get(conc2)]]
        data = scrapper.getPlanOfStudy("CS",SPRINGSUMMERCOOP=data.get('coop'),SEQUENCES=[data.get('sequence')], CONCENTRATIONARRAY=concentrationArray)
        return jsonify(data)

@app.route('/sePOS', methods=['GET', 'POST'])
def sePOS():
    if request.method == 'POST':
        major = "SE"
        data = request.get_json()
        output = scrapper.getPlanOfStudy(major, SPRINGSUMMERCOOP=data.get('coop'), SEQUENCES=[[data.get('sequence')],data.get('business')],CONCENTRATIONARRAY=[])
        return jsonify(output)
#@app.route('/CS', methods=['GET', 'POST'])
#def cs():
#    return render_template('CS.html')
@app.route('/degree/<degreename>', methods=['GET', 'POST'])
def degree(degreename):
    return render_template(f'{degreename}.html')


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


from flask import Flask
from flask import render_template
from flask import request
import requests
from flask import json
from flask import jsonify
from werkzeug.datastructures import ImmutableMultiDict
import scrapper
from course import Course as c
from sequence import Sequence as s, LinkedList, Node
from degree import Degree as d
import pandas as pd

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
        print(request.get_json())
        print("hi")
        data = request.get_json()
        conc1 = data.get('concentration1')
        conc2 = data.get('concentration2')
        concentrationArray = [[conc1[0],conc1[1]], [conc2[0], conc2[1]]]
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

# routes for getting dynamic data
@app.route('/getSequence/', methods=['GET', 'POST'])
def getSequence():
        output = getConcentration(request.get_json().get('name'))
        seqs = output[0]
        flags = output[1]
        outputStrings = []
        for i in range(len(seqs)):
            outputStrings.append(seqs[i].displayWebsite())

        return jsonify({"flags" : flags , "Subconcentrations" : outputStrings})
#test routes
#does not use for anything except testing

def getConcentration(name):
    degreeReq = d()
    degreeReq.convertCSVToDegree("CS")
    for data in degreeReq.getDataForWebsite():
        if type(data[0]) == s:
            for line in data[0].displayWebsite():
                line.strip()
            # data[1] is an internal flag (ask me questions)
            # data[2] is the number they have to chose
        else:
            for concentration in data[0][0]:
                if name == concentration.loc[0,"Type"]: # line for visual clarity
                    return [list(concentration.loc[:, "Sequence"]), list(concentration.loc[:, "Flag"])]
                          
@app.route('/temp2', methods=['GET', 'POST'])
def temp2():
    return render_template('temp2.html')



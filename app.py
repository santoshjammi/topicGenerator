# app.py

from flask import Flask, render_template,request
from getKeywords import getKeywords
app = Flask(__name__)

kws=[
    {
        'keyword' : '7.62x25',
        'generated': ['7.62x25 schematics and diagram',
'7.62x25 schematics and diagrams',
'7.62x25 schematics and parts',
'7.62x25 schematics and symbols',
'7.62x25 schematics barrel',
'7.62x25 schematics brass',
'7.62x25 schematics chart',
'7.62x25 schematics circuit',
'7.62x25 schematics diagram',
'7.62x25 schematics download',
'7.62x25 schematics electrical',
'7.62x25 schematics for home',
'7.62x25 schematics for minecraft',
'7.62x25 schematics for sale',
'7.62x25 schematics free',
'7.62x25 schematics guide',
'7.62x25 schematics hollow',
'7.62x25 schematics how to',
'7.62x25 schematics in autocad',
'7.62x25 schematics in excel',
'7.62x25 schematics in minecraft',
'7.62x25 schematics in powerpoint',
'7.62x25 schematics john deere',
'7.62x25 schematics key',
'7.62x25 schematics kids',
'7.62x25 schematics kit',
'7.62x25 schematics kits',
'7.62x25 schematics labeled',
'7.62x25 schematics layout',
'7.62x25 schematics list',
'7.62x25 schematics location',
'7.62x25 schematics manual',
'7.62x25 schematics minecraft',
'7.62x25 schematics names',
'7.62x25 schematics near me',
'7.62x25 schematics number',
'7.62x25 schematics numbers',
'7.62x25 schematics of 2',
'7.62x25 schematics of building',
'7.62x25 schematics of tesla',
'7.62x25 schematics of water',
'7.62x25 schematics parts',
'7.62x25 schematics pdf',
'7.62x25 schematics questions',
'7.62x25 schematics quick',
'7.62x25 schematics quiz',
'7.62x25 schematics quizlet',
'7.62x25 schematics rear',
'7.62x25 schematics red',
'7.62x25 schematics symbols',
'7.62x25 schematics tarkov',
'7.62x25 schematics using',
'7.62x25 schematics vs',
'7.62x25 schematics white',
'7.62x25 schematics with fabric',
'7.62x25 schematics with pictures',
'7.62x25 schematics with world',
'7.62x25 schematics xbox',
'7.62x25 schematics xbox one',
'7.62x25 schematics xfinity',
'7.62x25 schematics xp',
'7.62x25 schematics yamaha',
'7.62x25 schematics yba',
'7.62x25 schematics year',
'7.62x25 schematics youtube',
'7.62x25 schematics zillow',
'7.62x25 schematics zip',
'7.62x25 schematics zoning',
'7.62x25 schematics zoom']
    }
]

@app.route("/generateKeywords", methods = ['POST', 'GET'])
def home():
    keyword="The Night Agent"
    theDict={}

    if request.method == "POST":
       # getting input with name = fname in HTML form
        keyword = request.form.get("my_input")
        print(keyword)
        try:
            theList=getKeywords(keyword)
            theDict[keyword]=theList
        except Exception as e:
            print(e)
    return render_template("generateTopic.html",posts=theDict,title=keyword)

# @app.route('/generateKeywords', methods = ['POST', 'GET'])
# def my_form_post():
#     if request.method == 'POST':
#       user = request.form.get['my_input']
    
#     return render_template("generateTopic.html",posts="",title=user)


@app.route("/about")
def about():
    return render_template("about.html")

# @app.route("/")
# def index():
#     return render_template("index.html")

@app.route('/', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
       # getting input with name = fname in HTML form
       first_name = request.form.get("fname")
       # getting input with name = lname in HTML form 
       last_name = request.form.get("lname") 
       return "Your name is "+first_name + last_name
    return render_template("form.html")
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)



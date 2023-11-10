from flask import Flask, render_template,request,redirect,url_for 
from pymongo import MongoClient 
from bson.objectid import ObjectId 
from bson.errors import InvalidId 
import os
import random

mongo_uri = "mongodb://mongodb-service:27017" 
client = MongoClient(mongo_uri)   
db = client["mydatabase"]   
todos = db["todos"]
app = Flask(__name__)
title = "TODO with Flask"
heading = "ToDo Reminder"
#modify=ObjectId()

def redirect_url():
	return request.args.get('next') or \
		request.referrer or \
		url_for('index')


def is_healthy():
    return random.choice([True, False])


def is_ready():
    try:
        # Attempt to connect to MongoDB
        mongo_uri = "mongodb://mongodb-service:27017"
        client_check = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client_check.admin.command('ismaster')  # This checks if the connection is healthy
        client_check.close()  # Close the connection
        return True  # MongoDB connection is healthy
    except ConnectionFailure:
        return False  # MongoDB connection failed

@app.route('/readiness', methods=['GET'])
def readiness_check():
    # Implement your readiness check logic here
    # For example, you can check if your app has completed any necessary setup
    # and is ready to receive requests from clients
    if is_ready():
        return "Ready", 200
    else:
        return "Not Ready", 503 

@app.route("/list")
def lists ():
	#Display the all Tasks
	todos_l = todos.find()
	a1="active"
	return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading)

@app.route("/")
@app.route("/uncompleted")
def tasks ():
	#Display the Uncompleted Tasks
	todos_l = todos.find({"done":"no"})
	a2="active"
	return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading)


@app.route("/completed")
def completed ():
	#Display the Completed Tasks
	todos_l = todos.find({"done":"yes"})
	a3="active"
	return render_template('index.html',a3=a3,todos=todos_l,t=title,h=heading)

@app.route('/health', methods=['GET'])
def health_check():
    if is_healthy():
        return "Healthy", 200
    else:
        return "Unhealthy", 500

@app.route("/done")
def done ():
	#Done-or-not ICON
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	if(task[0]["done"]=="yes"):
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"no"}})
	else:
		todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})
	redir=redirect_url()	# Re-directed URL i.e. PREVIOUS URL from where it came into this one

#	if(str(redir)=="http://localhost:5000/search"):
#		redir+="?key="+id+"&refer="+refer

	return redirect(redir)

#@app.route("/add")
#def add():
#	return render_template('add.html',h=heading,t=title)

@app.route("/action", methods=['POST'])
def action ():
	#Adding a Task
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	todos.insert_one({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
	return redirect("/list")

@app.route("/remove")
def remove ():
	#Deleting a Task with various references
	key=request.values.get("_id")
	todos.delete_one({"_id":ObjectId(key)})
	return redirect("/")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/action3", methods=['POST'])
def action3 ():
	#Updating a Task with various references
	name=request.values.get("name")
	desc=request.values.get("desc")
	date=request.values.get("date")
	pr=request.values.get("pr")
	id=request.values.get("_id")
	todos.update_one({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
	return redirect("/")

@app.route("/search", methods=['GET'])
def search():
	#Searching a Task with various references

	key=request.values.get("key")
	refer=request.values.get("refer")
	if(refer=="id"):
		try:
			todos_l = todos.find({refer:ObjectId(key)})
			if not todos_l:
				return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="No such ObjectId is present")
		except InvalidId as err:
			pass
			return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading,error="Invalid ObjectId format given")
	else:
		todos_l = todos.find({refer:key})
	return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

@app.route("/about")
def about():
	return render_template('credits.html',t=title,h=heading)

if __name__ == "__main__":
	#env = os.environ.get('FLASK_ENV', 'development')
	#port = int(os.environ.get('PORT', 8080))
	#debug = False if env == 'production' else True
	#app.run(debug=True)
	app.run(host="0.0.0.0",port=8200, debug=True)
	# Careful with the debug mode..
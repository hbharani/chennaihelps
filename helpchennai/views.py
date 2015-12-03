from flask import render_template, Response,request, redirect, url_for, jsonify
from helpchennai import app
from pymongo import MongoClient, ASCENDING, DESCENDING, errors, GEOSPHERE
from forms import RequestHelp, OfferHelp
import json
import datetime
from bson.objectid import ObjectId

client = MongoClient()
db = client['Disaster_Help']

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/getpoints', methods=['POST'])
def getPoints():
	chennaiCollection = db["chennai"]
	boundingBox = [json.loads(request.data)]
	parcelJSON = []
	for address in chennaiCollection.find({"geometry":{"$geoWithin": {"$geometry": {"type" : "Polygon" ,"coordinates": boundingBox}}}, "satisfied":0}):
		parcelJSON.append({"type":"Feature", "geometry":address["geometry"],"properties":{"type":address["properties"]["type"],"id":str(address["_id"])}})
	return jsonify(allpoints = {"type":"FeatureCollection", "features":parcelJSON})

@app.route('/requesthelp', methods=['GET'])
def requestBubble():
	form = RequestHelp()
	return render_template('request-help.html', form = form)

@app.route('/offerhelp', methods=['GET'])
def offerBubble():
	form = OfferHelp()
	return render_template('offer-help.html', form = form)

@app.route('/uploadrequest', methods=['POST'])
def uploadRequest():
	form = RequestHelp()
	chennaiCollection = db["chennai"]
	print form.lat.data
	if form.validate_on_submit():
		document = {"type": "Feature","satisfied":0,"geometry": {"type": "Point","coordinates": [-999,-999]},"properties": {}}
		document["geometry"]["coordinates"][1] = float(form.lat.data)
		document["geometry"]["coordinates"][0]  = float(form.lng.data)
		document["properties"]["name"]  = form.name.data
		document["properties"]["phone"]  = form.phone.data
		document["properties"]["address"]  = form.address.data
		document["properties"]["email"]  = form.email.data
		document["properties"]["noofpeople"]  = form.noofpeople.data
		document["properties"]["service"]  = form.request.data
		document["properties"]["notes"]  = form.notes.data
		document["properties"]["type"] = "Requesting"
		document["timestamp"] = datetime.datetime.now()
		chennaiCollection.insert(document)
		return Response("1",mimetype='text' )
	else:
		return render_template('request-help.html', form = form)

@app.route('/uploadoffer', methods=['POST'])
def uploadOffer():
	form = OfferHelp()
	chennaiCollection = db["chennai"]
	print form.lat.data
	if form.validate_on_submit():
		document = {"type": "Feature","satisfied":0,"geometry": {"type": "Point","coordinates": [-999,-999]},"properties": {}}
		document["geometry"]["coordinates"][1] = float(form.lat.data)
		document["geometry"]["coordinates"][0]  = float(form.lng.data)
		document["properties"]["name"]  = form.name.data
		document["properties"]["phone"]  = form.phone.data
		document["properties"]["address"]  = form.address.data
		document["properties"]["email"]  = form.email.data
		document["properties"]["noofpeople"]  = form.noofpeople.data
		document["properties"]["service"]  = form.offer.data
		document["properties"]["notes"]  = form.notes.data
		document["properties"]["type"] = "Offering"
		document["timestamp"] = datetime.datetime.now()
		chennaiCollection.insert(document)
		return Response("1",mimetype='text' )
	else:
		return render_template('offer-help.html', form = form)

@app.route('/showinfo', methods=['GET'])
def showInfo():
	chennaiCollection = db["chennai"]
	document = chennaiCollection.find_one({'_id': ObjectId(request.args.get("id",""))})
	if "notes" in document["properties"]:
		 notes = document["properties"]["notes"]
	else:
		notes = ""
	if "address" in document["properties"]:
		 address = document["properties"]["address"]
	else:
		address = ""
	return render_template('show-info.html',
			name=document["properties"]["name"],phone=document["properties"]["phone"],
			address=address,
			email=document["properties"]["email"],noofpeople=document["properties"]["noofpeople"],
			type=document["properties"]["type"],service=document["properties"]["service"],
			id=str(document["_id"]), notes=notes)

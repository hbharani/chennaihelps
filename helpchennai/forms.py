from flask.ext.wtf import Form
from wtforms import StringField, IntegerField,SelectField, validators, HiddenField
from wtforms.validators import InputRequired, Email
from wtforms.fields.html5 import EmailField, TelField 
NO_OF_PEOPLE = [(str(y), str(y)) for y in range(1, 20)]
NO_OF_PEOPLE.append(('>20', '>20'))
SERVICES = [('Select','Select'),('Shelter', 'Shelter'),('Food','Food'), ('Transport', 'Transport'), ('Clothes','Clothes')]

class RequestHelp(Form):
	name = StringField('Name', validators=[InputRequired("*Required")])
	phone = TelField('Phone',validators=[InputRequired("*Required")])
	email = EmailField("Email")
	noofpeople = SelectField('No of People',choices=NO_OF_PEOPLE)
	request = SelectField('Request', validators=[InputRequired("*Required")], choices=SERVICES)
	notes = StringField('Notes')
	lat = HiddenField("lat")
	lng = HiddenField("lng")
	
class OfferHelp(Form):
	name = StringField('Name', validators=[InputRequired("*Required")])
	phone = TelField('Phone',validators=[InputRequired("*Required")])
	email = EmailField("Email")
	noofpeople = SelectField('No of People',choices=NO_OF_PEOPLE)
	offer = SelectField('Offer', validators=[InputRequired("*Required")], choices=SERVICES)
	notes = StringField('Notes')
	lat = HiddenField("lat")
	lng = HiddenField("lng")
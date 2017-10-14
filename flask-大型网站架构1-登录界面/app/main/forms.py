from wtforms.validators import Required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class NameForm(FlaskForm):
    name=StringField('What is your name?',validators=[Required()])
    submit=SubmitField('Submit')
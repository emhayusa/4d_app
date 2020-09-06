from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField, SelectField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

    submit = SubmitField('Sign In')

class UploadGmlForm(FlaskForm):
	file = FileField()
	submit = SubmitField('Upload')
	
class VerifyGmlForm(FlaskForm):
	city_gml_id = HiddenField('city_gml_id')
	filename = HiddenField('filename')
	respons = SelectField('respons', choices=[('1', 'Reject'),('2', 'Approve')], validators=[DataRequired()])
	reason = TextAreaField('reason')
	submit = SubmitField('Verify')
	
class VerifyAttributeForm(FlaskForm):
	id = HiddenField('id')
	respons = SelectField('respons', choices=[('1', 'Reject'),('2', 'Approve')], validators=[DataRequired()])
	reason = TextAreaField('reason')
	submit = SubmitField('Verify')

class VerifyPhotoForm(FlaskForm):
	id = HiddenField('id')
	respons = SelectField('respons', choices=[('1', 'Reject'),('2', 'Approve')], validators=[DataRequired()])
	reason = TextAreaField('reason')
	submit = SubmitField('Verify')

class VerifyVideoForm(FlaskForm):
	id = HiddenField('id')
	respons = SelectField('respons', choices=[('1', 'Reject'),('2', 'Approve')], validators=[DataRequired()])
	reason = TextAreaField('reason')
	submit = SubmitField('Verify')
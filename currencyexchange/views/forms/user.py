import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField

class UserUpdateForm(FlaskForm):
    name = StringField('name', validators=[validators.DataRequired()])
    phone = StringField('Phone', validators=[validators.DataRequired()])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    currency = StringField('Currency Code', [validators.Length(min=3, max=3)])
    submit = SubmitField('Update Profile')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise validators.ValidationError('Invalid phone number')

from flask_wtf import FlaskForm


from wtforms import (PasswordField, SelectField,
                     StringField, SubmitField,BooleanField)

from wtforms.validators import (data_required,
                                regexp)


class StdForm(FlaskForm):
    """
    This form for default regions
    """
    vendor = SelectField('-', validate_choice=False)

    model = SelectField('-', validate_choice=False)

    msk = StringField('msk',
                      validators=[data_required(), regexp(r'^MSK\d+$',
                                                          message="Incorrect symbols")])

    hostname = StringField('Hostname',
                           validators=[data_required(), regexp(r'^[.a-zA-Z0-9\-_а-яА-Я ]+$',
                                                               message="Incorrect symbols")])
    ip_mask = StringField('IPv4/Mask',
                          validators=[data_required(), regexp(r'\d+\.\d+\.\d+\.\d+[\\\/]2\d$',
                                                              message="Incorrect ip/mask format")])
    user_vlan = StringField('User_vid',
                            validators=[data_required(), regexp(r'^((?:\b(?:\d|[1-9]\d|[1-9]\d|'
                                                                r'[1-9]\d\d|[1-3]\d\d\d|'
                                                                r'40[0-8][0-9]|409[0-5])\b,?)+)$',
                                                                message="vlan is between 1 and 4094")])

    mgmt_vlan = StringField('mgmt-vid',
                            validators=[data_required(), regexp(r'^((?:\b(?:\d|[1-9]\d|[1-9]\d|'
                                                                r'[1-9]\d\d|[1-3]\d\d\d|'
                                                                r'40[0-8][0-9]|409[0-5])\b,?)+)$',
                                                                message="vlan is between 1 and 4094")])

    # trunk_vlan = StringField('trunk_vids',
    #                          validators=[data_required(), regexp(r'^( *(\d+ *to *\d+|\d+ *- *\d+|\d+)[, ]? *)+$',
    #                                                              message="Incorrect format. Example: 1-2,3 to 10,11. "
    #                                                                      "Whitespaces don't match")])
    trunk_vlan = StringField()
    multicast_vlan = StringField()
    op_description = StringField()
    snmp_location = StringField()


class SaratovForm(FlaskForm):
    """
    This form for Sararov
    """
    vendor = SelectField('-', validate_choice=False)

    model = SelectField('-', validate_choice=False)

    msk = StringField('msk',
                      validators=[data_required(), regexp(r'^MSK\d+$',
                                                          message="Incorrect symbols")])

    hostname = StringField('Hostname',
                           validators=[data_required(), regexp(r'^[a-zA-Z0-9\-_а-яА-Я ]+$',
                                                               message="Incorrect symbols")])
    ip_mask = StringField('IPv4/Mask',
                          validators=[data_required(), regexp(r'\d+\.\d+\.\d+\.\d+[\\\/]2\d$',
                                                              message="Incorrect ip/mask format")])
    user_vlan = StringField()
    multicast_vlan = StringField()
    op_description = StringField()
    op_checkbox = BooleanField()
    snmp_location = StringField()


class LoginForm(FlaskForm):
    username = StringField('Username', validators={data_required()})
    password = PasswordField('Password', validators={data_required()})
    Submit = SubmitField('Sign in')

class PenzaForm(FlaskForm):
    vendor = SelectField('-', validate_choice=False)

    model = SelectField('-', validate_choice=False)

    msk = StringField('msk',
                      validators=[data_required(), regexp(r'^MSK\d+$',
                                                          message="Incorrect symbols")])

    hostname = StringField('Hostname',
                           validators=[data_required(), regexp(r'^[.a-zA-Z0-9\-_а-яА-Я ]+$',
                                                               message="Incorrect symbols")])
    ip_mask = StringField('IPv4/Mask',
                          validators=[data_required(), regexp(r'\d+\.\d+\.\d+\.\d+[\\\/]2\d$',
                                                              message="Incorrect ip/mask format")])

    mgmt_vlan = StringField('mgmt-vid',
                            validators=[data_required(), regexp(r'^((?:\b(?:\d|[1-9]\d|[1-9]\d|'
                                                                r'[1-9]\d\d|[1-3]\d\d\d|'
                                                                r'40[0-8][0-9]|409[0-5])\b,?)+)$',
                                                                message="vlan is between 1 and 4094")])

    user_vlan = StringField('user_vlans',
                             validators=[data_required(), regexp(r'^( *(\d+ *to *\d+|\d+ *- *\d+|\d+)[, ]? *)+$',
                                                                 message="Incorrect format. Example: 1-2,3 to 10,11. "
                                                                         "Whitespaces don't match")])
    trunk_vlan = StringField()
    multicast_vlan = StringField()
    op_description = StringField()
    snmp_location = StringField()

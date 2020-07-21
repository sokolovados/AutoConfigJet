from flask_login import UserMixin
from configurator import db
from datetime import datetime



region_models = db.Table('region_models',
                         db.Column('model_id', db.Integer, db.ForeignKey('models.id')),
                         db.Column('city_id', db.Integer, db.ForeignKey('regions.id')))

region_checkboxes = db.Table('region_checkboxes',
                             db.Column('checkboxes_id', db.Integer, db.ForeignKey('checkboxes.id')),
                             db.Column('city_id', db.Integer, db.ForeignKey('regions.id')))

region_recommendations = db.Table('region_recommendations',
                                  db.Column('recommendations_id', db.Integer, db.ForeignKey('recommendations.id')),
                                  db.Column('city_id', db.Integer, db.ForeignKey('regions.id')))


class Regions(db.Model, UserMixin):
    __tablenname__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    mr = db.Column(db.String(80), nullable=False)
    mr_name = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(80), unique=True, nullable=False)
    city_name = db.Column(db.String(80), unique=True, nullable=False)
    models = db.relationship('Models', secondary=region_models,
                             backref=db.backref('models', lazy='dynamic'))
    checkbox = db.relationship('Checkboxes', secondary=region_checkboxes,
                               backref=db.backref('checkboxes', lazy='dynamic'))
    recommendations = db.relationship('Recommendations', secondary=region_recommendations,
                                      backref=db.backref('recommendations', lazy='dynamic'))





class Models(db.Model):
    __tablenname__ = 'models'
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), unique=True, nullable=False)


class Users(UserMixin, db.Model):
    __tablenname__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)



class Checkboxes(db.Model):
    __tablenname__ = 'checkboxes'
    id = db.Column(db.Integer, primary_key=True)
    checkbox = db.Column(db.String(80), unique=True, nullable=False)


class Recommendations(db.Model):
    __tablenname__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    recommendation = db.Column(db.String(80), unique=True, nullable=False)


class Accounting(db.Model):
    __tablenname__ = 'accounting'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    region = db.Column(db.String(80), nullable=False)
    msk = db.Column(db.String(80), nullable=False)
    ip = db.Column(db.String(80), nullable=False)
    hostname = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False,
                     default=datetime.utcnow)
    accounting = db.Column(db.String(200), nullable=False)


db.create_all()

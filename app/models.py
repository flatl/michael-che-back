import os
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from datetime import datetime
from time import time


class User(db.Model):
  __tablename__ = 'User'
  id = db.Column(db.Integer, primary_key=True)
  login = db.Column(db.String(64), index=True, unique=True)
  password_hash = db.Column(db.String(128))

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)


class Token(db.Model):
  __tablename__ = 'Token'
  value = db.Column(db.String(64), primary_key=True)
  expiredAt = db.Column(db.DateTime)

  def is_actual(self):
    return self.expiredAt > datetime.now() 

  @staticmethod
  def generate_token():
    return str(uuid4())

  @staticmethod
  def get_expired_datetime_from_now():
    additional_seconds = os.environ.get('TOKEN_VALIDITY_TIME_SS') or 60*60
    return datetime.fromtimestamp(time() + additional_seconds)
    


ProjectColor = db.Table(
  'ProjectColor',
  db.Model.metadata,
  db.Column('projectId', db.ForeignKey('Project.id')),
  db.Column('colorId', db.ForeignKey('Color.id'))
)

ProjectType = db.Table(
  'ProjectType',
  db.Model.metadata,
  db.Column('projectId', db.ForeignKey('Project.id')),
  db.Column('typeId', db.ForeignKey('Type.id'))
)

ProjectCategory = db.Table(
  'ProjectCategory',
  db.Model.metadata,
  db.Column('projectId', db.ForeignKey('Project.id')),
  db.Column('categoryId', db.ForeignKey('Category.id'))
)

ProjectImage = db.Table(
  'ProjectImage',
  db.Model.metadata,
  db.Column('projectId', db.ForeignKey('Project.id')),
  db.Column('imageId', db.ForeignKey('Image.id'))
)

class Project(db.Model):
  __tablename__ = 'Project'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(128))
  description = db.Column(db.String(1024))
  colors = db.relationship('Color', secondary=ProjectColor)
  types = db.relationship('Type', secondary=ProjectType)
  categories = db.relationship('Category', secondary=ProjectCategory)
  images = db.relationship('Image', secondary=ProjectImage)

  def json(self):
    return {
      'id': self.id,
      'title': self.title,
      'description': self.description,
      'colors': [color.value for color in self.colors],
      'types': [p_types.title for p_types in self.types],
      'categories': [category.title for category in self.categories],
      'images': [image.name for image in self.images]
    }

  @staticmethod
  def get_all_colors():
    project_colors = [project.colors for project in Project.query.all()]
    colors = [color.json() for pcolors in project_colors for color in pcolors]
    return exclude_repeats(colors, 'value')

  @staticmethod
  def get_all_types():
    project_types = [project.types for project in Project.query.all()]
    types = [ptype.json() for ptypes in project_types for ptype in ptypes]
    return exclude_repeats(types, 'title')

  @staticmethod
  def get_all_categories():
    project_categories = [project.categories for project in Project.query.all()]
    categories = [category.json() for pcategories in project_categories for category in pcategories]
    return exclude_repeats(categories, 'title')


class Color(db.Model):
  __tablename__ = 'Color'
  id = db.Column(db.Integer, primary_key=True)
  value = db.Column(db.String(8))

  def json(self):
    return {
      'id': self.id,
      'value': self.value
    }


class Type(db.Model):
  __tablename__ = 'Type'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(64))

  def json(self):
    return {
      'id': self.id,
      'title': self.title
    }


class Category(db.Model):
  __tablename__ = 'Category'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(64))
  
  def json(self):
    return {
      'id': self.id,
      'title': self.title
    }

class Image(db.Model):
  __tablename__ = 'Image'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128))

def exclude_repeats(lst, unique_prop_name):
  lst_props = set([item[unique_prop_name] for item in lst])
  return [list(filter(lambda item: item[unique_prop_name] == prop, lst))[0]\
    for prop in lst_props]

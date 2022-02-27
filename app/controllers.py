import os
import json
import random
from flask import request
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequestKeyError
from config import basedir
from app import db
from app.models import User, Token, Project, Color, Type, Category, Image
from app.responses import (
  SUCCESS_MESSAGE,
  EMPTY_DATA_MESSAGE,
  INCORRECT_DATA_MESSAGE,
  NO_TOKEN_MESSAGE,
  WRONG_TOKEN_MESSAGE,
  TOKEN_EXPIRED_MESSAGE
)

def add_project(request):
  get_list_prop = lambda prop: json.loads(request.form[prop])

  image_pathes = save_images(request.files)

  try:
    loaded_images = get_list_prop('images') 
    if (len(loaded_images)):
      image_pathes.extend(get_list_prop('images'))
  except (BadRequestKeyError, TypeError) as e:
    pass

  colors, types, categories, images = [], [], [], []

  for color_value in get_list_prop('colors'):
    color = Color(value=color_value)
    db.session.add(color)
    colors.append(color)
  
  for type_title in get_list_prop('types'):
    project_type = Type(title=type_title)
    db.session.add(project_type)
    types.append(project_type)

  for category_title in get_list_prop('categories'):
    category = Category(title=category_title)
    db.session.add(category)
    categories.append(category)

  for image_path in image_pathes:
    image = Image(name=image_path)
    db.session.add(image)
    images.append(image)
  
  db.session.commit()

  project = Project(title=request.form['title'],
    description=request.form['description'],
    colors=colors,
    types=types,
    categories=categories,
    images=images
  )

  db.session.add(project)
  db.session.commit()

  return SUCCESS_MESSAGE



def delete_project(request, id):
    project = Project.query.filter_by(id=id).first()
    if project:
      for ptype in project.types:
        has_type_in_another_project = any(
          any([t == ptype for t in proj.types])\
          for proj in Project.query.filter(Project.id != project.id)
        )
        if has_type_in_another_project:
          project.types.remove(ptype)
        else:
          db.session.delete(ptype)

      for category in project.categories:
        has_category_in_another_project = any(
          any([c == category for c in proj.categories])\
          for proj in Project.query.filter(Project.id != project.id)
        )
        if has_category_in_another_project:
          project.categories.remove(category)
        else:
          db.session.delete(category)
  
      for color in project.colors:
        has_color_in_another_project = any(
          any([c == color for c in proj.colors])\
          for proj in Project.query.filter(Project.id != project.id)
        )

        if has_color_in_another_project:
          project.colors.remove(color)
        else:
          db.session.delete(color)

      db.session.delete(project)
      db.session.commit()

      return SUCCESS_MESSAGE
    else:
      return INCORRECT_DATA_MESSAGE


def replace_project(request):
  project = Project.query.filter_by(id=request.form["id"]).first()
  
  if project:
    delete_project(request, project.id)
    return add_project(request)
  
  return INCORRECT_DATA_MESSAGE


def save_images(images):
  image_save_dir = os.environ.get('IMAGES_STATIC_PATH') or os.path.join(basedir, 'images')
  pathes = []
  for key in images:
    image = images[key]
    random_image_filename = str(int(random.random() * 1000)) + image.filename
    filename = secure_filename(random_image_filename)
    image.save(os.path.join(image_save_dir, filename))
    pathes.append(filename)
  return pathes


def check_token(next):
  @wraps(next)
  def func(*args, **kwargs):
    if request.method == 'GET':
      return next(*args, **kwargs)

    try:
      request_token = request.headers.get('Authorization')
      token = Token.query.filter_by(value=request_token).first()
      if token is None:
        return WRONG_TOKEN_MESSAGE
      elif not token.is_actual():
        return TOKEN_EXPIRED_MESSAGE
      else:
        return next(*args, **kwargs)
    except (TypeError, AttributeError) as e:
      print(e)
      return WRONG_TOKEN_MESSAGE
  return func

import os
import json
from config import basedir
from app import app, db
from flask import request, send_from_directory
from app.models import User, Token, Project, Color, Type, Category, Image
from app.controllers import (
  add_project,
  delete_project,
  replace_project,
  check_token
)
from app.responses import (
  SUCCESS_MESSAGE,
  EMPTY_DATA_MESSAGE,
  INCORRECT_DATA_MESSAGE,
  NO_TOKEN_MESSAGE,
  WRONG_TOKEN_MESSAGE,
  TOKEN_EXPIRED_MESSAGE
)

@app.route('/login', methods=['POST'])
def login():
  request_data = request.get_json()

  try:
    login = request_data['login']
    password = request_data['password']

    user = User.query.filter_by(login=login).first()
    if user is None or not user.check_password(password):
      return INCORRECT_DATA_MESSAGE
    
    token = Token(
      value=Token.generate_token(),
      expiredAt=Token.get_expired_datetime_from_now()
    )
    db.session.add(token)
    db.session.commit()

    return json.dumps({
      'success': True,
      'token': token.value,
      'expiredAt': token.expiredAt.isoformat()
    })

  except TypeError:
    return EMPTY_DATA_MESSAGE
  

@app.route('/projects', methods=['GET', 'POST', 'PUT', 'DELETE'])
@check_token
def projects():
  if request.method == 'GET':
    projects = Project.query.all()
    return json.dumps({
      'success': True,
      'data': [project.json() for project in projects]
    })
  elif request.method == 'DELETE':
    request_data = request.get_json()
    return delete_project(request, request_data['id'])
  elif request.method == 'POST':
    return add_project(request)
  elif request.method == 'PUT':
    return replace_project(request)


@app.route('/categories', methods=['GET'])
def categories():
  return json.dumps({
    'success': True,
    'data': Project.get_all_categories()
  })


@app.route('/types', methods=['GET'])
def types():
  return json.dumps({
    'success': True,
    'data': Project.get_all_types()
  })

@app.route('/colors', methods=['GET'])
def colors():
  return json.dumps({
    'success': True,
    'data': Project.get_all_colors()
  })

@app.route('/is_authed', methods=['POST'])
@check_token
def is_authed():
  return json.dumps({
    'success': True
  })

@app.route('/images/<filename>')
def get_image(filename):
  directory = os.environ.get('IMAGES_STATIC_PATH') or os.path.join(basedir, 'images')
  return send_from_directory(directory, filename)

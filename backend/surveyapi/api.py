"""
api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
from functools import wraps

import jwt

from .models import db, Survey, Question, Choice, User

api = Blueprint('api', __name__)


def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registration and/or authentication required.',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthenication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            user = User.query.filter_by(email=data['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return _verify


@api.route('/surveys/', methods=('POST',))
@token_required
def create_survey(current_user):
    data = request.get_json()
    survey = Survey(name=data['name'])
    questions = []
    for q in data['questions']:
        question = Question(text=q['text'])
        question.choices = [Choice(text=c['text']) for c in q['choices']]
        questions.append(question)
    survey.questions = questions
    survey.creator = current_user
    db.session.add(survey)
    db.session.commit()
    return jsonify(survey.to_dict()), 201


@api.route('/surveys', methods=('GET',))
def fetch_surveys():
    surveys = Survey.query.all()
    return jsonify({'surveys': [s.to_dict() for s in surveys]})


@api.route('/surveys/<int:id>/', methods=('GET', 'PUT'))
def survey(id):
    if request.method == 'GET':
        survey = Survey.query.get(id)
        return jsonify({'survey': survey.to_dict()})
    elif request.method == 'PUT':
        data = request.get_json()
        for q in data['questions']:
            choice = Choice.query.get(q['choice'])
            choice.selected = choice.selected + 1
        db.session.commit()
        survey = Survey.query.get(data['id'])
        return jsonify(survey.to_dict()), 201


@api.route('/register/', methods=('POST',))
def register():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@api.route('/login/', methods=('POST',))
def login():
    data = request.get_json()
    user = User.authenticate(**data)

    if not user:
        return jsonify({'message': 'Invalid credentials', 'authenticated': False}), 401

    token = jwt.encode({
        'sub': user.email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=30)},
        current_app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')})

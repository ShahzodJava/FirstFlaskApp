from flask import Flask, jsonify
from flask_cors import CORS

def create_app(test_config=None):
  app=Flask(__name__)

  @app.route('/')
  def hello():
    return jsonify({'message': 'HELLO WORLD'})

  @app.route('/smile')
  def smile():
    return ':)'

  return app
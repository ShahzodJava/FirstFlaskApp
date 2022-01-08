from sys import meta_path
from flask import Flask, jsonify, request, abort
from models import setup_db, Plant
from flask_cors import CORS

def paginate_plants(request,p):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * 5
  end = start + 5
  formatted_plants = [plant.format() for plant in p]
  current_plants = formatted_plants[start:end]
  return current_plants

def create_app(test_config=None):
  app=Flask(__name__)

  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/plants')
  def get_plants():
    p = Plant.query.order_by(Plant.id).all()
    current_plants = paginate_plants(request, p)

    if len(current_plants) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'plants': current_plants,
      'total_plants': len(Plant.query.all())
    })

  @app.route('/plants/<int:plant_id>', methods=['GET'])
  def get_plant(plant_id):
    plant = Plant.query.filter(Plant.id==plant_id).one_or_none()

    if plant is None:
      abort(404)
    else:
      return jsonify({
        'success':True,
        'plant': plant.format()

      })

  @app.route('/plants/<int:plant_id>', methods=['PATCH'])
  def update_plant(plant_id):
    body = request.get_json()

    try:
      plant = Plant.query.filter(Plant.id==plant_id).one_or_none()
      if plant is None:
        abort(404)

      if "is_poisonous" in body:
          plant.is_poisonous = body.get("is_poisonous")
      plant.update()

      return jsonify( { "success":True, "id":plant.id })
    except:
      abort(400)

  @app.route('/plants/<int:plant_id>', methods=['DELETE'])
  def delete_plant(plant_id):
    try:
      plant = Plant.query.filter(Plant.id==plant_id).one_or_none()
      if plant is None:
        abort(404)
      plant.delete()
      return jsonify({
        'success':True,
        "id":plant_id
      })
    except:
      abort(422)

  @app.route('/plants', methods=['POST'])
  def create_new_plant():
    body = request.get_json()
    name = body.get('name')
    scientific_name=body.get('scientific_name')
    is_poisonous = body.get('is_poisonous')
    primary_color = body.get('primary_color')
    try:

      plant = Plant(name=name, scientific_name=scientific_name, is_poisonous=is_poisonous,primary_color=primary_color)
      plant.insert()

      return jsonify({
        "success":True,
        "created":plant.id
      })
    except:
      abort(422)

  @app.errorhandler(404)
  def not_found(error):
    return (jsonify({
      "success":False,
      "error":404,
      "message":"resource not found"
    }), 404)

  @app.errorhandler(422)
  def unprocessable(error):
    return (jsonify({
      "success":False,
      "error":422,
      "message":"unprocessable"
    }), 422)

  @app.errorhandler(400)
  def bad_request(error):
    return (jsonify({
      "success":False,
      "error":400,
      "message":"bad request"
    }), 400)

  @app.errorhandler(405)
  def not_found(error):
    return (
      jsonify({"success": False, "error": 405, "message": "method not allowed"}),
      405,
    )


  return app
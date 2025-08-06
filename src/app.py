"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users, People, Planets, Favorites
from sqlalchemy import select
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = db.session.execute(select(Users)).scalars().all()
    results = [user.serialize() for user in all_users]
    

    response_body = {
        "msg": "ok",
        "results": results
    }

    return jsonify(response_body), 200 

@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = db.session.execute(select(Planets)).scalars().all()
    results = [planet.serialize() for planet in all_planets]
    

    response_body = {
        "msg": "ok",
        "results" : results
    }
    return jsonify(response_body), 200 

@app.route('/people', methods=['GET'])
def get_all_people():
    all_person = db.session.execute(select(People)).scalars().all()
    results = [person.serialize() for person in all_person]
    

    response_body = {
        "msg": "ok",
        "results": results
    }
    return jsonify(response_body), 200 

@app.route('/people/<int:id>', methods=['GET'])
def get_one_people(id):
    print(id)

    Person = db.session.get(People, id)

    if Person is None:
        return jsonify({"msg": "el personaje no existe"}) , 404

    response_body = {
        "msg": "ok",
        "result": Person.serialize()
    }
    return jsonify(response_body), 200 

@app.route('/planets/<int:id>', methods=['GET'])
def get_one_planet(id):
    print(id)
   
    planet = db.session.get(Planets, id)

    if planet is None:
        return jsonify({"msg": "el planeta no existe"}) , 404

    response_body = {
        "msg": "ok",
        "result": planet.serialize()
    }
    return jsonify(response_body), 200 

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def create_one_favorite_planet(planet_id):
    print(planet_id)
    request_body = request.json
    print(request_body) 

    n_favorites = Favorites(user_id = request_body["user_id"], people_id = None, planet_id = planet_id )
    db.session.add(n_favorites)
    db.session.commit()

    # if planet is None:
    #     return jsonify({"msg": "el planeta no existe"}) , 404

    response_body = {
         "msg": "ok",
        #"result": planet.serialize()
    }
    return jsonify(response_body), 200 

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def create_one_favorite_people(people_id):
    print(people_id)
    request_body = request.json
    print(request_body) 

    n_favorites = Favorites(user_id = request_body["user_id"], people_id = people_id, planet_id = None )
    db.session.add(n_favorites)
    db.session.commit()

    response_body = {
         "msg": "ok",
        
    }
    return jsonify(response_body), 200 


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_onefavorite_planet(planet_id):
    print(planet_id)

    # Busca el favorito que tenga ese planet_id
    fav_planet = db.session.execute(
        select(Favorites).where(Favorites.planet_id == planet_id)
    ).scalar_one_or_none()

    # Si no existe, devolvemos error 404
    if fav_planet is None:
        return jsonify({"msg": "favorito no encontrado"}), 404

    # Si existe, lo eliminamos
    db.session.delete(fav_planet)
    db.session.commit()
 
    response_body = {
        "msg": "favorito eliminado"
    }
    return jsonify(response_body), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_onefavorite_people(people_id):
    print(people_id)

    # Busca el favorito que tenga ese people_id
    fav_people = db.session.execute(
        select(Favorites).where(Favorites.people_id == people_id)
    ).scalar_one_or_none()

    # Si no existe, devolvemos error 404
    if fav_people is None:
        return jsonify({"msg": "favorito no encontrado"}), 404

    # Si existe, lo eliminamos
    db.session.delete(fav_people)
    db.session.commit()

    response_body = {
        "msg": "favorito eliminado"
    }
    return jsonify(response_body), 200


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    query_user= db.session.execute(select(Users).where(Users.email == email)).scalar_one_or_none()

    if query_user is None:
        return jsonify({"msg": "User not exist"}), 404
    
    if email != query_user.email or password != query_user.password:
        return jsonify({"msg": "Bad username or password"}),401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token), 200 

@app.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    # Validaciones básicas
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    # Verificar si el usuario ya existe
    existing_user = db.session.execute(
        select(Users).where(Users.email == email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({"msg": "User already exists"}), 409

    # Crear nuevo usuario
    new_user = Users(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/favorites", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    print(current_user)

    query_user= db.session.execute(select(Users).where(Users.email == current_user)).scalar_one_or_none()

    user_favorites = db.session.execute(select(Favorites).where(Favorites.user_id == query_user.id)).scalar_one_or_none()
    print(query_user)
    print(user_favorites)

    return jsonify(logged_in_as=current_user), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


@app.route("/")
def index():
    return "<h1>Welcome to the Pizza Code challenge</h1>"

# Route to retrieve all restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = db.session.query(Restaurant).all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200

# Route to retrieve a single restaurant by ID
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        return {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "pizza_id": rp.pizza_id,
                    "price": rp.price
                } for rp in restaurant.restaurant_pizzas
            ]
        }, 200
    return {"error": "Restaurant not found"}, 404

# Route to delete a restaurant by ID
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

# Route to retrieve all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas]), 200

# Route to create a restaurant pizza
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    # Ensure data contains necessary fields
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Validate price range
    if not 1 <= price <= 30:
        return jsonify({"errors": ["validation errors"]}), 400

    # Ensure pizza and restaurant exist
    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"error": "Pizza or Restaurant not found"}), 404

    # Create and save the restaurant_pizza entry
    restaurant_pizza = RestaurantPizza(
        price=price,
        pizza_id=pizza_id,
        restaurant_id=restaurant_id
    )
    db.session.add(restaurant_pizza)
    db.session.commit()

    # Return the restaurant pizza details
    return jsonify(restaurant_pizza.to_dict()), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)

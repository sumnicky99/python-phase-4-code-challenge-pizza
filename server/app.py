#!/usr/bin/env python3

# Import necessary modules
from models import db, Restaurant, RestaurantPizza, Pizza  
  # Import Flask-Migrate for database migrations
from flask_migrate import Migrate
 # Import Flask components
from flask import Flask, request, make_response 
# Import Flask-RESTful components
from flask_restful import Api, Resource  
import os

# Define base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
# Define database URI
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")  

# Initialize Flask application
app = Flask(__name__)  
# Configure database URI
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE  
# Disable track modifications
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  
 # Ensure JSON key order preservation
app.json.compact = False 

 # Initialize Flask-Migrate with app and db
migrate = Migrate(app, db) 

# Initialize SQLAlchemy with app context
db.init_app(app)  
# Initialize Flask-RESTful API
api = Api(app)  

# Define route for root endpoint
@app.route("/")  
def index():
    return "<h1>Code challenge</h1>"

 # Resource for handling all restaurants
class Restaurants(Resource): 
    def get(self):
        all_restaurants = []  # Initialize list for all restaurants
        for restaurant in Restaurant.query.all():
            # Convert to dict, exclude 'restaurant_pizzas'
            all_restaurants.append(restaurant.to_dict(rules=('-restaurant_pizzas',)))  
        # Return response with all restaurants
        return make_response(all_restaurants)  

# Register Restaurants resource with endpoint '/restaurants'
api.add_resource(Restaurants, '/restaurants')  


# Resource for handling a specific restaurant by ID
class RestaurantById(Resource):  
    def get(self, id):
        # Retrieve restaurant by ID
        restaurant = db.session.get(Restaurant, id)  
        if restaurant:
        # Return restaurant as JSON response
            return make_response(restaurant.to_dict())  
        else:
            return make_response({"error": "Restaurant not found"}, 404)  # Return error if restaurant not found

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id) 
         # Retrieve restaurant by ID
        if restaurant:
            db.session.delete(restaurant)  # Delete restaurant
            db.session.commit()  # Commit transaction
            return make_response({"": ""}, 204)  # Return successful deletion response
        else:
            return make_response({"error": "Restaurant not found"}, 404)  # Return error if restaurant not found

class Pizzas(Resource): 
     # Resource for handling all pizzas
    def get(self):
        all_pizzas = []  
        # Initialize list for all pizzas
        for pizza in Pizza.query.all():
            # Convert to dict, exclude 'joined_relationship'
            all_pizzas.append(pizza.to_dict(rules=('-joined_relationship',)))  
        return make_response(all_pizzas)  # Return response with all pizzas

class MakeRestaurantPizza(Resource):  
    # Resource for creating a new RestaurantPizza
    def post(self):
        try:
            new_pizza = RestaurantPizza( 
                 # Create new RestaurantPizza object
                price=request.json['price'],
                pizza_id=request.json['pizza_id'],
                restaurant_id=request.json['restaurant_id']
            )
             # Add new RestaurantPizza to session
            db.session.add(new_pizza) 
            # Commit transaction
            db.session.commit()  
            # Return newly created object as JSON response
            return make_response(new_pizza.to_dict(), 201)  
        except ValueError:
            # Handle validation errors
            return make_response({"errors": ["validation errors"]}, 400)  

# Register MakeRestaurantPizza resource with endpoint '/restaurant_pizzas'
api.add_resource(MakeRestaurantPizza, '/restaurant_pizzas')  
 # Register Pizzas resource with endpoint '/pizzas'
api.add_resource(Pizzas, '/pizzas') 
 # Register RestaurantById resource with endpoint '/restaurants/<id>'
api.add_resource(RestaurantById, '/restaurants/<int:id>') 


if __name__ == "__main__":
   # Run Flask application on port 5555 in debug mode
    app.run(port=5555, debug=True)  
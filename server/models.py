from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Define custom metadata with naming conventions
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)


# Restaurant model representing restaurants table
class Restaurant(db.Model, SerializerMixin):
    """Restaurant model representing restaurants table."""

    __tablename__ = "restaurants"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationships
    # One-to-many relationship with RestaurantPizza table
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    # Proxy association to access pizzas through restaurant_pizzas
    pizzas = association_proxy('restaurant_pizzas', 'pizza')
    
    # Serialization rules
    # Exclude nested 'restaurant_pizzas.restaurant' field from serialization
    serialize_rules = ('-restaurant_pizzas.restaurant',)

    def __repr__(self):
        """String representation of Restaurant object."""
        return f"<Restaurant {self.name}>"


# Pizza model representing pizzas table
class Pizza(db.Model, SerializerMixin):
    """Pizza model representing pizzas table."""

    __tablename__ = "pizzas"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationships
    # One-to-many relationship with RestaurantPizza table
    joined_relationship = db.relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')
    # Proxy association to access restaurants through joined_relationship
    restaurants = association_proxy('joined_relationship', 'restaurant')
    
    # Serialization rules
    # Exclude nested 'joined_relationship.pizza' field from serialization
    serialize_rules = ('-joined_relationship.pizza',)

    def __repr__(self):
        """String representation of Pizza object."""
        return f"<Pizza {self.name}, {self.ingredients}>"


# RestaurantPizza model representing restaurant_pizzas table
class RestaurantPizza(db.Model, SerializerMixin):
    """RestaurantPizza model representing restaurant_pizzas table."""

    __tablename__ = "restaurant_pizzas"

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # Relationships
    # Many-to-one relationship with Pizza table
    pizza = db.relationship('Pizza', back_populates='joined_relationship')
    # Many-to-one relationship with Restaurant table
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    
    # Serialization rules
    # Exclude nested 'pizza.joined_relationship' and 'restaurant.restaurant_pizzas' fields from serialization
    serialize_rules = ('-pizza.joined_relationship', '-restaurant.restaurant_pizzas')

    # Validation
    @validates('price')
    def validate_price(self, key, price):
        """Validator for price field."""
        if 1 <= price <= 30:
            return price
        else:
            raise ValueError("Price must be between 1 and 30")

    def __repr__(self):
        """String representation of RestaurantPizza object."""
        return f"<RestaurantPizza ${self.price}>"

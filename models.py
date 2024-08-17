from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Cuisine(db.Model):
    __tablename__ = 'cuisines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<Cuisine {self.name}>'

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('recipes', lazy=True))
    cuisine_id = db.Column(db.Integer, db.ForeignKey('cuisines.id'), nullable=True)
    cuisine = db.relationship('Cuisine', backref=db.backref('recipes', lazy=True))
    difficulty = db.Column(db.String(20), nullable=False, default='medium')
    
    # New fields
    calories = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fat = db.Column(db.Float, nullable=True)
    prep_time = db.Column(db.Integer, nullable=True)  # in minutes
    cook_time = db.Column(db.Integer, nullable=True)  # in minutes
    total_time = db.Column(db.Integer, nullable=True)  # in minutes
    cooking_method = db.Column(db.String(50), nullable=True)
    servings = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    rating_count = db.Column(db.Integer, default=0)

    categories = db.relationship('Category', secondary='recipe_categories', backref=db.backref('recipes_multi', lazy='dynamic'))

    def __repr__(self):
        return f'<Recipe {self.title}>'

# New association table for multiple categories
recipe_categories = db.Table('recipe_categories',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)
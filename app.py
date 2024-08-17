from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from models import db, Recipe, Category
from config import Config
import logging
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    try:
        recipes = Recipe.query.all()
        categories = Category.query.all()
        return render_template('index.html', recipes=recipes, categories=categories)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        flash("An error occurred while fetching recipes. Please try again later.", "error")
        return render_template('index.html', recipes=[], categories=[])

@app.route('/recipe/<int:id>')
def recipe(id):
    try:
        recipe = Recipe.query.get_or_404(id)
        return render_template('recipe.html', recipe=recipe)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        flash("An error occurred while fetching the recipe. Please try again later.", "error")
        return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            image = request.files['image']
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
            else:
                image_path = None

            new_recipe = Recipe(
                title=request.form['title'],
                description=request.form['description'],
                ingredients=request.form['ingredients'],
                instructions=request.form['instructions'],
                source=request.form['source'],
                image=image_path,
                category_id=request.form['category']
            )
            db.session.add(new_recipe)
            db.session.commit()
            flash('Recipe added successfully!', 'success')
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            flash("An error occurred while adding the recipe. Please try again.", "error")
    return render_template('add_recipe.html', categories=categories)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            recipe.title = request.form['title']
            recipe.description = request.form['description']
            recipe.ingredients = request.form['ingredients']
            recipe.instructions = request.form['instructions']
            recipe.source = request.form['source']
            
            # Handle category_id
            category_id = request.form['category']
            if category_id:
                recipe.category_id = int(category_id)
            else:
                recipe.category_id = None  # Set to NULL if no category is selected

            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                recipe.image = filename

            db.session.commit()
            flash('Recipe updated successfully!', 'success')
            return redirect(url_for('recipe', id=recipe.id))
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            flash("An error occurred while updating the recipe. Please try again.", "error")
    return render_template('edit_recipe.html', recipe=recipe, categories=categories)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    try:
        db.session.delete(recipe)
        db.session.commit()
        flash('Recipe deleted successfully!', 'success')
        return redirect(url_for('index'))
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.session.rollback()
        flash("An error occurred while deleting the recipe. Please try again.", "error")
        return redirect(url_for('recipe', id=id))

@app.route('/category/<int:id>')
def category(id):
    try:
        category = Category.query.get_or_404(id)
        return render_template('category.html', category=category)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        flash("An error occurred while fetching the category. Please try again later.", "error")
        return redirect(url_for('index'))

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        try:
            new_category = Category(name=request.form['name'])
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            flash("An error occurred while adding the category. Please try again.", "error")
    return render_template('add_category.html')

@app.route('/search')
def search():
    query = request.args.get('query', '')
    category_id = request.args.get('category', '')
    
    recipes = Recipe.query
    
    if query:
        recipes = recipes.filter(or_(Recipe.title.ilike(f'%{query}%'), Recipe.description.ilike(f'%{query}%')))
    
    if category_id:
        recipes = recipes.filter(Recipe.category_id == category_id)
    
    recipes = recipes.all()
    
    return jsonify([{
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description if recipe.description else 'No description available.',
        'image': recipe.image
    } for recipe in recipes])

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)  # Modify the port if needed
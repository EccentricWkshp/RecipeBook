from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from models import db, Recipe, Category, Cuisine
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
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', '')
    difficulty = request.args.get('difficulty', '')

    try:
        query = Recipe.query

        if search:
            query = query.filter(or_(Recipe.title.ilike(f'%{search}%'), Recipe.description.ilike(f'%{search}%')))
        
        if category_id:
            query = query.filter(Recipe.category_id == category_id)
        
        if difficulty:
            query = query.filter(Recipe.difficulty == difficulty)

        # Add an order_by clause to fix the MSSQL pagination issue
        query = query.order_by(Recipe.id)

        recipes = query.paginate(page=page, per_page=9, error_out=False)
        categories = Category.query.all()
        return render_template('index.html', recipes=recipes, categories=categories)
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        flash("An error occurred while fetching recipes. Please try again later.", "error")
        # Create an empty list to avoid the 'list' object has no attribute 'iter_pages' error
        empty_recipes = []
        return render_template('index.html', recipes=empty_recipes, categories=[])

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
    cuisines = Cuisine.query.all()
    if request.method == 'POST':
        try:
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
            else:
                image_path = None

            category_ids = request.form.getlist('categories')
            cuisine_id = request.form.get('cuisine')
            if cuisine_id == '':
                cuisine_id = None

            new_recipe = Recipe(
                title=request.form['title'],
                description=request.form.get('description', ''),
                ingredients=request.form.get('ingredients', ''),
                instructions=request.form.get('instructions', ''),
                prep_time=request.form.get('prep_time', type=int),
                cook_time=request.form.get('cook_time', type=int),
                total_time=request.form.get('total_time', type=int),
                servings=request.form.get('servings', type=int),
                cooking_method=request.form.get('cooking_method', ''),
                calories=request.form.get('calories', type=int),
                protein=request.form.get('protein', type=float),
                carbs=request.form.get('carbs', type=float),
                fat=request.form.get('fat', type=float),
                source=request.form.get('source', ''),
                image=image_path,
                cuisine_id=cuisine_id,
                difficulty=request.form.get('difficulty', ''),
                notes=request.form.get('notes', '')
            )

            for category_id in category_ids:
                category = Category.query.get(category_id)
                if category:
                    new_recipe.categories.append(category)

            db.session.add(new_recipe)
            db.session.commit()
            flash('Recipe added successfully!', 'success')
            return redirect(url_for('index'))
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            flash("An error occurred while adding the recipe. Please try again.", "error")
    return render_template('add_recipe.html', categories=categories, cuisines=cuisines)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    categories = Category.query.all()
    cuisines = Cuisine.query.all()
    if request.method == 'POST':
        try:
            recipe.title = request.form['title']
            recipe.description = request.form.get('description', '')
            recipe.ingredients = request.form.get('ingredients', '')
            recipe.instructions = request.form.get('instructions', '')
            recipe.prep_time = request.form.get('prep_time', type=int)
            recipe.cook_time = request.form.get('cook_time', type=int)
            recipe.total_time = request.form.get('total_time', type=int)
            recipe.servings = request.form.get('servings', type=int)
            recipe.cooking_method = request.form.get('cooking_method', '')
            recipe.calories = request.form.get('calories', type=int)
            recipe.protein = request.form.get('protein', type=float)
            recipe.carbs = request.form.get('carbs', type=float)
            recipe.fat = request.form.get('fat', type=float)
            recipe.source = request.form.get('source', '')
            recipe.difficulty = request.form.get('difficulty', '')
            recipe.notes = request.form.get('notes', '')
            
            category_ids = request.form.getlist('categories')
            recipe.categories = []
            for category_id in category_ids:
                category = Category.query.get(category_id)
                if category:
                    recipe.categories.append(category)

            cuisine_id = request.form.get('cuisine')
            if cuisine_id == '':
                recipe.cuisine_id = None
            else:
                recipe.cuisine_id = int(cuisine_id)

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
    return render_template('edit_recipe.html', recipe=recipe, categories=categories, cuisines=cuisines)

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

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        try:
            new_category = Category(name=request.form['name'])
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('add_category'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while adding the category. Please try again.", "error")
    
    categories = Category.query.all()
    return render_template('add_category.html', categories=categories)

@app.route('/edit_category/<int:id>', methods=['POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        try:
            category.name = request.form['name']
            db.session.commit()
            flash('Category updated successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while updating the category. Please try again.", "error")
    return redirect(url_for('add_category'))

@app.route('/delete_category/<int:id>', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("An error occurred while deleting the category. Please try again.", "error")
    return redirect(url_for('add_category'))

@app.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    recipes = Recipe.query.filter_by(category_id=id).all()
    return render_template('category.html', category=category, recipes=recipes)

@app.route('/add_cuisine', methods=['GET', 'POST'])
def add_cuisine():
    if request.method == 'POST':
        try:
            new_cuisine = Cuisine(name=request.form['name'])
            db.session.add(new_cuisine)
            db.session.commit()
            flash('Cuisine added successfully!', 'success')
            return redirect(url_for('add_cuisine'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while adding the cuisine. Please try again.", "error")
    
    cuisines = Cuisine.query.all()
    return render_template('add_cuisine.html', cuisines=cuisines)

@app.route('/edit_cuisine/<int:id>', methods=['POST'])
def edit_cuisine(id):
    cuisine = Cuisine.query.get_or_404(id)
    if request.method == 'POST':
        try:
            cuisine.name = request.form['name']
            db.session.commit()
            flash('Cuisine updated successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("An error occurred while updating the cuisine. Please try again.", "error")
    return redirect(url_for('add_cuisine'))

@app.route('/delete_cuisine/<int:id>', methods=['POST'])
def delete_cuisine(id):
    cuisine = Cuisine.query.get_or_404(id)
    try:
        db.session.delete(cuisine)
        db.session.commit()
        flash('Cuisine deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("An error occurred while deleting the cuisine. Please try again.", "error")
    return redirect(url_for('add_cuisine'))

@app.route('/cuisine/<int:id>')
def cuisine(id):
    cuisine = Cuisine.query.get_or_404(id)
    recipes = Recipe.query.filter_by(cuisine_id=id).all()
    return render_template('cuisine.html', cuisine=cuisine, recipes=recipes)

@app.route('/rate/<int:id>', methods=['POST'])
def rate_recipe(id):
    recipe = Recipe.query.get_or_404(id)
    data = request.json
    new_rating = data.get('rating')
    
    if new_rating is not None:
        try:
            new_rating = float(new_rating)
            if 1 <= new_rating <= 5:
                if recipe.rating is None:
                    recipe.rating = new_rating
                    recipe.rating_count = 1
                else:
                    total_rating = recipe.rating * recipe.rating_count
                    recipe.rating_count += 1
                    recipe.rating = (total_rating + new_rating) / recipe.rating_count
                
                db.session.commit()
                return jsonify({'success': True, 'new_average': recipe.rating})
            else:
                return jsonify({'success': False, 'error': 'Invalid rating value'}), 400
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid rating format'}), 400
    else:
        return jsonify({'success': False, 'error': 'No rating provided'}), 400

@app.route('/search')
def search():
    query = request.args.get('query', '')
    category_id = request.args.get('category', '')
    difficulty = request.args.get('difficulty', '')
    
    recipes = Recipe.query
    
    if query:
        recipes = recipes.filter(or_(Recipe.title.ilike(f'%{query}%'), Recipe.description.ilike(f'%{query}%')))
    
    if category_id:
        recipes = recipes.filter(Recipe.category_id == category_id)
    
    if difficulty:
        recipes = recipes.filter(Recipe.difficulty == difficulty)
    
    recipes = recipes.all()
    
    return jsonify([{
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description if recipe.description else 'No description available.',
        'image': recipe.image,
        'difficulty': recipe.difficulty
    } for recipe in recipes])

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
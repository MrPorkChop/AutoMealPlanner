from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('Recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recipes')
    recipes = c.fetchall()
    conn.close()
    
    return render_template_string('''
        <h1>Recipes</h1>
        <ul>
            {% for recipe in recipes %}
                <li>
                    <strong>{{ recipe[1] }}</strong> - <a href="{{ recipe[2] }}">{{ recipe[2] }}</a><br>
                    Ingredients: {{ recipe[3] }}<br>
                    <form method="POST" action="/delete_recipe/{{ recipe[0] }}">
                        <input type="submit" value="Delete">
                    </form>
                </li>
            {% endfor %}
        </ul>
        
        <h2>Add Recipe</h2>
        <form method="POST" action="/add_recipe">
            Title: <input type="text" name="title"><br>
            URL: <input type="text" name="url"><br>
            Ingredients (comma separated): <input type="text" name="ingredients"><br>
            <input type="submit" value="Add Recipe">
        </form>
        
        <h2>Generate Meal Plan</h2>
        <form method="POST" action="/generate_meal_plan">
            Days: <input type="number" name="days"><br>
            People: <input type="number" name="people"><br>
            <input type="submit" value="Generate">
        </form>
    ''', recipes=recipes)

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('Recipes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            ingredients TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Route to handle recipe deletion
@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    conn = sqlite3.connect('Recipes.db')
    c = conn.cursor()
    c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    title = request.form['title']
    url = request.form['url']
    ingredients = request.form['ingredients']
    conn = sqlite3.connect('Recipes.db')
    c = conn.cursor()
    c.execute('INSERT INTO recipes (title, url, ingredients) VALUES (?, ?, ?)', (title, url, ingredients))
    conn.commit()
    conn.close()
    return 'Recipe added!'

@app.route('/generate_meal_plan', methods=['POST'])
def generate_meal_plan():
    days = int(request.form['days'])
    people = int(request.form['people'])
    conn = sqlite3.connect('Recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recipes ORDER BY RANDOM() LIMIT ?', (days,))
    meals = c.fetchall()
    conn.close()

    meal_plan = []
    grocery_list = {}

    for meal in meals:
        meal_plan.append({'title': meal[1], 'url': meal[2]})
        ingredients = meal[3].split(', ')
        for ingredient in ingredients:
            if ingredient in grocery_list:
                grocery_list[ingredient] += people
            else:
                grocery_list[ingredient] = people

    return render_template_string('''
        <h1>Meal Plan</h1>
        <ul>
            {% for meal in meal_plan %}
                <li><a href="{{ meal.url }}">{{ meal.title }}</a></li>
            {% endfor %}
        </ul>
        <h2>Grocery List</h2>
        <ul>
            {% for ingredient, amount in grocery_list.items() %}
                <li>{{ ingredient }}: {{ amount }}</li>
            {% endfor %}
        </ul>
    ''', meal_plan=meal_plan, grocery_list=grocery_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000, ssl_context=("cert.pem", "key.pem"))


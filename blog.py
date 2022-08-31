import os
import sys
import sqlite3

if len(sys.argv) > 1:
    db_name = sys.argv[1]
else:
    db_name = 'food_blog.db'

if os.path.exists(db_name):
    os.remove(db_name)

con = sqlite3.connect(db_name)

# Create tables
meal_query = """
create table if not exists meals (
meal_id integer primary key, 
meal_name text not null unique);
"""

ing_query = """
create table if not exists ingredients (
ingredient_id integer primary key,
ingredient_name text not null unique);
"""

meas_query = """
create table if not exists measures (
measure_id integer primary key,
measure_name text unique);
"""

rec_query = """
create table if not exists recipes (
recipe_id integer primary key,
recipe_name text not null,
recipe_description text);
"""

ser_query = """
create table if not exists serve (
serve_id integer primary key,
recipe_id integer not null,
meal_id integer not null,
foreign key(recipe_id) references recipes(recipe_id),
foreign key(meal_id) references meals(meal_id));
"""

con.execute("pragma foreign_keys = on;")
con.execute(meal_query)
con.execute(ing_query)
con.execute(meas_query)
con.execute(rec_query)
con.execute(ser_query)

con.commit()


def stage1(_con):
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    for table, elements in data.items():
        sql_query = f"insert into {table} ({table[:-1]}_name)  values (?);"
        _con.executemany(sql_query, ((element, ) for element in elements))

    _con.commit()
    print("Tables were created!")


def stage2(_con):
    print("Pass the empty recipe name to exit.")
    while name := input("Recipe name: "):
        description = input("Recipe description: ")
        sql_query = "insert into recipes (recipe_name, recipe_description) values (?, ?);"
        _con.execute(sql_query, (name, description))
    _con.commit()
    print("Recipes were added!")


def stage3(_con):
    print("Pass the empty recipe name to exit.")
    while name := input("Recipe name: "):
        description = input("Recipe description: ")
        meals = _con.execute("select * from meals;").fetchall()
        print(" ".join(f"{meal[0]}) {meal[1]}" for meal in meals))
        try:
            nums = [int(n) for n in input("When the dish can be served: ").split(" ")]
            last_id = _con.execute("insert into recipes(recipe_name, recipe_description) values (?, ?);", (name, description)).lastrowid
            for num in nums:
                _con.execute("insert into serve (recipe_id, meal_id) values (?, ?);", (last_id, num))
        except ValueError:
            print("Enter integers separated by a space.")
    _con.commit()
    print("Recipes were added!")


stage1(con)
stage3(con)
con.close()


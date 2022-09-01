import os
import sys
import sqlite3
import argparse


parser = argparse.ArgumentParser(description="This program deals with recipes.")

parser.add_argument('database', nargs=1, default="")
parser.add_argument('--ingredients', default="")
parser.add_argument('--meals', default="")

args = parser.parse_args()


if len(sys.argv) > 1:
    db_name = args.database[0]
else:
    db_name = 'food_blog.db'

# if os.path.exists(db_name):
#     os.remove(db_name)

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

quan_query = """
create table if not exists quantity (
quantity_id integer primary key,
measure_id integer not null,
ingredient_id integer not null,
quantity integer not null,
recipe_id integer not null,
foreign key (measure_id) references measures (measure_id),
foreign key (ingredient_id) references ingredients (ingredient_id),
foreign key (recipe_id) references recipes (recipe_id));
"""

con.execute("pragma foreign_keys = on;")
con.execute(meal_query)
con.execute(ing_query)
con.execute(meas_query)
con.execute(rec_query)
con.execute(ser_query)
con.execute(quan_query)

con.commit()


def stage1(_con):
    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}
    try:
        for table, elements in data.items():
            sql_query = f"insert into {table} ({table[:-1]}_name)  values (?);"
            _con.executemany(sql_query, ((element, ) for element in elements))

        _con.commit()
        print("Tables were created!")
    except sqlite3.IntegrityError:
        pass


def stage4(_con):
    print("Pass the empty recipe name to exit.")
    while name := input("Recipe name: "):
        description = input("Recipe description: ")
        meals = _con.execute("select * from meals;").fetchall()
        print(" ".join(f"{meal[0]}) {meal[1]}" for meal in meals))
        try:
            nums = [int(n) for n in input("Enter proposed meals separated by a space: ").split(" ")]
            recipe_id = _con.execute("insert into recipes(recipe_name, recipe_description) values (?, ?);", (name, description)).lastrowid
            for num in nums:
                _con.execute("insert into serve (recipe_id, meal_id) values (?, ?);", (recipe_id, num))
            while quantities := (input("Input quantity of ingredient <press enter to stop>: ").split()):
                if len(quantities) == 3:
                    [quantity, measure, ingredient] = quantities
                elif len(quantities) == 2:
                    [quantity, ingredient], measure = quantities, ""
                else:
                    continue
                if measure:
                    measure = f"%{measure}%"
                measure_id = _con.execute(f"select measure_id from measures where measure_name like '{measure}';").fetchall()
                if len(measure_id) > 1:
                    print("The measure is not conclusive!")
                    continue
                measure_id = measure_id[0][0]
                ingredient_id = _con.execute(f"select ingredient_id from ingredients where ingredient_name like '%{ingredient}%';").fetchall()
                if len(ingredient_id) > 1:
                    print("The ingredient is not conclusive!")
                    continue
                ingredient_id = ingredient_id[0][0]

                _con.execute("insert into quantity (quantity, recipe_id, measure_id, ingredient_id) values (?, ?, ?, ?)", (quantity, recipe_id, measure_id, ingredient_id))

        except ValueError:
            print("Enter integers separated by a space.")
    _con.commit()
    print("Recipes were added!")


def get_name_id(_con, col, value):
    id = _con.execute(f"select {col}_id from {col}s where {col}_name = '{value}';").fetchone()
    return id[0]


def stage5(_con):
    ingredients = args.ingredients.split(",")
    ing_names = ",".join(f"'{ingredient}'" for ingredient in ingredients)

    meals = args.meals.split(",")
    meal_names = ",".join(f"'{meal}'" for meal in meals)

    def get_base_query(ingredient):
        return f"""select q.recipe_id as recipe_id
        from ingredients i
        join quantity q on q.ingredient_id = i.ingredient_id
        where i.ingredient_name = '{ingredient}'\n
        """

    ing_table = "INTERSECT\n".join(get_base_query(ingredient) for ingredient in ingredients)

    meal_table = f"""select s.recipe_id as recipe_id, r.recipe_name
        from serve s
        join meals m on m.meal_id = s.meal_id
        join recipes r on r.recipe_id = s.recipe_id
        where m.meal_name in ({meal_names})
    """
    sql_query = f"""select recipe_name
    from (
    {ing_table}) ing
    join (
    {meal_table}
    ) me on ing.recipe_id = me.recipe_id;
    """
    rec_names = _con.execute(sql_query).fetchall()
    if rec_names:
        print(f"Recipes selected for you: {', '.join(x[0] for x in rec_names)}")
    else:
        print("There are no such recipes in the database.")


stage1(con)

if args.ingredients and args.meals:
    stage5(con) 
else:
    stage4(con)

con.close()

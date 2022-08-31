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
cursor = con.cursor()

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
measure_name text unique
);
"""

cursor.execute(meal_query)
cursor.execute(ing_query)
cursor.execute(meas_query)

con.commit()

data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

for table, elements in data.items():
    sql_query = f"insert into {table} ({table[:-1]}_name)  values (?);"
    cursor.executemany(sql_query, ((element, ) for element in elements))

con.commit()
cursor.close()
con.close()

print("Tables were created!")

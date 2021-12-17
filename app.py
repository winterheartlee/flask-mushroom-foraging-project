import os
import json
import sys
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, request, jsonify)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/map")
def map():
    mushrooms = list(mongo.db.mushrooms.find())
    locations = list(mongo.db.locations.find())

    locations_maps_array = []
    for location in locations:
        name = location.get('name')
        lat = location.get('lat')
        lng = location.get('lng')
        id = location.get('_id')
        locations_maps_array.append([name, lat, lng, id])

    return render_template("map.html", locations=locations, locations_maps_array=locations_maps_array, mushrooms=mushrooms)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    return redirect(url_for("map", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_mushroom", methods=["GET", "POST"])
def add_mushroom():
    if request.method == "POST":
        mushroom = {
            "name": request.form.get("name"),
            "image_url": request.form.get("image_url"),
            "description": request.form.get("description"),
            "edible": request.form.get("edible"),
            "fruiting": request.form.get("fruiting"),
            "created_by": session["user"]
        }
        mongo.db.mushrooms.insert_one(mushroom)
        flash("Mushroom Successfully Added")
        return redirect(url_for("add_mushroom"))

    return render_template("add_mushroom.html")


@app.route("/edit_mushroom/<mushroom_id>", methods=["GET", "POST"])
def edit_mushroom(mushroom_id):
    if request.method == "POST":
        submit = {
            "name": request.form.get("name"),
            "image_url": request.form.get("image_url"),
            "description": request.form.get("description"),
            "edible": request.form.get("edible"),
            "fruiting": request.form.get("fruiting"),
            "created_by": session["user"]
        }
        mongo.db.mushrooms.update({"_id": ObjectId(mushroom_id)}, submit)
        flash("Mushroom Successfully Edited")

    mushroom = mongo.db.mushrooms.find_one({"_id": ObjectId(mushroom_id)})
    return render_template("edit_mushroom.html", mushroom=mushroom)


@app.route("/delete_mushroom/<mushroom_id>")
def delete_mushroom(mushroom_id):
    mongo.db.mushrooms.remove({"_id": ObjectId(mushroom_id)})
    flash("Entry Successfully Deleted")
    return redirect(url_for("map"))


@app.route('/_get_post_json/', methods=['POST'])
def get_post_json():    
    data = request.get_json()
    return jsonify(status="success", data=data)
    return render_template("test.html", data=data)



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)
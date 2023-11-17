import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
ckeditor = CKEditor(app)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home_page")
def home_page():
    return render_template("home.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists", 'error')
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!", 'success')
        return redirect(url_for("your_archive", username=session["user"]))

    return render_template("register.html")


@app.route("/your_archive")
def your_archive():
    archive = list(mongo.db.main.find())
    return render_template("your_archive.html", archive=archive)


@app.route("/detailed_view/<item_id>")
def detailed_view(item_id):

    archive = mongo.db.main.find_one({"_id": ObjectId(item_id)})
    return render_template("detailed_view.html", archive=archive)


@app.route("/add_archive", methods=["GET", "POST"])
def add_archive():
    if request.method == "POST":
        archive = {
            "category_name": request.form.get("category_name"),
            "ref_title": request.form.get("ref_title"),
            "ref_source": request.form.get("ref_source"),
            "ref_link": request.form.get("ref_link"),
            "ref_content": request.form.get("ckeditor"),
            "ref_reason": request.form.get("ref_reason"),
            "ref_importance": request.form.get("ref_importance"),
            "created_by": session["user"]
        }
        mongo.db.main.insert_one(archive)
        flash("Successfully Added To Your RefArchive", 'success')
        return redirect(url_for("your_archive"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_archive.html", categories=categories)


@app.route("/edit_archive/<item_id>", methods=["GET", "POST"])
def edit_archive(item_id):
    if request.method == "POST":
        archive = {"$set":{
            "category_name": request.form.get("category_name"),
            "ref_title": request.form.get("ref_title"),
            "ref_source": request.form.get("ref_source"),
            "ref_link": request.form.get("ref_link"),
            "ref_content": request.form.get("ckeditor"),
            "ref_reason": request.form.get("ref_reason"),
            "ref_importance": request.form.get("ref_importance"),
            "created_by": session["user"]
        }}
        mongo.db.main.update_one(archive)
        flash("Successfully Updated To Your RefArchive", 'success')
        return redirect(url_for("your_archive"))

    archive = mongo.db.main.find_one({"_id": ObjectId(item_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_archive.html", archive=archive, categories=categories)


@app.route("/delete_archive/<item_id>")
def delete_archive(item_id):
    mongo.db.main.delete_one({"_id": ObjectId(item_id)})
    flash("Item Successfully Deleted", 'success')
    return redirect(url_for("your_archive"))


@app.route("/logout")
def logout():
    # remove user form session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")), 'success')
                    return redirect(url_for(
                        "your_archive", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password", 'error')
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password", 'error')
            return redirect(url_for("login"))
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

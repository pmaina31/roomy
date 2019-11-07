import os
from datetime import date

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///roomy.db")

@app.route("/")
@login_required
def index():

    #list all available listings

    avail_listings = db.execute("SELECT address, roomsize, rentperday, propertydescription, status, roompicture from listings WHERE status = 0 ORDER BY address ASC")

   # pull stock details and sum stock totals including cash
    for listing in avail_listings:
        address = str(listing["address"])
        roomsize = float(listing["roomsize"])
        rentperday = float(listing["rentperday"])
        propertydescription = str(listing["propertydescription"])
        roompicture = str(listing["roompicture"])

    # render index page with some given values
    return render_template("avail_listings.html", avail_listings = avail_listings)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # clear existing user
    session.clear()

    if request.method == "POST":

        # Submit username
        if not request.form.get("emailaddress"):
            return apology("must provide email address")

        # Submit password
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        users = db.execute("SELECT * FROM users WHERE emailaddress = :emailaddress",
                          emailaddress=request.form.get("emailaddress"))

        # Ensure user exists
        if len(users) != 1 or not check_password_hash(users[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # remember user
        session["user_email"] = users[0]["emailaddress"]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget user
    session.clear()

    # Redirect user to login form
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    # user reached by POST
    if request.method == "POST":

        # return apology if username not provided
        if not request.form.get("emailaddress"):
            return apology("Kindly provide username")

       # return apology if password not provided
        elif not request.form.get("password"):
            return apology("Kindly provide password")

       # return apology if confirmation not provided
        elif not request.form.get("confirmation"):
            return apology("Kindly confirm your password")

       # return apology if passwords do not match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        elif not request.form.get("telephonenumber"):
            return apology("Kindly provide phone number")

        # generate hash password
        hash = generate_password_hash(request.form.get("password"))

        isadmin = 0

        # add new user
        newuser = db.execute("INSERT INTO users (email_address, hash, telephone_number, is_admin) VALUES(:emailaddress, :hash, :telephonenumber, :isadmin)",emailaddress=request.form.get("emailaddress"),hash=hash,telephonenumber=request.form.get("telephonenumber"),isadmin=isadmin)

        # if not a new trader
        if not newuser:
            return apology("email address already on file")

        # Remember who is logged in
        session["user_email"] = newuser

        # Display a flash message
        flash("Registered!")

        return redirect(url_for("index"))

    else:
        return render_template("register.html")

@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():

    if request.method == "POST":

        if not request.form.get("address"):
            return apology("Select desired location")

        elif not request.form.get("checkin"):
            return apology("Select desired Check in date")

        elif not request.form.get("checkout"):
            return apology("Select desired Check out date")

        elif not request.form.get("delta"):
            return apology("Select desired Check out date")


        rentperday = db.execute("SELECT rentperday FROM listings WHERE address= :address", address=request.form.get("address"))
        rentperday = rentperday[0]["rentperday"]

        delta = request.form.get("delta")



        #get delta days user.form

        total = delta * rentperday
        status = 1

        db.execute("UPDATE listings SET status=status WHERE address = :address", address=request.form.get("address"))

        db.execute("INSERT INTO bookings (emailaddress, address, checkin, checkout, rentperday, total) VALUES (:emailaddress, :address, :checkin, :checkout, :rentperday, :total)",
        emailaddress=session["user_email"],
        address=request.form.get("address"),
        rentperday=rentperday,
        checkin=request.form.get("checkin"),
        checkout=request.form.get("checkout"),
        total=total)

        flash("You are booked")

        return redirect(url_for("index"))

    else:
            avail_listings = db.execute("SELECT address FROM listings WHERE status = 0 ORDER BY address ASC")

            return render_template("booking.html", avail_listings = avail_listings)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)























import os

from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request, session, flash, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Here add the from weather import fuctions that gets the data from the API
from weather import lookup, login_required, today_date

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = "thisisasecret"

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///weather.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods = ['GET', 'POST'])
@login_required
def index():

    if request.method == "POST":
        # call function to get the API DATA.
        city = request.form.get("city")
        
        if not city:
            
            flash('Insert City', 'error')
            return redirect(url_for('index'))
            
        weather = lookup(city)
        
        # check if city exists.
        if weather['city'] == "Not Found":
            
            flash('City Not Found', 'error')
            return redirect(url_for('index'))
        
            
        date = today_date()

        # Query the data from citys.
        citys_db = db.execute("SELECT * FROM weather_data WHERE city = :city AND user_id = :user_id", city = city, user_id = session["user_id"])

        # Check if city already exists in database.
        if len(citys_db) == 0:
            flash('Inserted City', 'sucess')
            db.execute("INSERT INTO weather_data(city, country, temperature, description, humidity, wind, icon, user_id, date) VALUES(:city, :country, :temperature, :description, :humidity, :wind, :icon, :user_id, :date)", city = weather['city'], country = weather['country'], temperature = weather['temperature'], description = weather['description'], humidity = weather['humidity'], wind = weather['wind'], icon = weather['icon'], user_id = session["user_id"], date = date)

        # IF it does, Update to actual temperature
        else:
            flash('City Updated', 'sucess')
            db.execute("UPDATE weather_data SET temperature = :temperature, description = :description, humidity = :humidity, wind = :wind, icon = :icon, date = :date WHERE city = :city AND user_id = :user_id", temperature = weather['temperature'], description = weather['description'], humidity = weather['humidity'], wind = weather['wind'], icon = weather['icon'], date = date, city = city, user_id = session["user_id"])

        # Add to history database.
        history = db.execute("SELECT * FROM history WHERE City = :City AND user_id = :user_id", City = weather['city'], user_id = session['user_id'])

        # Check if already exists in history.
        if len(history) == 0:

            db.execute("INSERT INTO history(user_id, Date, City, Country, temperature, Description, Humidity, Wind) VALUES(:user_id, :Date, :City, :Country, :Temperature, :Description, :Humidity, :Wind)", user_id = session["user_id"], Date = date, City = weather['city'], Country = weather['country'], Temperature = weather['temperature'], Description = weather['description'], Humidity = weather['humidity'], Wind = weather['wind'])

        # Check if it already exists for today's date, so it doesn't repeat.
        else:
            history_date = history[0]['Date']

            if str(history_date) != str(date):
                db.execute("INSERT INTO history(user_id, Date, City, Country, temperature, Description, Humidity, Wind) VALUES(:user_id, :Date, :City, :Country, :Temperature, :Description, :Humidity, :Wind)", user_id = session["user_id"], Date = date, City = weather['city'], Country = weather['country'], Temperature = weather['temperature'], Description = weather['description'], Humidity = weather['humidity'], Wind = weather['wind'])

        # Query to add multiple citys on index.
        weather_data = citys_db = db.execute("SELECT * FROM weather_data WHERE user_id = :user_id", user_id = session["user_id"])

        return render_template("index.html", weather_data = weather_data)

    else:
        weather_data = citys_db = db.execute("SELECT * FROM weather_data WHERE user_id = :user_id", user_id = session["user_id"])

        return render_template("index.html", weather_data = weather_data)


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()
    
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("login.html")
        
    # User reached route via POST (as by submitting a form via POST)
    else:

        username = request.form.get("username")
        password = request.form.get("password")
        
        # Display errors.
        if not username:
            
            flash('Insert Username', 'error')
            return redirect(url_for('login'))
            
        if not password:
            
            flash('Insert Password', 'error')
            return redirect(url_for('login'))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username = username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or password != (rows[0]["hash"]):
            flash('Wrong User/Password', 'error')
            return redirect(url_for('login'))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        
        # Display errors.
        if not username:
            
            flash('Insert Username', 'error')
            return redirect(url_for('register'))
            
        if not password:
            
            flash('Insert Password', 'error')
            return redirect(url_for('register'))
        
        if not password_confirmation:
            
            flash('Insert Password Confirmation', 'error')
            return redirect(url_for('register'))
            
        if password != password_confirmation:
            
            flash('Password Not Confirmed', 'error')
            return redirect(url_for('register'))
            
        rows = db.execute("SELECT username FROM users WHERE username = :username", username = username)
        
        # Check if users already exists.
        if len(rows) > 0:
            
            flash('User already exists', 'error')
            return redirect(url_for('register'))

        # hash gonna store the password encripted, can check hash in sqlite after.
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)", username = username, password = password)
        
        return redirect("/login")


@app.route("/history")
@login_required
def history():

    # check Transaction database.
    history = db.execute("SELECT * FROM history WHERE user_id = :user_id", user_id = session['user_id'])

    return render_template("history.html", history = history)


@app.route("/delete/<name>")
@login_required
def delete(name):
    
    # Delete City
    db.execute("DELETE FROM weather_data WHERE city = :city AND user_id = :user_id", city = name, user_id = session['user_id'])
    
    # Display mensage
    flash(f"City deleted { name }", "sucess")
    
    return redirect(url_for('index'))
    
    
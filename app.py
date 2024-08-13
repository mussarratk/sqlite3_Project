import os
import sqlite3
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import json
from helpers import usd, ShoppingCart, CartItem, login_required

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///website.db")

# Set the secret key for Flask session
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# Define apology function
def apology(message, code=400):
    return render_template("apology.html", code=code, message=message)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Helper function to get the current user's shopping cart from the session
def get_shopping_cart():
    if "shopping_cart" not in session:
        session["shopping_cart"] = ShoppingCart()
    return session["shopping_cart"]

# Public Routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("public_templates/about.html")

@app.route("/courses")
def courses():
    return render_template("public_templates/courses.html")

@app.route("/portfolioprojects")
def portfolio_projects():
    return render_template("public_templates/portfolioprojects.html")

@app.route("/cs")
def computer_science():
    return render_template("public_templates/cs.html")

@app.route("/more")
def more():
    return render_template("public_templates/more.html")

@app.route("/project1.html")
def project1():
    return render_template("public_templates/project1.html")

@app.route("/project2.html")
def project2():
    return render_template("public_templates/project2.html")

@app.route("/project3.html")
def project3():
    return render_template("public_templates/project3.html")

# Secure route

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # Assuming ShoppingCart and inventory are properly defined and populated
    shoppingCart = ShoppingCart()
    inventory = db.execute("SELECT * FROM inventory")
    if request.method == "GET":
        return render_template("secure_templates/buy.html", inventory=inventory)

    if request.method == "POST":
        quantity = int(request.form.get("quantity"))
        itemId = int(request.form.get("itemId"))
        price = db.execute("SELECT price FROM inventory WHERE itemID = :itemId", itemId=itemId)

        # Create Item to add to cart
        newItem = CartItem(quantity, itemId, price)

        # When checkout is clicked
        if request.form["submit"] == "checkout":
            # Save the shopping cart in the session (you can store it in the database as well)
            session["shopping_cart"] = shoppingCart
            return redirect(url_for("checkout"))

        # When add item is clicked
        if request.form["submit"] == "addItem":
            # Check if item is already in our cart
            isNewItem = True
            for item in shoppingCart.items:
                if isNewItem is True:
                    if item.itemId == itemId:
                        item.quantity = item.quantity + quantity
                        item.description = db.execute("SELECT description FROM inventory WHERE itemID = :itemId", itemId=itemId)
                        item.name = db.execute("SELECT name FROM inventory WHERE itemID = :itemId", itemId=itemId)
                        isNewItem = False
            if isNewItem:
                shoppingCart.items.append(newItem)

        # When remove item is clicked
        elif request.form["submit"] == "removeItem":
            for item in shoppingCart.items:
                if item.itemId == itemId:
                    # If new quantity is not > 0, remove the item from the cart
                    if item.quantity > quantity:
                        item.quantity = item.quantity - quantity
                    else:
                        shoppingCart.items.remove(item)
                    break

        # Add any additional code or redirects as needed
        return redirect(url_for("buy"))

@app.route("/cart")
@login_required
def cart():
    # Retrieve the user's shopping cart
    cart = get_shopping_cart()

    # Calculate the total price of all items in the cart
    total_price = sum(item.price for item in cart.items)

    return render_template("secure_templates/cart.html", cart=cart, total_price=total_price)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = :user_id ORDER BY timestamp DESC", user_id=session["user_id"])
    # Render history page with transactions
    return render_template("secure_templates/history.html", transactions=transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect(url_for("index"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("secure_templates/login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    # User reached route via post by submitting the form
    if request.method == "POST":
        # Ensure Username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Check if passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return apology("username already exists", 400)

        # Generate hashed password
        hashed_password = generate_password_hash(request.form.get("password"))

        # Insert new user into database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                   request.form.get("username"), hashed_password)

        # Query database for newly inserted row
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to homepage
        return redirect(url_for("index"))

    # User reached route via get (as by clicking link or via redirect)
    else:
        return render_template("secure_templates/register.html")

@app.route("/forgottenpassword", methods=["GET", "POST"])
def forgottenpassword():
    """Reset forgotten password"""
    if request.method == "POST":
        # Get the username or email submitted in the form
        username_or_email = request.form.get("username_or_email")

        # Query the database to find the user with the given username or email
        user = db.execute("SELECT * FROM users WHERE username = :username OR email = :email",
                          username=username_or_email, email=username_or_email)

        if not user:
            # If no user found with the given username or email, show an error message
            return apology("User not found")

        # Generate a temporary password or a password reset token and send it to the user's email
        # Implement the logic to generate a temporary password or a token and send it via email
        # For example, you can use the `random` module to generate a random password/token.

        # Update the user's password in the database with the new temporary password or token
        # Implement the logic to update the user's password in the database
        # For example, you can use the `generate_password_hash` function to hash the new password/token.

        # Show a success message to the user
        flash("Temporary password/token has been sent to your email")

        # Redirect the user to the login page
        return redirect(url_for("login"))

    else:
        # If the request method is "GET", show the forgotten password form
        return render_template("secure_templates/forgottenpassword.html")
        
if __name__ == "__main__":
    app.run(debug=True)
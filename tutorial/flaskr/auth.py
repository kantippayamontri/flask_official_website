import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

from icecream import ic

bp = Blueprint("auth", __name__, url_prefix="/auth")


# need to request from /auth/register
"""
@bp.route associates the URL /register with the register view function.
When Flask receives a request to /auth/register, it will call the register view and use the return value as the response.
"""

"""
If the user submitted the form, request.method will be 'POST'. In this case, start validating the input.
"""


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        """
        request.form is a special type of dict mapping submitted form keys and values.
        The user will input their username and password.
        """
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                """
                db.execute takes a SQL query with ? placeholders for any user input, and a tuple of values to replace the placeholders with.
                The database library will take care of escaping the values so you are not vulnerable to a SQL injection attack.
                """
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?,?)",
                    (username, generate_password_hash(password)),
                )
                """
                db.commit() needs to be called afterwards to save the changes.
                """
                db.commit()
                ic(f"--- COMMIT SUCCESS ---")
            except db.IntegrityError:
                """
                An sqlite3.IntegrityError will occur if the username already exists, which should be shown to the user as another validation error.
                """
                error = f"User {username} is already registered."
        else:
            return {"error": "This is error."}

        flash(error)

        if error is None:
            # return {"username": username, "password": password}
            return redirect(url_for("auth.login"))
        else:
            return {"error": error}
    
    return render_template("auth/register.html")


@bp.route("/login", methods=["POST", "GET"])
def login():
    ic(f"request method: {request.method}")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        """
        fetchone() returns one row from the query. If the query returned no results, it returns None.
        fetchall() will be used, which returns a list of all results.
        """
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]

            # return {"username" : user["username"], "password" : user["password"]}
            # ic(url_for("index"))
            return redirect(url_for("index"))
        else:
            # return redirect(url_for("auth.login")) #url for blueprints.html
            return error

    return render_template("auth/login.html")


"""
bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested. 
load_logged_in_user checks if a user id is stored in the session and gets that user’s data from the database, storing it on g.user, which lasts for the length of the request.
If there is no user id, or if the id doesn’t exist, g.user will be None.
"""
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    # user_id = None # if use this line when log in -> need to log in every time.

    if user_id == None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )

"""
To log out, you need to remove the user id from the session.
Then load_logged_in_user won’t load a user on subsequent requests.
"""
@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

"""
This decorator returns a new view function that wraps the original view it’s applied to.
The new function checks if a user is loaded and redirects to the login page otherwise.
If a user is loaded the original view is called and continues normally.
You’ll use this decorator when writing the blog views.
"""
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            ic(url_for("auth.login"))
            return redirect(url_for("auth.login"))
        
        return view(**kwargs)
    return wrapped_view
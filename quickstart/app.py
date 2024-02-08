from dotenv import load_dotenv, dotenv_values
from icecream import ic
from flask import Flask, url_for, request, render_template, abort,redirect
from flask import make_response, after_this_request # for cookies
from flask import session
from flask import flash
from werkzeug import exceptions
from werkzeug.exceptions import HTTPException
import json

from markupsafe import escape

# load_dotenv() #take environment variables from .env.
# config = dotenv_values(".env")
# ic(config)

app = Flask(__name__)


@app.route('/')
def index():
    # username = request.cookies.get('username') #get the cookies
    username_cookie = request.cookies.get("username")
    
    if username_cookie is not None:
        return render_template("hello.html", name=username_cookie)
    
    app.logger.debug("A value for debugging")
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error(f"An error occurred")
    # return "Index page"
    return redirect(url_for("hello_world"))

@app.route("/login", methods=['GET', 'POST'])
def login():
    ic("Login")
    error=None
    if request.method == "POST": #handle for POST requests
        # searchword = request.args.get("username", "") # get value from ...../login?username=kkkkk
        username = request.form["username"] # get value from /login in username and password in body 
        password = request.form["password"]
        if (username != "") and (password != ""):
            return do_the_login(username=username )
        else:
            error="Invalid username or password"
            return render_template("login.html", error=error)
    else: #handle for GET requests
        return show_login_form()

def do_the_login(username="",):
    session["username"] = username    

    # set the cookie
    resp = make_response(render_template("hello.html", name=username))
    resp.set_cookie("username", username)
    
    return resp
    # return render_template("login.html", username=username)

def show_login_form():
    return "Show login form with get method"

@app.route('/hello')
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/hello/<name>")
def hello(name=None):
    ic(name)
    ic(escape(name))
    # return f"<p>Hello,{name}!</p>"
    return render_template("Hello.html", name=name) #render html template with jinja2 template

@app.route("/user/<username>")
def show_user_profile(username):
    #show the user profile for that user
    return f"User {escape(username)}"

@app.route("/post/<int:post_id>")
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f"Post {post_id}"

@app.route("/path/<path:subpath>")
def show_subpath(subpath):
    #show the subpath after /path/
    return f"Subpath {escape(subpath)}"

@app.route("/projects/") 
def projects():
    """
    if we direct to .../projects/ -> ok
    if we direct to .../projects -> flask will add slask to .../projects/ -> ok
    """
    return "The project page"

@app.route("/about")
def about():
    """
    if we direct to .../about -> ok
    if we direct to .../about/ -> 404 not found -> which helps search engines avoid indexing the same page twice.
    """
    return "The about page"

@app.route("/new_cookies", methods=["GET"])
def new_cookies():
    # add session new cookies
    session["new_cookies"] = "myvalue"
    
    response = make_response("This is a cookie")
    response.set_cookie("mycookies", "myvalue")
    return response

@app.route("/delete_cookies", methods=["GET"])
def delete_cookies():
    # ic(request.cookies)
    response = make_response("Delete a cookie")
    for key, _ in request.cookies.items():
        response.set_cookie(key, "", expires=0)
    return response

@app.errorhandler(404)
def page_not_found(error):
    # return render_template("page_not_found.html") ,404 #Method 1 : return only page not found 

    # Method 2 : return page and something
    resp = make_response(render_template("page_not_found.html"),404)
    resp.headers["X-Something"] = "A value"
    return resp

# @app.errorhandler(exceptions.BadRequest)
def handle_bad_request(error):
    ic(exceptions.BadRequest.code)
    return "--- Bad request ---"

@app.route('/show_abort')
def show_abort():
    # abort(401) #error authorized
    # abort(400) # bad request
    abort(403) 
    return "This is never executed"

app.register_error_handler(400, handle_bad_request) #another way to handle without decorators

@app.errorhandler(HTTPException)
def handle_http_exception(e): # error handle for http error
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.errorhandler(Exception)
def handle_exception(e): # error handle for all exceptions
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return render_template("500_generic.html", e=e), 500

@app.route("/error500", methods=["GET"])
def error500():
    ic(f"in error 500")
    return adfsdf

@app.route("/me")
def me_api():
    return {
        "username" : "Kan",
        "theme" : "dark theme",
        "image" : "www",
    }
    
# TODO: for session
# In order to use sessions you have to set a secret key. Here is how sessions work
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/logout")
def logout():
    ic(f"logout")
    # remove usename from the session if it's there 
    for key, _ in session.items():
        session.pop(key, None)
    
    # session.pop("username", None)
    return redirect(url_for("index"))
    
with app.test_request_context():
    """
    url_for function -> function to build url for each route
    first argument = name of the function
    """
    ic(url_for("index"))  
    ic(url_for("login"))
    ic(url_for("login",next="/"))
    ic(url_for("show_user_profile",username="John Doe"))
    ic(url_for("static", filename="style.css")) # create folder name "static" -> for development

with app.test_request_context("/hello", method="post"):
    assert request.path == "/hello"
    assert request.method == "POST"
    
if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000, template_folder="templates")
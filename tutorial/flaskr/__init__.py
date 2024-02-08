import os
from flask import Flask, render_template, redirect, url_for
import sqlite3
from icecream import ic


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    """instance_relative_config=True tells the app that configuration files are relative to the instance folder. The instance folder is located outside the flaskr package and can hold local data that shouldn’t be committed to version control, such as configuration secrets and the database file."""
    # print(app.instance_path)
    app.config.from_mapping(
        # SECRET_KEY="dev",  # secret key use "dev" for development but for production needs to use random values
        SECRET_KEY="17c0b283f57ca4966b4a6f61985ca5a86c50bee016e7df65b5007cf2201fbe5f", # print(secrets.token_hex())
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import db
    db.init_app(app)

    # register blueprint
    """
    Import and register the blueprint from the factory using app.register_blueprint().
    Place the new code at the end of the factory function before returning the app.
    """
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    """
    Unlike the auth blueprint, the blog blueprint does not have a url_prefix.
    So the index view will be at /, the create view at /create, and so on.
    The blog is the main feature of Flaskr, so it makes sense that the blog index will be the main index.
    """
    app.add_url_rule("/", endpoint="index") # when call / -> use blog.index instead route / in this file
    
    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return "Hello, world"
    
    # @app.route("/")
    # @auth.login_required #must login before go to the main page
    # def index():
    #     from . import db
    #     return render_template("index.html")
    #     # db = db.get_db()
    #     # posts = db.execute('SELECT p.id, title, body, created, author_id, username'
    #     # ' FROM post p JOIN user u ON p.author_id = u.id'
    #     # ' ORDER BY created DESC').fetchall()
    #     # ic(posts)
    #     # return redirect(url_for("index"), posts=posts)

    return app



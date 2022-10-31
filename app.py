import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

Counter=0

# Setup Logger
def setup_logger():
    #Create the logger
    logger = logging.getLogger()
    #Set default to DEBUG
    logger.setLevel(logging.DEBUG)

    #Create console handler
    s_handler = logging.StreamHandler()
    #Set level to INFO
    s_handler.setLevel(logging.INFO)

    #Create file handler
    f_handler = logging.FileHandler(filename='app.log')
    #Set level to DEBUG
    f_handler.setLevel(logging.DEBUG)

    #Add handlers to logger
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)

    return logger

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global Counter
    Counter+=1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

#Function to count number of posts in the database
def count_posts():
    connection = get_db_connection()
    cntPosts = connection.execute('SELECT COUNT(*) FROM posts').fetchone()
    connection.close()
    cntPosts = cntPosts[0]
    return cntPosts

# Function to count number of connections to the database
def count_conn():
    connection = get_db_connection()
    cntConn = connection.execute('SELECT COUNT(dbid) as TotalConnections FROM sys.sysprocesses').fetchall()
    connection.close()
    return cntConn

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define Healthcheck endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json'
    )

#    app.logger.info('Health check successful')
    logger.info("Health check successful")
    return response

# Define Metrics endpoint
@app.route('/metrics')
def metrics():
    response = app.response_class(
        response=json.dumps({"status":"success","data":{"db_connection_count": Counter,"post_count": count_posts()}}),
        status=200,
        mimetype='application/json'
    )

#    app.logger.info('Metrics request successful')
    logger.info("Metrics request successful")
    return response

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()

#    app.logger.info('Main request successful')
    logger.info("Main request successful")
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
#   logging.basicConfig(filename='app.log',level=logging.DEBUG)
   logger = setup_logger()
   
   app.run(host='0.0.0.0', port='3111')

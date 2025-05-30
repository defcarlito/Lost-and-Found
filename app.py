from flask import (
    Flask, 
    render_template, jsonify, redirect, session,
    request
    )
import sqlite3
import datetime
import os
from dotenv import load_dotenv
from msal import ConfidentialClientApplication

### handle secrets/user auth ###

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

REDIRECT_URI = "http://localhost:5000/getAToken" # where MS sends user after they sign in
SCOPE = ["User.Read"] # the info we are asking for
AUTHORITY = "https://login.microsoftonline.com/common" # the MS log in server

msal_app = ConfidentialClientApplication(
    CLIENT_ID, 
    authority=AUTHORITY, 
    client_credential=CLIENT_SECRET
)

################################

def get_posts():
    conn = sqlite3.connect('posts-db.db')
    conn.row_factory = sqlite3.Row # turns query results into dictionary
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    conn.close()
    return posts


@app.route('/api/posts')
def api_posts():
    posts = get_posts()
    post_list = []
    for post in posts:
        post_list.append(dict(post))
    return jsonify(post_list)

@app.route('/posts')
def posts():
    # send user to login screen if they aren't signed in
    if not session.get("user"):
        return redirect('/login')
    return render_template('posts.html')

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    # send user to login screen if they aren't signed in
    if not session.get("user"):
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        name = request.form['name']
        post_type = request.form['post_type']
        
        current_date = datetime.date.today().strftime("%Y-%m-%d")

        conn = sqlite3.connect('posts-db.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO posts (title, description, posted_by, post_type, date_found) VALUES (?, ?, ?, ?, ?)", (title, description, name, post_type, current_date))
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()

        image = request.files['image']
        image.save(f"static/uploads/{post_id}.jpg")
        return redirect('/')
    return render_template('create_post.html')

@app.route('/view-post/<post_id>')
def view_post(post_id):
    conn = sqlite3.connect('posts-db.db')
    conn.row_factory = sqlite3.Row # turns query results into dictionary
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE post_id = ?", (post_id,))
    post = cursor.fetchone()
    conn.close()
    return render_template('view_post.html', post=post)

@app.route('/login')
def login():
    auth_url = msal_app.get_authorization_request_url(
        SCOPE, 
        redirect_uri=REDIRECT_URI,
        prompt="select_account"
    )
    return redirect(auth_url)

@app.route('/getAToken')
def authorized():
    code = request.args.get("code")
    result = msal_app.acquire_token_by_authorization_code(
        code, 
        scopes=SCOPE, 
        redirect_uri=REDIRECT_URI
    )
    session["user"] = result.get("id_token_claims") # store user's email, name, other info
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/')
def home():
    if session.get("user"):
        return render_template('home_logged_in.html')
    else:
        return render_template('home_guest.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
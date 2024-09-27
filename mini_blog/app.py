from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisissecret'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder for uploaded images

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    pub_date = db.Column(db.DateTime, default=datetime.utcnow)
    image_url = db.Column(db.String(200))  # Optional: URL to the image for the blog post

    def __repr__(self):
        return f'<BlogPost {self.title} by {self.author}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Function to truncate words
def truncate_words(text, num_words):
    """Return the first num_words from text, joined by spaces."""
    words = text.split()
    if len(words) > num_words:
        return ' '.join(words[:num_words]) + '...'
    return text

# Register the custom filter
app.jinja_env.filters['truncatewords'] = truncate_words

# Home Page (List of blog posts)
@app.route('/')
def index():
    search_query = request.args.get('search')  # Get the search query from the URL parameters
    if search_query:
        # Filter blog posts based on the search query (title and content)
        data = BlogPost.query.filter(
            (BlogPost.title.ilike(f'%{search_query}%')) |
            (BlogPost.content.ilike(f'%{search_query}%'))
        ).all()
    else:
        data = BlogPost.query.all()
    
    return render_template("index.html", data=data)

# View a specific post
@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('view_post.html', post=post)

# Update a post
@app.route('/update_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        
        # Handle image upload
        image_url = request.form.get("image_url")  # Assuming the URL is entered in a form field
        if image_url:
            post.image_url = image_url
        
        db.session.commit()
        flash('Post updated successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('update_post.html', post=post)

# Delete a post
@app.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully', 'success')
    return redirect(url_for('index'))

# Register a new user
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Use pbkdf2:sha256 hashing method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user = User(username=username, first_name=first_name, last_name=last_name, email=email, password=hashed_password)

        try:
            db.session.add(user)
            db.session.commit()
            flash("User registered successfully!", "success")
            return redirect("/login")
        except Exception as e:
            db.session.rollback()
            flash(f"Error occurred: {e}", "danger")

    return render_template("register.html")

# Login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect('/')

# Create a new blog post
@app.route('/blog/create', methods=["GET", "POST"])
@login_required
def create_blog():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = current_user.username
        image_url = request.form.get("image_url")  # Get the image URL from the form

        new_post = BlogPost(title=title, content=content, author=author, image_url=image_url)  # Include image_url
        db.session.add(new_post)
        db.session.commit()

        flash("Blog post created successfully!", "success")
        return redirect('/')
    
    return render_template("create_blog.html")

if __name__ == '__main__':
    # Create the uploads folder if it does not exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.run(debug=True)

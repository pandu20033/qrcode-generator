from flask import Flask, render_template
from extensions import db, bcrypt
from flask_login import LoginManager
from models import User
from routes import register_blueprints
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/qr_codes'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extensions
db.init_app(app)
bcrypt.init_app(app)

# Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Register Blueprints
register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True)

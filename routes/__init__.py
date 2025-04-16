from .auth import auth_bp
from .qr import qr_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(qr_bp)

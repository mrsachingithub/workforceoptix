from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models to ensure they are registered with SQLAlchemy
    from app import models

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.employee_routes import employee_bp
    app.register_blueprint(employee_bp)

    from app.routes.project_routes import project_bp
    app.register_blueprint(project_bp)

    from app.routes.allocation_routes import allocation_bp
    app.register_blueprint(allocation_bp)

    from app.routes.bench_routes import bench_bp
    app.register_blueprint(bench_bp)
    
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
    from app.models import User

    @app.context_processor
    def inject_user():
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                return dict(current_user=user)
        except Exception:
            pass
        return dict(current_user=None)
    
    return app

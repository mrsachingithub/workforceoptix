from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@workforce.com', role='Admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin / admin123")
    else:
        print("Admin user already exists.")

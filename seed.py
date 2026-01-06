import os
from dotenv import load_dotenv

load_dotenv()
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_password:
        print("Error: ADMIN_PASSWORD environment variable not set.")
        exit(1)

    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@workforce.com', role='Admin')
        admin.set_password(admin_password)
        db.session.add(admin)
        print(f"Admin user created: admin")
    else:
        admin.set_password(admin_password)
        print("Admin password updated from environment variable.")
    
    db.session.commit()

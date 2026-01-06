from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    if users:
        print(f"{'Username':<20} {'Role':<15} {'Email'}")
        print("-" * 50)
        for user in users:
             print(f"{user.username:<20} {user.role:<15} {user.email}")
    else:
        print("No users found in the database.")

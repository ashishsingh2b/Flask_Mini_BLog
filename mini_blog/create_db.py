from app import app, db

# Create the database and the database table
with app.app_context():
    db.create_all()

print("Database created!")

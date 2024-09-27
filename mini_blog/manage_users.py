from app import app, db
from app import User  # Make sure to import your User model

def add_user(first_name, last_name, email, password):
    new_user = User(first_name="Ashish", last_name="Singh", email="ashish@gmail.com", password=password)
    db.session.add(new_user)
    db.session.commit()
    print(f'User {first_name} {last_name} added!')

def show_users():
    users = User.query.all()  # Fetch all users
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f'ID: {user.id}, Name: {user.first_name} {user.last_name}, Email: {user.email}, Created At: {user.created_at}')

if __name__ == "__main__":
    with app.app_context():
        # Example usage: Adding a new user
        add_user('John', 'Doe', 'john@example.com', 'password123')
        
        # Show all users
        print("\nCurrent Users in Database:")
        show_users()

import os
from app.views import app
from app.database import init_db

# Initialize the database
print("Initializing database...")
init_db()

if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000) 
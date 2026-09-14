import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy  # 1. Import SQLAlchemy

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 2. Configure the database connection string
# Render uses 'postgres://', but Python requires 'postgresql://'. We replace it dynamically.
db_url = os.environ.get("DATABASE_URL")

if db_url:
    # 1. Clean up Render's legacy prefix if present
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # 2. Force SQLAlchemy to use the modern 'psycopg' (v3) driver dialect
    if "postgresql+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    # Safe fallback for local development if the environment variable drops
    db_url = "sqlite:///thinkesports.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
# 3. Define the Database Table Structure
class PlayerRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    game_id = db.Column(db.String(120), nullable=False)

    def __init__(self, username, game_id):
        self.username = username
        self.game_id = game_id

# 4. Automatically create tables inside the database when the app starts
with app.app_context():
    try:
        db.create_all()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Database connection skipped during build: {str(e)}")

@app.route("/api/submit-details", methods=["POST"])
def receive_details():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    username = data.get("username")
    game_id = data.get("gameId")
    
    if not username or not game_id:
        return jsonify({"status": "error", "message": "Missing username or game ID"}), 400
    
    try:
        # 5. Save the data to the PostgreSQL database
        new_entry = PlayerRegistration(username=username, game_id=game_id)
        db.session.add(new_entry)
        db.session.commit()  # Saves changes permanently
        
        return jsonify({
            "status": "success",
            "message": f"Successfully saved {username} to the database!"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")
        return jsonify({"status": "error", "message": "Failed to save to database"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

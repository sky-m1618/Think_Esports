import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # 1. Import CORS

app = Flask(__name__)

# 2. Enable CORS so your Vue app can communicate with this API
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 3. Replace the home route with an API endpoint for receiving data
@app.route("/api/submit-details", methods=["POST"])
def receive_details():
    # Grab the JSON data sent by Vue
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
        
    # Extract the fields sent from your frontend form
    username = data.get("username")
    game_id = data.get("gameId")
    
    # Process the details (e.g., validate or prepare to save to a database)
    print(f"Received details for User: {username}, Game ID: {game_id}")
    
    # Send a response back to Vue
    return jsonify({
        "status": "success",
        "message": f"Details for {username} successfully received by the backend!"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

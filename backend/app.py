from app import create_app
app = create_app()
from flask import jsonify
@app.route('/api/test/server/production')
def test():
    return jsonify({
                "status": "success",
                "message": "Successfully saved to the database!"
            }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=app.config.get("DEBUG", False))

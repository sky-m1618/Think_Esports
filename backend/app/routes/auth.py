import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token


from app.models import Admin, Player

auth_bp = Blueprint("auth", __name__)

PHONE_RE = re.compile(r"^\d{10,15}$")


@auth_bp.post("/admin/login")
def admin_login():
    data = request.get_json(force=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    admin = Admin.query.filter(
        (Admin.username == username) | (Admin.email == username.lower())
    ).first()

    if not admin or not admin.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=admin.id, additional_claims={"role": "admin"})
    return jsonify({"token": token, "admin": admin.to_dict()})


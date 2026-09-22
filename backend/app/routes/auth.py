import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import Admin, Player

from app.models import Admin, Player

auth_bp = Blueprint("auth", __name__)



PHONE_RE = re.compile(r"^\d{10,15}$")
PIN_RE = re.compile(r"^\d{4}$")

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

@auth_bp.post("/player/register")
def player_register():
    """Brand-new phone number: create the player and set their PIN."""
    data = request.get_json(force=True) or {}
    phone = (data.get("phone_number") or "").strip()
    player_name = (data.get("player_name") or "").strip()
    pin = (data.get("pin") or "").strip()

    if not PHONE_RE.match(phone):
        return jsonify({"error": "Enter a valid phone number (10-15 digits)"}), 400
    if not player_name:
        return jsonify({"error": "player_name is required"}), 400
    if not PIN_RE.match(pin):
        return jsonify({"error": "PIN must be exactly 4 digits"}), 400
    if Player.query.filter_by(phone_number=phone).first():
        return jsonify({"error": "An account with this phone number already exists"}), 409

    player = Player(phone_number=phone, player_name=player_name)
    player.set_pin(pin)
    db.session.add(player)
    db.session.commit()

    token = create_access_token(identity=player.phone_number, additional_claims={"role": "player"})
    return jsonify({"token": token, "player": player.to_dict()}), 201


@auth_bp.post("/player/set-pin")
def player_set_pin():
    """Phone number already exists (e.g. added as a teammate) but has never
    set a PIN — first-time login for that record."""
    data = request.get_json(force=True) or {}
    phone = (data.get("phone_number") or "").strip()
    pin = (data.get("pin") or "").strip()

    if not PHONE_RE.match(phone):
        return jsonify({"error": "Enter a valid phone number (10-15 digits)"}), 400
    if not PIN_RE.match(pin):
        return jsonify({"error": "PIN must be exactly 4 digits"}), 400

    player = Player.query.filter_by(phone_number=phone).first()
    if not player:
        return jsonify({"error": "No account found for this phone number"}), 404
    if player.pin_hash:
        return jsonify({"error": "A PIN is already set for this account. Please log in instead."}), 409

    player.set_pin(pin)
    db.session.commit()

    token = create_access_token(identity=player.phone_number, additional_claims={"role": "player"})
    return jsonify({"token": token, "player": player.to_dict()})


@auth_bp.post("/player/login")
def player_login():
    data = request.get_json(force=True) or {}
    phone = (data.get("phone_number") or "").strip()
    pin = (data.get("pin") or "").strip()

    if not PHONE_RE.match(phone):
        return jsonify({"error": "Enter a valid phone number (10-15 digits)"}), 400

    player = Player.query.filter_by(phone_number=phone).first()
    if not player or not player.pin_hash:
        return jsonify({"error": "No PIN set for this account yet"}), 401
    if not player.check_pin(pin):
        return jsonify({"error": "Incorrect phone number or PIN"}), 401

    token = create_access_token(identity=player.phone_number, additional_claims={"role": "player"})
    return jsonify({"token": token, "player": player.to_dict()})
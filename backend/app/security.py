"""Role-aware JWT helpers.

Both admins and players authenticate through the same JWT mechanism, but we
tag each token with a `role` claim ("admin" or "player") so routes can be
restricted appropriately without maintaining two parallel auth stacks.
"""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt,
    get_jwt_identity,
)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def player_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "player":
            return jsonify({"error": "Player access required"}), 403
        return fn(*args, **kwargs)

    return wrapper


def current_player_phone():
    """Call inside a @player_required view."""
    return get_jwt_identity()


def current_admin_id():
    """Call inside an @admin_required view."""
    return get_jwt_identity()

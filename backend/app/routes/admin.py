from flask import Blueprint,jsonify
from sqlalchemy import func
from functools import wraps
from app.models import Player , Team , Tournament,Registration
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

admin_bp = Blueprint('admin',__name__)


@admin_bp.get("/stats")
@admin_required
def stats():
    total_players = Player.query.count()
    total_teams = Team.query.count()
    total_tournaments = Tournament.query.count()
    ongoing_tournaments = Tournament.query.filter_by(status="ongoing").count()

    revenue_row = (
        Registration.query.join(Tournament)
        .filter(Registration.payment_status == "confirmed")
        .with_entities(func.sum(Tournament.entry_fee))
        .scalar()
    )
    revenue = float(revenue_row or 0)

    pending_payments = Registration.query.filter_by(payment_status="pending").count()

    return jsonify(
        {
            "total_players": total_players,
            "total_teams": total_teams,
            "total_tournaments": total_tournaments,
            "ongoing_tournaments": ongoing_tournaments,
            "total_revenue": revenue,
            "pending_payments": pending_payments,
        }
    )

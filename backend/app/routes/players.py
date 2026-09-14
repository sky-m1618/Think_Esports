from flask import Blueprint, jsonify

from app.models import Player, Team, TeamMember, Registration
from app.security import player_required, current_player_phone, admin_required

players_bp = Blueprint("players", __name__)


@players_bp.get("/me")
@player_required
def me():
    phone = current_player_phone()
    player = Player.query.filter_by(phone_number=phone).first_or_404()

    member_rows = TeamMember.query.filter_by(player_phone=phone).all()
    team_ids = [m.team_id for m in member_rows]
    teams = Team.query.filter(Team.id.in_(team_ids)).all() if team_ids else []

    registrations = (
        Registration.query.filter(Registration.team_id.in_(team_ids)).all()
        if team_ids
        else []
    )

    return jsonify(
        {
            "player": player.to_dict(),
            "teams": [t.to_dict() for t in teams],
            "registrations": [r.to_dict() for r in registrations],
        }
    )


@players_bp.get("/check/<phone>")
def check_phone(phone):
    """Used by the team-creation form to flag whether a teammate phone is a
    registered player, and to warn about duplicates within the same team."""
    player = Player.query.filter_by(phone_number=phone).first()
    return jsonify({"exists": player is not None, "player_name": player.player_name if player else None})


# ---------------------------------------------------------------------------
# Admin: list / manage players
# ---------------------------------------------------------------------------
@players_bp.get("/")
@admin_required
def list_players():
    players = Player.query.order_by(Player.created_at.desc()).all()
    return jsonify([p.to_dict() for p in players])


@players_bp.delete("/<player_id>")
@admin_required
def delete_player(player_id):
    from app.extensions import db

    player = Player.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": "Player deleted"})

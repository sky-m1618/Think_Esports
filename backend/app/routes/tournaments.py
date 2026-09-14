from datetime import datetime

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Tournament, Registration, Team, TeamMember
from app.security import admin_required, player_required, current_player_phone, current_admin_id

tournaments_bp = Blueprint("tournaments", __name__)

VALID_STATUSES = {"upcoming", "ongoing", "completed"}


def parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@tournaments_bp.get("/")
def list_tournaments():
    status = request.args.get("status")
    query = Tournament.query
    if status and status in VALID_STATUSES:
        query = query.filter_by(status=status)
    tournaments = query.order_by(Tournament.start_date.asc()).all()
    return jsonify([t.to_dict() for t in tournaments])


@tournaments_bp.get("/<tournament_id>")
def get_tournament(tournament_id):
    t = Tournament.query.get_or_404(tournament_id)
    data = t.to_dict()
    data["registrations"] = [r.to_dict() for r in t.registrations]
    data["matches"] = [m.to_dict() for m in t.matches]
    return jsonify(data)


@tournaments_bp.post("/")
@admin_required
def create_tournament():
    data = request.get_json(force=True) or {}
    required = ["tournament_name", "max_teams", "start_date"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    t = Tournament(
        tournament_name=data["tournament_name"].strip(),
        description=data.get("description", ""),
        entry_fee=data.get("entry_fee", 0),
        prize_pool=data.get("prize_pool", 0),
        max_teams=int(data["max_teams"]),
        status=data.get("status", "upcoming"),
        rules=data.get("rules", ""),
        start_date=parse_dt(data["start_date"]),
        end_date=parse_dt(data.get("end_date")),
        created_by=current_admin_id(),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


@tournaments_bp.put("/<tournament_id>")
@admin_required
def update_tournament(tournament_id):
    t = Tournament.query.get_or_404(tournament_id)
    data = request.get_json(force=True) or {}

    for field in ["tournament_name", "description", "rules"]:
        if field in data:
            setattr(t, field, data[field])
    for field in ["entry_fee", "prize_pool", "max_teams"]:
        if field in data:
            setattr(t, field, data[field])
    if "status" in data and data["status"] in VALID_STATUSES:
        t.status = data["status"]
    if "start_date" in data:
        t.start_date = parse_dt(data["start_date"])
    if "end_date" in data:
        t.end_date = parse_dt(data["end_date"])

    db.session.commit()
    return jsonify(t.to_dict())


@tournaments_bp.delete("/<tournament_id>")
@admin_required
def delete_tournament(tournament_id):
    t = Tournament.query.get_or_404(tournament_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Tournament deleted"})


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
@tournaments_bp.post("/<tournament_id>/register")
@player_required
def register_team(tournament_id):
    """
    Registration rules:
      - Tournament must have available slots
      - Team must not already be registered
      - All team members must be registered players (guaranteed by team
        creation flow, re-checked here for safety)
      - registered_teams is incremented on success
      - payment_status starts as 'pending'
    """
    phone = current_player_phone()
    data = request.get_json(force=True) or {}
    team_id = data.get("team_id")

    team = Team.query.get_or_404(team_id)
    if team.leader_phone != phone:
        return jsonify({"error": "Only the team leader can register the team"}), 403

    tournament = Tournament.query.get_or_404(tournament_id)

    if tournament.registered_teams >= tournament.max_teams:
        return jsonify({"error": "Tournament is full"}), 400

    existing = Registration.query.filter_by(
        tournament_id=tournament_id, team_id=team_id
    ).first()
    if existing:
        return jsonify({"error": "Team is already registered for this tournament"}), 409

    member_phones = [m.player_phone for m in team.members]
    from app.models import Player

    registered_count = Player.query.filter(Player.phone_number.in_(member_phones)).count()
    if registered_count != len(member_phones):
        return jsonify({"error": "All team members must be registered players"}), 400

    registration = Registration(tournament_id=tournament_id, team_id=team_id)
    tournament.registered_teams += 1
    db.session.add(registration)
    db.session.commit()

    return jsonify(registration.to_dict()), 201


@tournaments_bp.put("/registrations/<registration_id>")
@admin_required
def update_registration(registration_id):
    reg = Registration.query.get_or_404(registration_id)
    data = request.get_json(force=True) or {}
    status = data.get("payment_status")
    if status not in ("pending", "confirmed"):
        return jsonify({"error": "payment_status must be 'pending' or 'confirmed'"}), 400
    reg.payment_status = status
    db.session.commit()
    return jsonify(reg.to_dict())


@tournaments_bp.delete("/registrations/<registration_id>")
@admin_required
def reject_registration(registration_id):
    reg = Registration.query.get_or_404(registration_id)
    tournament = Tournament.query.get(reg.tournament_id)
    if tournament and tournament.registered_teams > 0:
        tournament.registered_teams -= 1
    db.session.delete(reg)
    db.session.commit()
    return jsonify({"message": "Registration removed"})

import re

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import Team, TeamMember, Player
from app.security import player_required, current_player_phone, admin_required

teams_bp = Blueprint("teams", __name__)

PHONE_RE = re.compile(r"^\d{10,15}$")
TAG_RE = re.compile(r"^[A-Za-z0-9]{3,4}$")
MAX_ADDITIONAL_MEMBERS = 4  # + leader = 5 total


@teams_bp.post("/")
@player_required
def create_team():
    """
    Validation rules enforced here:
      - Team must have exactly 1 leader (the creator / logged-in player)
      - Team can have 0-4 additional members (max 5 total)
      - Each member's phone number must be unique across the team
      - Leader cannot also appear as a member
      - Phone numbers must be 10-15 digits
      - Team name must be unique (case-insensitive)
      - Team tag must be 3-4 alphanumeric characters
    """
    leader_phone = current_player_phone()
    data = request.get_json(force=True) or {}

    team_name = (data.get("team_name") or "").strip()
    team_tag = (data.get("team_tag") or "").strip().upper()
    logo_url = data.get("logo_url")
    members = data.get("members") or []  # [{player_name, phone_number}, ...]

    errors = []

    if not team_name:
        errors.append("Team name is required")
    elif Team.query.filter(func.lower(Team.team_name) == team_name.lower()).first():
        errors.append("Team name is already taken")

    if not TAG_RE.match(team_tag or ""):
        errors.append("Team tag must be 3-4 alphanumeric characters")

    if len(members) > MAX_ADDITIONAL_MEMBERS:
        errors.append(f"A team can have at most {MAX_ADDITIONAL_MEMBERS} additional members")

    seen_phones = {leader_phone}
    cleaned_members = []
    for i, m in enumerate(members):
        phone = (m.get("phone_number") or "").strip()
        name = (m.get("player_name") or "").strip()

        if not name:
            errors.append(f"Member #{i + 1}: name is required")
        if not PHONE_RE.match(phone):
            errors.append(f"Member #{i + 1}: invalid phone number")
        elif phone in seen_phones:
            errors.append(f"Member #{i + 1}: duplicate phone number ({phone})")
        seen_phones.add(phone)
        cleaned_members.append({"player_name": name, "phone_number": phone})

    if errors:
        return jsonify({"errors": errors}), 400

    leader = Player.query.filter_by(phone_number=leader_phone).first_or_404()

    team = Team(team_name=team_name, team_tag=team_tag, leader_phone=leader_phone, logo_url=logo_url)
    db.session.add(team)
    db.session.flush()  # get team.id

    db.session.add(
        TeamMember(
            team_id=team.id,
            player_phone=leader_phone,
            player_name=leader.player_name,
            role="leader",
        )
    )

    for m in cleaned_members:
        # Auto-create a Player record for teammates who aren't registered yet,
        # matching the phone-based auth model.
        player = Player.query.filter_by(phone_number=m["phone_number"]).first()
        if not player:
            player = Player(phone_number=m["phone_number"], player_name=m["player_name"])
            db.session.add(player)
        db.session.add(
            TeamMember(
                team_id=team.id,
                player_phone=m["phone_number"],
                player_name=m["player_name"],
                role="member",
            )
        )

    db.session.commit()
    return jsonify(team.to_dict()), 201


@teams_bp.get("/")
def list_teams():
    q = (request.args.get("q") or "").strip()
    query = Team.query
    if q:
        query = query.filter(Team.team_name.ilike(f"%{q}%"))
    teams = query.order_by(Team.created_at.desc()).all()
    return jsonify([t.to_dict(include_members=False) for t in teams])


@teams_bp.get("/<team_id>")
def get_team(team_id):
    team = Team.query.get_or_404(team_id)
    return jsonify(team.to_dict())


@teams_bp.get("/check-phone/<phone>")
def check_phone_in_use(phone):
    exists = Player.query.filter_by(phone_number=phone).first() is not None
    return jsonify({"registered": exists})


@teams_bp.delete("/<team_id>")
@admin_required
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    return jsonify({"message": "Team deleted"})

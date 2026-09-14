from datetime import datetime

from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Match, MatchResult, Tournament, VALID_MAPS
from app.security import admin_required

matches_bp = Blueprint("matches", __name__)


def parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@matches_bp.get("/tournament/<tournament_id>")
def list_matches(tournament_id):
    matches = (
        Match.query.filter_by(tournament_id=tournament_id)
        .order_by(Match.match_date.asc())
        .all()
    )
    return jsonify([m.to_dict() for m in matches])


@matches_bp.get("/<match_id>")
def get_match(match_id):
    m = Match.query.get_or_404(match_id)
    return jsonify(m.to_dict(include_results=True))


@matches_bp.post("/")
@admin_required
def create_match():
    data = request.get_json(force=True) or {}
    required = ["tournament_id", "match_name", "match_date"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    Tournament.query.get_or_404(data["tournament_id"])

    map_name = data.get("map_name", "Erangel")
    if map_name not in VALID_MAPS:
        return jsonify({"error": f"map_name must be one of {VALID_MAPS}"}), 400

    match = Match(
        tournament_id=data["tournament_id"],
        match_name=data["match_name"].strip(),
        match_date=parse_dt(data["match_date"]),
        map_name=map_name,
        status=data.get("status", "scheduled"),
    )
    db.session.add(match)
    db.session.commit()
    return jsonify(match.to_dict()), 201


@matches_bp.put("/<match_id>")
@admin_required
def update_match(match_id):
    match = Match.query.get_or_404(match_id)
    data = request.get_json(force=True) or {}

    if "match_name" in data:
        match.match_name = data["match_name"]
    if "match_date" in data:
        match.match_date = parse_dt(data["match_date"])
    if "map_name" in data:
        if data["map_name"] not in VALID_MAPS:
            return jsonify({"error": f"map_name must be one of {VALID_MAPS}"}), 400
        match.map_name = data["map_name"]
    if "status" in data and data["status"] in ("scheduled", "live", "completed"):
        match.status = data["status"]

    db.session.commit()
    return jsonify(match.to_dict())


@matches_bp.delete("/<match_id>")
@admin_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({"message": "Match deleted"})


# ---------------------------------------------------------------------------
# Results entry
# ---------------------------------------------------------------------------
@matches_bp.post("/<match_id>/results")
@admin_required
def add_result(match_id):
    match = Match.query.get_or_404(match_id)
    data = request.get_json(force=True) or {}

    team_id = data.get("team_id")
    placement = data.get("placement")
    kills = int(data.get("kills", 0))
    damage = float(data.get("damage", 0))

    if not team_id or placement is None:
        return jsonify({"error": "team_id and placement are required"}), 400

    placement = int(placement)
    points = MatchResult.placement_points(placement) + kills

    existing = MatchResult.query.filter_by(match_id=match_id, team_id=team_id).first()
    if existing:
        existing.placement = placement
        existing.kills = kills
        existing.damage = damage
        existing.points = points
        result = existing
    else:
        result = MatchResult(
            match_id=match_id,
            team_id=team_id,
            placement=placement,
            kills=kills,
            damage=damage,
            points=points,
        )
        db.session.add(result)

    db.session.commit()
    return jsonify(result.to_dict()), 201


@matches_bp.delete("/results/<result_id>")
@admin_required
def delete_result(result_id):
    result = MatchResult.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    return jsonify({"message": "Result deleted"})

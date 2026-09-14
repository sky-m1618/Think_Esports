from flask import Blueprint, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import MatchResult, Match, Team

leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.get("/<tournament_id>")
def tournament_leaderboard(tournament_id):
    """
    Aggregates MatchResult rows across every match in the tournament.
    Sort order: total points desc, then total kills desc, then total damage desc.
    """
    rows = (
        db.session.query(
            MatchResult.team_id,
            func.sum(MatchResult.points).label("total_points"),
            func.sum(MatchResult.kills).label("total_kills"),
            func.sum(MatchResult.damage).label("total_damage"),
            func.count(MatchResult.id).label("matches_played"),
        )
        .join(Match, Match.id == MatchResult.match_id)
        .filter(Match.tournament_id == tournament_id)
        .group_by(MatchResult.team_id)
        .all()
    )

    team_ids = [r.team_id for r in rows]
    teams = {t.id: t for t in Team.query.filter(Team.id.in_(team_ids)).all()}

    leaderboard = []
    for r in rows:
        team = teams.get(r.team_id)
        leaderboard.append(
            {
                "team_id": r.team_id,
                "team_name": team.team_name if team else "Unknown",
                "team_tag": team.team_tag if team else "",
                "total_points": int(r.total_points or 0),
                "total_kills": int(r.total_kills or 0),
                "total_damage": float(r.total_damage or 0),
                "matches_played": r.matches_played,
            }
        )

    leaderboard.sort(
        key=lambda x: (-x["total_points"], -x["total_kills"], -x["total_damage"])
    )
    for i, row in enumerate(leaderboard):
        row["rank"] = i + 1

    return jsonify(leaderboard)

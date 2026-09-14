import uuid
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from app import db

def gen_uuid():
    return str(uuid.uuid4())


def now():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Admins
# ---------------------------------------------------------------------------
class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Players
# ---------------------------------------------------------------------------
class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    player_name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "player_name": self.player_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------
class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    team_name = db.Column(db.String(80), nullable=False)
    team_tag = db.Column(db.String(4), nullable=False)
    leader_phone = db.Column(
        db.String(20), db.ForeignKey("players.phone_number"), nullable=False
    )
    logo_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    members = db.relationship(
        "TeamMember", backref="team", cascade="all, delete-orphan", lazy="joined"
    )
    leader = db.relationship("Player", foreign_keys=[leader_phone])

    def to_dict(self, include_members=True):
        data = {
            "id": self.id,
            "team_name": self.team_name,
            "team_tag": self.team_tag,
            "leader_phone": self.leader_phone,
            "leader_name": self.leader.player_name if self.leader else None,
            "logo_url": self.logo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "member_count": len(self.members),
        }
        if include_members:
            data["members"] = [m.to_dict() for m in self.members]
        return data


class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    team_id = db.Column(db.String(36), db.ForeignKey("teams.id"), nullable=False)
    player_phone = db.Column(
        db.String(20), db.ForeignKey("players.phone_number"), nullable=False
    )
    player_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="member")  # leader|member
    joined_at = db.Column(db.DateTime(timezone=True), default=now)

    __table_args__ = (
        db.UniqueConstraint("team_id", "player_phone", name="uq_team_player"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "team_id": self.team_id,
            "player_phone": self.player_phone,
            "player_name": self.player_name,
            "role": self.role,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
        }


# ---------------------------------------------------------------------------
# Tournaments
# ---------------------------------------------------------------------------
class Tournament(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    tournament_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    entry_fee = db.Column(db.Numeric(10, 2), default=0)
    prize_pool = db.Column(db.Numeric(10, 2), default=0)
    max_teams = db.Column(db.Integer, nullable=False)
    registered_teams = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="upcoming")  # upcoming|ongoing|completed
    rules = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    end_date = db.Column(db.DateTime(timezone=True), nullable=True)
    created_by = db.Column(db.String(36), db.ForeignKey("admins.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now)

    matches = db.relationship(
        "Match", backref="tournament", cascade="all, delete-orphan"
    )
    registrations = db.relationship(
        "Registration", backref="tournament", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_name": self.tournament_name,
            "description": self.description,
            "entry_fee": float(self.entry_fee or 0),
            "prize_pool": float(self.prize_pool or 0),
            "max_teams": self.max_teams,
            "registered_teams": self.registered_teams,
            "slots_left": max(self.max_teams - self.registered_teams, 0),
            "status": self.status,
            "rules": self.rules,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    tournament_id = db.Column(
        db.String(36), db.ForeignKey("tournaments.id"), nullable=False
    )
    team_id = db.Column(db.String(36), db.ForeignKey("teams.id"), nullable=False)
    registered_at = db.Column(db.DateTime(timezone=True), default=now)
    payment_status = db.Column(db.String(20), default="pending")  # pending|confirmed

    team = db.relationship("Team")

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "team_id", name="uq_tournament_team_registration"
        ),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "team_id": self.team_id,
            "team": self.team.to_dict(include_members=False) if self.team else None,
            "registered_at": self.registered_at.isoformat()
            if self.registered_at
            else None,
            "payment_status": self.payment_status,
        }


# ---------------------------------------------------------------------------
# Matches & Results
# ---------------------------------------------------------------------------
VALID_MAPS = ["Erangel", "Miramar", "Sanhok", "Vikendi", "Livik"]


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    tournament_id = db.Column(
        db.String(36), db.ForeignKey("tournaments.id"), nullable=False
    )
    match_name = db.Column(db.String(120), nullable=False)
    match_date = db.Column(db.DateTime(timezone=True), nullable=False)
    map_name = db.Column(db.String(20), nullable=False, default="Erangel")
    status = db.Column(db.String(20), default="scheduled")  # scheduled|live|completed

    results = db.relationship(
        "MatchResult", backref="match", cascade="all, delete-orphan"
    )

    def to_dict(self, include_results=False):
        data = {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "match_name": self.match_name,
            "match_date": self.match_date.isoformat() if self.match_date else None,
            "map_name": self.map_name,
            "status": self.status,
        }
        if include_results:
            data["results"] = [r.to_dict() for r in self.results]
        return data


class MatchResult(db.Model):
    __tablename__ = "match_results"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    match_id = db.Column(db.String(36), db.ForeignKey("matches.id"), nullable=False)
    team_id = db.Column(db.String(36), db.ForeignKey("teams.id"), nullable=False)
    placement = db.Column(db.Integer, nullable=False)
    kills = db.Column(db.Integer, default=0)
    damage = db.Column(db.Numeric(10, 2), default=0)
    points = db.Column(db.Integer, default=0)

    team = db.relationship("Team")

    __table_args__ = (
        db.UniqueConstraint("match_id", "team_id", name="uq_match_team_result"),
    )

    PLACEMENT_POINTS = {
        1: 15,
        2: 12,
        3: 10,
        4: 8,
        5: 6,
        6: 4,
        7: 2,
        8: 1,
    }

    @classmethod
    def placement_points(cls, placement):
        return cls.PLACEMENT_POINTS.get(placement, 0)

    def to_dict(self):
        return {
            "id": self.id,
            "match_id": self.match_id,
            "team_id": self.team_id,
            "team_name": self.team.team_name if self.team else None,
            "placement": self.placement,
            "kills": self.kills,
            "damage": float(self.damage or 0),
            "points": self.points,
        }

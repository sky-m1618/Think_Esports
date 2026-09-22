import os
from flask import Flask, jsonify
from werkzeug.security import generate_password_hash
from config import config_by_name
from app.extensions import db, migrate, jwt, cors
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from sqlalchemy import inspect, text


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    os.makedirs(os.path.join(app.root_path, "..", "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    from app.routes.auth import auth_bp
    from app.routes.teams import teams_bp
    from app.routes.tournaments import tournaments_bp
    from app.routes.matches import matches_bp
    from app.routes.leaderboard import leaderboard_bp
    from app.routes.admin import admin_bp
    from app.routes.players import players_bp
    # from app.routes.uploads import uploads_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(teams_bp, url_prefix="/api/teams")
    app.register_blueprint(tournaments_bp, url_prefix="/api/tournaments")
    app.register_blueprint(matches_bp, url_prefix="/api/matches")
    app.register_blueprint(leaderboard_bp, url_prefix="/api/leaderboard")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(players_bp, url_prefix="/api/players")
    # app.register_blueprint(uploads_bp, url_prefix="/api/uploads")
    
    with app.app_context():
        from app.models import Admin, Player, Team, TeamMember, Tournament, Registration, Match, MatchResult
        print("Registered Tables:", db.metadata.tables.keys())

        db.create_all()

        # --- Lightweight auto-patch for columns added after the table already
        #     existed. db.create_all() only creates missing TABLES, never alters
        #     existing ones, so new columns (like players.pin_hash) need this. ---
        inspector = inspect(db.engine)
        existing_columns = {col["name"] for col in inspector.get_columns("players")}
        if "pin_hash" not in existing_columns:
            print("Patching players table: adding pin_hash column...")
            db.session.execute(text("ALTER TABLE players ADD COLUMN pin_hash VARCHAR(255)"))
            db.session.commit()
            print("players.pin_hash added.")

        admin_username = "skym1618"
        existing_admin = Admin.query.filter_by(username=admin_username).first()

        if not existing_admin:
            new_admin = Admin(
                username=admin_username,
                email="akashmbytes@gmail.com",
            )
            new_admin.set_password("skym1618")
            db.session.add(new_admin)
            db.session.commit()
            print(f"--- Admin user '{admin_username}' successfully seeded! ---")
        else:
            print(f"--- Admin user '{admin_username}' already exists. Skipping seed. ---")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
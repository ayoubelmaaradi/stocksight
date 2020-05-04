from .twitter.twitter_controller import bp as twitter_bp
from .user.controllers import bp as user_bp


def register_blueprints(app):
    for bp in [twitter_bp, user_bp]:
        if app.config['API_ROOT']:
            bp.url_prefix = app.config['API_ROOT'] + bp.url_prefix
        app.register_blueprint(bp)

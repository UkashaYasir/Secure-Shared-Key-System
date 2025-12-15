from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Supabase Client early to catch config errors
    from securevault.supabase_client import get_supabase
    try:
        get_supabase()
    except Exception as e:
        print(f"Error initializing Supabase: {e}")

    # Register custom template filters
    from securevault.utils.filters import format_operation, format_details, format_datetime, operation_color, operation_icon
    app.jinja_env.filters['format_operation'] = format_operation
    app.jinja_env.filters['format_details'] = format_details
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['operation_color'] = operation_color
    app.jinja_env.filters['operation_icon'] = operation_icon

    from securevault import routes
    app.register_blueprint(routes.bp)

    return app

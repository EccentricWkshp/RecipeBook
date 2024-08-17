import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://recipe_user:YourStrongPassword123!"
        f"@192.168.1.194:1433/RecipeDB"
        f"?driver=ODBC+Driver+18+for+SQL+Server"
        f"&TrustServerCertificate=yes"
    )
    if os.environ.get('SQL_SERVER_INSTANCE'):
        SQLALCHEMY_DATABASE_URI += f"&instance={os.environ.get('SQL_SERVER_INSTANCE')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
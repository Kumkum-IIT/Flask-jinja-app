class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = 'mysecretkey'
    SECURITY_PASSWORD_SALT= 'mysecuritypasswordsalt'
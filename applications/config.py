class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'mysecretkey'
    SECURITY_PASSWORD_SALT = 'mysecuritypasswordsalt'
    JWT_SECRET_KEY = 'myjwtsecretkey'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False

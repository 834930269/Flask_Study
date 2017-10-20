import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KET') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    #QQ邮箱发送者必须和登陆者是同一人
    #gmail可以用这个:
    #FLASKY_MAIL_SENDER = 'Flasky Admin <flask@example.com>'
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    FLASKY_MAIL_SENDER = os.environ.get('MAIL_SENDER')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    UPLOADED_PHOTOS_DEST = os.path.abspath(os.path.join(os.getcwd(),"app/static/Gravatar"))
    FLASKY_POSTS_PER_PAGE = 15

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://'+os.environ.get('DATABASE_USERNAME')+':'+os.environ.get('DATABASE_PASSWORD')+'@localhost/data_dev'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql://'+os.environ.get('DATABASE_USERNAME')+':'+os.environ.get('DATABASE_PASSWORD')+'@localhost/data_test'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://'+os.environ.get('DATABASE_USERNAME')+':'+os.environ.get('DATABASE_PASSWORD')+'@localhost/data'

config={
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,

    'default' : DevelopmentConfig 
}
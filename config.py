import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_pr3cious_secret_key@#!%^')
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False

class ProductionConfig(Config):
    DEBUG = False


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
port = os.getenv('PORT', 8001)
url_api = os.getenv('URL_API',  'http://localhost:8001/')
server_api = os.getenv('SERVER_API',  'http://4d_participatory_api:8001/')
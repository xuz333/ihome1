import redis
class Config:
    """配置信息"""
    SECRET_KEY = "hsjwcf"
    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True # 对cookie中的session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400 # session数据的有效期，单位是秒，3600*24=86400 一天
class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True
class ProductionConfig(Config):
    """生产模式的配置信息"""
    pass
config_map = {
    "develop":DevelopmentConfig,
    "product":ProductionConfig
}


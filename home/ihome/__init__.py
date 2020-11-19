from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
#使用redis存储缓存和session信息
import redis
import logging #注意：flask中没有提供日志的功能，logging是python标准库中提供的日志
from flask_session import Session
from flask_wtf import CSRFProtect

from ihome.utils.commons import RegConverter # 导入万能的正则转换器

# 数据库
# db = SQLAlchemy(app) # db的创建方式一
db = SQLAlchemy() # db的创建方式二
# 创建redis连接对象
redis_storage = None

# 记录日志的四个级别
# logging.error() # 错误级别
# logging.warning() #警告级别
# logging.info() # 信息提示级别
# logging.debug() # 调试级别

from logging.handlers import RotatingFileHandler
# 设置日志的记录等级
# logging.basicConfig(level=logging.DEBUG) # 设置日志为调试级别
# logging.basicConfig(level=logging.INFO) # 设置日志为信息提示级别
logging.basicConfig(level=logging.WARNING) # 设置日志为警告级别
# logging.basicConfig(level=logging.ERROR) # 设置日志为错误级别

# 第一次将日志保存到logs/log文件中，当文件大小超过100M后会将文件改名为log1,同时生成一个新文件log,
# 如果文件大小超过再次超过100M后，会将文件改名为log2,同时生成一个空的日志文件log,依次类推....
# 创建日志记录器，指明日志的保存路径，每个日志文件的最大大小，保存的日志文件个数的上限
file_log_handler = RotatingFileHandler("logs/log",maxBytes=1024*1024*100,backupCount=10)
# 创建日志文件的格式
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
#为刚创建的日志文件创建日志记录器
file_log_handler.setFormatter(formatter)
#为全局的日志工具对象(flask app 使用的)添加日志记录器
logging.getLogger().addHandler(file_log_handler)





# 工厂模式
def create_app(config_name):
    """
    创建flask应用对象
    :param config_name: str 配置模式的名称 ("develop":开发模式; "product":生成模式)
    :return:
    """
    app = Flask(__name__)
    # 根据配置参数的名字获取配置参数类
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    #使用app初始化db
    db.init_app(app)

    # 初始化redis工具
    global redis_storage
    redis_storage = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 利用flask-session,将session数据保存到redis中
    Session(app)

    # 为flask补充csrf防护
    # CSRFProtect(app)

    # 为flask添加自定义转换器
    app.url_map.converters["re"] = RegConverter

    # 注册蓝图
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api,url_prefix="/api/v1.0")

    # 注册提供静态文件的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)

    return app
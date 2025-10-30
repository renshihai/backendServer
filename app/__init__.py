from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import pymysql
import logging
import os
import sys

# MySQL驱动注册
pymysql.install_as_MySQLdb()


# 不添加下面的代码的化，在虚拟环境下运行start_dev.bat 找不到 模块 config
# 将项目根目录添加到 Python 路径（关键！）
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    """应用工厂函数"""
    # app = Flask(__name__)
    app = Flask(__name__, template_folder='../templates')

    # 确定配置
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    '''
    # 加载配置
    if config_name == 'production':
        from config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from config.testing import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    '''
    try:
        config_module = f"config.{config_name}"
        config_class = f"{config_name.capitalize()}Config"
        module = __import__(config_module, fromlist=[config_class])
        app.config.from_object(getattr(module, config_class))
    except (ImportError, AttributeError):
        raise ValueError(f"Invalid config name: {config_name}")

    # 从环境变量覆盖配置
    app.config.from_prefixed_env()

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # 注册蓝图
    from app.routes import main_bp
    # from app.routes import tracking_bp
    app.register_blueprint(main_bp)
    # app.register_blueprint(tracking_bp, url_prefix='/api/track')

    # 配置日志
    setup_logging(app)

    # 开发环境特殊处理
    if app.config['DEBUG']:
        setup_development_environment(app)
    else:
        setup_production_environment(app)

    return app


def setup_logging(app):
    """配置日志"""
    if app.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format=app.config['LOG_FORMAT']
        )
    else:
        # 生产环境日志到文件
        logging.basicConfig(
            level=getattr(logging, app.config['LOG_LEVEL']),
            format=app.config['LOG_FORMAT'],
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )


def setup_development_environment(app):
    """开发环境特殊设置"""
    # 自动创建数据库表
    with app.app_context():
        try:
            from app import models
            db.create_all()
            print("开发环境数据库表创建完成")
        except Exception as e:
            print(f"数据库表创建错误: {e}")

    # 开发环境添加调试工具
    try:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)
    except ImportError:
        pass

def setup_production_environment(app):
    """生产环境特殊设置"""
    # 生产环境安全检查
    if app.config['SECRET_KEY'] == 'your-dev-secret-key-change-this':
        raise ValueError("生产环境必须设置强密钥")

    # 生产环境数据库迁移检查
    with app.app_context():
        try:
            # 检查数据库连接
            db.session.execute('SELECT 1')
            print("生产环境数据库连接正常")
        except Exception as e:
            print(f"生产环境数据库连接失败: {e}")
            raise
from .base import BaseConfig
import os


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""

    # 调试模式
    DEBUG = True
    TESTING = False

    # 开发环境数据库 - 使用SQLite便于开发
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        # f'sqlite:///{os.path.join(basedir, 'app.db')}'
        f'sqlite:///app.db'
    )

    # 开发环境特殊配置
    TRACKING_BUFFER_SIZE = 50  # 开发环境减小缓冲
    LOG_LEVEL = 'DEBUG'  # 开发环境更详细的日志

    # 开发服务器配置
    HOST = '127.0.0.1'
    PORT = 5000

    # 开发环境允许的域名
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

    # 开发环境不验证HTTPS
    PREFERRED_URL_SCHEME = 'http'

    # 开发环境禁用缓存
    SEND_FILE_MAX_AGE_DEFAULT = 0
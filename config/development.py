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
        # 'sqlite:///app.db'
        "mysql+pymysql://root:0210blF!@localhost/tracking_dev"
        # mysql+pymysql://用户名:密码@主机:端口/数据库名
        # "mysql+pymysql://root:ZNdoBekJXTpEbGiECqaPvnNyyGLSvfEu@crossover.proxy.rlwy.net:13598/railway"
    )
    # DATABASE_URL = "mysql+pymysql://root:0210blF!@localhost/behavior_db"
    print("当前db: ", SQLALCHEMY_DATABASE_URI)
    # 开发环境特殊配置
    TRACKING_BUFFER_SIZE = 50  # 开发环境减小缓冲
    LOG_LEVEL = 'DEBUG'  # 开发环境更详细的日志

    # 开发服务器配置
    # HOST = '127.0.0.1'
    # 核心原因：0.0.0.0 的含义
    # 0.0.0.0 是一个特殊的 IP 地址，表示绑定服务器上的所有可用网络接口（包括本地回环地址、局域网 IP 等）。当 Flask 绑定到 0.0.0.0 时，它会监听服务器上所有活跃的网络接口，因此运行时会列出所有可用的访问地址：
    # 127.0.0.1：本地回环地址（只能在本机访问）。
    # 192.168.1.135：你的电脑在局域网中的 IP 地址（同一局域网内的设备可通过此地址访问）。
    HOST = '0.0.0.0'
    PORT = 7000

    # 开发环境允许的域名
    # ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    ALLOWED_HOSTS = ['localhost', '0.0.0.0']

    # 开发环境不验证HTTPS
    PREFERRED_URL_SCHEME = 'http'

    # 开发环境禁用缓存
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # MySQL连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
from .base import BaseConfig
import os


class ProductionConfig(BaseConfig):
    """生产环境配置"""

    # 生产环境关闭调试
    DEBUG = False
    TESTING = False

    # 生产环境数据库 - 使用MySQL/PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        # 'mysql+pymysql://user:password@localhost/tracking_prod'
        # 'mysql://root:MkHvotVOKvHijvUowSITOmBCkiQBxEtL@crossover.proxy.rlwy.net:13598/railway'
        'mysql+pymysql://root:password@localhost/tracking_prod'
    )

    # 生产环境安全配置
    # SECRET_KEY='your-super-secret-key-change-this-in-production'
    # JWT_SECRET_KEY='your-jwt-secret-key-change-this-too'

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置SECRET_KEY环境变量")

    # 生产环境优化配置
    TRACKING_BUFFER_SIZE = 1000  # 生产环境增大缓冲
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_size': 20,
        'max_overflow': 30
    }

    # 生产环境域名
    ALLOWED_HOSTS = ['your-domain.com', 'api.your-domain.com']
    PREFERRED_URL_SCHEME = 'https'

    # 生产环境日志配置
    LOG_LEVEL = 'WARNING'

    # 生产环境性能配置
    JSONIFY_PRETTYPRINT_REGULAR = False  # 禁用美化输出提高性能

    # 生产环境安全头部
    SECURITY_HEADERS = True
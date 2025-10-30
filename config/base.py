import os
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
# load_dotenv()

class BaseConfig:
    """基础配置"""

    env_file = '.env.production' if os.environ.get('FLASK_CONFIG') == 'production' else '.env'
    load_dotenv(env_file)

    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 埋点相关配置
    TRACKING_ENABLED = True
    TRACKING_BUFFER_SIZE = 100  # 内存缓冲条数

    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
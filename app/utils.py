from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
import re


def hash_password(password):
    """对密码进行哈希处理"""
    return generate_password_hash(password)


def check_password(password_hash, password):
    """检查密码是否匹配"""
    return check_password_hash(password_hash, password)


def get_client_info():
    """获取客户端信息"""
    # 获取真实IP地址（考虑代理情况）
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr

    return {
        'ip_address': ip,
        'user_agent': request.headers.get('User-Agent'),
        'referrer': request.headers.get('Referer')
    }


def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """验证密码强度"""
    # 至少8个字符，包含字母和数字
    if len(password) < 8:
        return False, "密码至少需要8个字符"

    if not any(char.isdigit() for char in password):
        return False, "密码必须包含至少一个数字"

    if not any(char.isalpha() for char in password):
        return False, "密码必须包含至少一个字母"

    return True, "密码强度足够"
from app import db
from datetime import datetime
import json


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    # 关联关系：一个用户可以有多个事件
    events = db.relationship('Event', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """将用户对象转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    """埋点事件模型"""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    event_type = db.Column(db.String(50), nullable=False)  # 事件类型：click、view、login等
    event_name = db.Column(db.String(100), nullable=False)  # 事件名称
    page_url = db.Column(db.String(500))  # 页面URL
    element_id = db.Column(db.String(100))  # 元素ID
    event_metadata = db.Column(db.Text)  # 额外数据，存储为JSON格式
    ip_address = db.Column(db.String(45))  # IP地址
    user_agent = db.Column(db.Text)  # 用户代理
    created_at = db.Column(db.DateTime, default=datetime.now(), index=True)

    def to_dict(self):
        """将事件对象转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'event_name': self.event_name,
            'page_url': self.page_url,
            'element_id': self.element_id,
            'event_metadata': json.loads(self.event_metadata) if self.event_metadata else {},
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Event {self.event_type}:{self.event_name}>'
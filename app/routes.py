import datetime
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from app import db
from app.models import User, Event
from app.utils import hash_password, check_password, get_client_info, validate_email, validate_password
import json
import pandas as pd
from io import BytesIO
from flask import send_file
import tempfile
import os


# 获取项目根目录（app 文件夹的上级目录）
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 拼接模板文件夹路径（根目录下的 templates）
# TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# 用绝对路径配置 template_folder
# main_bp = Blueprint('main', __name__, template_folder=TEMPLATE_DIR)

# # 创建蓝图
main_bp = Blueprint('main', __name__)


@main_bp.route('/api/register', methods=['POST'])
def register():
    """
    用户注册接口
    """
    try:
        data = request.get_json()

        # 验证必要字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必要字段: {field}'}), 400

        # 验证邮箱格式
        if not validate_email(data['email']):
            return jsonify({'error': '邮箱格式不正确'}), 400

        # 验证密码强度
        is_valid, password_msg = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': password_msg}), 400

        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400

        # 检查邮箱是否已存在
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已存在'}), 400

        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password'])
        )

        db.session.add(user)
        db.session.commit()

        # 创建访问令牌
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': '用户注册成功',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/login', methods=['POST'])
def login():
    """
    用户登录接口
    """
    try:
        data = request.get_json()

        # 验证必要字段
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': '需要用户名和密码'}), 400

        # 查找用户
        user = User.query.filter_by(username=data['username']).first()

        # 验证用户和密码
        if user and check_password(user.password_hash, data['password']):
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'message': '登录成功',
                'access_token': access_token,
                'user': user.to_dict()
            })

        return jsonify({'error': '用户名或密码错误'}), 401

    except Exception as e:
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/events', methods=['POST'])
@jwt_required()
def record_event():
    """
    记录埋点事件接口
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        client_info = get_client_info()

        # 验证必要字段
        if not data.get('event_name'):
            return jsonify({'error': '事件名称不能为空'}), 400

        # 创建事件记录
        event = Event(
            user_id=current_user_id,
            event_type=data.get('event_type', 'custom'),
            event_name=data.get('event_name'),
            page_url=data.get('page_url'),
            element_id=data.get('element_id'),
            event_metadata=json.dumps(data.get('event_metadata', {})),
            ip_address=client_info['ip_address'],
            user_agent=client_info['user_agent']
        )

        db.session.add(event)
        db.session.commit()

        return jsonify({
            'message': '事件记录成功',
            'event': event.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/events/public', methods=['GET'])
def get_events_public():
    """
    公开获取事件数据接口（仅用于测试）
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        events_query = Event.query

        # 按时间倒序排列并分页
        events = events_query.order_by(Event.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'events': [event.to_dict() for event in events.items],
            'total': events.total,
            'pages': events.pages,
            'current_page': page,
            'per_page': per_page
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/events', methods=['GET'])
@jwt_required()
def get_events():
    """
    获取用户事件数据接口
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # 限制每页最多100条

        # 查询用户的事件数据
        # current_user_id = int(get_jwt_identity())
        # events_query = Event.query.filter_by(user_id=current_user_id)
        events_query = Event.query

        # 按时间倒序排列并分页
        events = events_query.order_by(Event.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'events': [event.to_dict() for event in events.items],
            'total': events.total,
            'pages': events.pages,
            'current_page': page,
            'per_page': per_page
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """
    获取用户个人信息接口
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        return jsonify({'user': user.to_dict()})

    except Exception as e:
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        'status': 'healthy',
        'message': '服务器运行正常',
        'timestamp': datetime.datetime.now().isoformat()
    })


# 错误处理
@main_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': '资源未找到'}), 404


@main_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500


@main_bp.route('/admin/events')
def events_page():
    """埋点事件浏览页面"""
    return render_template('events.html')

@main_bp.route('/login')
@main_bp.route('/')
def login_page():
    """登录页面"""
    return render_template('login.html')  # 你需要创建这个页面


@main_bp.route('/api/admin/events', methods=['GET'])
# @jwt_required()
def get_admin_events():
    """
    管理员获取事件数据接口 - 支持排序、筛选和分组
    """
    try:
        # 获取查询参数
        user_id = request.args.get('user_id', type=int)
        page_url = request.args.get('page_url')
        event_type = request.args.get('event_type')
        event_name = request.args.get('event_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 排序参数
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)  # 限制每页最多200条

        # 构建查询
        query = Event.query

        # 应用筛选条件
        if user_id:
            query = query.filter(Event.user_id == user_id)
        if page_url:
            query = query.filter(Event.page_url.contains(page_url))
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if event_name:
            query = query.filter(Event.event_name.contains(event_name))
        if start_date:
            query = query.filter(Event.created_at >= start_date)
        if end_date:
            query = query.filter(Event.created_at <= end_date)

        # 应用排序
        if sort_by == 'created_at':
            if sort_order == 'asc':
                query = query.order_by(Event.created_at.asc())
            else:
                query = query.order_by(Event.created_at.desc())
        elif sort_by == 'page_url':
            if sort_order == 'asc':
                query = query.order_by(Event.page_url.asc())
            else:
                query = query.order_by(Event.page_url.desc())

        # 执行分页查询
        events = query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # 获取事件统计
        total_events = query.count()

        return jsonify({
            'events': [event.to_dict() for event in events.items],
            'total': events.total,
            'pages': events.pages,
            'current_page': page,
            'per_page': per_page,
            'total_events': total_events
        })

    except Exception as e:
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """
    获取管理统计信息（总览和事件详细统计）
    """
    try:
        from sqlalchemy import func, distinct
        from datetime import datetime, date, timedelta

        # 总事件数
        total_events = Event.query.count()

        # 总用户数
        total_users = User.query.count()

        # 今日事件数
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_events = Event.query.filter(Event.created_at >= today_start).count()

        # 唯一页面数
        # 这行代码的用途是统计唯一页面URL的数量，让我详细解释每个部分的作用和实际应用场景：
        '''代码的用途是统计数据库中不同页面URL的数量。让我们详细分解一下：
            Event.page_url：这指的是Event模型（表）中的page_url字段，该字段存储了事件发生的页面URL。
            distinct(Event.page_url)：使用SQL的DISTINCT关键字，返回不重复的page_url值。
            func.count(...)：这是一个SQL函数，用于计算行的数量。在这里，它计算不重复的page_url的数量。
            db.session.query(...)：这是一个SQLAlchemy查询，用于构建数据库查询。
            .scalar()：执行查询并返回第一行的第一列的值。因为这里我们使用的是count函数，所以返回的就是统计的数量。
            or 0：如果查询结果为None（例如，当没有事件记录时），则返回0。
            所以，这行代码的目的是获取Event表中不同页面URL的数量，如果没有则返回0。
            通常，这个指标可以用来了解网站或应用中有多少不同的页面被用户访问过，从而分析用户活动的分布范围。
        '''
        unique_pages = db.session.query(
            func.count(distinct(Event.page_url))
        ).scalar() or 0

        # 事件类型分布
        event_type_stats = db.session.query(
            Event.event_type,
            func.count(Event.id).label('count')
        ).group_by(Event.event_type).all()

        # 页面统计（前10）
        page_stats = db.session.query(
            Event.page_url,
            func.count(Event.id).label('count')
        ).filter(Event.page_url.isnot(None)).group_by(Event.page_url).order_by(func.count(Event.id).desc()).limit(
            10).all()

        # 用户统计（前10）
        user_stats = db.session.query(
            Event.user_id,
            func.count(Event.id).label('count')
        ).group_by(Event.user_id).order_by(func.count(Event.id).desc()).limit(10).all()

        # 最近7天活动
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_activity = db.session.query(
            func.date(Event.created_at).label('date'),
            func.count(Event.id).label('count')
        ).filter(Event.created_at >= seven_days_ago) \
            .group_by(func.date(Event.created_at)) \
            .order_by(func.date(Event.created_at).desc()).all()

        # 格式化最近活动日期
        recent_activity_formatted = []
        for activity in recent_activity:
            activity_date = activity.date
            if isinstance(activity_date, (datetime, date)):
                activity_date_str = activity_date.isoformat()
            else:
                activity_date_str = str(activity_date)

            recent_activity_formatted.append({
                'date': activity_date_str,
                'count': activity.count
            })

        return jsonify({
            'total_events': total_events,
            'total_users': total_users,
            'today_events': today_events,
            'unique_pages': unique_pages,
            'type_stats': [
                {'type': stat[0], 'count': stat[1]}
                for stat in event_type_stats
            ],
            'page_stats': [
                {'page_url': stat[0], 'count': stat[1]}
                for stat in page_stats
            ],
            'user_stats': [
                {'user_id': stat[0], 'count': stat[1]}
                for stat in user_stats
            ],
            'recent_activity': recent_activity_formatted
        })

    except Exception as e:
        print(f"统计接口错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500

@main_bp.route('/api/admin/users', methods=['GET'])
# @jwt_required()
def get_users():
    """
    获取用户列表（用于筛选）
    """
    try:
        users = User.query.all()
        return jsonify({
            'users': [{'id': user.id, 'username': user.username} for user in users]
        })
    except Exception as e:
        return jsonify({'error': '服务器内部错误', 'details': str(e)}), 500


@main_bp.route('/api/admin/events/export/test', methods=['GET'])
def export_events_test():
    """
    导出功能测试端点
    """
    try:
        # 测试基本功能
        import pandas as pd
        from io import BytesIO

        # 创建测试数据
        data = {
            '测试列1': ['数据1', '数据2', '数据3'],
            '测试列2': [1, 2, 3]
        }
        df = pd.DataFrame(data)

        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)

        return jsonify({
            'message': '导出测试成功',
            'data_created': True,
            'pandas_available': True
        })

    except ImportError as e:
        return jsonify({
            'error': '依赖包未安装',
            'details': str(e),
            'required_packages': ['pandas', 'openpyxl']
        }), 500
    except Exception as e:
        return jsonify({
            'error': '测试失败',
            'details': str(e)
        }), 500

@main_bp.route('/api/admin/events/export', methods=['GET'])
def export_events():
    """
    导出事件数据接口
    支持格式：csv, excel
    """
    try:
        # 获取查询参数
        user_id = request.args.get('user_id', type=int)
        page_url = request.args.get('page_url')
        event_type = request.args.get('event_type')
        event_name = request.args.get('event_name')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        export_format = request.args.get('format', 'csv')  # csv 或 excel

        # 构建查询
        query = Event.query

        # 应用筛选条件
        if user_id:
            query = query.filter(Event.user_id == user_id)
        if page_url:
            query = query.filter(Event.page_url.contains(page_url))
        if event_type:
            query = query.filter(Event.event_type == event_type)
        if event_name:
            query = query.filter(Event.event_name.contains(event_name))
        if start_date:
            query = query.filter(Event.created_at >= start_date)
        if end_date:
            query = query.filter(Event.created_at <= end_date)

        # 按时间倒序排列
        events = query.order_by(Event.created_at.desc()).all()

        if not events:
            return jsonify({'error': '没有找到可导出的数据'}), 404

        # 准备数据
        data = []
        for event in events:
            # 解析事件数据
            event_data = {}

            data.append({
                '事件ID': event.id,
                '用户ID': event.user_id,
                '事件类型': event.event_type,
                '事件名称': event.event_name,
                '页面URL': event.page_url or '',
                '元素ID': event.element_id or '',
                'IP地址': event.ip_address or '',
                'User Agent': event.user_agent or '',
                '事件数据': json.dumps(event_data, ensure_ascii=False) if event_data else '',
                '创建时间': event.created_at.isoformat() if hasattr(event.created_at, 'isoformat') else str(
                    event.created_at)
            })

        # 创建 DataFrame
        df = pd.DataFrame(data)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"事件数据_{timestamp}"

        if export_format.lower() == 'excel':
            # 导出为 Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='事件数据', index=False)

                # 获取工作表并调整列宽
                worksheet = writer.sheets['事件数据']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'{filename}.xlsx'
            )

        else:
            # 导出为 CSV
            output = BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')  # utf-8-sig 会自动添加 BOM

            output.seek(0)

            response = send_file(
                output,
                mimetype='text/csv; charset=utf-8',  # 明确指定字符集
                as_attachment=True,
                download_name=f'{filename}.csv'
            )

            # 添加额外的头部信息
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            # 添加缓存控制头部，避免缓存问题
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'

            return response
    except Exception as e:
        print(f"导出错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '导出失败', 'details': str(e)}), 500


@main_bp.route('/api/admin/events/batch', methods=['DELETE'])
def batch_delete_events():
    """
    批量删除事件数据
    """
    try:
        data = request.get_json()

        if not data or 'event_ids' not in data:
            return jsonify({'error': '需要提供事件ID列表'}), 400

        event_ids = data['event_ids']
        if not isinstance(event_ids, list):
            return jsonify({'error': 'event_ids 必须是数组'}), 400

        # 删除事件
        deleted_count = Event.query.filter(Event.id.in_(event_ids)).delete()
        db.session.commit()

        return jsonify({
            'message': f'成功删除 {deleted_count} 个事件',
            'deleted_count': deleted_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除失败', 'details': str(e)}), 500

# # 在你的Flask routes.py中添加代理接口
# @main_bp.route('/proxy/icon-negative-list')
# def proxy_icon_list():
#     s3_url = "https://avira-pwm-extensions.s3.eu-central-1.amazonaws.com/icon-negative-list.json"
#     try:
#         response = request.get(s3_url)
#         return jsonify(response.json()), response.status_code
#     except Exception as e:
#         return jsonify({"error": "代理请求失败"}), 500
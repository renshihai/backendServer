import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class BackendClient:
    """
    Flask 后端服务器 Python 客户端
    封装所有 API 接口调用
    """

    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """
        初始化客户端
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.user_id = None
        self.session = requests.Session()

        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BackendClient/1.0'
        })

    def _handle_response(self, response: requests.Response) -> Dict:
        """
        统一处理响应

        Args:
            response: requests 响应对象

        Returns:
            解析后的 JSON 数据
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {e}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_data.get('msg', error_msg))
            except:
                pass
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {e}")
        except json.JSONDecodeError:
            raise Exception("响应不是有效的JSON格式")

    def _get_auth_headers(self) -> Dict:
        """
        获取认证头

        Returns:
            包含认证头的字典
        """
        if not self.token:
            raise Exception("请先登录获取token")
        return {'Authorization': f'Bearer {self.token}'}

    # ===== 用户认证相关接口 =====

    def register(self, username: str, email: str, password: str) -> Dict:
        """
        用户注册

        Args:
            username: 用户名
            email: 邮箱
            password: 密码

        Returns:
            注册结果
        """
        url = f"{self.base_url}/api/register"
        data = {
            'username': username,
            'email': email,
            'password': password
        }

        response = self.session.post(url, json=data)
        result = self._handle_response(response)

        # 如果注册成功，自动保存token
        if 'access_token' in result:
            self.token = result['access_token']
            self.user_id = result.get('user', {}).get('id')

        return result

    def login(self, username: str, password: str) -> Dict:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录结果
        """
        url = f"{self.base_url}/api/login"
        data = {
            'username': username,
            'password': password
        }

        response = self.session.post(url, json=data)
        result = self._handle_response(response)

        # 保存token和用户ID
        if 'access_token' in result:
            self.token = result['access_token']
            self.user_id = result.get('user', {}).get('id')

        return result

    def logout(self):
        """
        用户登出（清除本地token）
        """
        self.token = None
        self.user_id = None

    def get_user_profile(self) -> Dict:
        """
        获取当前用户信息

        Returns:
            用户信息
        """
        url = f"{self.base_url}/api/user/profile"
        headers = self._get_auth_headers()

        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    # ===== 事件管理相关接口 =====

    def record_event(self,
                     event_name: str,
                     event_type: str = "custom",
                     page_url: Optional[str] = None,
                     element_id: Optional[str] = None,
                     metadata: Optional[Dict] = None) -> Dict:
        """
        记录埋点事件

        Args:
            event_name: 事件名称
            event_type: 事件类型，默认 "custom"
            page_url: 页面URL
            element_id: 元素ID
            metadata: 额外元数据

        Returns:
            事件记录结果
        """
        url = f"{self.base_url}/api/events"
        headers = self._get_auth_headers()

        data = {
            'event_name': event_name,
            'event_type': event_type
        }

        if page_url:
            data['page_url'] = page_url
        if element_id:
            data['element_id'] = element_id
        if metadata:
            data['metadata'] = metadata

        response = self.session.post(url, headers=headers, json=data)
        return self._handle_response(response)

    def get_events(self,
                   page: int = 1,
                   per_page: int = 20) -> Dict:
        """
        获取当前用户的事件列表

        Args:
            page: 页码
            per_page: 每页数量

        Returns:
            事件列表
        """
        url = f"{self.base_url}/api/events"
        headers = self._get_auth_headers()

        params = {
            'page': page,
            'per_page': per_page
        }

        response = self.session.get(url, headers=headers, params=params)
        return self._handle_response(response)

    # ===== 管理员接口 =====

    def get_admin_events(self,
                         user_id: Optional[int] = None,
                         event_type: Optional[str] = None,
                         event_name: Optional[str] = None,
                         page_url: Optional[str] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         sort_by: str = "created_at",
                         sort_order: str = "desc",
                         page: int = 1,
                         per_page: int = 50) -> Dict:
        """
        管理员获取事件数据（支持筛选和排序）

        Args:
            user_id: 用户ID筛选
            event_type: 事件类型筛选
            event_name: 事件名称筛选
            page_url: 页面URL筛选
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            sort_by: 排序字段 (created_at, page_url)
            sort_order: 排序方式 (asc, desc)
            page: 页码
            per_page: 每页数量

        Returns:
            事件数据
        """
        url = f"{self.base_url}/api/admin/events"
        headers = self._get_auth_headers()

        params = {
            'sort_by': sort_by,
            'sort_order': sort_order,
            'page': page,
            'per_page': per_page
        }

        # 添加筛选参数
        if user_id:
            params['user_id'] = user_id
        if event_type:
            params['event_type'] = event_type
        if event_name:
            params['event_name'] = event_name
        if page_url:
            params['page_url'] = page_url
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        response = self.session.get(url, headers=headers, params=params)
        return self._handle_response(response)

    def get_event_stats(self) -> Dict:
        """
        获取事件统计信息

        Returns:
            统计信息
        """
        url = f"{self.base_url}/api/admin/stats"
        headers = self._get_auth_headers()

        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    def get_users_list(self) -> Dict:
        """
        获取用户列表（用于筛选）

        Returns:
            用户列表
        """
        url = f"{self.base_url}/api/admin/users"
        headers = self._get_auth_headers()

        response = self.session.get(url, headers=headers)
        return self._handle_response(response)

    # ===== 系统接口 =====

    def health_check(self) -> Dict:
        """
        健康检查

        Returns:
            健康状态
        """
        url = f"{self.base_url}/api/health"

        response = self.session.get(url)
        return self._handle_response(response)

    # ===== 工具方法 =====

    def set_token(self, token: str):
        """
        手动设置token（用于从外部获取token的情况）

        Args:
            token: JWT token
        """
        self.token = token

    def get_token(self) -> Optional[str]:
        """
        获取当前token

        Returns:
            当前token或None
        """
        return self.token

    def is_authenticated(self) -> bool:
        """
        检查是否已认证

        Returns:
            是否已认证
        """
        return self.token is not None

    def test_connection(self) -> bool:
        """
        测试服务器连接

        Returns:
            连接是否成功
        """
        try:
            result = self.health_check()
            return result.get('status') == 'healthy'
        except:
            return False

    def batch_record_events(self, events: List[Dict]) -> List[Dict]:
        """
        批量记录事件

        Args:
            events: 事件列表

        Returns:
            批量记录结果
        """
        results = []
        for event in events:
            try:
                result = self.record_event(**event)
                results.append({'success': True, 'data': result})
            except Exception as e:
                results.append({'success': False, 'error': str(e)})
        return results
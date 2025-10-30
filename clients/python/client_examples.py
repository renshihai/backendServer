from backend_client import BackendClient
import time
import random
from datetime import datetime, timedelta

def user_register(client):
    try:
        register_result = client.register(
            username="python_client_user_4",
            email="client_4@example.com",
            password="password123"
        )
        print("✅ 用户注册成功")
    except Exception as e:
        print(f"⚠️ 注册失败（可能用户已存在）: {e}")


def user_login(client,user_name, password):
    try:
        login_result = client.login(user_name,password)
        print(f"✅ 用户登录成功，用户ID: {client.user_id}")
        print(f"   Token: {client.token[:20]}...")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return


def  full_create():
    # 创建客户端实例
    client = BackendClient("http://127.0.0.1:7000")
    # client = BackendClient("http://120.79.213.91:7000")

    print("=== Flask后端服务器Python客户端示例 ===")

    # 测试连接
    print("\n1. 测试服务器连接...")
    if client.test_connection():
        print("✅ 服务器连接成功")
    else:
        print("❌ 服务器连接失败")
        return

    # 用户注册和登录示例
    print("\n2. 用户认证测试...")

    # 注册新用户
    user_register(client)
    # 用户登录
    user_login(client,"python_client_user_1", "password123")

    # 获取用户信息
    try:
        profile = client.get_user_profile()
        print(f"✅ 获取用户信息成功: {profile['user']['username']}")
    except Exception as e:
        print(f"❌ 获取用户信息失败: {e}")

    # 记录事件示例
    print("\n3. 记录事件测试...")

    # 记录单个事件
    try:
        event_result = client.record_event(
            event_name="python_client_test",
            event_type="custom",
            page_url="/python-test",
            element_id="test-button",
            metadata={
                "python_version": "3.8+",
                "test_timestamp": datetime.now().isoformat(),
                "random_value": random.randint(1, 100)
            }
        )
        print("✅ 事件记录成功")
    except Exception as e:
        print(f"❌ 事件记录失败: {e}")

    # 批量记录事件
    print("\n4. 批量记录事件测试...")

    events_to_record = [
        {
            "event_name": "page_view",
            "event_type": "view",
            "page_url": "/home",
            "metadata": {"source": "batch_test"}
        },
        {
            "event_name": "button_click",
            "event_type": "click",
            "page_url": "/home",
            "element_id": "nav-button",
            "metadata": {"button_type": "primary"}
        },
        {
            "event_name": "form_submit",
            "event_type": "submit",
            "page_url": "/contact",
            "metadata": {"form_name": "contact_form"}
        }
    ]

    batch_results = client.batch_record_events(events_to_record)
    success_count = sum(1 for r in batch_results if r['success'])
    print(f"✅ 批量记录完成: {success_count}/{len(events_to_record)} 成功")

    # 获取事件列表
    print("\n5. 获取事件列表测试...")

    try:
        events = client.get_events(page=1, per_page=10)
        print(f"✅ 获取到 {len(events['events'])} 个事件")
        for event in events['events'][:3]:  # 显示前3个
            print(f"   - {event['event_name']} ({event['created_at']})")
    except Exception as e:
        print(f"❌ 获取事件列表失败: {e}")

    # 管理员功能测试
    print("\n6. 管理员功能测试...")

    # 获取事件统计
    try:
        stats = client.get_event_stats()
        print("✅ 获取事件统计成功:")
        print(f"   - 事件类型: {len(stats['type_stats'])} 种")
        print(f"   - 热门页面: {len(stats['page_stats'])} 个")
        print(f"   - 活跃用户: {len(stats['user_stats'])} 个")
    except Exception as e:
        print(f"❌ 获取事件统计失败: {e}")

    # 高级事件查询
    try:
        admin_events = client.get_admin_events(
            event_type="click",
            sort_by="created_at",
            sort_order="desc",
            page=1,
            per_page=5
        )
        print(f"✅ 高级查询获取到 {len(admin_events['events'])} 个点击事件")
    except Exception as e:
        print(f"❌ 高级查询失败: {e}")

    # 获取用户列表
    try:
        users = client.get_users_list()
        print(f"✅ 获取用户列表成功: {len(users['users'])} 个用户")
    except Exception as e:
        print(f"❌ 获取用户列表失败: {e}")

    print("\n=== 测试完成 ===")


def advanced_usage_examples():
    """高级使用示例"""
    print("\n=== 高级使用示例 ===")

    client = BackendClient("http://127.0.0.1:5000")

    # 示例1: 从文件加载配置
    def load_config_from_file():
        # 模拟从配置文件加载认证信息
        config = {
            'username': 'test_user',
            'password': 'test_password',
            'server_url': 'http://127.0.0.1:5000'
        }
        return config

    # 示例2: 自动重试机制
    def record_event_with_retry(client, event_data, max_retries=3):
        for attempt in range(max_retries):
            try:
                return client.record_event(**event_data)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"第 {attempt + 1} 次尝试失败，重试...")
                time.sleep(1)

    # 示例3: 定期收集统计信息
    def collect_periodic_stats(client, interval_minutes=5):
        """定期收集统计信息"""
        while True:
            try:
                stats = client.get_event_stats()
                print(f"[{datetime.now()}] 统计信息收集完成")
                # 这里可以保存到文件或数据库
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("统计收集已停止")
                break
            except Exception as e:
                print(f"统计收集失败: {e}")
                time.sleep(60)  # 失败后等待1分钟再重试

    # 示例4: 监控特定用户行为
    def monitor_user_activity(client, user_id, check_interval=30):
        """监控特定用户的活动"""
        last_check = datetime.now() - timedelta(minutes=5)

        while True:
            try:
                # 查询最近5分钟的用户活动
                events = client.get_admin_events(
                    user_id=user_id,
                    start_date=last_check.isoformat(),
                    sort_by="created_at",
                    sort_order="desc"
                )

                if events['events']:
                    print(f"用户 {user_id} 有新活动: {len(events['events'])} 个事件")
                    for event in events['events']:
                        print(f"  - {event['event_name']} at {event['created_at']}")

                last_check = datetime.now()
                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("监控已停止")
                break
            except Exception as e:
                print(f"监控失败: {e}")
                time.sleep(60)


if __name__ == "__main__":
    if True:
        full_create()
        advanced_usage_examples()
    else:
        client = BackendClient("http://127.0.0.1:7000")
        user_login(client, "python_client_user_2", "password123")
        events_to_record = []
        for i in range(10):
            events_to_record.append(
            {
                "event_name": f"page_word_{i:03}",
                "event_type": "view",
                "page_url": "/home",
                "metadata": {"source": "batch_test"}
            }
            )
        batch_results = client.batch_record_events(events_to_record)
        success_count = sum(1 for r in batch_results if r['success'])
        print(f"✅ 批量记录完成: {success_count}/{len(events_to_record)} 成功")



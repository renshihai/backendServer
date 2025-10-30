#!/usr/bin/env python3
import requests
import json


def test_production():
    base_url = "http://localhost:7000"

    # 健康检查
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"健康检查失败: {e}")

    # 测试数据库连接
    try:
        response = requests.get(f"{base_url}/api/admin/stats")
        print(f"统计接口: {response.status_code}")
        if response.status_code == 200:
            print("数据库连接正常")
    except Exception as e:
        print(f"数据库测试失败: {e}")


if __name__ == '__main__':
    test_production()
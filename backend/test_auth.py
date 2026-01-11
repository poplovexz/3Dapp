"""
测试认证API的简单脚本

使用方法：
1. 启动后端服务：cd backend && python main.py
2. 运行测试脚本：python test_auth.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_send_code():
    """测试发送验证码"""
    print("\n=== 测试1: 发送验证码 ===")
    response = requests.post(
        f"{BASE_URL}/auth/send-code",
        json={"identifier": "13800138000", "code_type": "register"},
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_register():
    """测试用户注册"""
    print("\n=== 测试2: 用户注册 ===")
    # 注意：需要先获取真实的验证码
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "phone_number": "13800138000",
            "email": None,
            "password": "Test1234",
            "country_code": "+86",
            "region": "CN",
            "verification_code": "123456",  # 这里需要真实的验证码
        },
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_login():
    """测试用户登录"""
    print("\n=== 测试3: 用户登录 ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"identifier": "13800138000", "password": "Test1234"},
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_get_poses():
    """测试获取姿势列表"""
    print("\n=== 测试4: 获取姿势列表 ===")
    response = requests.get(f"{BASE_URL}/poses")
    print(f"状态码: {response.status_code}")
    poses = response.json()
    print(f"姿势数量: {len(poses['poses'])}")
    if poses["poses"]:
        print(
            f"第一个姿势: {poses['poses'][0]['name']} - {poses['poses'][0]['description']}"
        )


if __name__ == "__main__":
    print("=" * 50)
    print("角度拍摄 - 认证API测试")
    print("=" * 50)

    # 运行所有测试
    try:
        test_get_poses()  # 先测试不需要认证的API

        print("\n注意：注册和登录测试需要真实的验证码")
        print("1. 请先运行 test_send_code() 获取验证码")
        print("2. 将验证码替换到 test_register() 中")
        print("3. 再运行注册和登录测试")

        print("\n可选测试：")
        print("- test_send_code(): 发送验证码到手机")
        print("- test_register(): 用户注册（需要真实验证码）")
        print("- test_login(): 用户登录")
        print("- test_get_poses(): 获取姿势列表")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback

        traceback.print_exc()

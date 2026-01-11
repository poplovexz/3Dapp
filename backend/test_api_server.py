import requests
import json
import time


BASE_URL = "http://127.0.0.1:8000"


def print_response(response):
    print(f"\n{response.request.method} {response.url}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}\n")
    return response


def test_health_check():
    print("\n" + "=" * 60)
    print("测试 1: 健康检查")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    assert response.status_code == 200
    return True


def test_send_code():
    print("\n" + "=" * 60)
    print("测试 2: 发送验证码（模拟）")
    print("=" * 60)
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/send-code",
        json={"identifier": "test@example.com", "type": "register"},
    )
    print_response(response)
    return True


def test_register():
    print("\n" + "=" * 60)
    print("测试 3: 注册用户")
    print("=" * 60)
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "identifier": "test@example.com",
            "code": "123456",
            "password": "TestPass123",
        },
    )
    print_response(response)
    if response.status_code == 200:
        return response.json()["data"]["token"]
    return None


def test_login():
    print("\n" + "=" * 60)
    print("测试 4: 用户登录")
    print("=" * 60)
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"identifier": "test@example.com", "password": "TestPass123"},
    )
    print_response(response)
    if response.status_code == 200:
        return response.json()["data"]["token"]
    return None


def test_get_me(token):
    print("\n" + "=" * 60)
    print("测试 5: 获取用户信息")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print_response(response)
    assert response.status_code == 200
    return response.json()["data"]["user_id"]


def test_get_poses(token):
    print("\n" + "=" * 60)
    print("测试 6: 获取姿势列表")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/poses", headers=headers)
    print_response(response)
    assert response.status_code == 200
    poses = response.json()["data"]
    if poses:
        return poses[0]["id"]
    return None


def test_generate_image(token, pose_id):
    print("\n" + "=" * 60)
    print("测试 7: 生成图片")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    fake_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBD"
    response = requests.post(
        f"{BASE_URL}/api/v1/generate",
        headers=headers,
        json={"pose_id": pose_id, "source_image_b64": fake_image},
    )
    print_response(response)
    assert response.status_code == 200
    return response.json()["data"]["job_id"]


def test_generate_360(token):
    print("\n" + "=" * 60)
    print("测试 8: 生成360视频")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    fake_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBD"
    response = requests.post(
        f"{BASE_URL}/api/v1/generate-360",
        headers=headers,
        json={"source_image_b64": fake_image, "frame_count": 8},
    )
    print_response(response)
    assert response.status_code == 200


def test_job_status(token, job_id):
    print("\n" + "=" * 60)
    print("测试 9: 查询任务状态")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/job/{job_id}", headers=headers)
    print_response(response)
    assert response.status_code == 200


def test_admin_login():
    print("\n" + "=" * 60)
    print("测试 10: 管理员登录")
    print("=" * 60)
    response = requests.post(
        f"{BASE_URL}/api/v1/admin/login",
        json={"username": "admin", "password": "AdminPass123"},
    )
    print_response(response)
    if response.status_code == 200:
        return response.json()["data"]["token"]
    return None


def test_admin_get_users(admin_token):
    print("\n" + "=" * 60)
    print("测试 11: 管理员获取用户列表")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
    print_response(response)
    assert response.status_code == 200


def test_admin_statistics(admin_token):
    print("\n" + "=" * 60)
    print("测试 12: 管理员获取统计信息")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/v1/admin/statistics", headers=headers)
    print_response(response)
    assert response.status_code == 200


def test_admin_packages(admin_token):
    print("\n" + "=" * 60)
    print("测试 13: 管理员获取套餐列表")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/v1/admin/packages", headers=headers)
    print_response(response)
    assert response.status_code == 200


def test_admin_create_package(admin_token):
    print("\n" + "=" * 60)
    print("测试 14: 管理员创建套餐")
    print("=" * 60)
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.post(
        f"{BASE_URL}/api/v1/admin/packages",
        headers=headers,
        json={
            "name": "测试套餐",
            "price_cents": 999,
            "duration_days": 30,
            "free_generations": 50,
            "custom_pose_limit": 10,
        },
    )
    print_response(response)
    assert response.status_code == 200


def main():
    print("\n" + "=" * 60)
    print("角度拍摄 API - 完整测试套件")
    print("=" * 60)
    print(f"\nAPI地址: {BASE_URL}")
    print("文档地址: {BASE_URL}/docs")

    print("\n提示: 请确保API服务正在运行（python api_server.py）")
    input("\n按Enter开始测试...")

    try:
        test_health_check()
        test_send_code()

        token = test_login()
        if not token:
            print("\n尝试注册...")
            token = test_register()

        if token:
            user_id = test_get_me(token)
            pose_id = test_get_poses(token)
            if pose_id:
                job_id = test_generate_image(token, pose_id)
                test_job_status(token, job_id)
            test_generate_360(token)
        else:
            print("\n登录/注册失败，跳过需要认证的测试")

        admin_token = test_admin_login()
        if admin_token:
            test_admin_get_users(admin_token)
            test_admin_statistics(admin_token)
            test_admin_packages(admin_token)
            test_admin_create_package(admin_token)
        else:
            print("\n管理员登录失败，跳过管理功能测试")

        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到API服务")
        print("请确保API服务正在运行: python api_server.py")
    except AssertionError as e:
        print(f"\n错误: 断言失败 - {e}")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    main()

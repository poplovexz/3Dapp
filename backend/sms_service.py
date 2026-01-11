import requests
import os
from typing import Optional
import json
import time
import hmac
import urllib.parse
from datetime import datetime
import hashlib
import base64


class SMSService:
    """阿里云短信服务"""

    def __init__(self):
        # 从环境变量读取配置
        self.access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID", "")
        self.access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET", "")
        self.sign_name = os.getenv("ALIYUN_SMS_SIGN_NAME", "角度拍摄")  # 短信签名
        self.template_code = os.getenv(
            "ALIYUN_SMS_TEMPLATE_CODE", "SMS_123456789"
        )  # 模板代码

        if not self.access_key_id or not self.access_key_secret:
            print("警告：阿里云短信配置不完整")

    def send_code(self, phone_number: str, code: str) -> bool:
        """
        发送短信验证码

        Args:
            phone_number: 手机号（如：13800138000）
            code: 验证码（6位数字）

        Returns:
            bool: 是否发送成功
        """
        # 检查配置
        if not self.access_key_id or not self.access_key_secret:
            print("阿里云短信配置缺失，发送失败")
            return False

        # 构造请求参数
        params = {
            "PhoneNumbers": phone_number,
            "SignName": self.sign_name,
            "TemplateCode": self.template_code,
            "TemplateParam": json.dumps({"code": code}),
        }

        # 添加公共参数
        common_params = {
            "AccessKeyId": self.access_key_id,
            "Action": "SendSms",
            "Format": "JSON",
            "RegionId": "cn-hangzhou",
            "SignatureMethod": "HMAC-SHA1",
            "SignatureNonce": str(int(time.time() * 1000)),
            "SignatureVersion": "1.0",
            "Timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "Version": "2017-05-25",
        }

        params.update(common_params)

        # 计算签名
        signature = self._calculate_signature(params)
        params["Signature"] = signature

        # 构造请求URL
        url = "https://dysmsapi.aliyuncs.com/?" + urllib.parse.urlencode(params)

        # 发送请求
        try:
            response = requests.get(url, timeout=10)
            result = response.json()

            if result.get("Code") == "OK":
                print(f"短信发送成功：{phone_number}")
                return True
            else:
                print(f"短信发送失败：{result}")
                return False

        except Exception as e:
            print(f"短信发送异常：{e}")
            return False

    def _calculate_signature(self, params: dict) -> str:
        """计算阿里云API签名"""
        # 按字母顺序排序参数
        sorted_params = sorted(params.items())

        # 拼接参数
        canonicalized_query_string = "&".join(
            [
                f"{urllib.parse.quote(str(key), safe='')}={urllib.parse.quote(str(value), safe='')}"
                for key, value in sorted_params
            ]
        )

        string_to_sign = (
            "GET&"
            + urllib.parse.quote("/", safe="")
            + "&"
            + urllib.parse.quote(canonicalized_query_string, safe="")
        )

        # HMAC-SHA1签名
        secret_key = self.access_key_secret or ""
        key = secret_key + "&"
        signature = hmac.new(
            key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1
        ).digest()

        # Base64编码
        signature = base64.b64encode(signature).decode()

        # URL编码
        return urllib.parse.quote(signature, safe="")

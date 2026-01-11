import os
from typing import Optional


class EmailService:
    """邮件服务"""

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY", "")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@anglephoto.com")

        if not self.api_key:
            print("警告：SendGrid配置不完整")

    def send_verification_code(self, to_email: str, code: str) -> bool:
        """
        发送验证码邮件

        Args:
            to_email: 收件人邮箱
            code: 验证码（6位数字）

        Returns:
            bool: 是否发送成功
        """
        if not self.api_key:
            print("SendGrid配置缺失，发送失败")
            return False

        # 尝试导入sendgrid
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
        except ImportError:
            print("SendGrid未安装，使用模拟发送")
            # 模拟发送
            print(f"[模拟] 验证码邮件发送到：{to_email}，验证码：{code}")
            return True

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject="角度拍摄 - 验证码",
            html_content=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">您的验证码</h2>
                    <p style="font-size: 24px; font-weight: bold; color: #0066cc; margin: 20px 0;">
                        {code}
                    </p>
                    <p style="color: #666; font-size: 14px;">
                        验证码5分钟内有效，请勿泄露给他人。
                    </p>
                    <p style="color: #999; font-size: 12px;">
                        如果您没有注册角度拍摄，请忽略此邮件。
                    </p>
                </div>
            """,
        )

        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            if response.status_code == 202:
                print(f"验证码邮件发送成功：{to_email}")
                return True
            else:
                print(f"邮件发送失败：{response.status_code}")
                return False

        except Exception as e:
            print(f"邮件发送异常：{e}")
            return False

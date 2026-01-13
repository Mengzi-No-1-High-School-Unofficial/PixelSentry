"""Camoufox 浏览器自动化助手"""
import asyncio
import logging
from typing import Any

from camoufox.async_api import AsyncCamoufox

from app.config import settings

logger = logging.getLogger(__name__)


class CamoufoxHelper:
    """Camoufox 浏览器自动化助手"""

    def __init__(self):
        self.headless = settings.CAMOUFOX_HEADLESS
        self.timeout = settings.CAMOUFOX_TIMEOUT

    async def get_login_token(self, uid: str, paste_id: str) -> str:
        """获取登录 Token"""
        async with AsyncCamoufox(headless=self.headless) as browser:
            page = await browser.new_page()
            try:
                # 访问页面
                await page.goto("https://www.luogu.me/token/apply", timeout=self.timeout)

                # 等待页面加载
                await asyncio.sleep(2)

                # 使用 JavaScript 发送 POST 请求
                response = await page.evaluate(
                    """
                    async (params) => {
                        const response = await fetch('https://www.luogu.me/token/generate', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(params)
                        });
                        return await response.json();
                    }
                    """,
                    {"uid": uid, "pasteId": paste_id},
                )

                if not response.get("success"):
                    raise ValueError(f"获取登录 Token 失败: {response}")

                token = response.get("token")
                if not token:
                    raise ValueError("响应中没有 token 字段")

                logger.info(f"成功获取登录 Token: {token[:10]}...")
                return token

            except Exception as e:
                logger.error(f"获取登录 Token 失败: {e}")
                raise
            finally:
                await page.close()

    async def login_paintboard(self, token: str) -> None:
        """使用 Token 登录保存站"""
        async with AsyncCamoufox(headless=self.headless) as browser:
            page = await browser.new_page()
            try:
                # 访问登录页面
                await page.goto("https://www.luogu.me/", timeout=self.timeout)

                # 等待页面加载
                await asyncio.sleep(2)

                # 发送登录请求
                await page.evaluate(
                    """
                    async (token) => {
                        const formData = new URLSearchParams();
                        formData.append('token', token);
                        
                        await fetch('https://www.luogu.me/user/login', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                            body: formData.toString()
                        });
                    }
                    """,
                    token,
                )

                # 等待 Cookie 设置
                await asyncio.sleep(2)

                logger.info("成功登录保存站")

            except Exception as e:
                logger.error(f"登录保存站失败: {e}")
                raise
            finally:
                await page.close()

    async def get_access_key(self, token: str) -> str:
        """获取 Access Key"""
        async with AsyncCamoufox(headless=self.headless) as browser:
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # 先登录
                await page.goto("https://www.luogu.me/paintboard/token", timeout=self.timeout)
                await asyncio.sleep(2)

                # 设置登录 Token
                await page.evaluate(
                    """
                    async (token) => {
                        const formData = new URLSearchParams();
                        formData.append('token', token);
                        
                        await fetch('https://www.luogu.me/user/login', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                            body: formData.toString()
                        });
                    }
                    """,
                    token,
                )

                await asyncio.sleep(2)

                # 申请 Access Key
                response = await page.evaluate(
                    """
                    async () => {
                        const response = await fetch('https://www.luogu.me/paintboard/apply', {
                            method: 'POST'
                        });
                        return await response.json();
                    }
                    """
                )

                if not response.get("success"):
                    raise ValueError(f"获取 Access Key 失败: {response}")

                access_key = response.get("token")
                if not access_key:
                    raise ValueError("响应中没有 token 字段")

                logger.info(f"成功获取 Access Key: {access_key}")
                return access_key

            except Exception as e:
                logger.error(f"获取 Access Key 失败: {e}")
                raise
            finally:
                await page.close()
                await context.close()

    async def get_full_token_flow(self, uid: str, paste_id: str) -> dict[str, Any]:
        """完整的 Token 获取流程"""
        try:
            # 1. 获取登录 Token
            login_token = await self.get_login_token(uid, paste_id)

            # 2. 获取 Access Key
            access_key = await self.get_access_key(login_token)

            return {"success": True, "login_token": login_token, "access_key": access_key}

        except Exception as e:
            logger.error(f"完整流程失败: {e}")
            return {"success": False, "error": str(e)}


# 全局实例
camoufox_helper = CamoufoxHelper()

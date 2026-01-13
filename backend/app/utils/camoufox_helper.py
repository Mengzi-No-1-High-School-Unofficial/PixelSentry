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

    async def get_uid_from_paste_id(self, paste_id: str) -> dict:
        """从剪贴板 ID 获取 UID 和用户名
        
        Args:
            paste_id: 剪贴板 ID
            
        Returns:
            {"success": bool, "uid": str, "username": str, "error": str}
        """
        try:
            async with AsyncCamoufox(headless=self.headless) as browser:
                page = await browser.new_page()
                
                try:
                    # 访问剪贴板页面
                    await page.goto(
                        f"https://www.luogu.com/paste/{paste_id}",
                        timeout=self.timeout
                    )
                    
                    # 等待页面加载
                    await asyncio.sleep(2)
                    
                    # 验证页面内容是否包含 lgs_register_verification
                    page_content = await page.content()
                    if 'lgs_register_verification' not in page_content:
                        logger.error(f"剪贴板 {paste_id} 页面不包含 lgs_register_verification 字样")
                        return {
                            "success": False,
                            "uid": None,
                            "username": None,
                            "error": "剪贴板内容无效，请确保剪贴板包含正确的验证信息"
                        }
                    
                    # 查找用户链接 - 使用多个选择器作为备选
                    selectors = [
                        'a[href^="/user/"]',
                        '.author a[href^="/user/"]',
                        '.lfe-caption a[href^="/user/"]',
                    ]
                    
                    user_link = None
                    for selector in selectors:
                        try:
                            user_link = await page.query_selector(selector)
                            if user_link:
                                break
                        except Exception:
                            continue
                    
                    if not user_link:
                        logger.error(f"无法在剪贴板页面找到用户链接")
                        return {
                            "success": False,
                            "uid": None,
                            "username": None,
                            "error": "无法找到用户信息，可能是私有剪贴板"
                        }
                    
                    # 获取 href 属性
                    href = await user_link.get_attribute('href')
                    
                    # 获取用户名（链接的文本内容）
                    username_element = await user_link.query_selector('span')
                    username = await username_element.inner_text() if username_element else None
                    
                    # 解析 UID
                    if href and '/user/' in href:
                        uid = href.split('/user/')[-1].split('?')[0].split('#')[0]
                        logger.info(f"成功从剪贴板 {paste_id} 解析出 UID: {uid}, 用户名: {username}")
                        return {"success": True, "uid": uid, "username": username, "error": None}
                    else:
                        logger.error(f"用户链接格式不正确: {href}")
                        return {
                            "success": False,
                            "uid": None,
                            "username": None,
                            "error": "用户链接格式不正确"
                        }
                        
                finally:
                    await page.close()
                    
        except Exception as e:
            logger.error(f"从剪贴板获取 UID 失败: {e}")
            return {"success": False, "uid": None, "username": None, "error": str(e)}

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

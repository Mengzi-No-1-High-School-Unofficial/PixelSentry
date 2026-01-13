"""Camoufox 浏览器实例池"""
import asyncio
import logging
from typing import Optional

from camoufox.async_api import AsyncCamoufox
from playwright.async_api import Page, Browser

from app.config import settings

logger = logging.getLogger(__name__)


class CamoufoxPool:
    """Camoufox 浏览器实例池"""

    def __init__(self):
        self.luogu_me_browser: Optional[Browser] = None
        self.luogu_me_page: Optional[Page] = None
        self.luogu_paste_browser: Optional[Browser] = None
        self.luogu_paste_page: Optional[Page] = None
        self._camoufox_context = None
        self._camoufox_paste_context = None
        self._lock = asyncio.Lock()
        self.headless = settings.CAMOUFOX_HEADLESS

    async def init(self):
        """初始化实例池"""
        logger.info("初始化 Camoufox 实例池")
        await self._init_luogu_me_browser()
        # paste 浏览器按需初始化，或者也可以在这里预热
        # await self._init_luogu_paste_browser()

    async def _init_luogu_me_browser(self):
        """初始化 luogu.me 专用浏览器实例"""
        # ... (Keep existing _init_luogu_me_browser implementation)
        try:
            logger.info("启动 luogu.me 专用浏览器实例")
            
            from camoufox.async_api import AsyncCamoufox
            
            # 创建 AsyncCamoufox 实例
            camoufox = AsyncCamoufox(headless=self.headless, humanize=True)
            
            # 启动浏览器并获取上下文
            self._camoufox_context = await camoufox.__aenter__()
            self.luogu_me_browser = self._camoufox_context
            
            # 创建新页面
            self.luogu_me_page = await self.luogu_me_browser.new_page()
            
            # 访问 luogu.me 首页并停留
            await self.luogu_me_page.goto("https://www.luogu.me/", timeout=30000)
            logger.info("luogu.me 浏览器实例已就绪")
            
        except Exception as e:
            logger.error(f"初始化 luogu.me 浏览器失败: {e}")
            raise

    async def _init_luogu_paste_browser(self):
        """初始化 luogu.paste 专用浏览器实例"""
        try:
            logger.info("启动 luogu.paste 专用浏览器实例")
            
            from camoufox.async_api import AsyncCamoufox
            
            # 创建 AsyncCamoufox 实例
            camoufox = AsyncCamoufox(headless=self.headless, humanize=True)
            
            # 启动浏览器并获取上下文
            self._camoufox_paste_context = await camoufox.__aenter__()
            self.luogu_paste_browser = self._camoufox_paste_context
            
            if not self.luogu_paste_browser:
                raise RuntimeError("Failed to initialize luogu.paste browser")

            # 创建新页面
            self.luogu_paste_page = await self.luogu_paste_browser.new_page()
            
            logger.info("luogu.paste 浏览器实例已就绪")
            
        except Exception as e:
            logger.error(f"初始化 luogu.paste 浏览器失败: {e}")
            raise

    async def _cleanup_luogu_me_browser(self):
        """清理 luogu.me 浏览器实例"""
        try:
            if self.luogu_me_page:
                await self.luogu_me_page.close()
                self.luogu_me_page = None
            if self.luogu_me_browser:
                await self.luogu_me_browser.close()
                self.luogu_me_browser = None
            if self._camoufox_context:
                # 退出上下文管理器
                try:
                    await self._camoufox_context.__aexit__(None, None, None)
                except:
                    pass
                self._camoufox_context = None
            logger.info("luogu.me 浏览器实例已清理")
        except Exception as e:
            logger.error(f"清理 luogu.me 浏览器失败: {e}")

    async def _cleanup_luogu_paste_browser(self):
        """清理 luogu.paste 浏览器实例"""
        try:
            if self.luogu_paste_page:
                await self.luogu_paste_page.close()
                self.luogu_paste_page = None
            if self.luogu_paste_browser:
                await self.luogu_paste_browser.close()
                self.luogu_paste_browser = None
            if self._camoufox_paste_context:
                # 退出上下文管理器
                try:
                    await self._camoufox_paste_context.__aexit__(None, None, None)
                except:
                    pass
                self._camoufox_paste_context = None
            logger.info("luogu.paste 浏览器实例已清理")
        except Exception as e:
            logger.error(f"清理 luogu.paste 浏览器失败: {e}")

    async def get_luogu_me_page(self) -> Page:
        """获取 luogu.me 页面（复用实例）"""
        async with self._lock:
            try:
                # 检查实例是否存在且有效
                if not self.luogu_me_browser or not self.luogu_me_page:
                    logger.warning("luogu.me 实例不存在，重新初始化")
                    await self._init_luogu_me_browser()
                
                if not self.luogu_me_page:
                     raise RuntimeError("Failed to initialize luogu.me page")

                # 清除 Cookie，避免冲突
                await self.luogu_me_page.context.clear_cookies()
                
                return self.luogu_me_page
                
            except Exception as e:
                logger.error(f"获取 luogu.me 页面失败，尝试重启: {e}")
                await self._cleanup_luogu_me_browser()
                await self._init_luogu_me_browser()
                if not self.luogu_me_page:
                     raise RuntimeError("Failed to re-initialize luogu.me page")
                return self.luogu_me_page

    async def get_luogu_paste_page(self) -> Page:
        """获取 luogu.paste 页面（复用实例）"""
        async with self._lock:
            try:
                # 检查实例是否存在且有效
                if not self.luogu_paste_browser or not self.luogu_paste_page:
                    logger.warning("luogu.paste 实例不存在，初始化")
                    await self._init_luogu_paste_browser()
                
                if not self.luogu_paste_page:
                     raise RuntimeError("Failed to initialize luogu.paste page")

                # 清除 Cookie 和缓存，确保干净的环境，类似于新开的浏览器
                await self.luogu_paste_page.context.clear_cookies()
                
                return self.luogu_paste_page
                
            except Exception as e:
                logger.error(f"获取 luogu.paste 页面失败，尝试重启: {e}")
                await self._cleanup_luogu_paste_browser()
                await self._init_luogu_paste_browser()
                if not self.luogu_paste_page:
                     raise RuntimeError("Failed to re-initialize luogu.paste page")
                return self.luogu_paste_page

    async def cleanup(self):
        """清理所有资源"""
        logger.info("清理 Camoufox 实例池")
        await self._cleanup_luogu_me_browser()
        await self._cleanup_luogu_paste_browser()


# 全局实例
camoufox_pool = CamoufoxPool()

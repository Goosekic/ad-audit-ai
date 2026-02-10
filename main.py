#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广告分析工具主程序
基于FastAPI的Web服务，提供抖音广告分析、视频内容提取、语音识别等功能
"""

import os
import sys
from pathlib import Path

# 设置UTF-8编码环境
if sys.platform == "win32":
    # Windows系统设置控制台编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from loguru import logger
import json
import argparse
import config

# 配置日志
logger.remove()  # 移除默认处理器
logger.add(
    config.LOG_DIR / "ad_analysis.log",
    rotation=config.LOG_CONFIG["rotation"],
    retention=config.LOG_CONFIG["retention"],
    compression=config.LOG_CONFIG["compression"],
    encoding=config.LOG_CONFIG["encoding"],
    level=config.LOG_CONFIG["level"],
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 替换print为logger
print = logger.info

# 创建FastAPI应用
app = FastAPI(
    title="广告分析工具",
    description="基于豆包AI的抖音广告分析工具，支持视频分析、语音识别、质量评分",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义中间件：确保JSON响应包含charset=utf-8
class CharsetMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 检查Content-Type是否为application/json
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type and "charset" not in content_type.lower():
            # 添加charset=utf-8
            response.headers["content-type"] = "application/json; charset=utf-8"
        
        return response

app.add_middleware(CharsetMiddleware)

# 挂载静态文件和模板
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

# 导入路由
try:
    from src.api.router import router as api_router
    app.include_router(api_router, prefix="/api")
    print("✓ 加载API路由")
except ImportError as e:
    print(f"✗ 加载API路由失败: {e}")

# 尝试导入新模块的路由
try:
    from src.session_crawler.routes import router as session_router
    app.include_router(session_router, prefix="/api/session")
    print("✓ 加载Session抓取路由")
except ImportError as e:
    print(f"✗ 加载Session抓取路由失败: {e}")

try:
    from src.whisper_service.routes import router as whisper_router
    app.include_router(whisper_router, prefix="/api/whisper")
    print("✓ 加载Whisper服务路由")
except ImportError as e:
    print(f"✗ 加载Whisper服务路由失败: {e}")

try:
    from src.douyin_analyzer.routes import router as douyin_router
    app.include_router(douyin_router, prefix="/api/douyin")
    print("✓ 加载抖音分析路由")
except ImportError as e:
    print(f"✗ 加载抖音分析路由失败: {e}")

try:
    from src.core.routes import router as core_router
    app.include_router(core_router, prefix="/api/core")
    print("✓ 加载核心分析路由")
except ImportError as e:
    print(f"✗ 加载核心分析路由失败: {e}")

try:
    from src.install.installer import Installer
    # 创建安装页面路由
    @app.get("/install", response_class=HTMLResponse)
    async def install_page(request: Request):
        return templates.TemplateResponse("install.html", {"request": request})
    
    @app.post("/api/install/check")
    async def install_check():
        installer = Installer()
        checks = installer.run_system_checks()
        return {"success": True, "checks": checks}
    
    @app.post("/api/install/run")
    async def install_run():
        installer = Installer()
        results = installer.install_all(interactive=False)
        return results
    
    print("✓ 加载安装功能")
except ImportError as e:
    print(f"✗ 加载安装功能失败: {e}")

try:
    from src.packaging.packager import Packager
    from src.packaging.nsis_creator import NsisCreator
    
    @app.get("/packaging", response_class=HTMLResponse)
    async def packaging_page(request: Request):
        return templates.TemplateResponse("packaging.html", {"request": request})
    
    @app.post("/api/packaging/build")
    async def build_package():
        packager = Packager()
        results = packager.package_all()
        return results
    
    print("✓ 加载打包功能")
except ImportError as e:
    print(f"✗ 加载打包功能失败: {e}")

# 首页路由
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 视频审核页面
@app.get("/video-audit", response_class=HTMLResponse)
async def video_audit_page(request: Request):
    return templates.TemplateResponse("video_ad_audit.html", {"request": request})

# 抖音分析页面
@app.get("/douyin-analyzer", response_class=HTMLResponse)
async def douyin_analyzer_page(request: Request):
    return templates.TemplateResponse("douyin_analyzer.html", {"request": request})

# 语音识别页面
@app.get("/whisper-audio", response_class=HTMLResponse)
async def whisper_audio_page(request: Request):
    return templates.TemplateResponse("whisper_audio.html", {"request": request})

# Session管理页面
@app.get("/session-manager", response_class=HTMLResponse)
async def session_manager_page(request: Request):
    return templates.TemplateResponse("session_manager.html", {"request": request})



# 健康检查接口
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "广告分析工具",
        "version": "1.0.0",
        "modules": {
            "api_router": "loaded" if 'api_router' in locals() else "missing",
            "session_crawler": "loaded" if 'session_router' in locals() else "missing",
            "whisper_service": "loaded" if 'whisper_router' in locals() else "missing",
            "douyin_analyzer": "loaded" if 'douyin_router' in locals() else "missing",
            "core_analysis": "loaded" if 'core_router' in locals() else "missing",
            "install": "loaded" if 'Installer' in locals() else "missing",
            "packaging": "loaded" if 'Packager' in locals() else "missing",
        }
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("广告分析工具启动成功")
    print(f"服务地址: http://{config.SERVER_CONFIG['host']}:{config.SERVER_CONFIG['port']}")
    print(f"接口文档: http://{config.SERVER_CONFIG['host']}:{config.SERVER_CONFIG['port']}/api/docs")
    print("=" * 60)
    print("可用功能:")
    print("1. 首页: /")
    print("2. 视频审核: /video-audit")
    print("3. 抖音分析: /douyin-analyzer")
    print("4. 语音识别: /whisper-audio")
    print("5. Session管理: /session-manager")
    print("6. 一键安装: /install")
    print("7. 打包工具: /packaging")
    print("8. 健康检查: /health")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    print("广告分析工具正在关闭...")

# 主函数
def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="广告分析工具")
    parser.add_argument("--host", type=str, help=f"服务器主机地址 (默认: {config.SERVER_CONFIG['host']})")
    parser.add_argument("--port", type=int, help=f"服务器端口 (默认: {config.SERVER_CONFIG['port']})")
    parser.add_argument("--reload", action="store_true", help="启用热重载模式")
    parser.add_argument("--workers", type=int, help=f"工作进程数 (默认: {config.SERVER_CONFIG['workers']})")
    args = parser.parse_args()
    
    # 使用命令行参数覆盖配置
    server_config = config.SERVER_CONFIG.copy()
    if args.host:
        server_config["host"] = args.host
    if args.port:
        server_config["port"] = args.port
    if args.reload:
        server_config["reload"] = True
    if args.workers:
        server_config["workers"] = args.workers
    
    print("正在启动广告分析工具...")
    
    # 检查必要目录
    for directory in [config.LOG_DIR, config.DATA_DIR, config.MODEL_DIR]:
        if not directory.exists():
            directory.mkdir(parents=True)
            print(f"创建目录: {directory}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=server_config["host"],
        port=server_config["port"],
        reload=server_config["reload"],
        workers=server_config["workers"],
        log_level="info"
    )

if __name__ == "__main__":
    main()
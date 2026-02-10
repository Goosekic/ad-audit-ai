#!/usr/bin/env python3
"""
Check and install Playwright browser if needed.
This script is called from start.bat to avoid batch script syntax issues.
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run command and return (success, output)"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def main():
    print("Checking Playwright browser installation...")
    
    # Check for local offline browser installation first
    project_dir = os.path.dirname(os.path.abspath(__file__))
    local_browsers_path = os.path.join(project_dir, "browsers")
    chromium_path = os.path.join(local_browsers_path, "chromium-1208", "chrome-win", "chrome.exe")
    
    if os.path.exists(chromium_path):
        print(f"✅ 检测到离线安装的Chromium浏览器")
        print(f"   路径: {chromium_path}")
        print("Session抓取功能已启用")
        
        # Set environment variable for this process
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = local_browsers_path
        
        # 测试浏览器是否实际可用（快速测试）
        try:
            print("正在验证浏览器可用性...")
            import subprocess
            import tempfile
            import time
            
            # 创建一个临时测试脚本
            test_script = f'''
import asyncio
import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"{local_browsers_path}"
from playwright.async_api import async_playwright

async def test():
    playwright = await async_playwright().start()
    try:
        browser = await playwright.chromium.launch(
            executable_path=r"{chromium_path}",
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--timeout=5000']
        )
        page = await browser.new_page()
        await page.goto('about:blank', wait_until='domcontentloaded', timeout=5000)
        await browser.close()
        await playwright.stop()
        return True
    except:
        return False

result = asyncio.run(test())
print("SUCCESS" if result else "FAILED")
'''
            
            # 写入临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_script)
                temp_file = f.name
            
            # 运行测试
            python_exe = sys.executable
            result = subprocess.run(
                [python_exe, temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 清理临时文件
            import atexit
            import os as os_module
            atexit.register(lambda: os_module.unlink(temp_file) if os_module.path.exists(temp_file) else None)
            
            if "SUCCESS" in result.stdout:
                print("✅ 浏览器验证通过，功能正常")
            else:
                print("⚠️  浏览器验证失败，但可能仍可使用")
                
        except Exception as e:
            print(f"⚠️  浏览器快速验证跳过: {str(e)[:100]}")
        
        return 0
    
    # Use current Python executable
    python_exe = sys.executable
    
    # Check if playwright is available
    success, output = run_command(f'"{python_exe}" -m playwright --version')
    if not success:
        print("Warning: Playwright not found or cannot be executed")
        print("Session capture functionality will not be available")
        return 0
    
    print(f"Playwright version: {output}")
    
    # Check if Chromium browser is already installed
    success, output = run_command(f'"{python_exe}" -m playwright install --list')
    if not success:
        print("Warning: Cannot list installed browsers")
        print("Session capture functionality may not work")
        return 0
    
    if "chromium" in output.lower():
        print("Chromium browser already installed")
        return 0
    
    # Install Chromium browser with retry mechanism
    print("=" * 60)
    print("开始安装Chromium浏览器（约200MB，可能需要10-20分钟）")
    print("=" * 60)
    print("注意：如果网络不稳定，安装可能会失败")
    print("      但应用程序仍会正常启动，只是无法使用Session抓取功能")
    print()
    
    # 多个镜像源列表（测试可用的镜像源）
    mirror_sources = [
        ("腾讯云镜像源", "https://mirrors.cloud.tencent.com/playwright/"),
        ("华为云镜像源", "https://mirrors.huaweicloud.com/playwright/"),
        ("默认源", None)  # None表示不使用镜像
    ]
    
    max_retries = 3
    installed = False
    
    for retry in range(max_retries):
        for mirror_name, mirror_url in mirror_sources:
            if retry > 0:
                print(f"\n第 {retry + 1} 次重试，使用 {mirror_name}...")
            else:
                print(f"\n尝试使用 {mirror_name}...")
            
            # 设置环境变量
            env = os.environ.copy()
            if mirror_url:
                env['PLAYWRIGHT_DOWNLOAD_HOST'] = mirror_url
                print(f"镜像地址: {mirror_url}")
            
            try:
                # 执行安装命令
                print("正在下载Chromium浏览器，请稍候...")
                print("如果网络不稳定，可能需要较长时间")
                
                result = subprocess.run(
                    f'"{python_exe}" -m playwright install chromium',
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=1800,  # 30分钟超时
                    env=env
                )
                
                if result.returncode == 0:
                    print(f"\n✅ Chromium浏览器安装成功！使用 {mirror_name}")
                    print("Session抓取功能现在可用")
                    return 0
                else:
                    # 提取错误信息
                    error_msg = result.stderr[:500] if result.stderr else "未知错误"
                    print(f"\n⚠️  使用 {mirror_name} 安装失败")
                    
                    # 检查特定错误类型
                    if "ECONNRESET" in error_msg:
                        print("错误类型: 网络连接中断")
                        print("可能原因: 网络不稳定、防火墙阻止或下载超时")
                    elif "timed out" in error_msg.lower():
                        print("错误类型: 下载超时")
                        print("可能原因: 网络速度过慢或镜像源响应慢")
                    else:
                        print(f"错误详情: {error_msg}")
                    
                    # 继续尝试下一个镜像源
                    continue
                    
            except subprocess.TimeoutExpired:
                print(f"\n⏱️  使用 {mirror_name} 安装超时（30分钟）")
                print("可能原因: 网络速度过慢或文件过大")
                continue
                
            except Exception as e:
                print(f"\n❌ 使用 {mirror_name} 安装时发生异常: {str(e)}")
                continue
    
    # 所有尝试都失败
    print("\n" + "=" * 60)
    print("❌ 自动安装Chromium浏览器失败")
    print("=" * 60)
    print("\nSession抓取功能将不可用，但其他功能正常")
    print("\n您可以手动安装Chromium浏览器：")
    print("\n方法1: 使用命令行手动安装")
    print(f'    "{python_exe}" -m playwright install chromium')
    print("\n方法2: 设置镜像源后安装")
    print('    set PLAYWRIGHT_DOWNLOAD_HOST=https://mirrors.cloud.tencent.com/playwright/')
    print(f'    "{python_exe}" -m playwright install chromium')
    print("\n方法3: 离线安装（如果网络问题持续）")
    print("    1. 访问 https://github.com/microsoft/playwright/releases")
    print("    2. 下载对应版本的Chromium浏览器")
    print("    3. 解压到: %LOCALAPPDATA%\\ms-playwright")
    print("\n安装完成后，重启应用程序即可使用Session抓取功能")
    print("\n注意: 手动安装期间，应用程序其他功能仍然可用")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
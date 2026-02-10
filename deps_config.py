"""
统一的依赖配置管理
所有部署脚本和打包脚本都应使用此配置来确保依赖版本一致性
"""

from typing import Dict, List, Tuple

# 基础配置
PYTHON_MIN_VERSION: Tuple[int, int] = (3, 8)

# 必需依赖包 - 精确版本以确保兼容性
REQUIRED_DEPS: Dict[str, str] = {
    # 基础依赖
    "fastapi": "==0.128.3",
    "uvicorn": "==0.40.0",
    "python-dotenv": "==1.2.1",
    "loguru": "==0.7.3",
    
    # HTTP客户端
    "httpx": "==0.28.1",
    "aiohttp": "==3.13.3",
    "requests": "==2.32.5",
    "requests-aws4auth": "==1.3.1",
    
    # 模板和静态文件
    "Jinja2": "==3.1.6",
    
    # 视频处理
    "opencv-python": "==4.13.0.92",
    "moviepy": "==2.2.1",
    "ffmpeg-python": "==0.2.0",
    "imageio-ffmpeg": "==0.6.0",
    
    # 语音识别和音频处理
    "speechrecognition": "==3.10.4",
    "openai-whisper": "==20250625",  # 最新稳定版本，与PyTorch 2.10.0兼容
    "pydub": "==0.25.1",
    "torchaudio": "==2.10.0",  # 与torch 2.10.0匹配，安装脚本会使用CPU版本
    
    # 字幕处理
    "pysubs2": "==1.8.0",
    
    # OCR文字识别
    "easyocr": "==1.7.2",
    "pyclipper": "==1.4.0",
    "shapely": "==2.1.2",
    
    # 浏览器自动化
    "playwright": "==1.58.0",
    
    # 数据分析和科学计算
    "numpy": "==2.3.0",  # 固定稳定版本，与PyTorch 2.10.0兼容
    "scipy": "==1.17.0",
    "torch": "==2.10.0",  # 稳定版本，安装脚本会使用CPU版本
    "torchvision": "==0.25.0",  # 与torch 2.10.0匹配，安装脚本会使用CPU版本
    "numba": ">=0.63.1",
    
    # 图像处理
    "Pillow": "==11.3.0",
    "imageio": "==2.37.2",
    "scikit-image": "==0.26.0",
    
    # 抖音链接解析
    "yt-dlp": ">=2024.1.1",
    
    # 打包和安装
    "pyinstaller": "==6.18.0",
    
    # 其他工具
    "pydantic": "==2.12.5",
    "tqdm": "==4.67.3",
    "colorama": "==0.4.6",
    
    # 文本处理
    "jieba": ">=0.42.0",
    "beautifulsoup4": ">=4.12.0",
}

# 可选依赖包
OPTIONAL_DEPS: Dict[str, str] = {
    "pyautogui": ">=0.9.0",
    "selenium": ">=4.10.0",
}

# 无版本要求的包（仅名称）
NO_VERSION_DEPS: List[str] = [
    "python-multipart",
]

def get_requirements_list() -> List[str]:
    """生成requirements.txt格式的依赖列表"""
    deps = []
    
    # 添加必需依赖
    for package, version in REQUIRED_DEPS.items():
        if version:
            deps.append(f"{package}{version}")
        else:
            deps.append(package)
    
    # 添加无版本要求的包
    deps.extend(NO_VERSION_DEPS)
    
    return deps

def get_installer_required_packages() -> List[str]:
    """生成installer.py格式的必需包列表"""
    packages = []
    
    for package, version in REQUIRED_DEPS.items():
        if version:
            packages.append(f"{package}{version}")
        else:
            packages.append(package)
    
    # 添加无版本要求的包
    packages.extend(NO_VERSION_DEPS)
    
    return packages

def get_installer_optional_packages() -> List[str]:
    """生成installer.py格式的可选包列表"""
    packages = []
    
    for package, version in OPTIONAL_DEPS.items():
        if version:
            packages.append(f"{package}{version}")
        else:
            packages.append(package)
    
    return packages

def validate_dependencies() -> bool:
    """验证依赖配置是否完整"""
    required_fields = ["torch", "torchvision", "torchaudio"]
    
    for field in required_fields:
        if field not in REQUIRED_DEPS:
            print(f"错误: 缺少必需依赖 {field}")
            return False
    
    # 检查版本兼容性
    torch_version = REQUIRED_DEPS.get("torch", "")
    torchvision_version = REQUIRED_DEPS.get("torchvision", "")
    torchaudio_version = REQUIRED_DEPS.get("torchaudio", "")
    
    if torch_version and torchvision_version and torchaudio_version:
        # 检查是否为CPU版本
        is_cpu_version = "+cpu" in torch_version or "+cpu" in torchvision_version or "+cpu" in torchaudio_version
        
        # 提取主版本号（忽略==前缀和+cpu后缀）
        torch_clean = torch_version.replace("==", "").replace("+cpu", "")
        torchvision_clean = torchvision_version.replace("==", "").replace("+cpu", "")
        torchaudio_clean = torchaudio_version.replace("==", "").replace("+cpu", "")
        
        torch_major = torch_clean.split(".")[0] if "." in torch_clean else ""
        torchvision_major = torchvision_clean.split(".")[0] if "." in torchvision_clean else ""
        torchaudio_major = torchaudio_clean.split(".")[0] if "." in torchaudio_clean else ""
        
        if torch_major and torchvision_major and torchaudio_major:
            # PyTorch和torchvision主版本号可能不同是正常的（如torch 2.x, torchvision 0.x）
            # 我们只检查torch和torchaudio的主版本号是否匹配
            if not (torch_major == torchaudio_major):
                print(f"警告: PyTorch相关包版本可能不兼容")
                print(f"  torch: {torch_version}, torchvision: {torchvision_version}, torchaudio: {torchaudio_version}")
                if is_cpu_version:
                    print(f"  注意: 检测到CPU版本，这是正常现象")
            elif is_cpu_version:
                print(f"信息: PyTorch CPU版本配置正确")
                print(f"  torch: {torch_version}, torchvision: {torchvision_version}, torchaudio: {torchaudio_version}")
    
    return True

if __name__ == "__main__":
    # 测试配置
    if validate_dependencies():
        print("依赖配置验证通过")
        print("\nrequirements.txt格式:")
        for dep in get_requirements_list():
            print(f"  {dep}")
        
        print("\ninstaller.py必需包格式:")
        for dep in get_installer_required_packages():
            print(f"  {dep}")
    else:
        print("依赖配置验证失败")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推箱子游戏打包脚本
Box Game Executable Builder
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python():
    """检查Python环境"""
    print("🐍 检查Python环境...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Python版本: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Python环境检查失败")
        return False

def check_pyinstaller():
    """检查PyInstaller"""
    print("📦 检查PyInstaller...")
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("⚠️ PyInstaller未安装，正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                          check=True)
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False

def check_dependencies():
    """检查项目依赖"""
    print("🔍 检查项目依赖...")
    required_modules = [
        'numpy', 'scipy', 'matplotlib', 'PyQt5', 'cv2', 
        'PIL', 'pandas', 'sklearn', 'seaborn', 'yaml', 
        'openpyxl', 'loguru', 'colorama', 'psutil'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"⚠️ 缺失模块: {', '.join(missing_modules)}")
        print("正在安装requirements.txt...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True)
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False
    
    return True

def clean_build_files():
    """清理构建文件"""
    print("🧹 清理之前的构建文件...")
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 已删除目录: {dir_name}")
    
    for pattern in files_to_clean:
        for file_path in Path('.').glob(pattern):
            file_path.unlink()
            print(f"✅ 已删除文件: {file_path}")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    print("这可能需要几分钟时间，请耐心等待...")
    
    # PyInstaller命令参数
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "推箱子游戏",
        "--exclude", "PyQt6",
        "--exclude", "PySide2",
        "--exclude", "PySide6",
        "--add-data", "interfaces;interfaces",
        "--add-data", "utils;utils", 
        "--add-data", "data_processing;data_processing",
        "--add-data", "backends;backends",
        "--add-data", "config;config",
        "--add-data", "extern;extern",
        "--add-data", "multiple_skins;multiple_skins",
        "--add-data", "server;server",
        "--add-data", "with_nn;with_nn",
        "--add-data", "config.json;.",
        # 核心模块
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.sip",
        "--hidden-import", "numpy",
        "--hidden-import", "scipy",
        "--hidden-import", "matplotlib",
        "--hidden-import", "cv2",
        "--hidden-import", "PIL",
        "--hidden-import", "pandas",
        "--hidden-import", "sklearn",
        "--hidden-import", "seaborn",
        "--hidden-import", "yaml",
        "--hidden-import", "openpyxl",
        "--hidden-import", "loguru",
        "--hidden-import", "colorama",
        "--hidden-import", "psutil",
        # 科学计算模块
        "--hidden-import", "scipy.ndimage",
        "--hidden-import", "scipy.signal",
        "--hidden-import", "scipy.optimize",
        "--hidden-import", "matplotlib.pyplot",
        "--hidden-import", "matplotlib.backends.backend_qt5agg",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "skimage",
        # sklearn子模块
        "--hidden-import", "sklearn.ensemble",
        "--hidden-import", "sklearn.cluster",
        "--hidden-import", "sklearn.decomposition",
        "--hidden-import", "sklearn.preprocessing",
        "--hidden-import", "sklearn.metrics",
        "--hidden-import", "sklearn.model_selection",
        "--hidden-import", "sklearn.neighbors",
        "--hidden-import", "sklearn.svm",
        "--hidden-import", "sklearn.tree",
        "--hidden-import", "sklearn.linear_model",
        "--hidden-import", "sklearn.naive_bayes",
        "--hidden-import", "sklearn.neural_network",
        "--hidden-import", "sklearn.feature_extraction",
        "--hidden-import", "sklearn.feature_selection",
        "--hidden-import", "sklearn.pipeline",
        "--hidden-import", "sklearn.cross_decomposition",
        "--hidden-import", "sklearn.covariance",
        "--hidden-import", "sklearn.manifold",
        "--hidden-import", "sklearn.mixture",
        "--hidden-import", "sklearn.semi_supervised",
        "--hidden-import", "sklearn.calibration",
        "--hidden-import", "sklearn.multioutput",
        "--hidden-import", "sklearn.compose",
        "--hidden-import", "sklearn.impute",
        "--hidden-import", "sklearn.kernel_ridge",
        "--hidden-import", "sklearn.discriminant_analysis",
        "--hidden-import", "sklearn.gaussian_process",
        "--hidden-import", "sklearn.isotonic",
        "--hidden-import", "sklearn.kernel_approximation",
        # sklearn.metrics子模块
        "--hidden-import", "sklearn.metrics.cluster",
        "--hidden-import", "sklearn.metrics.pairwise",
        "--hidden-import", "sklearn.metrics.ranking",
        "--hidden-import", "sklearn.metrics.regression",
        "--hidden-import", "sklearn.metrics.scorer",
        "--hidden-import", "sklearn.metrics._classification",
        "--hidden-import", "sklearn.metrics._regression",
        "--hidden-import", "sklearn.metrics._ranking",
        "--hidden-import", "sklearn.metrics._scorer",
        "--hidden-import", "sklearn.metrics._dist_metrics",
        "--hidden-import", "sklearn.metrics._pairwise_distances_reduction",
        "--hidden-import", "sklearn.metrics._pairwise_fast",
        "--hidden-import", "sklearn.metrics._pairwise",
        "box_game_app_optimized.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败！")
        print(f"错误信息: {e.stderr}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("推箱子游戏打包工具")
    print("Box Game Executable Builder")
    print("=" * 60)
    print()
    
    # 检查环境
    if not check_python():
        return False
    
    if not check_pyinstaller():
        return False
    
    if not check_dependencies():
        return False
    
    # 清理文件
    clean_build_files()
    
    # 构建可执行文件
    if build_executable():
        print()
        print("🎉 打包完成！")
        print("📁 可执行文件位置: dist/推箱子游戏.exe")
        print()
        
        # 检查文件是否存在
        exe_path = Path("dist/推箱子游戏.exe")
        if exe_path.exists():
            print(f"✅ 文件大小: {exe_path.stat().st_size / (1024*1024):.1f} MB")
            print("🚀 可以运行了！")
            
            # 询问是否打开目录
            try:
                response = input("是否打开输出目录？(y/n): ").lower().strip()
                if response in ['y', 'yes', '是']:
                    os.startfile("dist")
            except KeyboardInterrupt:
                print("\n👋 再见！")
        else:
            print("❌ 可执行文件未找到")
            return False
    else:
        print("❌ 打包失败")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1) 
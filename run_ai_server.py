#!/usr/bin/env python3
"""
AI增强版数字员工系统启动脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import httpx
        print("✅ 基础依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少基础依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    # 检查AI服务依赖
    ai_services = []
    try:
        import openai
        ai_services.append("OpenAI")
    except ImportError:
        pass
    
    try:
        import anthropic
        ai_services.append("Anthropic")
    except ImportError:
        pass
    
    if ai_services:
        print(f"✅ AI服务依赖: {', '.join(ai_services)}")
    else:
        print("⚠️  未安装AI服务依赖，将使用本地降级模式")
    
    return True


def check_environment():
    """检查环境配置"""
    from dotenv import load_dotenv
    
    # 加载.env文件
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ 加载环境配置: {env_file}")
    else:
        print(f"⚠️  未找到.env文件，使用默认配置")
        print(f"   建议复制 .env.example 为 .env 并配置AI服务密钥")
    
    # 检查AI配置
    ai_configured = False
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API密钥已配置")
        ai_configured = True
    
    if os.getenv("ANTHROPIC_API_KEY"):
        print("✅ Anthropic API密钥已配置")
        ai_configured = True
    
    if not ai_configured:
        print("⚠️  未配置AI服务密钥，将使用本地降级模式")
        print("   性能和质量会受到影响，建议配置至少一个AI服务")
    
    return True


def main():
    """主函数"""
    print("🚀 启动AI增强版数字员工系统...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    print("=" * 50)
    print("🎯 系统配置完成，正在启动服务...")
    
    # 导入应用
    try:
        from digital_employee.api.main_v2 import app
        from config import config
        
        # 启动服务器
        import uvicorn
        
        host = config.get("app.host", "0.0.0.0")
        port = config.get("app.port", 8000)
        debug = config.is_debug()
        
        print(f"📡 服务地址: http://{host}:{port}")
        print(f"📖 API文档: http://{host}:{port}/docs")
        print(f"🏠 主页: http://{host}:{port}/")
        print(f"📊 系统状态: http://{host}:{port}/system/status")
        print("=" * 50)
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=debug,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
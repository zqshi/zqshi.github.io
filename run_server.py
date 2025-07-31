#!/usr/bin/env python3
"""
数字员工系统启动脚本
"""

import uvicorn
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("启动数字员工系统...")
    print("API文档地址: http://localhost:8000/docs")
    print("主页地址: http://localhost:8000")
    print("系统状态: http://localhost:8000/system/status")
    print()
    
    uvicorn.run(
        "digital_employee.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
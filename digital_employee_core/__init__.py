"""
数字员工核心系统模块

本模块包含数字员工系统的核心组件：
- 智能Prompt管理系统
- Agent实现框架
- 测试和验证工具

版本: 1.0.0
作者: Digital Employee System Team
"""

__version__ = "1.0.0"
__author__ = "Digital Employee System Team"

# 核心组件导入
try:
    from .prompt_manager import (
        # Prompt管理器
        PromptManager,
        PromptTemplate,
        PromptVersion,
        PromptConstraint,
        
        # 工具函数
        create_prompt_manager,
        validate_prompt_template
    )
    
    from .agent_implementations import (
        # Agent基类和实现
        DigitalEmployeeAgent,
        CustomerServiceAgent,
        DataAnalysisAgent,
        ContentCreationAgent,
        ProjectManagementAgent,
        TechnicalSupportAgent,
        
        # 工具函数
        create_agent,
        get_available_agents
    )
    
    # 标记核心组件可用
    _CORE_COMPONENTS_AVAILABLE = True
    
except ImportError as e:
    # 如果导入失败，提供基础信息
    _CORE_COMPONENTS_AVAILABLE = False
    _IMPORT_ERROR = str(e)

# 模块级别的配置
DEFAULT_AGENT_CONFIG = {
    "max_conversation_history": 50,
    "response_timeout": 30,
    "enable_memory_integration": True,
    "log_level": "INFO",
    "enable_prompt_caching": True,
    "max_prompt_cache_size": 100
}

def get_module_info():
    """
    获取模块信息
    
    Returns:
        dict: 包含版本、作者等信息的字典
    """
    info = {
        "name": "Digital Employee Core Module",
        "version": __version__,
        "author": __author__,
        "description": "数字员工核心系统",
        "components_available": _CORE_COMPONENTS_AVAILABLE
    }
    
    if _CORE_COMPONENTS_AVAILABLE:
        info["components"] = {
            "prompt_manager": "智能Prompt管理系统",
            "agent_implementations": "Agent实现框架"
        }
    else:
        info["import_error"] = _IMPORT_ERROR
    
    return info

def check_dependencies():
    """
    检查模块依赖是否满足
    
    Returns:
        dict: 依赖检查结果
    """
    dependencies = {}
    
    # 检查基础依赖
    try:
        import json
        dependencies["json"] = {"available": True, "version": "built-in"}
    except ImportError:
        dependencies["json"] = {"available": False, "error": "Missing json module"}
    
    try:
        import logging
        dependencies["logging"] = {"available": True, "version": "built-in"} 
    except ImportError:
        dependencies["logging"] = {"available": False, "error": "Missing logging module"}
    
    try:
        import time
        dependencies["time"] = {"available": True, "version": "built-in"}
    except ImportError:
        dependencies["time"] = {"available": False, "error": "Missing time module"}
    
    # 检查可选依赖
    try:
        import requests
        dependencies["requests"] = {"available": True, "version": getattr(requests, '__version__', 'unknown')}
    except ImportError:
        dependencies["requests"] = {"available": False, "error": "Optional: HTTP requests support"}
    
    return dependencies

# 便捷的创建函数
def create_digital_employee_system(config=None):
    """
    创建完整的数字员工系统
    
    Args:
        config (dict, optional): 系统配置参数
        
    Returns:
        dict: 包含各组件的系统字典
    """
    if not _CORE_COMPONENTS_AVAILABLE:
        raise ImportError(f"核心组件不可用: {_IMPORT_ERROR}")
    
    config = config or DEFAULT_AGENT_CONFIG
    
    # 创建Prompt管理器
    prompt_manager = create_prompt_manager()
    
    # 获取可用的Agent类型
    available_agents = get_available_agents()
    
    return {
        "prompt_manager": prompt_manager,
        "available_agents": available_agents,
        "config": config,
        "version": __version__
    }

# 导出的公共API
if _CORE_COMPONENTS_AVAILABLE:
    __all__ = [
        # 版本信息
        '__version__',
        '__author__',
        
        # Prompt管理
        'PromptManager',
        'PromptTemplate',
        'PromptVersion', 
        'PromptConstraint',
        'create_prompt_manager',
        'validate_prompt_template',
        
        # Agent实现
        'DigitalEmployeeAgent',
        'CustomerServiceAgent',
        'DataAnalysisAgent',
        'ContentCreationAgent',
        'ProjectManagementAgent',
        'TechnicalSupportAgent',
        'create_agent',
        'get_available_agents',
        
        # 系统工具
        'create_digital_employee_system',
        'get_module_info',
        'check_dependencies',
        'DEFAULT_AGENT_CONFIG'
    ]
else:
    __all__ = [
        '__version__',
        '__author__',
        'get_module_info', 
        'check_dependencies',
        'DEFAULT_AGENT_CONFIG'
    ]
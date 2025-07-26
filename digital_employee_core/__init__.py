"""
数字员工核心模块 (Digital Employee Core Module)

企业级数字员工系统核心实现，基于Multi-Agent架构和Claude AI
支持完整的产品开发流程和智能任务处理

主要功能：
- 智能意图识别和流程编排
- 标准产品开发流程执行
- Multi-Agent协作和调度
- Claude AI驱动的智能推理

版本: 3.0.0
作者: Digital Employee System Team
"""

__version__ = "3.0.0"
__author__ = "Digital Employee System Team"

import logging

# 设置模块日志
logger = logging.getLogger(__name__)

# 尝试导入核心组件
try:
    # Claude集成
    from .claude_integration import (
        ClaudeService,
        create_claude_service,
        ClaudeDigitalEmployee,
        create_claude_digital_employee
    )
    
    # 意图识别和流程编排
    from .intent_recognition import (
        SmartIntentRecognizer,
        ProcessOrchestrator,
        create_intent_recognizer,
        create_process_orchestrator,
        IntentType,
        ProcessStage,
        IntentRecognitionResult
    )
    
    # 流程执行引擎
    from .process_engine import (
        ProductDevelopmentProcessEngine,
        create_process_engine
    )
    
    # Multi-Agent数字员工系统
    from .multi_agent_digital_employee import (
        MultiAgentDigitalEmployee,
        create_multi_agent_digital_employee,
        create_compatible_multi_agent_employee
    )
    
    _CORE_COMPONENTS_AVAILABLE = True
    _IMPORT_ERROR = None
    
    logger.info("数字员工核心组件加载成功")
    
except ImportError as e:
    _CORE_COMPONENTS_AVAILABLE = False
    _IMPORT_ERROR = str(e)
    logger.error(f"数字员工核心组件加载失败: {e}")
    
    # 创建占位符类
    class MockComponent:
        def __init__(self, *args, **kwargs):
            self.mock = True
            self.active_sessions = {}
        
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
        
        async def process_user_request(self, *args, **kwargs):
            from collections import namedtuple
            MockResponse = namedtuple('MockResponse', ['content', 'response_type', 'next_stage', 'requires_user_input', 'suggested_inputs', 'additional_info'])
            
            class MockStage:
                def __init__(self, value):
                    self.value = value
            
            return MockResponse(
                content="数字员工核心模块未正确加载，请检查系统配置。",
                response_type="error",
                next_stage=MockStage("error"),
                requires_user_input=False,
                suggested_inputs=["检查系统状态", "重新启动"],
                additional_info={"mock": True, "error": str(_IMPORT_ERROR)}
            )
    
    # 使用占位符
    ClaudeService = MockComponent
    MultiAgentDigitalEmployee = MockComponent
    create_claude_service = lambda: MockComponent()
    create_multi_agent_digital_employee = lambda: MockComponent()
    create_compatible_multi_agent_employee = lambda: MockComponent()

# 工厂函数
def create_unified_digital_employee():
    """创建统一数字员工实例"""
    if not _CORE_COMPONENTS_AVAILABLE:
        logger.warning(f"使用Mock数字员工，原因: {_IMPORT_ERROR}")
        return MockComponent()
    
    try:
        # 优先使用Multi-Agent系统
        return create_compatible_multi_agent_employee()
    except Exception as e:
        logger.error(f"创建Multi-Agent数字员工失败: {e}")
        # Fallback到Claude数字员工
        try:
            claude_service = create_claude_service()
            return create_claude_digital_employee(claude_service)
        except Exception as e2:
            logger.error(f"创建Claude数字员工失败: {e2}")
            return MockComponent()

# 兼容性导出
UnifiedDigitalEmployee = create_unified_digital_employee

# 导出主要接口
__all__ = [
    'create_unified_digital_employee',
    'UnifiedDigitalEmployee',
    'ClaudeService',
    'MultiAgentDigitalEmployee',
    'create_claude_service',
    'create_multi_agent_digital_employee',
    'create_compatible_multi_agent_employee'
]
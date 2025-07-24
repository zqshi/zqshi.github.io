"""
数字员工Agent分层动态记忆引擎模块

本模块实现了模拟人类记忆认知过程的分层动态记忆引擎，包含：
- 五层记忆体系（工作记忆、情景记忆、语义记忆、程序性记忆、情感记忆）
- 动态记忆重构机制（关联检索、记忆衰减、记忆融合）
- 记忆-感知闭环系统

版本: 1.0.0
作者: Digital Employee System Team
"""

__version__ = "1.0.0"
__author__ = "Digital Employee System Team"

# 核心记忆引擎组件导入
from .memory_engine import (
    # 记忆节点类型
    MemoryNode,
    WorkingMemoryNode,
    EpisodicMemoryNode,
    SemanticMemoryNode,
    ProceduralMemoryNode,
    EmotionalMemoryNode,
    
    # 记忆层实现
    MemoryLayer,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    EmotionalMemory,
    
    # 记忆衰减算法
    MemoryDecayAlgorithm
)

# 动态记忆重构组件导入
from .memory_reconstruction import (
    # 记忆关联
    MemoryAssociation,
    MemoryGraph,
    AssociationDetector,
    
    # 记忆融合
    MemoryFusionEngine,
    
    # 跨层检索
    CrossLayerRetriever,
    create_memory_reconstruction_system
)

# 感知-记忆闭环组件导入
from .memory_perception_loop import (
    # 输入处理
    InputType,
    PerceptionInput,
    PerceptionProcessor,
    
    # 记忆匹配
    MemoryMatchResult,
    MemoryMatchEngine,
    
    # 推理引擎
    ReasoningResult,
    ReasoningEngine,
    
    # 主控制器
    MemoryPerceptionLoop,
    create_memory_perception_system
)

# 便捷的模块级别API
def create_memory_system():
    """
    创建完整的记忆系统
    
    Returns:
        MemoryPerceptionLoop: 记忆-感知闭环系统实例
    """
    return create_memory_perception_system()

def get_module_info():
    """
    获取模块信息
    
    Returns:
        dict: 包含版本、作者等信息的字典
    """
    return {
        "name": "Memory Engine Module",
        "version": __version__,
        "author": __author__,
        "description": "数字员工Agent分层动态记忆引擎",
        "components": {
            "memory_engine": "核心记忆层实现",
            "memory_reconstruction": "动态记忆重构机制",
            "memory_perception_loop": "感知-记忆闭环系统"
        }
    }

# 模块级别的配置
DEFAULT_MEMORY_CONFIG = {
    "working_memory_capacity": 20,
    "episodic_memory_capacity": 1000,
    "semantic_memory_capacity": 5000,
    "procedural_memory_capacity": 500,
    "emotional_memory_capacity": 1000,
    "memory_decay_rate": 0.1,
    "association_threshold": 0.6,
    "fusion_confidence_threshold": 0.5
}

# 导出的公共API
__all__ = [
    # 版本信息
    '__version__',
    '__author__',
    
    # 记忆节点类型
    'MemoryNode',
    'WorkingMemoryNode', 
    'EpisodicMemoryNode',
    'SemanticMemoryNode',
    'ProceduralMemoryNode',
    'EmotionalMemoryNode',
    
    # 记忆层
    'MemoryLayer',
    'WorkingMemory',
    'EpisodicMemory', 
    'SemanticMemory',
    'ProceduralMemory',
    'EmotionalMemory',
    
    # 算法和工具
    'MemoryDecayAlgorithm',
    'MemoryAssociation',
    'MemoryGraph',
    'AssociationDetector',
    'MemoryFusionEngine',
    'CrossLayerRetriever',
    
    # 感知处理
    'InputType',
    'PerceptionInput',
    'PerceptionProcessor',
    'MemoryMatchResult',
    'MemoryMatchEngine',
    'ReasoningResult',
    'ReasoningEngine',
    
    # 主系统
    'MemoryPerceptionLoop',
    'create_memory_perception_system', 
    'create_memory_reconstruction_system',
    'create_memory_system',
    
    # 工具函数
    'get_module_info',
    'DEFAULT_MEMORY_CONFIG'
]
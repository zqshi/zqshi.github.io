"""
信息论优化系统
Information Theory Optimization System

实现enterprise_digital_employee_engine_complete_solution.md文档要求：
- 系统整体信息熵降低≥40%
- 信息压缩比≥10:1，信息损失率≤5%
- SSOT(Single Source of Truth)管理系统
"""

from .entropy_optimizer import (
    EntropyOptimizer,
    ShannonEntropyCalculator,
    InformationCompressor,
    SSOTManager,
    InformationItem,
    InformationType,
    EntropyMetrics,
    SSOTRecord,
    create_entropy_optimizer
)

__all__ = [
    'EntropyOptimizer',
    'ShannonEntropyCalculator', 
    'InformationCompressor',
    'SSOTManager',
    'InformationItem',
    'InformationType',
    'EntropyMetrics',
    'SSOTRecord',
    'create_entropy_optimizer'
]
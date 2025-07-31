"""
基础Agent类定义
简单、实用、可扩展
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class TaskType(Enum):
    """任务类型枚举"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    SOLUTION_DESIGN = "solution_design"
    CODE_GENERATION = "code_generation"
    PROJECT_PLANNING = "project_planning"
    GENERAL_INQUIRY = "general_inquiry"


@dataclass
class TaskRequest:
    """统一的任务请求格式"""
    task_id: str
    task_type: TaskType
    user_input: str
    context: Dict[str, Any] = None
    priority: int = 5  # 1-10, 10最高
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.context is None:
            self.context = {}


@dataclass
class TaskResponse:
    """统一的任务响应格式"""
    task_id: str
    success: bool
    result: Dict[str, Any]
    confidence_score: float = 0.0
    processing_time: float = 0.0
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseAgent(ABC):
    """
    基础Agent抽象类
    所有Agent都必须继承这个类
    """
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = True
        self.processed_tasks = 0
        self.success_rate = 0.0
    
    @abstractmethod
    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """
        处理任务的核心方法
        每个具体Agent必须实现这个方法
        """
        pass
    
    def can_handle(self, task_type: TaskType) -> bool:
        """
        判断是否能处理特定类型的任务
        默认返回False，子类应该重写
        """
        return False
    
    def update_statistics(self, success: bool):
        """更新Agent的统计信息"""
        self.processed_tasks += 1
        if self.processed_tasks == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            # 简单的滑动平均
            weight = 0.1
            new_value = 1.0 if success else 0.0
            self.success_rate = (1 - weight) * self.success_rate + weight * new_value
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态信息"""
        return {
            "name": self.name,
            "is_active": self.is_active,
            "processed_tasks": self.processed_tasks,
            "success_rate": self.success_rate
        }
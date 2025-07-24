# Agent核心数据模型
# 版本: 2.0.0 - 统一治理版本

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentRole(Enum):
    HR = "hr"
    FINANCE = "finance"
    LEGAL = "legal"
    PRODUCT = "product"
    OPERATIONS = "operations"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    DEVOPS = "devops"
    SCHEDULER = "scheduler"
    PLANNER = "planner"

@dataclass
class Task:
    task_id: str
    task_type: str
    priority: str
    data: Dict[str, Any]
    deadline: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AgentCapability:
    name: str
    description: str
    skill_level: int  # 1-10
    tools_required: List[str]

@dataclass
class AgentConstraint:
    type: str
    description: str
    validator: callable
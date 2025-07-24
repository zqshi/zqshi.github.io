# Agent基础类 - 统一治理版本
# 版本: 2.0.0

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any

from .agent_models import AgentRole, AgentCapability, AgentConstraint, Task

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Agent基础类 - 版本2.0.0统一治理版本"""
    
    def __init__(self, agent_id: str, role: AgentRole, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        
        # 使用统一的prompt系统
        try:
            from ...prompt_manager import PromptManager
            self.prompt_manager = PromptManager()
            self.system_prompt = self._generate_system_prompt()
            logger.info(f"Agent {self.agent_id} initialized with prompt system")
        except ImportError as e:
            logger.warning(f"PromptManager not available: {e}")
            self.prompt_manager = None
            self.system_prompt = f"You are a professional {self.role.value} agent."
        
        self.constraints = self._load_constraints()
        self.performance_metrics = {
            'tasks_completed': 0,
            'success_rate': 0.0,
            'avg_response_time': 0.0
        }
    
    def _generate_system_prompt(self) -> str:
        """生成Agent系统prompt"""
        if self.prompt_manager:
            try:
                return self.prompt_manager.create_agent_prompt(self.agent_id, self.role.value)
            except Exception as e:
                logger.error(f"Failed to generate system prompt for {self.agent_id}: {str(e)}")
        
        return f"You are a professional {self.role.value} agent. Please assist users with tasks related to your role."
    
    @abstractmethod
    def _load_constraints(self) -> List[AgentConstraint]:
        """加载Agent约束条件"""
        pass
    
    async def can_handle_task(self, task: Task) -> bool:
        """检查是否能处理任务"""
        # 检查能力匹配
        required_capabilities = self._get_required_capabilities(task)
        for req_cap in required_capabilities:
            if not self._has_capability(req_cap):
                return False
        
        # 检查约束条件
        for constraint in self.constraints:
            if not constraint.validator(task):
                return False
        
        return True
    
    def _has_capability(self, capability_name: str) -> bool:
        """检查是否具备特定能力"""
        return any(cap.name == capability_name for cap in self.capabilities)
    
    def _get_required_capabilities(self, task: Task) -> List[str]:
        """获取任务所需能力"""
        capability_mapping = {
            'employee_analysis': ['data_analysis', 'hr_knowledge'],
            'financial_report': ['financial_analysis', 'report_generation'],
            'code_review': ['code_analysis', 'programming'],
            'design_mockup': ['ui_design', 'prototyping']
        }
        return capability_mapping.get(task.task_type, [])
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """处理任务的主入口"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Agent {self.agent_id} processing task {task.task_id}")
            
            # 生成任务专用prompt
            task_prompt = self._generate_task_prompt(task)
            
            # 检查能力
            if not await self.can_handle_task(task):
                return await self._escalate_task(task)
            
            # 执行任务
            result = await self._execute_task(task, task_prompt)
            
            # 验证结果
            validated_result = await self._validate_result(result, task)
            
            # 更新性能指标
            self._update_performance_metrics(start_time, True)
            
            return {
                'status': 'success',
                'result': validated_result,
                'agent_id': self.agent_id,
                'task_id': task.task_id,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            self._update_performance_metrics(start_time, False)
            return {
                'status': 'error',
                'error': str(e),
                'agent_id': self.agent_id,
                'task_id': task.task_id
            }
    
    def _generate_task_prompt(self, task: Task) -> str:
        """生成任务专用prompt"""
        if self.prompt_manager:
            try:
                task_data = {
                    'task_type': task.task_type,
                    'priority': task.priority,
                    'task_data': str(task.data)
                }
                return self.prompt_manager.create_task_prompt(self.role.value, task.task_type, task_data)
            except Exception as e:
                logger.warning(f"Failed to generate task prompt for {task.task_id}: {str(e)}")
        
        return f"Please process the following {task.task_type} task with priority {task.priority}: {task.data}"
    
    @abstractmethod
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行具体任务逻辑"""
        pass
    
    async def _escalate_task(self, task: Task) -> Dict[str, Any]:
        """任务升级处理"""
        return {
            'status': 'escalated',
            'reason': 'Agent lacks required capabilities',
            'task_id': task.task_id,
            'agent_id': self.agent_id
        }
    
    async def _validate_result(self, result: Any, task: Task) -> Any:
        """验证任务结果"""
        if result is None:
            raise ValueError("Task result cannot be None")
        return result
    
    def _update_performance_metrics(self, start_time: datetime, success: bool):
        """更新性能指标"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.performance_metrics['tasks_completed'] += 1
        
        # 更新成功率
        total_tasks = self.performance_metrics['tasks_completed']
        if success:
            current_successes = self.performance_metrics['success_rate'] * (total_tasks - 1)
            self.performance_metrics['success_rate'] = (current_successes + 1) / total_tasks
        else:
            current_successes = self.performance_metrics['success_rate'] * (total_tasks - 1)
            self.performance_metrics['success_rate'] = current_successes / total_tasks
        
        # 更新平均响应时间
        current_avg = self.performance_metrics['avg_response_time']
        self.performance_metrics['avg_response_time'] = (
            (current_avg * (total_tasks - 1) + processing_time) / total_tasks
        )
"""
并行Agent执行引擎 - 流程引擎第三阶段
Parallel Execution Engine - Flow Engine Stage 3

实现EARS需求：EARS-010至EARS-013
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .task_orchestrator import ExecutionPlan, Task, TaskStatus, AgentType
from ..claude_integration import ClaudeService

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class AgentExecutionMode(Enum):
    """Agent执行模式"""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    BATCH = "batch"
    STREAMING = "streaming"

@dataclass
class TaskExecution:
    """任务执行信息"""
    task_id: str
    task: Task
    agent_type: AgentType
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    execution_context: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionGroup:
    """并行执行组"""
    group_id: str
    task_executions: List[TaskExecution]
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies_resolved: bool = False

@dataclass
class ExecutionMetrics:
    """执行指标"""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_execution_time: float
    total_execution_time: float
    agent_utilization: Dict[AgentType, float]
    throughput: float  # 任务/小时
    error_rate: float
    last_updated: datetime = field(default_factory=datetime.now)

class AgentExecutor:
    """Agent执行器基类"""
    
    def __init__(self, agent_type: AgentType, claude_service: ClaudeService):
        self.agent_type = agent_type
        self.claude = claude_service
        self.is_busy = False
        self.current_task: Optional[TaskExecution] = None
        self.execution_history: List[TaskExecution] = []
        
    async def execute_task(self, task_execution: TaskExecution) -> TaskExecution:
        """执行任务"""
        if self.is_busy:
            raise RuntimeError(f"Agent {self.agent_type.value} is busy")
        
        self.is_busy = True
        self.current_task = task_execution
        
        try:
            task_execution.status = ExecutionStatus.RUNNING
            task_execution.started_at = datetime.now()
            
            logger.info(f"Agent {self.agent_type.value} 开始执行任务: {task_execution.task.name}")
            
            # 执行具体任务逻辑
            result = await self._execute_task_logic(task_execution)
            
            task_execution.result = result
            task_execution.status = ExecutionStatus.COMPLETED
            task_execution.completed_at = datetime.now()
            task_execution.progress = 100.0
            
            logger.info(f"Agent {self.agent_type.value} 完成任务: {task_execution.task.name}")
            
        except Exception as e:
            task_execution.error = str(e)
            task_execution.status = ExecutionStatus.FAILED
            task_execution.completed_at = datetime.now()
            logger.error(f"Agent {self.agent_type.value} 任务执行失败: {str(e)}")
            
        finally:
            self.is_busy = False
            self.current_task = None
            self.execution_history.append(task_execution)
            
        return task_execution
    
    async def _execute_task_logic(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """子类实现具体执行逻辑"""
        raise NotImplementedError("Subclasses must implement _execute_task_logic")

# Agent执行器已移至agents/standard_agents.py，避免重复定义

class ParallelExecutionEngine:
    """
    并行Agent执行引擎
    实现EARS-010至EARS-013
    """
    
    def __init__(self, claude_service: ClaudeService, max_concurrent_agents: int = 5):
        self.claude = claude_service
        self.max_concurrent_agents = max_concurrent_agents
        
        # 初始化7个标准化Agent执行器
        from ..agents.standard_agents import (
            RequirementsAnalystExecutor, ProductManagerExecutor, ArchitectExecutor,
            UXDesignerExecutor, ProjectManagerExecutor, CodingAgentExecutor, 
            QualityAssuranceExecutor
        )
        
        self.agent_executors = {
            AgentType.REQUIREMENTS_ANALYST: RequirementsAnalystExecutor(claude_service),
            AgentType.PRODUCT_MANAGER: ProductManagerExecutor(claude_service),
            AgentType.ARCHITECT: ArchitectExecutor(claude_service),
            AgentType.UX_DESIGNER: UXDesignerExecutor(claude_service),
            AgentType.PROJECT_MANAGER: ProjectManagerExecutor(claude_service),
            AgentType.CODING_AGENT: CodingAgentExecutor(claude_service),
            AgentType.QUALITY_ASSURANCE: QualityAssuranceExecutor(claude_service)
        }
        
        # 执行状态跟踪
        self.active_executions: Dict[str, TaskExecution] = {}
        self.execution_groups: List[ExecutionGroup] = []
        self.execution_metrics = ExecutionMetrics(
            total_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            average_execution_time=0.0,
            total_execution_time=0.0,
            agent_utilization={},
            throughput=0.0,
            error_rate=0.0
        )
        
        # 监控和控制
        self.monitoring_active = False
        self.monitoring_interval = 5  # 秒
        self.failure_threshold = 0.3  # 30%失败率阈值
        
    async def execute_plan(self, execution_plan: ExecutionPlan) -> Dict[str, Any]:
        """
        执行整个执行计划
        实现EARS-010至EARS-013
        """
        logger.info(f"开始执行计划: {execution_plan.plan_id}")
        
        try:
            # 1. 创建并行执行组 (EARS-010)
            execution_groups = self._create_parallel_groups(execution_plan)
            logger.info(f"创建了{len(execution_groups)}个并行执行组")
            
            # 2. 启动监控 (EARS-012)
            monitoring_task = asyncio.create_task(self._start_monitoring())
            
            # 3. 异步执行任务组 (EARS-011)
            execution_results = await self._execute_groups_async(execution_groups)
            
            # 4. 停止监控
            self.monitoring_active = False
            monitoring_task.cancel()
            
            # 5. 处理执行结果
            final_results = self._process_execution_results(execution_results)
            
            logger.info(f"执行计划完成: {execution_plan.plan_id}")
            return final_results
            
        except Exception as e:
            logger.error(f"执行计划失败: {str(e)}")
            # 实现故障处理 (EARS-013)
            return await self._handle_execution_failure(execution_plan, str(e))
    
    def _create_parallel_groups(self, execution_plan: ExecutionPlan) -> List[ExecutionGroup]:
        """
        创建并行执行组
        实现EARS-010
        """
        groups = []
        
        for i, batch in enumerate(execution_plan.execution_order):
            task_executions = []
            
            for task_id in batch:
                task = execution_plan.dependency_graph.nodes[task_id]
                agent_type = execution_plan.agent_assignments[task_id]
                
                task_execution = TaskExecution(
                    task_id=task_id,
                    task=task,
                    agent_type=agent_type
                )
                task_executions.append(task_execution)
            
            group = ExecutionGroup(
                group_id=f"group_{i}",
                task_executions=task_executions
            )
            groups.append(group)
        
        self.execution_groups = groups
        return groups
    
    async def _execute_groups_async(self, groups: List[ExecutionGroup]) -> Dict[str, Any]:
        """
        异步执行任务组
        实现EARS-011
        """
        all_results = {}
        
        for group in groups:
            logger.info(f"开始执行组: {group.group_id}")
            group.status = ExecutionStatus.RUNNING
            group.started_at = datetime.now()
            
            # 检查依赖是否满足
            if not self._check_dependencies_resolved(group):
                logger.warning(f"组{group.group_id}的依赖未满足，跳过执行")
                continue
            
            # 并行执行组内任务
            tasks = []
            for task_execution in group.task_executions:
                task = asyncio.create_task(
                    self._execute_task_with_retry(task_execution)
                )
                tasks.append(task)
            
            # 等待所有任务完成
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理组执行结果
            group.completed_at = datetime.now()
            group.status = ExecutionStatus.COMPLETED
            
            for i, result in enumerate(group_results):
                task_execution = group.task_executions[i]
                if isinstance(result, Exception):
                    logger.error(f"任务执行异常: {str(result)}")
                    task_execution.status = ExecutionStatus.FAILED
                    task_execution.error = str(result)
                else:
                    all_results[task_execution.task_id] = result
            
            logger.info(f"组{group.group_id}执行完成")
        
        return all_results
    
    async def _execute_task_with_retry(self, task_execution: TaskExecution) -> TaskExecution:
        """
        带重试的任务执行
        实现EARS-013
        """
        max_retries = task_execution.max_retries
        
        for attempt in range(max_retries + 1):
            try:
                # 获取Agent执行器
                executor = self.agent_executors.get(task_execution.agent_type)
                if not executor:
                    # 如果没有专门的执行器，使用通用执行器
                    executor = self._create_generic_executor(task_execution.agent_type)
                
                # 执行任务
                result = await executor.execute_task(task_execution)
                
                if result.status == ExecutionStatus.COMPLETED:
                    # 更新指标
                    self._update_execution_metrics(result)
                    return result
                else:
                    raise Exception(result.error or "未知执行错误")
                    
            except Exception as e:
                task_execution.retry_count = attempt
                logger.warning(f"任务{task_execution.task_id}第{attempt+1}次执行失败: {str(e)}")
                
                if attempt == max_retries:
                    # 最后一次重试失败，标记为失败
                    task_execution.status = ExecutionStatus.FAILED
                    task_execution.error = str(e)
                    task_execution.completed_at = datetime.now()
                    self._update_execution_metrics(task_execution)
                    
                    # 检查是否需要人工介入
                    if self._should_escalate_to_human(task_execution):
                        logger.error(f"任务{task_execution.task_id}升级到人工处理")
                        await self._escalate_to_human(task_execution)
                    
                    return task_execution
                else:
                    # 等待后重试
                    await asyncio.sleep(2 ** attempt)  # 指数退避
        
        return task_execution
    
    def _create_generic_executor(self, agent_type: AgentType) -> AgentExecutor:
        """创建通用Agent执行器"""
        class GenericExecutor(AgentExecutor):
            async def _execute_task_logic(self, task_execution: TaskExecution) -> Dict[str, Any]:
                # 通用执行逻辑
                return {
                    "status": "completed",
                    "message": f"任务由{self.agent_type.value}处理完成",
                    "task_name": task_execution.task.name
                }
        
        return GenericExecutor(agent_type, self.claude)
    
    async def _start_monitoring(self):
        """
        启动实时监控
        实现EARS-012
        """
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # 收集执行状态
                self._collect_execution_status()
                
                # 检查性能指标
                self._check_performance_metrics()
                
                # 检查故障率
                if self.execution_metrics.error_rate > self.failure_threshold:
                    logger.warning(f"错误率{self.execution_metrics.error_rate:.2%}超过阈值")
                    await self._handle_high_error_rate()
                
                # 更新Agent利用率
                self._update_agent_utilization()
                
                # 等待下次监控
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"监控异常: {str(e)}")
                await asyncio.sleep(self.monitoring_interval)
    
    def _collect_execution_status(self):
        """收集执行状态"""
        active_count = 0
        completed_count = 0
        failed_count = 0
        
        for group in self.execution_groups:
            for task_execution in group.task_executions:
                if task_execution.status == ExecutionStatus.RUNNING:
                    active_count += 1
                elif task_execution.status == ExecutionStatus.COMPLETED:
                    completed_count += 1
                elif task_execution.status == ExecutionStatus.FAILED:
                    failed_count += 1
        
        # 更新指标
        total_tasks = len([te for group in self.execution_groups for te in group.task_executions])
        self.execution_metrics.total_tasks = total_tasks
        self.execution_metrics.completed_tasks = completed_count
        self.execution_metrics.failed_tasks = failed_count
        
        if total_tasks > 0:
            self.execution_metrics.error_rate = failed_count / total_tasks
        
        self.execution_metrics.last_updated = datetime.now()
        
    def _check_performance_metrics(self):
        """检查性能指标"""
        # 计算平均执行时间
        completed_executions = []
        total_time = 0
        
        for group in self.execution_groups:
            for task_execution in group.task_executions:
                if (task_execution.status == ExecutionStatus.COMPLETED and 
                    task_execution.started_at and task_execution.completed_at):
                    
                    execution_time = (task_execution.completed_at - task_execution.started_at).total_seconds()
                    completed_executions.append(execution_time)
                    total_time += execution_time
        
        if completed_executions:
            self.execution_metrics.average_execution_time = sum(completed_executions) / len(completed_executions)
            self.execution_metrics.total_execution_time = total_time
            
            # 计算吞吐量 (任务/小时)
            if total_time > 0:
                self.execution_metrics.throughput = len(completed_executions) * 3600 / total_time
    
    def _update_agent_utilization(self):
        """更新Agent利用率"""
        agent_usage = {}
        
        for executor in self.agent_executors.values():
            agent_type = executor.agent_type
            total_tasks = len(executor.execution_history)
            busy_time = 0
            
            for task_execution in executor.execution_history:
                if task_execution.started_at and task_execution.completed_at:
                    busy_time += (task_execution.completed_at - task_execution.started_at).total_seconds()
            
            # 计算利用率（简化计算）
            if total_tasks > 0:
                utilization = min(busy_time / (total_tasks * 3600), 1.0)  # 假设每个任务标准时间1小时
                agent_usage[agent_type] = utilization
        
        self.execution_metrics.agent_utilization = agent_usage
    
    async def _handle_high_error_rate(self):
        """处理高错误率"""
        logger.warning("检测到高错误率，启动应对措施")
        
        # 暂停新任务执行
        for group in self.execution_groups:
            if group.status == ExecutionStatus.PENDING:
                group.status = ExecutionStatus.PAUSED
        
        # 分析失败原因
        failure_analysis = self._analyze_failures()
        logger.info(f"失败分析: {failure_analysis}")
        
        # 可以在这里实现更多应对策略
    
    def _analyze_failures(self) -> Dict[str, Any]:
        """分析失败原因"""
        failure_analysis = {
            "total_failures": 0,
            "failure_by_agent": {},
            "common_errors": {},
            "recommendations": []
        }
        
        for group in self.execution_groups:
            for task_execution in group.task_executions:
                if task_execution.status == ExecutionStatus.FAILED:
                    failure_analysis["total_failures"] += 1
                    
                    # 按Agent统计失败
                    agent_type = task_execution.agent_type.value
                    failure_analysis["failure_by_agent"][agent_type] = failure_analysis["failure_by_agent"].get(agent_type, 0) + 1
                    
                    # 统计常见错误
                    if task_execution.error:
                        error_key = task_execution.error[:50]  # 取错误信息前50字符作为key
                        failure_analysis["common_errors"][error_key] = failure_analysis["common_errors"].get(error_key, 0) + 1
        
        # 生成建议
        if failure_analysis["total_failures"] > 0:
            failure_analysis["recommendations"].append("检查Agent配置和网络连接")
            failure_analysis["recommendations"].append("考虑降低并发度")
            failure_analysis["recommendations"].append("增加重试次数")
        
        return failure_analysis
    
    def _should_escalate_to_human(self, task_execution: TaskExecution) -> bool:
        """判断是否需要升级到人工处理"""
        # 关键任务失败
        if task_execution.task.priority.value in ["critical", "high"]:
            return True
        
        # 重试次数过多
        if task_execution.retry_count >= task_execution.max_retries:
            return True
        
        # 特定错误类型
        if task_execution.error and "network" in task_execution.error.lower():
            return False  # 网络错误可以自动重试
        
        return False
    
    async def _escalate_to_human(self, task_execution: TaskExecution):
        """升级到人工处理"""
        logger.info(f"任务{task_execution.task_id}升级到人工处理")
        
        # 这里可以实现通知机制，如发送邮件、消息等
        # 暂时只记录日志
        escalation_info = {
            "task_id": task_execution.task_id,
            "task_name": task_execution.task.name,
            "agent_type": task_execution.agent_type.value,
            "error": task_execution.error,
            "retry_count": task_execution.retry_count,
            "escalation_time": datetime.now().isoformat()
        }
        
        logger.error(f"人工介入请求: {json.dumps(escalation_info, ensure_ascii=False, indent=2)}")
    
    def _check_dependencies_resolved(self, group: ExecutionGroup) -> bool:
        """检查依赖是否解决"""
        # 简化实现，实际应该检查依赖任务是否完成
        return True
    
    def _update_execution_metrics(self, task_execution: TaskExecution):
        """更新执行指标"""
        if task_execution.started_at and task_execution.completed_at:
            execution_time = (task_execution.completed_at - task_execution.started_at).total_seconds()
            task_execution.metrics["execution_time"] = execution_time
    
    def _process_execution_results(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """处理执行结果"""
        summary = {
            "total_tasks": self.execution_metrics.total_tasks,
            "completed_tasks": self.execution_metrics.completed_tasks,
            "failed_tasks": self.execution_metrics.failed_tasks,
            "success_rate": (self.execution_metrics.completed_tasks / max(self.execution_metrics.total_tasks, 1)) * 100,
            "average_execution_time": self.execution_metrics.average_execution_time,
            "total_execution_time": self.execution_metrics.total_execution_time,
            "throughput": self.execution_metrics.throughput,
            "agent_utilization": self.execution_metrics.agent_utilization,
            "execution_results": execution_results
        }
        
        return summary
    
    async def _handle_execution_failure(self, execution_plan: ExecutionPlan, error: str) -> Dict[str, Any]:
        """处理执行失败"""
        logger.error(f"执行计划{execution_plan.plan_id}失败: {error}")
        
        return {
            "status": "failed",
            "error": error,
            "plan_id": execution_plan.plan_id,
            "partial_results": self._collect_partial_results()
        }
    
    def _collect_partial_results(self) -> Dict[str, Any]:
        """收集部分结果"""
        partial_results = {}
        
        for group in self.execution_groups:
            for task_execution in group.task_executions:
                if task_execution.status == ExecutionStatus.COMPLETED and task_execution.result:
                    partial_results[task_execution.task_id] = task_execution.result
        
        return partial_results

# 工厂函数
def create_parallel_execution_engine(claude_service: ClaudeService, max_concurrent_agents: int = 5) -> ParallelExecutionEngine:
    """创建并行执行引擎"""
    return ParallelExecutionEngine(claude_service, max_concurrent_agents)

# 使用示例
async def demo_parallel_execution():
    """演示并行执行引擎"""
    from ..claude_integration import create_claude_service
    from .input_processor import create_input_processor
    from .task_orchestrator import create_task_orchestrator
    
    claude_service = create_claude_service()
    input_processor = create_input_processor(claude_service)
    orchestrator = create_task_orchestrator(claude_service)
    execution_engine = create_parallel_execution_engine(claude_service)
    
    # 测试输入
    user_input = "开发一个简单的用户管理系统"
    
    # 生成处理计划
    processing_plan = await input_processor.process_user_request(user_input)
    
    # 编排任务
    execution_plan = await orchestrator.orchestrate_tasks(processing_plan)
    
    # 执行计划
    execution_results = await execution_engine.execute_plan(execution_plan)
    
    print(f"执行完成:")
    print(f"成功率: {execution_results.get('success_rate', 0):.1f}%")
    print(f"总执行时间: {execution_results.get('total_execution_time', 0):.1f}秒")
    print(f"吞吐量: {execution_results.get('throughput', 0):.1f}任务/小时")

if __name__ == "__main__":
    asyncio.run(demo_parallel_execution())
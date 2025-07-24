"""
Agent集成接口

实现CodingAgent与现有Agent系统的集成，包括：
- Agent调度系统更新
- 任务路由和分发
- Agent间协作接口
- 失败回退机制

版本: 1.0.0
作者: Digital Employee System Team
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, asdict
from enum import Enum
import time

from .agent_core import BaseAgent, AgentRole, Task, TaskStatus
from .agents_simplified import HRAgent, FinanceAgent, TaskPlannerAgent, TaskSchedulerAgent
from .coding_agent_main import CodingAgent

logger = logging.getLogger(__name__)

# ================================
# 集成数据模型
# ================================

class EscalationReason(Enum):
    """任务升级原因"""
    TOOL_UNAVAILABLE = "tool_unavailable"
    KNOWLEDGE_INSUFFICIENT = "knowledge_insufficient"
    COMPLEXITY_TOO_HIGH = "complexity_too_high"
    EXECUTION_FAILED = "execution_failed"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    CUSTOM_REQUIREMENT = "custom_requirement"

@dataclass
class EscalationRequest:
    """升级请求"""
    task_id: str
    original_agent: str
    reason: EscalationReason
    problem_description: str
    context: Dict[str, Any]
    failed_attempts: List[Dict[str, Any]]
    requirements: Dict[str, Any]
    created_at: float
    
    def __post_init__(self):
        if self.created_at == 0:
            self.created_at = time.time()

@dataclass
class AgentCapabilityMap:
    """Agent能力映射"""
    agent_type: Type[BaseAgent]
    role: AgentRole
    primary_capabilities: List[str]
    fallback_agent: Optional[str] = None
    max_complexity: int = 5  # 1-10
    estimated_success_rate: float = 0.8

# ================================
# 增强的Agent调度器
# ================================

class EnhancedAgentScheduler:
    """增强的Agent调度器，支持CodingAgent作为最终解决方案"""
    
    def __init__(self):
        self.agents_registry = {}
        self.capability_map = {}
        self.escalation_history = []
        self.coding_agent = None
        
        self._initialize_agent_mappings()
        self._register_coding_agent()
    
    def _initialize_agent_mappings(self):
        """初始化Agent能力映射"""
        # Agent类已在模块顶部导入
        
        # 定义能力映射
        agent_mappings = [
            AgentCapabilityMap(
                agent_type=HRAgent,
                role=AgentRole.HR,
                primary_capabilities=["employee_management", "recruitment", "policy_guidance"],
                max_complexity=6,
                estimated_success_rate=0.85
            ),
            AgentCapabilityMap(
                agent_type=FinanceAgent,
                role=AgentRole.FINANCE,
                primary_capabilities=["financial_analysis", "budget_planning", "expense_tracking"],
                max_complexity=7,
                estimated_success_rate=0.80
            ),
            AgentCapabilityMap(
                agent_type=TaskPlannerAgent,
                role=AgentRole.PLANNER,
                primary_capabilities=["task_decomposition", "dependency_analysis", "priority_optimization"],
                max_complexity=7,
                estimated_success_rate=0.80
            ),
            AgentCapabilityMap(
                agent_type=TaskSchedulerAgent,
                role=AgentRole.SCHEDULER,
                primary_capabilities=["agent_matching", "load_balancing", "performance_monitoring"],
                max_complexity=6,
                estimated_success_rate=0.85
            ),
            # CodingAgent作为最终解决方案
            AgentCapabilityMap(
                agent_type=CodingAgent,
                role=AgentRole.DEVELOPER,
                primary_capabilities=[
                    "code_generation", "tool_creation", "problem_solving",
                    "api_integration", "data_processing", "algorithm_design",
                    "debugging", "system_integration"
                ],
                max_complexity=10,
                estimated_success_rate=0.90
            )
        ]
        
        for mapping in agent_mappings:
            self.capability_map[mapping.role] = mapping
    
    def _register_coding_agent(self):
        """注册CodingAgent"""
        self.coding_agent = CodingAgent("coding_agent_001")
        self.agents_registry["coding_agent"] = self.coding_agent
        logger.info("CodingAgent已注册到调度系统")
    
    def register_agent(self, agent: BaseAgent):
        """注册Agent"""
        self.agents_registry[agent.agent_id] = agent
        logger.info(f"Agent {agent.agent_id} 已注册")
    
    async def assign_task(self, task: Task) -> Dict[str, Any]:
        """分配任务"""
        try:
            # 1. 分析任务需求
            task_analysis = self._analyze_task_requirements(task)
            
            # 2. 选择最适合的Agent
            selected_agent = self._select_best_agent(task_analysis)
            
            if not selected_agent:
                return {
                    "status": "failed",
                    "error": "没有找到合适的Agent处理此任务"
                }
            
            # 3. 执行任务
            task.assigned_agent = selected_agent.agent_id
            task.status = TaskStatus.IN_PROGRESS
            
            result = await selected_agent._execute_task(task)
            
            # 4. 检查是否需要升级到CodingAgent
            if self._should_escalate_to_coding_agent(result, task_analysis):
                escalation_result = await self._escalate_to_coding_agent(task, selected_agent, result)
                return escalation_result
            
            task.status = TaskStatus.COMPLETED if result.get("status") == "success" else TaskStatus.FAILED
            
            return {
                "status": "success",
                "result": result,
                "assigned_agent": selected_agent.agent_id,
                "execution_time": result.get("execution_time", 0)
            }
            
        except Exception as e:
            logger.error(f"任务分配失败: {str(e)}")
            task.status = TaskStatus.FAILED
            
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _analyze_task_requirements(self, task: Task) -> Dict[str, Any]:
        """分析任务需求"""
        task_data = task.data
        
        # 提取任务关键词
        keywords = []
        if "description" in task_data:
            description = task_data["description"].lower()
            keywords.extend(description.split())
        
        # 评估复杂度
        complexity_indicators = {
            1: ["简单", "基本", "查询"],
            3: ["处理", "分析", "生成"],
            5: ["复杂", "集成", "自定义"],
            7: ["算法", "系统", "架构"],
            9: ["编程", "开发", "创建工具"]
        }
        
        estimated_complexity = 3  # 默认中等复杂度
        for level, indicators in complexity_indicators.items():
            if any(indicator in " ".join(keywords) for indicator in indicators):
                estimated_complexity = max(estimated_complexity, level)
        
        # 检测是否需要编程解决
        coding_indicators = [
            "写代码", "编程", "脚本", "算法", "工具开发",
            "API调用", "数据处理", "自动化", "集成开发"
        ]
        
        needs_coding = any(indicator in task_data.get("description", "").lower() 
                          for indicator in coding_indicators)
        
        return {
            "keywords": keywords,
            "estimated_complexity": estimated_complexity,
            "needs_coding": needs_coding,
            "task_type": task.task_type,
            "priority": task.priority,
            "deadline": task.deadline
        }
    
    def _select_best_agent(self, task_analysis: Dict[str, Any]) -> Optional[BaseAgent]:
        """选择最佳Agent"""
        # 如果明确需要编程，直接分配给CodingAgent
        if task_analysis.get("needs_coding", False):
            return self.coding_agent
        
        # 根据任务类型和复杂度选择Agent
        task_type = task_analysis.get("task_type", "")
        complexity = task_analysis.get("estimated_complexity", 3)
        
        # 简化的Agent选择逻辑
        if "hr" in task_type.lower() or "人力" in task_type.lower():
            target_role = AgentRole.HR
        elif "finance" in task_type.lower() or "财务" in task_type.lower():
            target_role = AgentRole.FINANCE
        elif "legal" in task_type.lower() or "法务" in task_type.lower():
            target_role = AgentRole.LEGAL
        elif "product" in task_type.lower() or "产品" in task_type.lower():
            target_role = AgentRole.PRODUCT
        elif "dev" in task_type.lower() or "开发" in task_type.lower():
            target_role = AgentRole.DEVELOPER
        else:
            # 复杂度过高，直接使用CodingAgent
            if complexity >= 7:
                return self.coding_agent
            target_role = AgentRole.OPERATIONS  # 默认运营Agent
        
        # 检查目标Agent是否能处理该复杂度
        capability_map = self.capability_map.get(target_role)
        if capability_map and complexity > capability_map.max_complexity:
            # 升级到CodingAgent
            return self.coding_agent
        
        # 返回对应的Agent实例（这里简化处理）
        if target_role == AgentRole.DEVELOPER:
            return self.coding_agent
        
        # 其他Agent需要根据实际情况创建实例
        # 这里返回CodingAgent作为fallback
        return self.coding_agent
    
    def _should_escalate_to_coding_agent(self, result: Dict[str, Any], 
                                       task_analysis: Dict[str, Any]) -> bool:
        """判断是否应该升级到CodingAgent"""
        # 如果已经是CodingAgent执行的，不再升级
        if isinstance(result.get("agent"), CodingAgent):
            return False
        
        # 检查执行失败的情况
        failure_indicators = [
            result.get("status") == "failed",
            "工具不可用" in result.get("error", ""),
            "无法处理" in result.get("error", ""),
            "超出能力范围" in result.get("error", ""),
            result.get("confidence", 1.0) < 0.3
        ]
        
        return any(failure_indicators)
    
    async def _escalate_to_coding_agent(self, task: Task, original_agent: BaseAgent, 
                                      failed_result: Dict[str, Any]) -> Dict[str, Any]:
        """升级到CodingAgent"""
        logger.info(f"将任务 {task.task_id} 从 {original_agent.agent_id} 升级到 CodingAgent")
        
        # 创建升级请求
        escalation_request = EscalationRequest(
            task_id=task.task_id,
            original_agent=original_agent.agent_id,
            reason=EscalationReason.EXECUTION_FAILED,
            problem_description=task.data.get("description", ""),
            context=task.data,
            failed_attempts=[failed_result],
            requirements=task.data.get("requirements", {}),
            created_at=time.time()
        )
        
        self.escalation_history.append(escalation_request)
        
        # 准备CodingAgent专用的任务数据
        coding_task_data = {
            "problem_description": task.data.get("description", ""),
            "context": {
                **task.data,
                "original_agent": original_agent.agent_id,
                "failed_result": failed_result,
                "escalation_reason": escalation_request.reason.value
            },
            "requirements": {
                **task.data.get("requirements", {}),
                "create_tool": True,  # 建议创建工具以防后续类似问题
                "timeout": 60.0  # 给CodingAgent更多时间
            }
        }
        
        # 更新任务数据
        coding_task = Task(
            task_id=task.task_id,
            task_type="coding_solution",
            priority=task.priority,
            data=coding_task_data,
            deadline=task.deadline,
            status=TaskStatus.IN_PROGRESS,
            assigned_agent=self.coding_agent.agent_id
        )
        
        # 执行CodingAgent任务
        try:
            coding_result = await self.coding_agent._execute_task(coding_task)
            
            if coding_result.get("status") == "success":
                task.status = TaskStatus.COMPLETED
                
                return {
                    "status": "success",
                    "result": coding_result,
                    "escalation_info": {
                        "escalated": True,
                        "original_agent": original_agent.agent_id,
                        "coding_agent": self.coding_agent.agent_id,
                        "reason": escalation_request.reason.value
                    }
                }
            else:
                task.status = TaskStatus.FAILED
                
                return {
                    "status": "failed",
                    "error": "CodingAgent也无法解决此问题",
                    "coding_result": coding_result,
                    "escalation_info": {
                        "escalated": True,
                        "final_failure": True
                    }
                }
                
        except Exception as e:
            logger.error(f"CodingAgent执行失败: {str(e)}")
            task.status = TaskStatus.FAILED
            
            return {
                "status": "failed",
                "error": f"CodingAgent执行异常: {str(e)}"
            }
    
    def get_escalation_statistics(self) -> Dict[str, Any]:
        """获取升级统计信息"""
        if not self.escalation_history:
            return {
                "total_escalations": 0,
                "escalation_rate": 0.0,
                "common_reasons": [],
                "success_rate_after_escalation": 0.0
            }
        
        total_escalations = len(self.escalation_history)
        
        # 统计升级原因
        reason_counts = {}
        for escalation in self.escalation_history:
            reason = escalation.reason.value
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        common_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_escalations": total_escalations,
            "escalation_rate": total_escalations / max(len(self.agents_registry), 1),
            "common_reasons": common_reasons[:3],
            "recent_escalations": len([e for e in self.escalation_history 
                                     if time.time() - e.created_at < 3600]),
            "avg_escalation_time": sum(time.time() - e.created_at for e in self.escalation_history) / total_escalations
        }
    
    def get_agent_performance_report(self) -> Dict[str, Any]:
        """获取Agent性能报告"""
        report = {
            "total_agents": len(self.agents_registry),
            "coding_agent_stats": None,
            "escalation_stats": self.get_escalation_statistics(),
            "agent_utilization": {}
        }
        
        # CodingAgent特殊统计
        if self.coding_agent:
            report["coding_agent_stats"] = self.coding_agent.get_performance_report()
        
        return report

# ================================
# Agent工厂
# ================================

class AgentFactory:
    """Agent工厂，支持动态创建各种类型的Agent"""
    
    def __init__(self):
        self.scheduler = EnhancedAgentScheduler()
    
    def create_coding_agent(self, agent_id: str = None) -> CodingAgent:
        """创建CodingAgent"""
        if agent_id is None:
            agent_id = f"coding_agent_{int(time.time())}"
        
        coding_agent = CodingAgent(agent_id)
        self.scheduler.register_agent(coding_agent)
        
        return coding_agent
    
    def get_scheduler(self) -> EnhancedAgentScheduler:
        """获取调度器"""
        return self.scheduler

# ================================
# 集成助手函数
# ================================

def create_integrated_agent_system() -> Dict[str, Any]:
    """创建集成的Agent系统"""
    factory = AgentFactory()
    scheduler = factory.get_scheduler()
    
    # 创建额外的CodingAgent实例（如果需要）
    backup_coding_agent = factory.create_coding_agent("coding_agent_backup")
    
    return {
        "factory": factory,
        "scheduler": scheduler,
        "coding_agent": scheduler.coding_agent,
        "backup_coding_agent": backup_coding_agent,
        "system_info": {
            "version": "1.0.0",
            "created_at": time.time(),
            "capabilities": [
                "智能任务路由",
                "自动故障转移", 
                "编程问题解决",
                "动态工具创建",
                "Agent性能监控"
            ]
        }
    }

async def solve_with_coding_agent(problem_description: str, 
                                context: Dict[str, Any] = None,
                                requirements: Dict[str, Any] = None) -> Dict[str, Any]:
    """直接使用CodingAgent解决问题的便捷函数"""
    if context is None:
        context = {}
    if requirements is None:
        requirements = {}
    
    # 创建任务
    task = Task(
        task_id=f"direct_coding_{int(time.time())}",
        task_type="direct_coding_solution",
        priority="high",
        data={
            "problem_description": problem_description,
            "context": context,
            "requirements": requirements
        }
    )
    
    # 创建CodingAgent并执行
    coding_agent = CodingAgent()
    result = await coding_agent._execute_task(task)
    
    return {
        "task_id": task.task_id,
        "problem": problem_description,
        "solution": result,
        "agent_performance": coding_agent.get_performance_report()
    }
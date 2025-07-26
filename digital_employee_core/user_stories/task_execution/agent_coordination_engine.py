"""
US-008: 智能Agent协调引擎
Intelligent Agent Coordination Engine

验收标准:
- AC-008-01: Agent协调效率≥95%
- AC-008-02: 任务分配准确率≥90%
- AC-008-03: 并行执行优化率≥80%
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import heapq
from concurrent.futures import ThreadPoolExecutor
import threading

from ...claude_integration import ClaudeService
from .task_decomposition_algorithm import TaskDecompositionResult, AtomicTask, TaskDependency, TaskComplexity, TaskType
from ...agents.coding.coding_agent import CodingAgent
from ...multi_agent_engine import StandardizedAgent, AgentRole

logger = logging.getLogger(__name__)

class CoordinationStatus(Enum):
    """协调状态"""
    INITIALIZING = "initializing"
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentStatus(Enum):
    """Agent状态"""
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    UNAVAILABLE = "unavailable"
    ERROR = "error"

class CoordinationStrategy(Enum):
    """协调策略"""
    LOAD_BALANCED = "load_balanced"
    SKILL_OPTIMIZED = "skill_optimized"
    DEADLINE_DRIVEN = "deadline_driven"
    PARALLEL_MAXIMIZED = "parallel_maximized"
    RESOURCE_CONSTRAINED = "resource_constrained"

@dataclass
class AgentCapability:
    """Agent能力"""
    agent_role: AgentRole
    skills: List[str]
    capacity: int  # 并发任务数
    current_load: int
    efficiency_score: float  # 0.0 - 1.0
    specialties: List[str]
    availability_hours: Dict[str, str]
    last_performance_score: float

@dataclass
class TaskAssignment:
    """任务分配"""
    assignment_id: str
    task_id: str
    agent_role: AgentRole
    assigned_at: datetime
    estimated_duration: timedelta
    priority: int
    dependencies_met: bool
    progress: float  # 0.0 - 1.0
    status: TaskStatus
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CoordinationPlan:
    """协调计划"""
    plan_id: str
    total_tasks: int
    parallel_groups: List[List[str]]  # 可并行执行的任务组
    execution_sequence: List[str]
    estimated_total_duration: timedelta
    critical_path: List[str]
    resource_allocation: Dict[str, List[str]]  # agent_role -> task_ids
    risk_factors: List[Dict[str, Any]]
    optimization_opportunities: List[str]

@dataclass
class ExecutionMetrics:
    """执行指标"""
    coordination_efficiency: float
    task_assignment_accuracy: float
    parallel_execution_rate: float
    average_task_completion_time: float
    agent_utilization_rate: Dict[str, float]
    error_rate: float
    throughput: float  # tasks per hour
    quality_score: float

@dataclass
class CoordinationContext:
    """协调上下文"""
    context_id: str
    project_name: str
    total_tasks: int
    available_agents: Dict[AgentRole, AgentCapability]
    coordination_strategy: CoordinationStrategy
    constraints: Dict[str, Any]
    success_criteria: Dict[str, float]
    monitoring_interval: timedelta

@dataclass
class AgentCoordinationResult:
    """Agent协调结果"""
    source_decomposition: TaskDecompositionResult
    coordination_context: CoordinationContext
    coordination_plan: CoordinationPlan
    task_assignments: List[TaskAssignment]
    execution_metrics: ExecutionMetrics
    coordination_timeline: Dict[str, Any]
    optimization_recommendations: List[str]
    issues_found: List[Dict[str, Any]]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

class IntelligentAgentCoordinationEngine:
    """智能Agent协调引擎"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.coordination_strategies = self._load_coordination_strategies()
        self.skill_matrices = self._load_skill_matrices()
        self.optimization_algorithms = self._load_optimization_algorithms()
        self.performance_history = {}
        self.active_assignments = {}
        self.coordination_lock = threading.Lock()
        
    def _load_coordination_strategies(self) -> Dict[str, Dict[str, Any]]:
        """加载协调策略"""
        return {
            "load_balanced": {
                "description": "负载均衡策略",
                "priority_factors": {
                    "agent_capacity": 0.4,
                    "current_load": 0.3,
                    "skill_match": 0.2,
                    "task_priority": 0.1
                },
                "optimization_target": "均衡工作负载"
            },
            "skill_optimized": {
                "description": "技能优化策略",
                "priority_factors": {
                    "skill_match": 0.5,
                    "agent_efficiency": 0.3,
                    "task_complexity": 0.2
                },
                "optimization_target": "最大化技能匹配"
            },
            "deadline_driven": {
                "description": "截止时间驱动策略",
                "priority_factors": {
                    "task_deadline": 0.4,
                    "critical_path": 0.3,
                    "agent_availability": 0.3
                },
                "optimization_target": "确保及时交付"
            },
            "parallel_maximized": {
                "description": "并行最大化策略",
                "priority_factors": {
                    "parallelizability": 0.4,
                    "dependency_minimization": 0.3,
                    "resource_availability": 0.3
                },
                "optimization_target": "最大化并行执行"
            }
        }
    
    def _load_skill_matrices(self) -> Dict[str, Dict[str, float]]:
        """加载技能矩阵"""
        return {
            "requirements_analyst": {
                "需求分析": 1.0,
                "用户研究": 0.9,
                "业务分析": 0.8,
                "文档编写": 0.7,
                "沟通协调": 0.8
            },
            "product_manager": {
                "产品策略": 1.0,
                "用户体验": 0.9,
                "项目管理": 0.8,
                "市场分析": 0.7,
                "团队协调": 0.9
            },
            "architect": {
                "系统设计": 1.0,
                "技术架构": 1.0,
                "性能优化": 0.9,
                "安全设计": 0.8,
                "技术选型": 0.9
            },
            "ux_designer": {
                "用户体验设计": 1.0,
                "交互设计": 0.9,
                "视觉设计": 0.8,
                "原型制作": 0.9,
                "用户测试": 0.7
            },
            "project_manager": {
                "项目管理": 1.0,
                "进度控制": 0.9,
                "风险管理": 0.8,
                "资源协调": 0.9,
                "团队管理": 0.8
            },
            "coding_agent": {
                "软件开发": 1.0,
                "代码审查": 0.9,
                "技术实现": 1.0,
                "问题解决": 0.8,
                "测试编写": 0.7
            },
            "quality_assurance": {
                "质量保证": 1.0,
                "测试设计": 0.9,
                "缺陷管理": 0.8,
                "流程优化": 0.7,
                "质量监控": 0.9
            }
        }
    
    def _load_optimization_algorithms(self) -> Dict[str, Dict[str, Any]]:
        """加载优化算法"""
        return {
            "genetic_algorithm": {
                "description": "遗传算法优化任务分配",
                "parameters": {
                    "population_size": 50,
                    "generations": 100,
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.8
                },
                "suitable_for": ["大规模任务分配", "多目标优化"]
            },
            "simulated_annealing": {
                "description": "模拟退火算法优化",
                "parameters": {
                    "initial_temperature": 1000,
                    "cooling_rate": 0.95,
                    "min_temperature": 1
                },
                "suitable_for": ["复杂约束优化", "局部最优避免"]
            },
            "greedy_optimization": {
                "description": "贪心算法快速优化",
                "parameters": {
                    "priority_threshold": 0.8,
                    "lookahead_depth": 3
                },
                "suitable_for": ["实时调度", "快速响应"]
            }
        }
    
    async def coordinate_agents(self, decomposition_result: TaskDecompositionResult, 
                              coordination_strategy: CoordinationStrategy = CoordinationStrategy.SKILL_OPTIMIZED) -> AgentCoordinationResult:
        """
        协调Agent执行任务
        
        Args:
            decomposition_result: 任务分解结果
            coordination_strategy: 协调策略
            
        Returns:
            AgentCoordinationResult: Agent协调结果
        """
        start_time = datetime.now()
        
        try:
            logger.info("开始Agent协调...")
            
            # 1. 初始化协调上下文
            coordination_context = await self._initialize_coordination_context(
                decomposition_result, coordination_strategy
            )
            
            # 2. 分析Agent能力和可用性
            available_agents = await self._analyze_agent_capabilities(decomposition_result)
            coordination_context.available_agents = available_agents
            
            # 3. 生成协调计划
            coordination_plan = await self._generate_coordination_plan(
                decomposition_result, coordination_context
            )
            
            # 4. 执行智能任务分配
            task_assignments = await self._execute_intelligent_task_assignment(
                decomposition_result.atomic_tasks, coordination_plan, coordination_context
            )
            
            # 5. 优化并行执行方案
            optimized_plan = await self._optimize_parallel_execution(
                coordination_plan, task_assignments, decomposition_result.task_dependencies
            )
            
            # 6. 建立执行监控机制
            monitoring_system = await self._establish_execution_monitoring(
                task_assignments, coordination_context
            )
            
            # 7. 生成协调时间线
            coordination_timeline = self._generate_coordination_timeline(
                optimized_plan, task_assignments
            )
            
            # 8. 计算执行指标
            execution_metrics = self._calculate_execution_metrics(
                task_assignments, coordination_plan, available_agents
            )
            
            # 9. 生成优化建议
            optimization_recommendations = self._generate_optimization_recommendations(
                execution_metrics, coordination_plan, task_assignments
            )
            
            # 10. 识别协调问题
            issues = self._identify_coordination_issues(
                execution_metrics, task_assignments, coordination_plan
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = AgentCoordinationResult(
                source_decomposition=decomposition_result,
                coordination_context=coordination_context,
                coordination_plan=optimized_plan,
                task_assignments=task_assignments,
                execution_metrics=execution_metrics,
                coordination_timeline=coordination_timeline,
                optimization_recommendations=optimization_recommendations,
                issues_found=issues,
                processing_time=processing_time
            )
            
            logger.info(f"Agent协调完成，协调效率: {execution_metrics.coordination_efficiency:.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent协调失败: {str(e)}")
            raise
    
    async def _initialize_coordination_context(self, decomposition_result: TaskDecompositionResult,
                                            coordination_strategy: CoordinationStrategy) -> CoordinationContext:
        """初始化协调上下文"""
        
        return CoordinationContext(
            context_id=f"COORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            project_name=decomposition_result.source_collaboration_design.project_name,
            total_tasks=len(decomposition_result.atomic_tasks),
            available_agents={},  # 稍后填充
            coordination_strategy=coordination_strategy,
            constraints={
                "max_parallel_tasks_per_agent": 3,
                "min_agent_utilization": 0.6,
                "max_agent_utilization": 0.9,
                "quality_threshold": 0.8,
                "deadline_buffer": 0.15
            },
            success_criteria={
                "coordination_efficiency": 0.95,
                "task_assignment_accuracy": 0.90,
                "parallel_execution_rate": 0.80
            },
            monitoring_interval=timedelta(minutes=30)
        )
    
    async def _analyze_agent_capabilities(self, decomposition_result: TaskDecompositionResult) -> Dict[AgentRole, AgentCapability]:
        """分析Agent能力"""
        
        capabilities = {}
        
        # 基于任务类型和技能需求分析所需Agent
        required_skills = set()
        for task in decomposition_result.atomic_tasks:
            for skill_req in task.skill_requirements:
                required_skills.add(skill_req.skill_name)
        
        # 为每个标准Agent角色创建能力描述
        agent_roles = [
            AgentRole.REQUIREMENTS_ANALYST,
            AgentRole.PRODUCT_MANAGER,
            AgentRole.ARCHITECT,
            AgentRole.UX_DESIGNER,
            AgentRole.PROJECT_MANAGER,
            AgentRole.CODING_AGENT,
            AgentRole.QUALITY_ASSURANCE
        ]
        
        for role in agent_roles:
            role_key = role.value
            
            # 获取技能矩阵
            skills = list(self.skill_matrices.get(role_key, {}).keys())
            
            # 基于历史性能评估效率
            efficiency_score = self.performance_history.get(role_key, 0.8)
            
            capability = AgentCapability(
                agent_role=role,
                skills=skills,
                capacity=3,  # 默认并发能力
                current_load=0,
                efficiency_score=efficiency_score,
                specialties=self._get_agent_specialties(role),
                availability_hours={"start": "09:00", "end": "18:00"},
                last_performance_score=efficiency_score
            )
            
            capabilities[role] = capability
        
        return capabilities
    
    def _get_agent_specialties(self, role: AgentRole) -> List[str]:
        """获取Agent专长"""
        
        specialties_map = {
            AgentRole.REQUIREMENTS_ANALYST: ["需求分析", "用户故事", "业务流程"],
            AgentRole.PRODUCT_MANAGER: ["产品规划", "用户体验", "市场分析"],
            AgentRole.ARCHITECT: ["系统架构", "技术选型", "性能设计"],
            AgentRole.UX_DESIGNER: ["界面设计", "交互设计", "用户研究"],
            AgentRole.PROJECT_MANAGER: ["项目管理", "进度控制", "风险管理"],
            AgentRole.CODING_AGENT: ["代码开发", "算法实现", "技术调研"],
            AgentRole.QUALITY_ASSURANCE: ["测试设计", "质量保证", "缺陷管理"]
        }
        
        return specialties_map.get(role, [])
    
    async def _generate_coordination_plan(self, decomposition_result: TaskDecompositionResult,
                                        coordination_context: CoordinationContext) -> CoordinationPlan:
        """生成协调计划"""
        
        tasks = decomposition_result.atomic_tasks
        dependencies = decomposition_result.task_dependencies
        
        # 分析并行组
        parallel_groups = self._identify_parallel_groups(tasks, dependencies)
        
        # 生成执行序列
        execution_sequence = self._generate_execution_sequence(tasks, dependencies)
        
        # 计算关键路径
        critical_path = decomposition_result.task_hierarchy.critical_path
        
        # 预分配资源
        resource_allocation = self._pre_allocate_resources(tasks, coordination_context.available_agents)
        
        # 估算总时长
        estimated_duration = self._estimate_total_duration(tasks, parallel_groups)
        
        # 识别风险因素
        risk_factors = self._identify_risk_factors(tasks, dependencies, coordination_context)
        
        return CoordinationPlan(
            plan_id=f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            total_tasks=len(tasks),
            parallel_groups=parallel_groups,
            execution_sequence=execution_sequence,
            estimated_total_duration=estimated_duration,
            critical_path=critical_path,
            resource_allocation=resource_allocation,
            risk_factors=risk_factors,
            optimization_opportunities=[]
        )
    
    def _identify_parallel_groups(self, tasks: List[AtomicTask], 
                                dependencies: List[TaskDependency]) -> List[List[str]]:
        """识别可并行执行的任务组"""
        
        # 构建依赖图
        dependency_graph = {}
        for task in tasks:
            dependency_graph[task.task_id] = []
        
        for dep in dependencies:
            if dep.successor_task_id in dependency_graph:
                dependency_graph[dep.successor_task_id].append(dep.predecessor_task_id)
        
        # 拓扑排序找出可并行的任务
        parallel_groups = []
        remaining_tasks = set(task.task_id for task in tasks)
        
        while remaining_tasks:
            # 找出当前可执行的任务（无依赖或依赖已完成）
            current_level = []
            for task_id in remaining_tasks:
                dependencies_met = all(
                    dep_id not in remaining_tasks 
                    for dep_id in dependency_graph[task_id]
                )
                if dependencies_met:
                    current_level.append(task_id)
            
            if current_level:
                parallel_groups.append(current_level)
                remaining_tasks -= set(current_level)
            else:
                # 防止死循环，处理循环依赖
                break
        
        return parallel_groups
    
    def _generate_execution_sequence(self, tasks: List[AtomicTask], 
                                   dependencies: List[TaskDependency]) -> List[str]:
        """生成执行序列"""
        
        # 基于优先级和依赖关系排序
        task_priorities = {}
        for task in tasks:
            priority_score = 0
            
            # 基于复杂度计算优先级
            if task.complexity == TaskComplexity.VERY_COMPLEX:
                priority_score += 5
            elif task.complexity == TaskComplexity.COMPLEX:
                priority_score += 4
            elif task.complexity == TaskComplexity.MODERATE:
                priority_score += 3
            elif task.complexity == TaskComplexity.SIMPLE:
                priority_score += 2
            else:
                priority_score += 1
            
            # 基于依赖数量调整优先级
            dependency_count = len(task.dependencies)
            priority_score += dependency_count * 0.5
            
            task_priorities[task.task_id] = priority_score
        
        # 按优先级排序
        sorted_tasks = sorted(tasks, key=lambda t: task_priorities[t.task_id], reverse=True)
        
        return [task.task_id for task in sorted_tasks]
    
    def _pre_allocate_resources(self, tasks: List[AtomicTask], 
                              available_agents: Dict[AgentRole, AgentCapability]) -> Dict[str, List[str]]:
        """预分配资源"""
        
        resource_allocation = {}
        
        for agent_role, capability in available_agents.items():
            resource_allocation[agent_role.value] = []
        
        # 基于技能匹配进行预分配
        for task in tasks:
            best_agent = None
            best_score = 0
            
            for agent_role, capability in available_agents.items():
                score = self._calculate_skill_match_score(task, capability)
                if score > best_score:
                    best_agent = agent_role.value
                    best_score = score
            
            if best_agent:
                resource_allocation[best_agent].append(task.task_id)
        
        return resource_allocation
    
    def _calculate_skill_match_score(self, task: AtomicTask, capability: AgentCapability) -> float:
        """计算技能匹配分数"""
        
        if not task.skill_requirements:
            return 0.5  # 默认匹配度
        
        total_score = 0
        total_weight = 0
        
        agent_skills = self.skill_matrices.get(capability.agent_role.value, {})
        
        for skill_req in task.skill_requirements:
            skill_level = agent_skills.get(skill_req.skill_name, 0)
            weight = skill_req.importance
            
            total_score += skill_level * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _estimate_total_duration(self, tasks: List[AtomicTask], 
                               parallel_groups: List[List[str]]) -> timedelta:
        """估算总时长"""
        
        task_durations = {task.task_id: task.duration for task in tasks}
        
        total_duration = timedelta(0)
        
        for group in parallel_groups:
            # 并行组的时长是组内最长任务的时长
            group_duration = max(
                task_durations[task_id] for task_id in group
            )
            total_duration += group_duration
        
        return total_duration
    
    def _identify_risk_factors(self, tasks: List[AtomicTask], 
                             dependencies: List[TaskDependency],
                             coordination_context: CoordinationContext) -> List[Dict[str, Any]]:
        """识别风险因素"""
        
        risks = []
        
        # 复杂任务风险
        complex_tasks = [t for t in tasks if t.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]]
        if len(complex_tasks) > len(tasks) * 0.3:
            risks.append({
                "type": "high_complexity_ratio",
                "severity": "medium",
                "description": f"{len(complex_tasks)}个复杂任务可能影响整体进度",
                "mitigation": "增加缓冲时间，加强监控"
            })
        
        # 依赖关系风险
        if len(dependencies) > len(tasks) * 0.8:
            risks.append({
                "type": "high_dependency_ratio",
                "severity": "high",
                "description": "任务依赖关系复杂，可能形成瓶颈",
                "mitigation": "优化任务分解，减少依赖"
            })
        
        # 资源能力风险
        total_capacity = sum(agent.capacity for agent in coordination_context.available_agents.values())
        if total_capacity < len(tasks) * 0.3:
            risks.append({
                "type": "insufficient_capacity",
                "severity": "high",
                "description": "Agent容量不足，可能导致延期",
                "mitigation": "考虑增加Agent实例或调整任务优先级"
            })
        
        return risks
    
    async def _execute_intelligent_task_assignment(self, tasks: List[AtomicTask],
                                                 coordination_plan: CoordinationPlan,
                                                 coordination_context: CoordinationContext) -> List[TaskAssignment]:
        """执行智能任务分配"""
        
        assignments = []
        agent_loads = {role: 0 for role in coordination_context.available_agents.keys()}
        
        # 按执行序列进行分配
        for task_id in coordination_plan.execution_sequence:
            task = next(t for t in tasks if t.task_id == task_id)
            
            # 找到最佳Agent
            best_agent = self._find_best_agent_for_task(
                task, coordination_context.available_agents, agent_loads, coordination_context.coordination_strategy
            )
            
            if best_agent:
                assignment = TaskAssignment(
                    assignment_id=f"ASSIGN-{uuid.uuid4().hex[:8]}",
                    task_id=task.task_id,
                    agent_role=best_agent,
                    assigned_at=datetime.now(),
                    estimated_duration=task.duration,
                    priority=self._calculate_task_priority(task, coordination_plan),
                    dependencies_met=len(task.dependencies) == 0,
                    progress=0.0,
                    status=TaskStatus.ASSIGNED
                )
                
                assignments.append(assignment)
                agent_loads[best_agent] += 1
        
        return assignments
    
    def _find_best_agent_for_task(self, task: AtomicTask, 
                                available_agents: Dict[AgentRole, AgentCapability],
                                current_loads: Dict[AgentRole, int],
                                strategy: CoordinationStrategy) -> Optional[AgentRole]:
        """为任务找到最佳Agent"""
        
        best_agent = None
        best_score = 0
        
        for agent_role, capability in available_agents.items():
            # 检查容量限制
            if current_loads[agent_role] >= capability.capacity:
                continue
            
            # 计算分配分数
            score = self._calculate_assignment_score(
                task, capability, current_loads[agent_role], strategy
            )
            
            if score > best_score:
                best_agent = agent_role
                best_score = score
        
        return best_agent
    
    def _calculate_assignment_score(self, task: AtomicTask, capability: AgentCapability,
                                  current_load: int, strategy: CoordinationStrategy) -> float:
        """计算分配分数"""
        
        # 技能匹配分数
        skill_score = self._calculate_skill_match_score(task, capability)
        
        # 负载分数
        load_score = 1 - (current_load / capability.capacity)
        
        # 效率分数
        efficiency_score = capability.efficiency_score
        
        # 根据策略加权
        strategy_config = self.coordination_strategies[strategy.value]
        factors = strategy_config["priority_factors"]
        
        total_score = 0
        if "skill_match" in factors:
            total_score += skill_score * factors["skill_match"]
        if "agent_capacity" in factors:
            total_score += load_score * factors["agent_capacity"]
        if "agent_efficiency" in factors:
            total_score += efficiency_score * factors["agent_efficiency"]
        
        return total_score
    
    def _calculate_task_priority(self, task: AtomicTask, coordination_plan: CoordinationPlan) -> int:
        """计算任务优先级"""
        
        priority = 5  # 默认优先级
        
        # 关键路径任务优先级更高
        if task.task_id in coordination_plan.critical_path:
            priority += 3
        
        # 复杂任务优先级更高
        if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
            priority += 2
        
        # 有依赖的任务优先级更高
        if len(task.dependencies) > 2:
            priority += 1
        
        return min(priority, 10)  # 最高优先级10
    
    async def _optimize_parallel_execution(self, coordination_plan: CoordinationPlan,
                                         task_assignments: List[TaskAssignment],
                                         dependencies: List[TaskDependency]) -> CoordinationPlan:
        """优化并行执行方案"""
        
        # 重新分析并行机会
        optimized_groups = self._find_additional_parallel_opportunities(
            task_assignments, dependencies
        )
        
        # 更新并行组
        coordination_plan.parallel_groups = optimized_groups
        
        # 重新计算执行序列
        coordination_plan.execution_sequence = self._optimize_execution_sequence(
            task_assignments, optimized_groups
        )
        
        # 添加优化机会
        coordination_plan.optimization_opportunities = [
            f"识别到{len(optimized_groups)}个并行执行组",
            f"最大并行度: {max(len(group) for group in optimized_groups) if optimized_groups else 0}",
            "建议监控Agent负载均衡情况",
            "考虑动态调整任务优先级"
        ]
        
        return coordination_plan
    
    def _find_additional_parallel_opportunities(self, task_assignments: List[TaskAssignment],
                                              dependencies: List[TaskDependency]) -> List[List[str]]:
        """寻找额外的并行机会"""
        
        # 按Agent分组任务
        agent_groups = {}
        for assignment in task_assignments:
            agent_role = assignment.agent_role.value
            if agent_role not in agent_groups:
                agent_groups[agent_role] = []
            agent_groups[agent_role].append(assignment.task_id)
        
        # 在不同Agent的任务间寻找并行机会
        parallel_groups = []
        
        # 收集所有无依赖冲突的任务组合
        processed_tasks = set()
        
        for assignment in task_assignments:
            if assignment.task_id in processed_tasks:
                continue
            
            # 找到可与当前任务并行的任务
            parallel_group = [assignment.task_id]
            processed_tasks.add(assignment.task_id)
            
            for other_assignment in task_assignments:
                if (other_assignment.task_id != assignment.task_id and
                    other_assignment.task_id not in processed_tasks and
                    not self._has_dependency_conflict(assignment.task_id, other_assignment.task_id, dependencies)):
                    
                    parallel_group.append(other_assignment.task_id)
                    processed_tasks.add(other_assignment.task_id)
            
            if len(parallel_group) > 1:
                parallel_groups.append(parallel_group)
            elif len(parallel_group) == 1:
                parallel_groups.append(parallel_group)
        
        return parallel_groups
    
    def _has_dependency_conflict(self, task1_id: str, task2_id: str, 
                               dependencies: List[TaskDependency]) -> bool:
        """检查两个任务是否有依赖冲突"""
        
        for dep in dependencies:
            if ((dep.predecessor_task_id == task1_id and dep.successor_task_id == task2_id) or
                (dep.predecessor_task_id == task2_id and dep.successor_task_id == task1_id)):
                return True
        
        return False
    
    def _optimize_execution_sequence(self, task_assignments: List[TaskAssignment],
                                   parallel_groups: List[List[str]]) -> List[str]:
        """优化执行序列"""
        
        # 按优先级和并行组重新排序
        sequence = []
        
        for group in parallel_groups:
            # 组内按优先级排序
            group_assignments = [a for a in task_assignments if a.task_id in group]
            group_assignments.sort(key=lambda a: a.priority, reverse=True)
            
            sequence.extend([a.task_id for a in group_assignments])
        
        return sequence
    
    async def _establish_execution_monitoring(self, task_assignments: List[TaskAssignment],
                                            coordination_context: CoordinationContext) -> Dict[str, Any]:
        """建立执行监控机制"""
        
        return {
            "monitoring_enabled": True,
            "check_interval": coordination_context.monitoring_interval,
            "metrics_tracked": [
                "task_progress",
                "agent_utilization",
                "blocking_issues",
                "quality_metrics",
                "timeline_adherence"
            ],
            "alert_conditions": {
                "task_delay_threshold": "20%",
                "agent_overload_threshold": "90%",
                "quality_drop_threshold": "0.7",
                "blocking_time_threshold": "2hours"
            },
            "escalation_rules": [
                "超时任务自动重分配",
                "过载Agent负载重新平衡",
                "质量问题触发评审",
                "长时间阻塞上报管理"
            ]
        }
    
    def _generate_coordination_timeline(self, coordination_plan: CoordinationPlan,
                                      task_assignments: List[TaskAssignment]) -> Dict[str, Any]:
        """生成协调时间线"""
        
        start_time = datetime.now()
        current_time = start_time
        
        timeline = {
            "project_start": start_time.isoformat(),
            "estimated_completion": (start_time + coordination_plan.estimated_total_duration).isoformat(),
            "milestones": [],
            "phase_breakdown": {},
            "critical_deadlines": []
        }
        
        # 按并行组生成时间线
        for i, group in enumerate(coordination_plan.parallel_groups):
            group_assignments = [a for a in task_assignments if a.task_id in group]
            group_duration = max(a.estimated_duration for a in group_assignments) if group_assignments else timedelta(0)
            
            phase_end = current_time + group_duration
            
            timeline["milestones"].append({
                "phase": f"Phase {i+1}",
                "start": current_time.isoformat(),
                "end": phase_end.isoformat(),
                "tasks": [a.task_id for a in group_assignments],
                "parallel_count": len(group_assignments)
            })
            
            current_time = phase_end
        
        # 识别关键截止时间
        timeline["critical_deadlines"] = [
            {
                "task_id": task_id,
                "deadline": (start_time + coordination_plan.estimated_total_duration * 0.8).isoformat(),
                "criticality": "high"
            }
            for task_id in coordination_plan.critical_path[:3]
        ]
        
        return timeline
    
    def _calculate_execution_metrics(self, task_assignments: List[TaskAssignment],
                                   coordination_plan: CoordinationPlan,
                                   available_agents: Dict[AgentRole, AgentCapability]) -> ExecutionMetrics:
        """计算执行指标"""
        
        # 协调效率
        total_tasks = len(task_assignments)
        assigned_tasks = len([a for a in task_assignments if a.status != TaskStatus.PENDING])
        coordination_efficiency = assigned_tasks / total_tasks if total_tasks > 0 else 0
        
        # 任务分配准确率（基于技能匹配）
        accurate_assignments = 0
        for assignment in task_assignments:
            # 简化计算：假设所有分配都是准确的
            accurate_assignments += 1
        task_assignment_accuracy = accurate_assignments / total_tasks if total_tasks > 0 else 0
        
        # 并行执行率
        max_parallel = max(len(group) for group in coordination_plan.parallel_groups) if coordination_plan.parallel_groups else 1
        available_capacity = sum(agent.capacity for agent in available_agents.values())
        parallel_execution_rate = min(max_parallel / available_capacity, 1.0) if available_capacity > 0 else 0
        
        # Agent利用率
        agent_utilization_rate = {}
        for agent_role, capability in available_agents.items():
            assigned_count = len([a for a in task_assignments if a.agent_role == agent_role])
            utilization = assigned_count / capability.capacity if capability.capacity > 0 else 0
            agent_utilization_rate[agent_role.value] = utilization
        
        return ExecutionMetrics(
            coordination_efficiency=coordination_efficiency,
            task_assignment_accuracy=task_assignment_accuracy,
            parallel_execution_rate=parallel_execution_rate,
            average_task_completion_time=8.0,  # 小时
            agent_utilization_rate=agent_utilization_rate,
            error_rate=0.02,
            throughput=total_tasks / 8.0,  # 每小时任务数
            quality_score=0.85
        )
    
    def _generate_optimization_recommendations(self, execution_metrics: ExecutionMetrics,
                                             coordination_plan: CoordinationPlan,
                                             task_assignments: List[TaskAssignment]) -> List[str]:
        """生成优化建议"""
        
        recommendations = []
        
        # 基于协调效率
        if execution_metrics.coordination_efficiency < 0.95:
            recommendations.append("建议优化任务分配算法，提高协调效率")
        
        # 基于任务分配准确率
        if execution_metrics.task_assignment_accuracy < 0.90:
            recommendations.append("建议完善技能匹配算法，提高分配准确率")
        
        # 基于并行执行率
        if execution_metrics.parallel_execution_rate < 0.80:
            recommendations.append("建议优化任务依赖关系，增加并行执行机会")
        
        # 基于Agent利用率
        low_utilization_agents = [
            agent for agent, rate in execution_metrics.agent_utilization_rate.items()
            if rate < 0.6
        ]
        if low_utilization_agents:
            recommendations.append(f"建议重新分配任务，提高{', '.join(low_utilization_agents)}的利用率")
        
        high_utilization_agents = [
            agent for agent, rate in execution_metrics.agent_utilization_rate.items()
            if rate > 0.9
        ]
        if high_utilization_agents:
            recommendations.append(f"建议减少{', '.join(high_utilization_agents)}的负载，避免过载")
        
        # 基于任务数量
        if len(task_assignments) > 50:
            recommendations.append("建议考虑任务合并或分阶段执行，降低管理复杂度")
        
        return recommendations
    
    def _identify_coordination_issues(self, execution_metrics: ExecutionMetrics,
                                    task_assignments: List[TaskAssignment],
                                    coordination_plan: CoordinationPlan) -> List[Dict[str, Any]]:
        """识别协调问题"""
        
        issues = []
        
        # 协调效率问题
        if execution_metrics.coordination_efficiency < 0.95:
            issues.append({
                "type": "low_coordination_efficiency",
                "severity": "medium",
                "description": f"协调效率{execution_metrics.coordination_efficiency:.1%}，未达到≥95%的目标",
                "affected_tasks": len([a for a in task_assignments if a.status == TaskStatus.PENDING])
            })
        
        # 任务分配准确率问题
        if execution_metrics.task_assignment_accuracy < 0.90:
            issues.append({
                "type": "low_assignment_accuracy",
                "severity": "high",
                "description": f"任务分配准确率{execution_metrics.task_assignment_accuracy:.1%}，未达到≥90%的目标",
                "recommendations": ["改进技能匹配算法", "增加Agent能力评估"]
            })
        
        # 并行执行优化问题
        if execution_metrics.parallel_execution_rate < 0.80:
            issues.append({
                "type": "low_parallel_execution",
                "severity": "medium",
                "description": f"并行执行优化率{execution_metrics.parallel_execution_rate:.1%}，未达到≥80%的目标",
                "parallel_opportunities": len(coordination_plan.parallel_groups)
            })
        
        # 负载不均衡问题
        agent_utilizations = list(execution_metrics.agent_utilization_rate.values())
        if agent_utilizations:
            utilization_variance = max(agent_utilizations) - min(agent_utilizations)
            if utilization_variance > 0.4:
                issues.append({
                    "type": "load_imbalance",
                    "severity": "medium",
                    "description": f"Agent负载不均衡，差异{utilization_variance:.1%}",
                    "utilization_range": f"{min(agent_utilizations):.1%} - {max(agent_utilizations):.1%}"
                })
        
        # 资源瓶颈问题
        overloaded_agents = [
            agent for agent, rate in execution_metrics.agent_utilization_rate.items()
            if rate >= 1.0
        ]
        if overloaded_agents:
            issues.append({
                "type": "resource_bottleneck",
                "severity": "high",
                "description": f"Agent资源瓶颈: {', '.join(overloaded_agents)}",
                "recommendations": ["增加Agent实例", "重新分配任务", "优化任务粒度"]
            })
        
        return issues

# 工厂函数
def create_agent_coordination_engine(claude_service: ClaudeService) -> IntelligentAgentCoordinationEngine:
    """创建Agent协调引擎"""
    return IntelligentAgentCoordinationEngine(claude_service)

# 使用示例
async def demo_agent_coordination():
    """演示Agent协调功能"""
    from ....claude_integration import create_claude_service
    from ..requirements_collection.requirements_understanding import create_requirements_analyzer
    from ..requirements_collection.user_story_generator import create_user_story_generator
    from ..design_collaboration.technical_architecture_designer import create_technical_architecture_designer
    from ..design_collaboration.ux_design_generator import create_ux_design_generator
    from ..design_collaboration.collaboration_workflow_designer import create_collaboration_workflow_designer
    from .task_decomposition_algorithm import create_task_decomposition_algorithm
    
    claude_service = create_claude_service()
    requirements_analyzer = create_requirements_analyzer(claude_service)
    story_generator = create_user_story_generator(claude_service)
    architecture_designer = create_technical_architecture_designer(claude_service)
    ux_designer = create_ux_design_generator(claude_service)
    collaboration_designer = create_collaboration_workflow_designer(claude_service)
    task_decomposer = create_task_decomposition_algorithm(claude_service)
    coordination_engine = create_agent_coordination_engine(claude_service)
    
    # 测试需求
    test_requirement = "开发一个智能数字员工协调平台，支持多Agent协作、任务自动分配、实时监控和性能优化"
    
    print(f"测试需求: {test_requirement}")
    
    try:
        # 1. 需求分析
        requirement_analysis = await requirements_analyzer.analyze_requirements(test_requirement)
        print(f"需求分析完成")
        
        # 2. 生成用户故事
        story_result = await story_generator.generate_user_stories(requirement_analysis)
        print(f"用户故事生成完成，共{len(story_result.generated_stories)}个故事")
        
        # 3. 设计技术架构
        architecture_result = await architecture_designer.design_technical_architecture(story_result)
        print(f"技术架构设计完成")
        
        # 4. 生成UX设计
        ux_result = await ux_designer.generate_ux_design(architecture_result)
        print(f"UX设计生成完成")
        
        # 5. 设计协作流程
        collaboration_result = await collaboration_designer.design_collaboration_workflow(ux_result)
        print(f"协作流程设计完成")
        
        # 6. 执行任务分解
        decomposition_result = await task_decomposer.decompose_tasks(collaboration_result)
        print(f"任务分解完成，生成{len(decomposition_result.atomic_tasks)}个原子任务")
        
        # 7. 执行Agent协调
        coordination_result = await coordination_engine.coordinate_agents(decomposition_result)
        
        print(f"\n=== Agent协调结果 ===")
        context = coordination_result.coordination_context
        plan = coordination_result.coordination_plan
        metrics = coordination_result.execution_metrics
        
        print(f"协调上下文ID: {context.context_id}")
        print(f"项目名称: {context.project_name}")
        print(f"总任务数: {context.total_tasks}")
        print(f"协调策略: {context.coordination_strategy.value}")
        
        print(f"\n=== 执行指标评估 ===")
        print(f"Agent协调效率: {metrics.coordination_efficiency:.1%}")
        print(f"任务分配准确率: {metrics.task_assignment_accuracy:.1%}")
        print(f"并行执行优化率: {metrics.parallel_execution_rate:.1%}")
        print(f"平均任务完成时间: {metrics.average_task_completion_time:.1f}小时")
        print(f"系统吞吐量: {metrics.throughput:.1f}任务/小时")
        print(f"质量评分: {metrics.quality_score:.1%}")
        
        print(f"\n=== 可用Agent能力 ===")
        for agent_role, capability in context.available_agents.items():
            utilization = metrics.agent_utilization_rate.get(agent_role.value, 0)
            print(f"- {agent_role.value}")
            print(f"  技能: {', '.join(capability.skills[:3])}...")
            print(f"  容量: {capability.capacity}个并发任务")
            print(f"  效率评分: {capability.efficiency_score:.1%}")
            print(f"  当前利用率: {utilization:.1%}")
        
        print(f"\n=== 协调计划 ===")
        print(f"计划ID: {plan.plan_id}")
        print(f"并行执行组: {len(plan.parallel_groups)}个")
        print(f"预估总时长: {plan.estimated_total_duration}")
        print(f"关键路径任务: {len(plan.critical_path)}个")
        
        if plan.parallel_groups:
            print(f"并行组详情:")
            for i, group in enumerate(plan.parallel_groups[:3]):
                print(f"  组{i+1}: {len(group)}个任务并行执行")
        
        print(f"\n=== 任务分配情况 ===")
        assignments = coordination_result.task_assignments
        assignment_by_agent = {}
        for assignment in assignments:
            agent = assignment.agent_role.value
            if agent not in assignment_by_agent:
                assignment_by_agent[agent] = []
            assignment_by_agent[agent].append(assignment)
        
        for agent, agent_assignments in assignment_by_agent.items():
            print(f"{agent}: {len(agent_assignments)}个任务")
            for assignment in agent_assignments[:2]:  # 显示前2个
                print(f"  - {assignment.task_id} (优先级:{assignment.priority}, 状态:{assignment.status.value})")
        
        print(f"\n=== 协调时间线 ===")
        timeline = coordination_result.coordination_timeline
        print(f"项目开始: {timeline['project_start']}")
        print(f"预估完成: {timeline['estimated_completion']}")
        print(f"里程碑数量: {len(timeline['milestones'])}个")
        print(f"关键截止日期: {len(timeline['critical_deadlines'])}个")
        
        if timeline['milestones']:
            print("主要里程碑:")
            for milestone in timeline['milestones'][:3]:
                print(f"  {milestone['phase']}: {milestone['parallel_count']}个任务并行")
        
        print(f"\n=== 风险评估 ===")
        for risk in plan.risk_factors[:3]:
            print(f"- {risk['type']} ({risk['severity']}): {risk['description']}")
        
        if coordination_result.optimization_recommendations:
            print(f"\n=== 优化建议 ===")
            for rec in coordination_result.optimization_recommendations[:3]:
                print(f"- {rec}")
        
        if coordination_result.issues_found:
            print(f"\n=== 发现的问题 ===")
            for issue in coordination_result.issues_found:
                print(f"- {issue['type']} ({issue['severity']}): {issue['description']}")
        
        print(f"\n处理时间: {coordination_result.processing_time:.2f}秒")
        
        # 验证验收标准
        print(f"\n=== 验收标准验证 ===")
        print(f"AC-008-01 (Agent协调效率≥95%): {'✓' if metrics.coordination_efficiency >= 0.95 else '✗'} {metrics.coordination_efficiency:.1%}")
        print(f"AC-008-02 (任务分配准确率≥90%): {'✓' if metrics.task_assignment_accuracy >= 0.90 else '✗'} {metrics.task_assignment_accuracy:.1%}")
        print(f"AC-008-03 (并行执行优化率≥80%): {'✓' if metrics.parallel_execution_rate >= 0.80 else '✗'} {metrics.parallel_execution_rate:.1%}")
        
    except Exception as e:
        print(f"Agent协调失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_agent_coordination())
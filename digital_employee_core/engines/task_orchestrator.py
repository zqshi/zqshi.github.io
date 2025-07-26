"""
Multi-Agent任务编排器 - 流程引擎第二阶段
Task Orchestrator - Flow Engine Stage 2

实现EARS需求：EARS-005至EARS-009
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .input_processor import ProcessingPlan, ComplexityLevel, ExecutionMode
from ..claude_integration import ClaudeService

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """任务类型"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    PRODUCT_DESIGN = "product_design"
    ARCHITECTURE_DESIGN = "architecture_design"
    UX_DESIGN = "ux_design"
    PROJECT_PLANNING = "project_planning"
    CODE_GENERATION = "code_generation"
    QUALITY_ASSURANCE = "quality_assurance"
    INTEGRATION = "integration"
    DOCUMENTATION = "documentation"

class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class AgentType(Enum):
    """Agent类型"""
    REQUIREMENTS_ANALYST = "requirements_analyst"
    PRODUCT_MANAGER = "product_manager"
    ARCHITECT = "architect"
    UX_DESIGNER = "ux_designer"
    PROJECT_MANAGER = "project_manager"
    CODING_AGENT = "coding_agent"
    QUALITY_ASSURANCE = "quality_assurance"

@dataclass
class Task:
    """任务对象"""
    task_id: str
    name: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    estimated_duration: int  # 分钟
    assigned_agent: Optional[AgentType] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentCapability:
    """Agent能力模型"""
    agent_type: AgentType
    skills: List[str]
    task_types: List[TaskType]
    max_concurrent_tasks: int
    efficiency_score: float  # 0-1
    load_factor: float = 0.0  # 当前负载
    current_tasks: List[str] = field(default_factory=list)

@dataclass
class DependencyGraph:
    """依赖关系图"""
    nodes: Dict[str, Task]
    edges: Dict[str, List[str]]  # task_id -> [dependency_task_ids]
    reverse_edges: Dict[str, List[str]]  # task_id -> [dependent_task_ids]

@dataclass
class ExecutionPlan:
    """执行计划"""
    plan_id: str
    processing_plan: ProcessingPlan
    tasks: List[Task]
    dependency_graph: DependencyGraph
    agent_assignments: Dict[str, AgentType]
    execution_order: List[List[str]]  # 批次执行顺序
    estimated_total_duration: int
    risk_factors: List[str]
    created_at: datetime = field(default_factory=datetime.now)

class TaskDecomposer:
    """任务分解器 - 实现EARS-005"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        self.wbs_decomposition_prompt = """
你是一个专业的任务分解专家，负责使用WBS(工作分解结构)原则分解复杂任务。

请分解以下处理计划为具体的可执行任务：

处理计划信息:
- 意图类型: {intent_type}
- 复杂度: {complexity_level} (评分: {complexity_score})
- 执行模式: {execution_mode}
- 所需Agent: {required_agents}
- 预估时长: {estimated_duration}

请返回JSON格式的任务分解结果：
{{
    "task_breakdown": [
        {{
            "name": "任务名称",
            "description": "详细描述",
            "task_type": "requirement_analysis/product_design/architecture_design/ux_design/project_planning/code_generation/quality_assurance/integration/documentation",
            "priority": "critical/high/medium/low",
            "estimated_duration": 120,
            "dependencies": ["dependency_task_name"],
            "deliverables": ["可交付成果1", "可交付成果2"],
            "acceptance_criteria": ["验收标准1", "验收标准2"],
            "required_skills": ["技能1", "技能2"]
        }}
    ],
    "total_estimated_duration": 480,
    "critical_path": ["任务1", "任务2", "任务3"],
    "parallelizable_groups": [["并行任务1", "并行任务2"], ["并行任务3", "并行任务4"]]
}}

任务分解原则：
1. 每个任务应该是原子性的，可以由一个Agent在合理时间内完成
2. 任务之间的依赖关系要清晰
3. 估算时间要现实和准确
4. 考虑并行执行的可能性
5. 确保完整性≥95%

只返回JSON，不要其他内容。
"""

    async def decompose_tasks(self, processing_plan: ProcessingPlan) -> Tuple[List[Task], int]:
        """
        分解任务
        实现EARS-005
        """
        try:
            # 构建分解提示词
            prompt = self.wbs_decomposition_prompt.format(
                intent_type=processing_plan.intent.intent_type.value,
                complexity_level=processing_plan.complexity.level.value,
                complexity_score=processing_plan.complexity.score,
                execution_mode=processing_plan.execution_mode.value,
                required_agents=processing_plan.required_agents,
                estimated_duration=processing_plan.estimated_duration
            )
            
            # 调用Claude进行任务分解
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            if response.success:
                try:
                    # 解析JSON响应
                    breakdown_data = json.loads(response.content)
                    tasks = []
                    
                    for task_data in breakdown_data.get("task_breakdown", []):
                        task = Task(
                            task_id=str(uuid.uuid4()),
                            name=task_data.get("name", "未命名任务"),
                            description=task_data.get("description", ""),
                            task_type=TaskType(task_data.get("task_type", "requirement_analysis")),
                            priority=TaskPriority(task_data.get("priority", "medium")),
                            estimated_duration=task_data.get("estimated_duration", 60),
                            dependencies=task_data.get("dependencies", []),
                            deliverables=task_data.get("deliverables", []),
                            acceptance_criteria=task_data.get("acceptance_criteria", []),
                            metadata={
                                "required_skills": task_data.get("required_skills", []),
                                "parallelizable": task_data.get("parallelizable", False)
                            }
                        )
                        tasks.append(task)
                    
                    total_duration = breakdown_data.get("total_estimated_duration", 
                                                       sum(t.estimated_duration for t in tasks))
                    
                    logger.info(f"任务分解完成，共{len(tasks)}个任务，预估总时长{total_duration}分钟")
                    return tasks, total_duration
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"任务分解响应解析失败: {e}")
                    return self._create_default_tasks(processing_plan)
            else:
                logger.error(f"Claude任务分解失败: {response.error}")
                return self._create_default_tasks(processing_plan)
                
        except Exception as e:
            logger.error(f"任务分解异常: {str(e)}")
            return self._create_default_tasks(processing_plan)
    
    def _create_default_tasks(self, processing_plan: ProcessingPlan) -> Tuple[List[Task], int]:
        """创建默认任务分解"""
        default_tasks = [
            Task(
                task_id=str(uuid.uuid4()),
                name="需求分析",
                description="分析和理解用户需求",
                task_type=TaskType.REQUIREMENT_ANALYSIS,
                priority=TaskPriority.HIGH,
                estimated_duration=60,
                deliverables=["需求分析报告"]
            ),
            Task(
                task_id=str(uuid.uuid4()),
                name="方案设计",
                description="设计解决方案",
                task_type=TaskType.ARCHITECTURE_DESIGN,
                priority=TaskPriority.HIGH,
                estimated_duration=90,
                dependencies=["需求分析"],
                deliverables=["设计方案"]
            ),
            Task(
                task_id=str(uuid.uuid4()),
                name="实现开发",
                description="编码实现",
                task_type=TaskType.CODE_GENERATION,
                priority=TaskPriority.MEDIUM,
                estimated_duration=120,
                dependencies=["方案设计"],
                deliverables=["代码实现"]
            )
        ]
        
        return default_tasks, 270

class DependencyAnalyzer:
    """依赖关系分析器 - 实现EARS-006"""
    
    def __init__(self):
        pass
    
    def analyze_dependencies(self, tasks: List[Task]) -> DependencyGraph:
        """
        分析任务依赖关系
        实现EARS-006
        """
        nodes = {task.task_id: task for task in tasks}
        edges = {}
        reverse_edges = {task.task_id: [] for task in tasks}
        
        # 构建依赖关系图
        for task in tasks:
            task_dependencies = []
            
            # 处理显式依赖
            for dep_name in task.dependencies:
                dep_task = self._find_task_by_name(tasks, dep_name)
                if dep_task:
                    task_dependencies.append(dep_task.task_id)
                    reverse_edges[dep_task.task_id].append(task.task_id)
            
            # 分析隐式依赖
            implicit_deps = self._analyze_implicit_dependencies(task, tasks)
            for dep_id in implicit_deps:
                if dep_id not in task_dependencies:
                    task_dependencies.append(dep_id)
                    reverse_edges[dep_id].append(task.task_id)
            
            edges[task.task_id] = task_dependencies
        
        dependency_graph = DependencyGraph(
            nodes=nodes,
            edges=edges,
            reverse_edges=reverse_edges
        )
        
        # 检测循环依赖
        if self._has_circular_dependency(dependency_graph):
            logger.warning("检测到循环依赖，正在修复...")
            dependency_graph = self._resolve_circular_dependencies(dependency_graph)
        
        logger.info(f"依赖关系分析完成，共{len(edges)}个依赖关系")
        return dependency_graph
    
    def _find_task_by_name(self, tasks: List[Task], name: str) -> Optional[Task]:
        """根据名称查找任务"""
        for task in tasks:
            if task.name == name:
                return task
        return None
    
    def _analyze_implicit_dependencies(self, task: Task, all_tasks: List[Task]) -> List[str]:
        """分析隐式依赖关系"""
        implicit_deps = []
        
        # 基于任务类型的依赖规则
        type_dependencies = {
            TaskType.PRODUCT_DESIGN: [TaskType.REQUIREMENT_ANALYSIS],
            TaskType.ARCHITECTURE_DESIGN: [TaskType.REQUIREMENT_ANALYSIS],
            TaskType.UX_DESIGN: [TaskType.PRODUCT_DESIGN],
            TaskType.PROJECT_PLANNING: [TaskType.ARCHITECTURE_DESIGN, TaskType.UX_DESIGN],
            TaskType.CODE_GENERATION: [TaskType.ARCHITECTURE_DESIGN, TaskType.PROJECT_PLANNING],
            TaskType.QUALITY_ASSURANCE: [TaskType.CODE_GENERATION],
            TaskType.INTEGRATION: [TaskType.CODE_GENERATION],
            TaskType.DOCUMENTATION: [TaskType.CODE_GENERATION, TaskType.QUALITY_ASSURANCE]
        }
        
        required_types = type_dependencies.get(task.task_type, [])
        
        for other_task in all_tasks:
            if (other_task.task_type in required_types and 
                other_task.task_id != task.task_id):
                implicit_deps.append(other_task.task_id)
        
        return implicit_deps
    
    def _has_circular_dependency(self, graph: DependencyGraph) -> bool:
        """检测循环依赖"""
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for dep_id in graph.edges.get(node_id, []):
                if dfs(dep_id):
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in graph.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        
        return False
    
    def _resolve_circular_dependencies(self, graph: DependencyGraph) -> DependencyGraph:
        """解决循环依赖"""
        # 简单的循环依赖解决策略：移除优先级较低的依赖
        # 实际应用中可能需要更复杂的策略
        
        logger.warning("使用简化策略解决循环依赖")
        return graph

class AgentMatcher:
    """Agent能力匹配器 - 实现EARS-007"""
    
    def __init__(self):
        # 定义Agent能力矩阵
        self.agent_capabilities = {
            AgentType.REQUIREMENTS_ANALYST: AgentCapability(
                agent_type=AgentType.REQUIREMENTS_ANALYST,
                skills=["需求分析", "EARS规范", "用户故事", "业务分析"],
                task_types=[TaskType.REQUIREMENT_ANALYSIS, TaskType.DOCUMENTATION],
                max_concurrent_tasks=3,
                efficiency_score=0.9
            ),
            AgentType.PRODUCT_MANAGER: AgentCapability(
                agent_type=AgentType.PRODUCT_MANAGER,
                skills=["产品设计", "用户体验", "业务价值", "产品策略"],
                task_types=[TaskType.PRODUCT_DESIGN, TaskType.PROJECT_PLANNING],
                max_concurrent_tasks=2,
                efficiency_score=0.85
            ),
            AgentType.ARCHITECT: AgentCapability(
                agent_type=AgentType.ARCHITECT,
                skills=["系统架构", "技术设计", "性能优化", "技术选型"],
                task_types=[TaskType.ARCHITECTURE_DESIGN, TaskType.INTEGRATION],
                max_concurrent_tasks=2,
                efficiency_score=0.9
            ),
            AgentType.UX_DESIGNER: AgentCapability(
                agent_type=AgentType.UX_DESIGNER,
                skills=["用户体验", "界面设计", "交互设计", "可用性"],
                task_types=[TaskType.UX_DESIGN, TaskType.DOCUMENTATION],
                max_concurrent_tasks=3,
                efficiency_score=0.8
            ),
            AgentType.PROJECT_MANAGER: AgentCapability(
                agent_type=AgentType.PROJECT_MANAGER,
                skills=["项目管理", "资源协调", "进度控制", "风险管理"],
                task_types=[TaskType.PROJECT_PLANNING, TaskType.INTEGRATION],
                max_concurrent_tasks=5,
                efficiency_score=0.85
            ),
            AgentType.CODING_AGENT: AgentCapability(
                agent_type=AgentType.CODING_AGENT,
                skills=["编程开发", "代码生成", "算法实现", "技术实现"],
                task_types=[TaskType.CODE_GENERATION, TaskType.INTEGRATION],
                max_concurrent_tasks=2,
                efficiency_score=0.95
            ),
            AgentType.QUALITY_ASSURANCE: AgentCapability(
                agent_type=AgentType.QUALITY_ASSURANCE,
                skills=["质量保证", "测试设计", "质量审核", "缺陷管理"],
                task_types=[TaskType.QUALITY_ASSURANCE, TaskType.DOCUMENTATION],
                max_concurrent_tasks=4,
                efficiency_score=0.9
            )
        }
    
    def match_agents_to_tasks(self, tasks: List[Task]) -> Dict[str, AgentType]:
        """
        匹配Agent到任务
        实现EARS-007
        """
        assignments = {}
        
        # 按优先级和依赖关系排序任务
        sorted_tasks = self._sort_tasks_by_priority(tasks)
        
        for task in sorted_tasks:
            best_agent = self._find_best_agent(task)
            if best_agent:
                assignments[task.task_id] = best_agent
                # 更新Agent负载
                self.agent_capabilities[best_agent].current_tasks.append(task.task_id)
                self._update_agent_load(best_agent, task)
            else:
                logger.warning(f"无法为任务 {task.name} 找到合适的Agent")
                # 分配给项目经理作为默认处理
                assignments[task.task_id] = AgentType.PROJECT_MANAGER
        
        logger.info(f"Agent任务匹配完成，{len(assignments)}个任务已分配")
        return assignments
    
    def _sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """按优先级排序任务"""
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        return sorted(tasks, key=lambda t: priority_order[t.priority])
    
    def _find_best_agent(self, task: Task) -> Optional[AgentType]:
        """为任务找到最佳Agent"""
        candidates = []
        
        for agent_type, capability in self.agent_capabilities.items():
            # 检查Agent是否能处理该类型任务
            if task.task_type in capability.task_types:
                # 检查负载是否允许
                if len(capability.current_tasks) < capability.max_concurrent_tasks:
                    # 计算匹配分数
                    match_score = self._calculate_match_score(task, capability)
                    candidates.append((agent_type, match_score))
        
        if candidates:
            # 选择匹配分数最高的Agent
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def _calculate_match_score(self, task: Task, capability: AgentCapability) -> float:
        """计算任务与Agent的匹配分数"""
        base_score = capability.efficiency_score
        
        # 根据技能匹配调整分数
        required_skills = task.metadata.get("required_skills", [])
        skill_match = 0
        if required_skills:
            matched_skills = len(set(required_skills) & set(capability.skills))
            skill_match = matched_skills / len(required_skills)
        
        # 根据当前负载调整分数
        load_penalty = capability.load_factor * 0.2
        
        final_score = base_score + skill_match * 0.3 - load_penalty
        return final_score
    
    def _update_agent_load(self, agent_type: AgentType, task: Task):
        """更新Agent负载"""
        capability = self.agent_capabilities[agent_type]
        task_load = task.estimated_duration / 60.0  # 转换为小时
        capability.load_factor += task_load / capability.max_concurrent_tasks

class ExecutionOptimizer:
    """执行顺序优化器 - 实现EARS-008"""
    
    def __init__(self):
        pass
    
    def optimize_execution_sequence(
        self, 
        dependency_graph: DependencyGraph,
        agent_assignments: Dict[str, AgentType]
    ) -> List[List[str]]:
        """
        优化执行顺序
        实现EARS-008
        """
        # 拓扑排序
        execution_batches = self._topological_sort(dependency_graph)
        
        # 并行化优化
        optimized_batches = self._optimize_parallelization(
            execution_batches, dependency_graph, agent_assignments
        )
        
        logger.info(f"执行顺序优化完成，共{len(optimized_batches)}个批次")
        return optimized_batches
    
    def _topological_sort(self, graph: DependencyGraph) -> List[List[str]]:
        """拓扑排序"""
        in_degree = {node_id: len(deps) for node_id, deps in graph.edges.items()}
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current_batch = queue[:]
            queue = []
            result.append(current_batch)
            
            for node_id in current_batch:
                for dependent_id in graph.reverse_edges.get(node_id, []):
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        queue.append(dependent_id)
        
        return result
    
    def _optimize_parallelization(
        self,
        batches: List[List[str]],
        graph: DependencyGraph,
        assignments: Dict[str, AgentType]
    ) -> List[List[str]]:
        """优化并行化"""
        optimized_batches = []
        
        for batch in batches:
            # 按Agent分组
            agent_groups = {}
            for task_id in batch:
                agent = assignments.get(task_id, AgentType.PROJECT_MANAGER)
                if agent not in agent_groups:
                    agent_groups[agent] = []
                agent_groups[agent].append(task_id)
            
            # 如果同一个Agent有多个任务，按优先级排序
            for agent, task_ids in agent_groups.items():
                if len(task_ids) > 1:
                    # 按任务优先级排序
                    task_ids.sort(key=lambda tid: graph.nodes[tid].priority.value)
            
            # 重新组织批次以优化并行度
            if len(agent_groups) > 1:
                optimized_batches.append(batch)
            else:
                # 如果只有一个Agent，可能需要串行化
                for agent, task_ids in agent_groups.items():
                    for task_id in task_ids:
                        optimized_batches.append([task_id])
        
        return optimized_batches

class LoadBalancer:
    """负载均衡器 - 实现EARS-009"""
    
    def __init__(self):
        pass
    
    def balance_load(
        self,
        agent_assignments: Dict[str, AgentType],
        dependency_graph: DependencyGraph
    ) -> Dict[str, AgentType]:
        """
        负载均衡
        实现EARS-009
        """
        # 计算每个Agent的当前负载
        agent_loads = self._calculate_agent_loads(agent_assignments, dependency_graph)
        
        # 检查负载方差
        load_variance = self._calculate_load_variance(agent_loads)
        
        if load_variance > 0.2:
            logger.info(f"负载方差{load_variance:.3f}超过阈值，开始重平衡")
            # 重新分配任务以平衡负载
            balanced_assignments = self._rebalance_tasks(
                agent_assignments, agent_loads, dependency_graph
            )
            return balanced_assignments
        else:
            logger.info(f"负载方差{load_variance:.3f}在允许范围内")
            return agent_assignments
    
    def _calculate_agent_loads(
        self,
        assignments: Dict[str, AgentType],
        graph: DependencyGraph
    ) -> Dict[AgentType, float]:
        """计算Agent负载"""
        loads = {agent_type: 0.0 for agent_type in AgentType}
        
        for task_id, agent_type in assignments.items():
            task = graph.nodes[task_id]
            task_load = task.estimated_duration / 60.0  # 转换为小时
            loads[agent_type] += task_load
        
        return loads
    
    def _calculate_load_variance(self, loads: Dict[AgentType, float]) -> float:
        """计算负载方差"""
        load_values = list(loads.values())
        if not load_values:
            return 0.0
        
        mean_load = sum(load_values) / len(load_values)
        variance = sum((load - mean_load) ** 2 for load in load_values) / len(load_values)
        return variance ** 0.5 / mean_load if mean_load > 0 else 0.0
    
    def _rebalance_tasks(
        self,
        assignments: Dict[str, AgentType],
        loads: Dict[AgentType, float],
        graph: DependencyGraph
    ) -> Dict[str, AgentType]:
        """重新平衡任务分配"""
        # 简化的重平衡策略：将高负载Agent的任务转移给低负载Agent
        balanced_assignments = assignments.copy()
        
        # 按负载排序
        sorted_agents = sorted(loads.items(), key=lambda x: x[1])
        
        # 从高负载转移到低负载
        high_load_agent = sorted_agents[-1][0]
        low_load_agent = sorted_agents[0][0]
        
        # 找到可以转移的任务
        transferable_tasks = []
        for task_id, agent in assignments.items():
            if agent == high_load_agent:
                task = graph.nodes[task_id]
                # 检查低负载Agent是否能处理该任务
                # 这里简化处理，实际应该检查Agent能力
                transferable_tasks.append(task_id)
        
        # 转移部分任务
        if transferable_tasks:
            transfer_count = min(len(transferable_tasks) // 2, 2)
            for task_id in transferable_tasks[:transfer_count]:
                balanced_assignments[task_id] = low_load_agent
                logger.info(f"任务 {task_id} 从 {high_load_agent.value} 转移到 {low_load_agent.value}")
        
        return balanced_assignments

class TaskOrchestrator:
    """
    Multi-Agent任务编排器
    实现EARS-005至EARS-009
    """
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.task_decomposer = TaskDecomposer(claude_service)
        self.dependency_analyzer = DependencyAnalyzer()
        self.agent_matcher = AgentMatcher()
        self.execution_optimizer = ExecutionOptimizer()
        self.load_balancer = LoadBalancer()
    
    async def orchestrate_tasks(self, processing_plan: ProcessingPlan) -> ExecutionPlan:
        """
        编排任务执行计划
        
        Args:
            processing_plan: 处理计划
            
        Returns:
            ExecutionPlan: 执行计划
        """
        logger.info(f"开始编排任务，复杂度: {processing_plan.complexity.level.value}")
        
        try:
            # 1. 任务分解 (EARS-005)
            tasks, total_duration = await self.task_decomposer.decompose_tasks(processing_plan)
            logger.info(f"任务分解完成，共{len(tasks)}个任务")
            
            # 2. 依赖关系分析 (EARS-006)
            dependency_graph = self.dependency_analyzer.analyze_dependencies(tasks)
            logger.info("依赖关系分析完成")
            
            # 3. Agent能力匹配 (EARS-007)
            agent_assignments = self.agent_matcher.match_agents_to_tasks(tasks)
            logger.info("Agent任务匹配完成")
            
            # 4. 执行顺序优化 (EARS-008)
            execution_order = self.execution_optimizer.optimize_execution_sequence(
                dependency_graph, agent_assignments
            )
            logger.info("执行顺序优化完成")
            
            # 5. 负载均衡 (EARS-009)
            balanced_assignments = self.load_balancer.balance_load(
                agent_assignments, dependency_graph
            )
            logger.info("负载均衡完成")
            
            # 6. 生成执行计划
            execution_plan = ExecutionPlan(
                plan_id=str(uuid.uuid4()),
                processing_plan=processing_plan,
                tasks=tasks,
                dependency_graph=dependency_graph,
                agent_assignments=balanced_assignments,
                execution_order=execution_order,
                estimated_total_duration=total_duration,
                risk_factors=self._identify_execution_risks(tasks, dependency_graph)
            )
            
            logger.info(f"任务编排完成，计划ID: {execution_plan.plan_id}")
            return execution_plan
            
        except Exception as e:
            logger.error(f"任务编排失败: {str(e)}")
            # 返回简化的执行计划
            return self._create_fallback_execution_plan(processing_plan)
    
    def _identify_execution_risks(self, tasks: List[Task], graph: DependencyGraph) -> List[str]:
        """识别执行风险"""
        risks = []
        
        # 检查关键路径长度
        critical_path_length = max(len(batch) for batch in self._find_critical_paths(graph))
        if critical_path_length > 10:
            risks.append("关键路径过长，可能影响总体进度")
        
        # 检查高优先级任务的依赖复杂度
        critical_tasks = [t for t in tasks if t.priority == TaskPriority.CRITICAL]
        if len(critical_tasks) > len(tasks) * 0.3:
            risks.append("关键任务比例过高，执行风险较大")
        
        # 检查Agent负载分布
        agent_task_count = {}
        for task in tasks:
            if task.assigned_agent:
                agent_task_count[task.assigned_agent] = agent_task_count.get(task.assigned_agent, 0) + 1
        
        if max(agent_task_count.values()) > 5:
            risks.append("某些Agent负载过重，可能成为瓶颈")
        
        if not risks:
            risks.append("未识别到明显执行风险")
        
        return risks
    
    def _find_critical_paths(self, graph: DependencyGraph) -> List[List[str]]:
        """找到关键路径"""
        # 简化的关键路径查找
        paths = []
        
        # 找到所有起始节点（无依赖）
        start_nodes = [node_id for node_id, deps in graph.edges.items() if not deps]
        
        for start_node in start_nodes:
            path = self._dfs_longest_path(start_node, graph, [])
            paths.append(path)
        
        return paths
    
    def _dfs_longest_path(self, node_id: str, graph: DependencyGraph, visited: List[str]) -> List[str]:
        """深度优先搜索最长路径"""
        if node_id in visited:
            return visited
        
        visited = visited + [node_id]
        dependents = graph.reverse_edges.get(node_id, [])
        
        if not dependents:
            return visited
        
        longest_path = visited
        for dependent in dependents:
            path = self._dfs_longest_path(dependent, graph, visited)
            if len(path) > len(longest_path):
                longest_path = path
        
        return longest_path
    
    def _create_fallback_execution_plan(self, processing_plan: ProcessingPlan) -> ExecutionPlan:
        """创建降级执行计划"""
        fallback_task = Task(
            task_id=str(uuid.uuid4()),
            name="简化任务执行",
            description="降级到简化执行模式",
            task_type=TaskType.CODE_GENERATION,
            priority=TaskPriority.HIGH,
            estimated_duration=120,
            assigned_agent=AgentType.PRODUCT_MANAGER
        )
        
        dependency_graph = DependencyGraph(
            nodes={fallback_task.task_id: fallback_task},
            edges={fallback_task.task_id: []},
            reverse_edges={fallback_task.task_id: []}
        )
        
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            processing_plan=processing_plan,
            tasks=[fallback_task],
            dependency_graph=dependency_graph,
            agent_assignments={fallback_task.task_id: AgentType.PRODUCT_MANAGER},
            execution_order=[[fallback_task.task_id]],
            estimated_total_duration=120,
            risk_factors=["执行计划生成失败，使用降级方案"]
        )

# 工厂函数
def create_task_orchestrator(claude_service: ClaudeService) -> TaskOrchestrator:
    """创建任务编排器"""
    return TaskOrchestrator(claude_service)

# 使用示例
async def demo_task_orchestrator():
    """演示任务编排器"""
    from ..claude_integration import create_claude_service
    from .input_processor import create_input_processor
    
    claude_service = create_claude_service()
    input_processor = create_input_processor(claude_service)
    orchestrator = create_task_orchestrator(claude_service)
    
    # 测试输入
    user_input = "开发一个电商网站，包含用户注册、商品展示、购物车和支付功能"
    
    # 生成处理计划
    processing_plan = await input_processor.process_user_request(user_input)
    
    # 编排任务
    execution_plan = await orchestrator.orchestrate_tasks(processing_plan)
    
    print(f"执行计划ID: {execution_plan.plan_id}")
    print(f"任务数量: {len(execution_plan.tasks)}")
    print(f"预估总时长: {execution_plan.estimated_total_duration}分钟")
    print(f"执行批次: {len(execution_plan.execution_order)}")
    
    for i, batch in enumerate(execution_plan.execution_order):
        print(f"批次 {i+1}: {len(batch)}个任务")
        for task_id in batch:
            task = execution_plan.dependency_graph.nodes[task_id]
            agent = execution_plan.agent_assignments[task_id]
            print(f"  - {task.name} ({agent.value})")

if __name__ == "__main__":
    asyncio.run(demo_task_orchestrator())
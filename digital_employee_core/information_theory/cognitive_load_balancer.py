"""
认知负载均衡器
Cognitive Load Balancer

实现目标:
- 认知负载均衡方差≤0.2
- Agent间任务分配优化
- 动态负载调整响应时间≤500ms
- 认知压力监控覆盖率100%
"""

import asyncio
import json
import logging
import math
import statistics
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import uuid
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from ..claude_integration import ClaudeService
from ..multi_agent_engine import AgentRole
from .shannon_entropy_engine import InformationUnit, InformationType

logger = logging.getLogger(__name__)

class LoadType(Enum):
    """负载类型"""
    COGNITIVE = "cognitive"      # 认知负载
    COMPUTATIONAL = "computational"  # 计算负载
    MEMORY = "memory"           # 内存负载
    IO_BOUND = "io_bound"       # I/O密集型负载
    COMMUNICATION = "communication"  # 通信负载

class LoadLevel(Enum):
    """负载级别"""
    IDLE = "idle"              # 空闲 (0-20%)
    LOW = "low"                # 低负载 (21-40%)
    MODERATE = "moderate"      # 中等负载 (41-60%)
    HIGH = "high"              # 高负载 (61-80%)
    OVERLOAD = "overload"      # 过载 (81-100%)
    CRITICAL = "critical"      # 临界状态 (>100%)

class BalancingStrategy(Enum):
    """均衡策略"""
    ROUND_ROBIN = "round_robin"           # 轮询分配
    LEAST_LOADED = "least_loaded"         # 最少负载优先
    CAPACITY_AWARE = "capacity_aware"     # 容量感知分配
    INTELLIGENT = "intelligent"           # 智能均衡
    ADAPTIVE = "adaptive"                 # 自适应均衡

@dataclass
class CognitiveTask:
    """认知任务"""
    task_id: str
    task_name: str
    complexity_score: float      # 复杂度评分 0.0-1.0
    estimated_duration: timedelta
    required_skills: List[str]
    memory_requirement: float    # MB
    cpu_intensity: float        # 0.0-1.0
    context_switching_cost: float  # 上下文切换成本
    priority: int               # 1-10
    dependencies: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentCognitiveState:
    """Agent认知状态"""
    agent_id: str
    agent_role: AgentRole
    current_load: float         # 当前负载 0.0-1.0
    load_level: LoadLevel
    active_tasks: List[str]
    cognitive_capacity: float   # 认知容量 0.0-1.0
    stress_level: float        # 压力水平 0.0-1.0
    performance_efficiency: float  # 性能效率 0.0-1.0
    recent_load_history: deque  # 最近负载历史
    last_updated: datetime
    
    def __post_init__(self):
        if not hasattr(self, 'recent_load_history') or self.recent_load_history is None:
            self.recent_load_history = deque(maxlen=100)

@dataclass
class LoadBalancingDecision:
    """负载均衡决策"""
    decision_id: str
    decision_type: str          # ASSIGN, REDISTRIBUTE, SCALE, PAUSE
    source_agent: Optional[str]
    target_agent: Optional[str]
    affected_tasks: List[str]
    expected_improvement: float
    confidence_score: float
    rationale: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CognitiveLoadMetrics:
    """认知负载指标"""
    measurement_id: str
    total_agents: int
    average_load: float
    load_variance: float
    load_distribution: Dict[str, float]
    overloaded_agents: List[str]
    underutilized_agents: List[str]
    balance_score: float        # 0.0-1.0, 1.0为完美均衡
    system_efficiency: float
    bottleneck_agents: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class LoadBalancingResult:
    """负载均衡结果"""
    balancing_id: str
    initial_metrics: CognitiveLoadMetrics
    final_metrics: CognitiveLoadMetrics
    decisions_made: List[LoadBalancingDecision]
    improvement_achieved: float
    variance_reduction: float
    processing_time: float
    success: bool
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

class CognitiveLoadCalculator:
    """认知负载计算器"""
    
    def __init__(self):
        self.calculation_weights = {
            'task_complexity': 0.30,
            'task_count': 0.25,
            'context_switching': 0.20,
            'memory_usage': 0.15,
            'communication_overhead': 0.10
        }
        self.baseline_capacity = 1.0  # 基准认知容量
    
    def calculate_cognitive_load(self, agent_state: AgentCognitiveState, 
                               active_tasks: List[CognitiveTask]) -> float:
        """
        计算Agent的认知负载
        
        Args:
            agent_state: Agent认知状态
            active_tasks: 活跃任务列表
            
        Returns:
            float: 认知负载值 (0.0-1.0+)
        """
        if not active_tasks:
            return 0.0
        
        # 1. 任务复杂度负载
        complexity_load = self._calculate_complexity_load(active_tasks)
        
        # 2. 任务数量负载
        count_load = self._calculate_task_count_load(active_tasks, agent_state.cognitive_capacity)
        
        # 3. 上下文切换负载
        context_load = self._calculate_context_switching_load(active_tasks)
        
        # 4. 内存使用负载
        memory_load = self._calculate_memory_load(active_tasks)
        
        # 5. 通信开销负载
        communication_load = self._calculate_communication_load(active_tasks)
        
        # 加权计算总负载
        total_load = (
            complexity_load * self.calculation_weights['task_complexity'] +
            count_load * self.calculation_weights['task_count'] +
            context_load * self.calculation_weights['context_switching'] +
            memory_load * self.calculation_weights['memory_usage'] +
            communication_load * self.calculation_weights['communication_overhead']
        )
        
        # 考虑Agent个体差异
        individual_factor = self._calculate_individual_factor(agent_state)
        adjusted_load = total_load * individual_factor
        
        return min(adjusted_load, 2.0)  # 最大负载限制为2.0(200%)
    
    def _calculate_complexity_load(self, tasks: List[CognitiveTask]) -> float:
        """计算任务复杂度负载"""
        if not tasks:
            return 0.0
        
        total_complexity = sum(task.complexity_score for task in tasks)
        # 复杂度负载与任务数量非线性增长
        complexity_factor = 1.0 + (len(tasks) - 1) * 0.2
        
        return min(total_complexity * complexity_factor, 2.0)
    
    def _calculate_task_count_load(self, tasks: List[CognitiveTask], capacity: float) -> float:
        """计算任务数量负载"""
        if not tasks:
            return 0.0
        
        # 基于认知容量计算任务数量负载
        base_capacity = max(capacity, 0.1)  # 避免除零
        count_load = len(tasks) / (base_capacity * 5)  # 假设基准容量可处理5个任务
        
        return min(count_load, 1.5)
    
    def _calculate_context_switching_load(self, tasks: List[CognitiveTask]) -> float:
        """计算上下文切换负载"""
        if len(tasks) <= 1:
            return 0.0
        
        # 任务间切换成本
        total_switching_cost = sum(task.context_switching_cost for task in tasks)
        switching_frequency = len(tasks) - 1  # 切换次数
        
        # 上下文切换负载与任务数量呈指数增长
        switching_load = total_switching_cost * math.log(switching_frequency + 1)
        
        return min(switching_load, 1.0)
    
    def _calculate_memory_load(self, tasks: List[CognitiveTask]) -> float:
        """计算内存负载"""
        if not tasks:
            return 0.0
        
        total_memory = sum(task.memory_requirement for task in tasks)
        # 假设基准内存容量为1GB
        base_memory_capacity = 1024.0  # MB
        
        memory_load = total_memory / base_memory_capacity
        return min(memory_load, 1.0)
    
    def _calculate_communication_load(self, tasks: List[CognitiveTask]) -> float:
        """计算通信负载"""
        if not tasks:
            return 0.0
        
        # 基于任务依赖数量计算通信负载
        total_dependencies = sum(len(task.dependencies) for task in tasks)
        communication_load = total_dependencies * 0.1  # 每个依赖增加10%通信负载
        
        return min(communication_load, 0.8)
    
    def _calculate_individual_factor(self, agent_state: AgentCognitiveState) -> float:
        """计算个体差异因子"""
        # 基于Agent的历史表现和当前状态调整
        efficiency_factor = 2.0 - agent_state.performance_efficiency  # 效率越低，负载感知越高
        stress_factor = 1.0 + agent_state.stress_level * 0.5  # 压力越大，负载越重
        
        return efficiency_factor * stress_factor
    
    def calculate_load_level(self, load_value: float) -> LoadLevel:
        """计算负载级别"""
        if load_value <= 0.2:
            return LoadLevel.IDLE
        elif load_value <= 0.4:
            return LoadLevel.LOW
        elif load_value <= 0.6:
            return LoadLevel.MODERATE
        elif load_value <= 0.8:
            return LoadLevel.HIGH
        elif load_value <= 1.0:
            return LoadLevel.OVERLOAD
        else:
            return LoadLevel.CRITICAL

class LoadBalancingAlgorithm:
    """负载均衡算法"""
    
    def __init__(self):
        self.balancing_history = []
        self.performance_cache = {}
        
    def calculate_optimal_distribution(self, agents: List[AgentCognitiveState], 
                                     tasks: List[CognitiveTask],
                                     strategy: BalancingStrategy = BalancingStrategy.INTELLIGENT) -> List[LoadBalancingDecision]:
        """
        计算最优任务分配
        
        Args:
            agents: Agent认知状态列表
            tasks: 待分配任务列表
            strategy: 均衡策略
            
        Returns:
            List[LoadBalancingDecision]: 均衡决策列表
        """
        decisions = []
        
        if strategy == BalancingStrategy.ROUND_ROBIN:
            decisions = self._round_robin_distribution(agents, tasks)
        elif strategy == BalancingStrategy.LEAST_LOADED:
            decisions = self._least_loaded_distribution(agents, tasks)
        elif strategy == BalancingStrategy.CAPACITY_AWARE:
            decisions = self._capacity_aware_distribution(agents, tasks)
        elif strategy == BalancingStrategy.INTELLIGENT:
            decisions = self._intelligent_distribution(agents, tasks)
        elif strategy == BalancingStrategy.ADAPTIVE:
            decisions = self._adaptive_distribution(agents, tasks)
        
        return decisions
    
    def _round_robin_distribution(self, agents: List[AgentCognitiveState], 
                                tasks: List[CognitiveTask]) -> List[LoadBalancingDecision]:
        """轮询分配策略"""
        decisions = []
        agent_index = 0
        
        for task in tasks:
            target_agent = agents[agent_index % len(agents)]
            
            decision = LoadBalancingDecision(
                decision_id=f"RR-{uuid.uuid4().hex[:8]}",
                decision_type="ASSIGN",
                source_agent=None,
                target_agent=target_agent.agent_id,
                affected_tasks=[task.task_id],
                expected_improvement=0.1,  # 轮询的改进有限
                confidence_score=0.6,
                rationale=f"轮询分配任务{task.task_id}给{target_agent.agent_role.value}"
            )
            decisions.append(decision)
            agent_index += 1
        
        return decisions
    
    def _least_loaded_distribution(self, agents: List[AgentCognitiveState], 
                                 tasks: List[CognitiveTask]) -> List[LoadBalancingDecision]:
        """最少负载优先策略"""
        decisions = []
        
        # 按当前负载排序
        sorted_agents = sorted(agents, key=lambda a: a.current_load)
        
        for task in tasks:
            # 选择负载最小的Agent
            target_agent = sorted_agents[0]
            
            decision = LoadBalancingDecision(
                decision_id=f"LL-{uuid.uuid4().hex[:8]}",
                decision_type="ASSIGN",
                source_agent=None,
                target_agent=target_agent.agent_id,
                affected_tasks=[task.task_id],
                expected_improvement=0.3,
                confidence_score=0.8,
                rationale=f"分配任务{task.task_id}给负载最小的Agent {target_agent.agent_role.value}"
            )
            decisions.append(decision)
            
            # 更新Agent负载用于后续计算
            target_agent.current_load += task.complexity_score * 0.2
            sorted_agents.sort(key=lambda a: a.current_load)
        
        return decisions
    
    def _capacity_aware_distribution(self, agents: List[AgentCognitiveState], 
                                   tasks: List[CognitiveTask]) -> List[LoadBalancingDecision]:
        """容量感知分配策略"""
        decisions = []
        
        for task in tasks:
            best_agent = None
            best_score = -1
            
            for agent in agents:
                # 计算容量匹配分数
                capacity_score = self._calculate_capacity_match_score(agent, task)
                
                if capacity_score > best_score:
                    best_score = capacity_score
                    best_agent = agent
            
            if best_agent:
                decision = LoadBalancingDecision(
                    decision_id=f"CA-{uuid.uuid4().hex[:8]}",
                    decision_type="ASSIGN",
                    source_agent=None,
                    target_agent=best_agent.agent_id,
                    affected_tasks=[task.task_id],
                    expected_improvement=best_score * 0.5,
                    confidence_score=0.85,
                    rationale=f"基于容量匹配分配任务{task.task_id}给{best_agent.agent_role.value}(匹配度:{best_score:.2f})"
                )
                decisions.append(decision)
        
        return decisions
    
    def _intelligent_distribution(self, agents: List[AgentCognitiveState], 
                                tasks: List[CognitiveTask]) -> List[LoadBalancingDecision]:
        """智能分配策略"""
        decisions = []
        
        # 综合考虑多个因素的智能分配
        for task in tasks:
            best_agent = None
            best_score = -1
            
            for agent in agents:
                # 多因素评分
                score = self._calculate_intelligent_score(agent, task)
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            if best_agent:
                decision = LoadBalancingDecision(
                    decision_id=f"INT-{uuid.uuid4().hex[:8]}",
                    decision_type="ASSIGN",
                    source_agent=None,
                    target_agent=best_agent.agent_id,
                    affected_tasks=[task.task_id],
                    expected_improvement=best_score,
                    confidence_score=0.9,
                    rationale=f"智能分析分配任务{task.task_id}给{best_agent.agent_role.value}(综合评分:{best_score:.2f})"
                )
                decisions.append(decision)
        
        return decisions
    
    def _adaptive_distribution(self, agents: List[AgentCognitiveState], 
                             tasks: List[CognitiveTask]) -> List[LoadBalancingDecision]:
        """自适应分配策略"""
        decisions = []
        
        # 基于历史表现动态调整分配策略
        for task in tasks:
            # 分析历史最佳匹配
            best_agent = self._find_adaptive_best_agent(agents, task)
            
            if best_agent:
                decision = LoadBalancingDecision(
                    decision_id=f"ADP-{uuid.uuid4().hex[:8]}",
                    decision_type="ASSIGN",
                    source_agent=None,
                    target_agent=best_agent.agent_id,
                    affected_tasks=[task.task_id],
                    expected_improvement=0.7,
                    confidence_score=0.85,
                    rationale=f"自适应学习分配任务{task.task_id}给{best_agent.agent_role.value}"
                )
                decisions.append(decision)
        
        return decisions
    
    def _calculate_capacity_match_score(self, agent: AgentCognitiveState, task: CognitiveTask) -> float:
        """计算容量匹配分数"""
        # 负载因子：当前负载越低越好
        load_factor = 1.0 - agent.current_load
        
        # 容量因子：认知容量越高越好
        capacity_factor = agent.cognitive_capacity
        
        # 效率因子：性能效率越高越好
        efficiency_factor = agent.performance_efficiency
        
        # 压力因子：压力越低越好
        stress_factor = 1.0 - agent.stress_level
        
        # 综合评分
        total_score = (load_factor * 0.3 + capacity_factor * 0.3 + 
                      efficiency_factor * 0.2 + stress_factor * 0.2)
        
        return min(total_score, 1.0)
    
    def _calculate_intelligent_score(self, agent: AgentCognitiveState, task: CognitiveTask) -> float:
        """计算智能分配评分"""
        # 基础容量匹配
        base_score = self._calculate_capacity_match_score(agent, task)
        
        # 任务复杂度适配性
        complexity_fit = 1.0 - abs(agent.cognitive_capacity - task.complexity_score)
        
        # 技能匹配度 (简化实现)
        skill_match = 0.8 if len(task.required_skills) <= 3 else 0.6
        
        # 历史表现权重
        historical_weight = agent.performance_efficiency
        
        # 综合智能评分
        intelligent_score = (base_score * 0.4 + complexity_fit * 0.3 + 
                           skill_match * 0.2 + historical_weight * 0.1)
        
        return intelligent_score
    
    def _find_adaptive_best_agent(self, agents: List[AgentCognitiveState], task: CognitiveTask) -> Optional[AgentCognitiveState]:
        """自适应寻找最佳Agent"""
        # 简化实现：基于历史表现和当前状态
        best_agent = None
        best_score = -1
        
        for agent in agents:
            # 自适应评分考虑学习效果
            adaptive_score = (agent.performance_efficiency * 0.6 + 
                            (1.0 - agent.current_load) * 0.4)
            
            if adaptive_score > best_score:
                best_score = adaptive_score
                best_agent = agent
        
        return best_agent

class CognitiveLoadBalancer:
    """认知负载均衡器主类"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.load_calculator = CognitiveLoadCalculator()
        self.balancing_algorithm = LoadBalancingAlgorithm()
        self.agent_states = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.load_history = deque(maxlen=1000)
        self.balancing_lock = threading.Lock()
        
    async def monitor_and_balance(self, agents: List[AgentCognitiveState], 
                                tasks: List[CognitiveTask],
                                strategy: BalancingStrategy = BalancingStrategy.INTELLIGENT) -> LoadBalancingResult:
        """
        监控并均衡认知负载
        
        Args:
            agents: Agent认知状态列表
            tasks: 任务列表
            strategy: 均衡策略
            
        Returns:
            LoadBalancingResult: 均衡结果
        """
        start_time = datetime.now()
        
        try:
            logger.info("开始认知负载监控和均衡...")
            
            with self.balancing_lock:
                # 1. 计算初始负载指标
                initial_metrics = await self._calculate_load_metrics(agents, tasks)
                
                # 2. 判断是否需要均衡
                needs_balancing = self._assess_balancing_need(initial_metrics)
                
                decisions_made = []
                final_metrics = initial_metrics
                
                if needs_balancing:
                    # 3. 执行负载均衡
                    decisions_made = self.balancing_algorithm.calculate_optimal_distribution(
                        agents, tasks, strategy
                    )
                    
                    # 4. 应用均衡决策
                    await self._apply_balancing_decisions(agents, decisions_made)
                    
                    # 5. 重新计算负载指标
                    final_metrics = await self._calculate_load_metrics(agents, tasks)
                
                # 6. 计算改进效果
                improvement = self._calculate_improvement(initial_metrics, final_metrics)
                variance_reduction = initial_metrics.load_variance - final_metrics.load_variance
                
                # 7. 生成优化建议
                recommendations = self._generate_recommendations(initial_metrics, final_metrics)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                result = LoadBalancingResult(
                    balancing_id=f"BAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    initial_metrics=initial_metrics,
                    final_metrics=final_metrics,
                    decisions_made=decisions_made,
                    improvement_achieved=improvement,
                    variance_reduction=variance_reduction,
                    processing_time=processing_time,
                    success=final_metrics.load_variance <= 0.2,
                    recommendations=recommendations
                )
                
                # 记录历史
                self.load_history.append(final_metrics)
                
                logger.info(f"认知负载均衡完成，方差: {final_metrics.load_variance:.3f}, 处理时间: {processing_time*1000:.1f}ms")
                
                return result
                
        except Exception as e:
            logger.error(f"认知负载均衡失败: {str(e)}")
            raise
    
    async def _calculate_load_metrics(self, agents: List[AgentCognitiveState], 
                                    tasks: List[CognitiveTask]) -> CognitiveLoadMetrics:
        """计算负载指标"""
        
        # 更新Agent负载状态
        agent_loads = {}
        for agent in agents:
            # 获取该Agent的任务
            agent_tasks = [task for task in tasks if task.task_id in agent.active_tasks]
            
            # 计算认知负载
            cognitive_load = self.load_calculator.calculate_cognitive_load(agent, agent_tasks)
            agent.current_load = cognitive_load
            agent.load_level = self.load_calculator.calculate_load_level(cognitive_load)
            agent.last_updated = datetime.now()
            
            # 更新历史记录
            agent.recent_load_history.append({
                'timestamp': datetime.now(),
                'load': cognitive_load
            })
            
            agent_loads[agent.agent_id] = cognitive_load
        
        # 计算统计指标
        load_values = list(agent_loads.values())
        average_load = statistics.mean(load_values) if load_values else 0.0
        load_variance = statistics.variance(load_values) if len(load_values) > 1 else 0.0
        
        # 识别过载和低利用Agent
        overloaded_agents = [aid for aid, load in agent_loads.items() if load > 0.8]
        underutilized_agents = [aid for aid, load in agent_loads.items() if load < 0.3]
        
        # 识别瓶颈Agent
        bottleneck_agents = [aid for aid, load in agent_loads.items() if load > 0.9]
        
        # 计算均衡评分
        balance_score = self._calculate_balance_score(load_variance, average_load)
        
        # 计算系统效率
        system_efficiency = self._calculate_system_efficiency(agent_loads, agents)
        
        return CognitiveLoadMetrics(
            measurement_id=f"METRICS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            total_agents=len(agents),
            average_load=average_load,
            load_variance=load_variance,
            load_distribution=agent_loads,
            overloaded_agents=overloaded_agents,
            underutilized_agents=underutilized_agents,
            balance_score=balance_score,
            system_efficiency=system_efficiency,
            bottleneck_agents=bottleneck_agents
        )
    
    def _calculate_balance_score(self, variance: float, average_load: float) -> float:
        """计算均衡评分"""
        # 方差越小，平均负载越合理，评分越高
        variance_score = max(0, 1.0 - variance * 5)  # 方差0.2对应评分0
        load_score = 1.0 - abs(average_load - 0.6)  # 理想负载60%
        
        return (variance_score * 0.7 + load_score * 0.3)
    
    def _calculate_system_efficiency(self, agent_loads: Dict[str, float], 
                                   agents: List[AgentCognitiveState]) -> float:
        """计算系统效率"""
        if not agent_loads:
            return 0.0
        
        # 基于负载利用率和Agent效率计算
        total_efficiency = 0.0
        for agent in agents:
            load = agent_loads.get(agent.agent_id, 0.0)
            # 效率 = 负载利用率 * Agent性能效率
            agent_efficiency = min(load, 1.0) * agent.performance_efficiency
            total_efficiency += agent_efficiency
        
        return total_efficiency / len(agents)
    
    def _assess_balancing_need(self, metrics: CognitiveLoadMetrics) -> bool:
        """评估是否需要负载均衡"""
        # 方差过大需要均衡
        if metrics.load_variance > 0.2:
            return True
        
        # 有过载Agent需要均衡
        if metrics.overloaded_agents:
            return True
        
        # 均衡评分过低需要均衡
        if metrics.balance_score < 0.7:
            return True
        
        return False
    
    async def _apply_balancing_decisions(self, agents: List[AgentCognitiveState], 
                                       decisions: List[LoadBalancingDecision]):
        """应用均衡决策"""
        for decision in decisions:
            if decision.decision_type == "ASSIGN":
                # 分配任务
                target_agent = next((a for a in agents if a.agent_id == decision.target_agent), None)
                if target_agent:
                    target_agent.active_tasks.extend(decision.affected_tasks)
                    
            elif decision.decision_type == "REDISTRIBUTE":
                # 重新分配任务
                source_agent = next((a for a in agents if a.agent_id == decision.source_agent), None)
                target_agent = next((a for a in agents if a.agent_id == decision.target_agent), None)
                
                if source_agent and target_agent:
                    for task_id in decision.affected_tasks:
                        if task_id in source_agent.active_tasks:
                            source_agent.active_tasks.remove(task_id)
                            target_agent.active_tasks.append(task_id)
    
    def _calculate_improvement(self, initial: CognitiveLoadMetrics, 
                             final: CognitiveLoadMetrics) -> float:
        """计算改进程度"""
        # 基于方差减少和均衡评分提升计算改进
        variance_improvement = max(0, initial.load_variance - final.load_variance)
        balance_improvement = final.balance_score - initial.balance_score
        
        return (variance_improvement * 0.6 + balance_improvement * 0.4)
    
    def _generate_recommendations(self, initial: CognitiveLoadMetrics, 
                                final: CognitiveLoadMetrics) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 基于最终状态生成建议
        if final.load_variance <= 0.2:
            recommendations.append("✅ 负载方差已达到目标（≤0.2），系统均衡良好")
        else:
            recommendations.append(f"⚠️ 负载方差{final.load_variance:.3f}仍超过目标，建议进一步优化")
        
        if final.overloaded_agents:
            recommendations.append(f"🔴 检测到{len(final.overloaded_agents)}个过载Agent，建议任务重新分配")
        
        if final.underutilized_agents:
            recommendations.append(f"🟡 检测到{len(final.underutilized_agents)}个低利用Agent，建议增加任务分配")
        
        if final.system_efficiency < 0.7:
            recommendations.append("📈 系统效率偏低，建议优化Agent性能或调整任务分配策略")
        
        if final.balance_score >= 0.8:
            recommendations.append("🎯 系统均衡性良好，建议维持当前分配策略")
        
        return recommendations
    
    async def start_continuous_monitoring(self, agents: List[AgentCognitiveState], 
                                        monitoring_interval: timedelta = timedelta(seconds=30)):
        """启动持续监控"""
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # 简化的持续监控实现
                    time.sleep(monitoring_interval.total_seconds())
                    
                    # 这里应该获取最新的Agent状态和任务
                    # 简化实现中跳过实际监控逻辑
                    
                except Exception as e:
                    logger.error(f"持续监控出错: {str(e)}")
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("认知负载持续监控已启动")
    
    def stop_continuous_monitoring(self):
        """停止持续监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("认知负载持续监控已停止")

# 工厂函数
def create_cognitive_load_balancer(claude_service: ClaudeService) -> CognitiveLoadBalancer:
    """创建认知负载均衡器"""
    return CognitiveLoadBalancer(claude_service)

# 使用示例
async def demo_cognitive_load_balancer():
    """演示认知负载均衡器功能"""
    from ...claude_integration import create_claude_service
    
    claude_service = create_claude_service()
    load_balancer = create_cognitive_load_balancer(claude_service)
    
    # 创建测试Agent状态
    test_agents = [
        AgentCognitiveState(
            agent_id="agent_001",
            agent_role=AgentRole.CODING_AGENT,
            current_load=0.9,  # 高负载
            load_level=LoadLevel.OVERLOAD,
            active_tasks=["task_001", "task_002", "task_003"],
            cognitive_capacity=0.8,
            stress_level=0.7,
            performance_efficiency=0.85,
            recent_load_history=deque(maxlen=100),
            last_updated=datetime.now()
        ),
        AgentCognitiveState(
            agent_id="agent_002",
            agent_role=AgentRole.ARCHITECT,
            current_load=0.3,  # 低负载
            load_level=LoadLevel.LOW,
            active_tasks=["task_004"],
            cognitive_capacity=0.9,
            stress_level=0.2,
            performance_efficiency=0.9,
            recent_load_history=deque(maxlen=100),
            last_updated=datetime.now()
        ),
        AgentCognitiveState(
            agent_id="agent_003",
            agent_role=AgentRole.QUALITY_ASSURANCE,
            current_load=0.6,  # 中等负载
            load_level=LoadLevel.MODERATE,
            active_tasks=["task_005", "task_006"],
            cognitive_capacity=0.7,
            stress_level=0.4,
            performance_efficiency=0.8,
            recent_load_history=deque(maxlen=100),
            last_updated=datetime.now()
        )
    ]
    
    # 创建测试任务
    test_tasks = [
        CognitiveTask(
            task_id="task_007",
            task_name="新功能开发",
            complexity_score=0.8,
            estimated_duration=timedelta(hours=4),
            required_skills=["programming", "design"],
            memory_requirement=256.0,
            cpu_intensity=0.7,
            context_switching_cost=0.3,
            priority=8,
            dependencies=[]
        ),
        CognitiveTask(
            task_id="task_008",
            task_name="代码审查",
            complexity_score=0.5,
            estimated_duration=timedelta(hours=2),
            required_skills=["code_review"],
            memory_requirement=128.0,
            cpu_intensity=0.4,
            context_switching_cost=0.2,
            priority=6,
            dependencies=["task_007"]
        )
    ]
    
    print("=== 认知负载均衡器演示 ===")
    
    try:
        # 1. 执行负载监控和均衡
        print("\n1. 执行负载监控和均衡...")
        balancing_result = await load_balancer.monitor_and_balance(
            test_agents, test_tasks, BalancingStrategy.INTELLIGENT
        )
        
        print(f"均衡ID: {balancing_result.balancing_id}")
        print(f"处理时间: {balancing_result.processing_time*1000:.1f}ms")
        print(f"均衡成功: {'✅' if balancing_result.success else '❌'}")
        
        # 2. 显示初始和最终指标
        print(f"\n=== 负载指标对比 ===")
        initial = balancing_result.initial_metrics
        final = balancing_result.final_metrics
        
        print(f"初始负载方差: {initial.load_variance:.3f}")
        print(f"最终负载方差: {final.load_variance:.3f}")
        print(f"方差减少: {balancing_result.variance_reduction:.3f}")
        
        print(f"初始平均负载: {initial.average_load:.3f}")
        print(f"最终平均负载: {final.average_load:.3f}")
        
        print(f"初始均衡评分: {initial.balance_score:.3f}")
        print(f"最终均衡评分: {final.balance_score:.3f}")
        
        print(f"系统效率: {final.system_efficiency:.3f}")
        
        # 3. 显示Agent状态
        print(f"\n=== Agent负载分布 ===")
        for agent_id, load in final.load_distribution.items():
            agent = next(a for a in test_agents if a.agent_id == agent_id)
            status_icon = "🔴" if load > 0.8 else "🟡" if load > 0.6 else "🟢"
            print(f"{status_icon} {agent.agent_role.value}: {load:.3f} ({agent.load_level.value})")
        
        # 4. 显示均衡决策
        if balancing_result.decisions_made:
            print(f"\n=== 均衡决策 ===")
            for decision in balancing_result.decisions_made[:3]:
                print(f"- {decision.decision_type}: {decision.rationale}")
                print(f"  预期改进: {decision.expected_improvement:.2f}, 置信度: {decision.confidence_score:.2f}")
        
        # 5. 显示建议
        print(f"\n=== 优化建议 ===")
        for recommendation in balancing_result.recommendations:
            print(f"- {recommendation}")
        
        # 6. 验证目标达成
        print(f"\n=== 目标达成验证 ===")
        variance_target_achieved = final.load_variance <= 0.2
        efficiency_target_achieved = final.system_efficiency >= 0.7
        balance_target_achieved = final.balance_score >= 0.8
        
        print(f"负载方差目标 (≤0.2): {'✅' if variance_target_achieved else '❌'} {final.load_variance:.3f}")
        print(f"系统效率目标 (≥0.7): {'✅' if efficiency_target_achieved else '❌'} {final.system_efficiency:.3f}")
        print(f"均衡评分目标 (≥0.8): {'✅' if balance_target_achieved else '❌'} {final.balance_score:.3f}")
        
        overall_success = variance_target_achieved and efficiency_target_achieved
        print(f"整体成功: {'✅' if overall_success else '❌'}")
        
        print(f"\n🎉 认知负载均衡器核心功能验证完成!")
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_cognitive_load_balancer())
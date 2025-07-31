# Agent开发和集成规范

## 🎯 Agent设计理念

### 核心原则
- **专业化驱动**：每个Agent专注于特定领域的任务
- **松耦合集成**：Agent之间通过标准接口协作
- **渐进式演进**：从统一Agent到专业Agent的平滑演进
- **数据驱动决策**：基于使用数据决定Agent分离时机

### Agent生命周期
```
设计 → 开发 → 测试 → 注册 → 部署 → 监控 → 优化 → 废弃
```

---

## 🏗️ Agent架构规范

### Agent分层架构
```
┌─────────────────────────────────────┐
│            Agent接口层               │  ← 统一接口，版本管理
├─────────────────────────────────────┤
│            业务逻辑层               │  ← 专业化实现，AI增强
├─────────────────────────────────────┤
│            AI服务层                 │  ← LLM调用，Prompt管理
├─────────────────────────────────────┤
│            基础设施层               │  ← 日志、监控、配置
└─────────────────────────────────────┘
```

### Agent基础类设计
```python
# digital_employee/core/agent_base.py (扩展版)
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging

@dataclass
class AgentCapability:
    """Agent能力描述"""
    name: str                          # 能力名称
    description: str                   # 能力描述
    input_schema: Dict[str, Any]       # 输入数据schema
    output_schema: Dict[str, Any]      # 输出数据schema
    confidence_threshold: float = 0.7  # 置信度阈值
    avg_processing_time: float = 0.0   # 平均处理时间
    success_rate: float = 0.0          # 成功率

@dataclass
class AgentMetadata:
    """Agent元数据"""
    name: str
    version: str
    description: str
    author: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class AgentRegistry:
    """Agent注册表 - 单例模式"""
    _instance = None
    _agents: Dict[str, 'BaseAgent'] = {}
    _capabilities: Dict[str, List[str]] = {}  # capability_name -> [agent_names]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, agent: 'BaseAgent') -> bool:
        """注册Agent"""
        try:
            agent_name = agent.metadata.name
            
            # 检查重复注册
            if agent_name in self._agents:
                existing_version = self._agents[agent_name].metadata.version
                new_version = agent.metadata.version
                if self._is_newer_version(new_version, existing_version):
                    logger.info(f"Upgrading agent {agent_name} from {existing_version} to {new_version}")
                else:
                    logger.warning(f"Agent {agent_name} already registered with newer or same version")
                    return False
            
            # 注册Agent
            self._agents[agent_name] = agent
            
            # 注册能力映射
            for capability in agent.metadata.capabilities:
                if capability.name not in self._capabilities:
                    self._capabilities[capability.name] = []
                if agent_name not in self._capabilities[capability.name]:
                    self._capabilities[capability.name].append(agent_name)
            
            logger.info(f"Agent {agent_name} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent.metadata.name}: {e}")
            return False
    
    def discover_agents(self, capability: str) -> List['BaseAgent']:
        """根据能力发现Agent"""
        agent_names = self._capabilities.get(capability, [])
        return [self._agents[name] for name in agent_names if name in self._agents]
    
    def get_agent(self, name: str) -> Optional['BaseAgent']:
        """获取指定Agent"""
        return self._agents.get(name)
    
    def list_all_agents(self) -> List['BaseAgent']:
        """列出所有已注册Agent"""
        return list(self._agents.values())

class BaseAgent(ABC):
    """增强的Agent基类"""
    
    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata
        self.logger = logging.getLogger(f"agent.{metadata.name}")
        
        # 性能统计
        self.processed_tasks = 0
        self.successful_tasks = 0
        self.total_processing_time = 0.0
        self.last_error: Optional[Exception] = None
        
        # 状态管理
        self.is_active = True
        self.is_healthy = True
        self.current_load = 0  # 当前处理中的任务数
        self.max_concurrent_tasks = 5
        
        # 自动注册到注册表
        AgentRegistry().register(self)
    
    @abstractmethod
    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """处理任务 - 必须实现"""
        pass
    
    @abstractmethod
    def can_handle(self, task_type: TaskType, context: Dict[str, Any] = None) -> float:
        """
        评估是否能处理任务
        返回: 0.0-1.0 的置信度分数，0表示不能处理，1表示完全胜任
        """
        pass
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 基础健康检查
            if not self.is_active:
                return False
            
            # 检查负载
            if self.current_load >= self.max_concurrent_tasks:
                self.logger.warning(f"Agent {self.metadata.name} overloaded")
                return False
            
            # 子类可以重写此方法添加自定义检查
            return await self._custom_health_check()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.is_healthy = False
            return False
    
    async def _custom_health_check(self) -> bool:
        """自定义健康检查 - 子类可重写"""
        return True
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if self.processed_tasks == 0:
            return {
                "processed_tasks": 0,
                "success_rate": 0.0,
                "avg_processing_time": 0.0,
                "current_load": self.current_load,
                "is_healthy": self.is_healthy
            }
        
        return {
            "processed_tasks": self.processed_tasks,
            "success_rate": self.successful_tasks / self.processed_tasks,
            "avg_processing_time": self.total_processing_time / self.processed_tasks,
            "current_load": self.current_load,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "is_healthy": self.is_healthy,
            "last_error": str(self.last_error) if self.last_error else None
        }
    
    def update_performance_stats(self, success: bool, processing_time: float, error: Exception = None):
        """更新性能统计"""
        self.processed_tasks += 1
        if success:
            self.successful_tasks += 1
        else:
            self.last_error = error
        
        self.total_processing_time += processing_time
        
        # 更新能力置信度
        for capability in self.metadata.capabilities:
            capability.success_rate = self.successful_tasks / self.processed_tasks
            capability.avg_processing_time = self.total_processing_time / self.processed_tasks
```

---

## 🧠 专业化Agent开发规范

### Agent开发模板
```python
# agents/specialized/requirement_analysis_agent.py
from typing import Dict, Any
from ...core.agent_base import BaseAgent, AgentMetadata, AgentCapability
from ...core.ai_service import AIService, AIRequest

class RequirementAnalysisAgent(BaseAgent):
    """需求分析专业Agent"""
    
    def __init__(self, ai_service: AIService):
        # 定义Agent能力
        capabilities = [
            AgentCapability(
                name="functional_requirement_extraction",
                description="提取功能性需求",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_input": {"type": "string"},
                        "context": {"type": "object"}
                    },
                    "required": ["user_input"]
                },
                output_schema={
                    "type": "object", 
                    "properties": {
                        "functional_requirements": {"type": "array"},
                        "confidence_score": {"type": "number"}
                    }
                },
                confidence_threshold=0.8
            ),
            AgentCapability(
                name="non_functional_requirement_analysis",
                description="分析非功能性需求",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                confidence_threshold=0.7
            )
        ]
        
        # 创建Agent元数据
        metadata = AgentMetadata(
            name="requirement_analysis_agent",
            version="1.0.0",
            description="专业的需求分析Agent，专注于需求提取和分析",
            author="Digital Employee Team",
            capabilities=capabilities,
            tags=["requirement", "analysis", "business"]
        )
        
        super().__init__(metadata)
        self.ai_service = ai_service
        
        # 加载专业化提示词
        self.system_prompts = {
            "functional_analysis": """
            你是一个资深的业务需求分析师，拥有10年以上的需求分析经验。
            请按照以下要求分析用户需求：
            1. 识别核心功能需求
            2. 评估需求的复杂度和优先级
            3. 提出澄清问题
            4. 识别潜在的风险点
            """,
            "non_functional_analysis": """
            你是一个系统架构师，专注于非功能性需求分析。
            请从以下维度分析需求：
            1. 性能要求（响应时间、吞吐量）
            2. 可用性要求（SLA、容错）
            3. 安全性要求（认证、授权、数据保护）
            4. 可扩展性要求（用户增长、数据增长）
            """
        }
    
    def can_handle(self, task_type: TaskType, context: Dict[str, Any] = None) -> float:
        """评估处理能力"""
        if task_type == TaskType.REQUIREMENT_ANALYSIS:
            # 检查输入复杂度
            user_input = context.get("user_input", "") if context else ""
            
            # 简单启发式评估
            if len(user_input) < 50:
                return 0.9  # 简单需求，高置信度
            elif len(user_input) < 200:
                return 0.8  # 中等复杂度
            else:
                return 0.6  # 复杂需求，需要更多澄清
        
        return 0.0  # 不能处理其他类型任务
    
    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """处理需求分析任务"""
        import time
        start_time = time.time()
        
        try:
            self.current_load += 1
            
            # 1. 功能需求分析
            functional_reqs = await self._analyze_functional_requirements(
                request.user_input, request.context
            )
            
            # 2. 非功能需求分析
            non_functional_reqs = await self._analyze_non_functional_requirements(
                request.user_input, request.context
            )
            
            # 3. 生成澄清问题
            clarification_questions = await self._generate_clarification_questions(
                request.user_input, functional_reqs, non_functional_reqs
            )
            
            # 4. 风险评估
            risk_assessment = await self._assess_risks(functional_reqs, non_functional_reqs)
            
            # 5. 组装结果
            result = {
                "functional_requirements": functional_reqs,
                "non_functional_requirements": non_functional_reqs,
                "clarification_questions": clarification_questions,
                "risk_assessment": risk_assessment,
                "confidence_score": self._calculate_confidence(functional_reqs, non_functional_reqs),
                "processing_metadata": {
                    "agent_name": self.metadata.name,
                    "agent_version": self.metadata.version,
                    "capabilities_used": ["functional_requirement_extraction", "non_functional_requirement_analysis"]
                }
            }
            
            processing_time = time.time() - start_time
            self.update_performance_stats(True, processing_time)
            
            return TaskResponse(
                task_id=request.task_id,
                success=True,
                result=result,
                confidence_score=result["confidence_score"],
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.update_performance_stats(False, processing_time, e)
            
            return TaskResponse(
                task_id=request.task_id,
                success=False,
                result={},
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
            
        finally:
            self.current_load -= 1
    
    async def _analyze_functional_requirements(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """分析功能需求"""
        prompt = f"""
        分析以下用户需求，提取功能性需求：
        
        用户需求: {user_input}
        上下文: {context}
        
        请以JSON数组格式返回功能需求列表，每个需求应该清晰、可测试、可实现。
        示例格式: ["用户可以注册账户", "用户可以登录系统", "用户可以修改个人信息"]
        """
        
        ai_request = AIRequest(
            prompt=prompt,
            system_prompt=self.system_prompts["functional_analysis"],
            temperature=0.3  # 较低温度保证一致性
        )
        
        response = await self.ai_service.generate_response(ai_request)
        
        # 解析AI响应
        return self._parse_requirements_list(response.content)
    
    async def _analyze_non_functional_requirements(self, user_input: str, context: Dict[str, Any]) -> List[str]:
        """分析非功能性需求"""
        # 类似实现
        pass
    
    def _parse_requirements_list(self, ai_response: str) -> List[str]:
        """解析AI响应中的需求列表"""
        try:
            import json
            import re
            
            # 尝试直接解析JSON
            if ai_response.strip().startswith('['):
                return json.loads(ai_response)
            
            # 使用正则表达式提取列表项
            patterns = [
                r'"([^"]+)"',  # 引号包围的项
                r'- (.+)',     # 破折号列表
                r'\d+\.\s*(.+)'  # 数字列表
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, ai_response, re.MULTILINE)
                if matches:
                    return [match.strip() for match in matches]
            
            # 兜底方案：按行分割
            lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
            return lines[:10]  # 最多返回10项
            
        except Exception as e:
            self.logger.warning(f"Failed to parse requirements list: {e}")
            return [f"需求分析结果（原始）: {ai_response[:200]}..."]
```

---

## 🔄 Agent协作和编排规范

### Agent协作模式

#### 1. 顺序协作模式
```python
class SequentialAgentOrchestrator:
    """顺序协作编排器"""
    
    def __init__(self, agent_registry: AgentRegistry):
        self.registry = agent_registry
        self.logger = logging.getLogger(__name__)
    
    async def execute_workflow(self, workflow: List[Dict[str, Any]], initial_request: TaskRequest) -> TaskResponse:
        """执行顺序工作流"""
        context = initial_request.context.copy()
        current_result = {}
        
        for step in workflow:
            agent_name = step["agent"]
            capability = step["capability"]
            transform_input = step.get("transform_input", lambda x: x)
            
            # 获取Agent
            agent = self.registry.get_agent(agent_name)
            if not agent:
                raise AgentNotFoundError(f"Agent {agent_name} not found")
            
            # 检查Agent健康状态
            if not await agent.health_check():
                raise AgentUnhealthyError(f"Agent {agent_name} is unhealthy")
            
            # 转换输入
            transformed_input = transform_input(current_result)
            
            # 创建子任务请求
            sub_request = TaskRequest(
                task_id=f"{initial_request.task_id}-{step['step_id']}",
                task_type=step["task_type"],
                user_input=transformed_input.get("user_input", initial_request.user_input),
                context={**context, **transformed_input.get("context", {})}
            )
            
            # 执行任务
            response = await agent.process_task(sub_request)
            
            if not response.success:
                # 失败处理策略
                if step.get("required", True):
                    raise AgentProcessingError(f"Required step failed: {agent_name}")
                else:
                    self.logger.warning(f"Optional step failed: {agent_name}, continuing...")
                    continue
            
            # 更新上下文和结果
            current_result.update(response.result)
            context.update(response.result.get("context", {}))
        
        return TaskResponse(
            task_id=initial_request.task_id,
            success=True,
            result=current_result,
            confidence_score=min([step.get("confidence", 1.0) for step in workflow]),
            processing_time=sum([step.get("processing_time", 0.0) for step in workflow])
        )

# 使用示例
workflow = [
    {
        "step_id": "requirement_analysis",
        "agent": "requirement_analysis_agent",
        "task_type": TaskType.REQUIREMENT_ANALYSIS,
        "capability": "functional_requirement_extraction",
        "required": True,
        "transform_input": lambda result: {"user_input": result.get("original_input", "")}
    },
    {
        "step_id": "architecture_design", 
        "agent": "architecture_design_agent",
        "task_type": TaskType.SOLUTION_DESIGN,
        "capability": "architecture_recommendation",
        "required": True,
        "transform_input": lambda result: {
            "user_input": f"Based on requirements: {result.get('functional_requirements', [])}",
            "context": {"requirements": result.get('functional_requirements', [])}
        }
    }
]
```

#### 2. 并行协作模式
```python
class ParallelAgentOrchestrator:
    """并行协作编排器"""
    
    async def execute_parallel_tasks(self, tasks: List[Dict[str, Any]], initial_request: TaskRequest) -> TaskResponse:
        """并行执行多个任务"""
        import asyncio
        
        # 创建并行任务
        parallel_tasks = []
        for task_config in tasks:
            agent = self.registry.get_agent(task_config["agent"])
            sub_request = self._create_sub_request(initial_request, task_config)
            parallel_tasks.append(agent.process_task(sub_request))
        
        # 并行执行
        responses = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        
        # 合并结果
        merged_result = {}
        total_confidence = 0.0
        successful_tasks = 0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                self.logger.error(f"Parallel task {i} failed: {response}")
                continue
            
            if response.success:
                merged_result.update(response.result)
                total_confidence += response.confidence_score
                successful_tasks += 1
        
        return TaskResponse(
            task_id=initial_request.task_id,
            success=successful_tasks > 0,
            result=merged_result,
            confidence_score=total_confidence / max(successful_tasks, 1),
            processing_time=max([r.processing_time for r in responses if not isinstance(r, Exception)])
        )
```

---

## 📊 Agent监控和性能管理

### 监控指标规范
```python
# core/agent_monitoring.py
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict, Any
import time

# Agent相关监控指标
AGENT_TASK_COUNT = Counter(
    'agent_tasks_total', 
    'Total tasks processed by agent',
    ['agent_name', 'task_type', 'status']
)

AGENT_PROCESSING_TIME = Histogram(
    'agent_processing_seconds',
    'Time spent processing tasks',
    ['agent_name', 'task_type']
)

AGENT_HEALTH = Gauge(
    'agent_health_status',
    'Agent health status (1=healthy, 0=unhealthy)',
    ['agent_name']
)

AGENT_CONCURRENT_TASKS = Gauge(
    'agent_concurrent_tasks',
    'Number of concurrent tasks',
    ['agent_name']
)

AGENT_INFO = Info(
    'agent_info',
    'Agent metadata information',
    ['agent_name']
)

class AgentPerformanceMonitor:
    """Agent性能监控器"""
    
    def __init__(self):
        self.performance_data: Dict[str, Dict[str, Any]] = {}
        self.alert_thresholds = {
            "success_rate_min": 0.85,
            "avg_processing_time_max": 30.0,
            "error_rate_max": 0.15
        }
    
    def record_task_execution(self, agent_name: str, task_type: str, 
                            success: bool, processing_time: float):
        """记录任务执行"""
        status = "success" if success else "error"
        
        # Prometheus指标
        AGENT_TASK_COUNT.labels(
            agent_name=agent_name,
            task_type=task_type.value,
            status=status
        ).inc()
        
        AGENT_PROCESSING_TIME.labels(
            agent_name=agent_name,
            task_type=task_type.value
        ).observe(processing_time)
        
        # 内部统计
        if agent_name not in self.performance_data:
            self.performance_data[agent_name] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "total_time": 0.0,
                "task_types": {}
            }
        
        agent_data = self.performance_data[agent_name]
        agent_data["total_tasks"] += 1
        agent_data["total_time"] += processing_time
        
        if success:
            agent_data["successful_tasks"] += 1
        
        # 按任务类型统计
        task_type_str = task_type.value
        if task_type_str not in agent_data["task_types"]:
            agent_data["task_types"][task_type_str] = {
                "count": 0, "success": 0, "total_time": 0.0
            }
        
        type_data = agent_data["task_types"][task_type_str]
        type_data["count"] += 1
        type_data["total_time"] += processing_time
        if success:
            type_data["success"] += 1
    
    def update_agent_health(self, agent_name: str, is_healthy: bool):
        """更新Agent健康状态"""
        AGENT_HEALTH.labels(agent_name=agent_name).set(1 if is_healthy else 0)
    
    def update_concurrent_tasks(self, agent_name: str, concurrent_count: int):
        """更新并发任务数"""
        AGENT_CONCURRENT_TASKS.labels(agent_name=agent_name).set(concurrent_count)
    
    def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """检查性能告警"""
        alerts = []
        
        for agent_name, data in self.performance_data.items():
            if data["total_tasks"] < 10:  # 样本量太小，跳过
                continue
            
            success_rate = data["successful_tasks"] / data["total_tasks"]
            avg_processing_time = data["total_time"] / data["total_tasks"]
            error_rate = 1 - success_rate
            
            # 成功率告警
            if success_rate < self.alert_thresholds["success_rate_min"]:
                alerts.append({
                    "type": "LOW_SUCCESS_RATE",
                    "agent": agent_name,
                    "current_value": success_rate,
                    "threshold": self.alert_thresholds["success_rate_min"],
                    "severity": "HIGH"
                })
            
            # 处理时间告警
            if avg_processing_time > self.alert_thresholds["avg_processing_time_max"]:
                alerts.append({
                    "type": "HIGH_PROCESSING_TIME",
                    "agent": agent_name,
                    "current_value": avg_processing_time,
                    "threshold": self.alert_thresholds["avg_processing_time_max"],
                    "severity": "MEDIUM"
                })
        
        return alerts
```

---

## 🔧 Agent配置和管理

### Agent配置规范
```yaml
# config/agents.yaml
agents:
  requirement_analysis_agent:
    enabled: true
    version: "1.0.0"
    max_concurrent_tasks: 3
    timeout_seconds: 30
    retry_attempts: 2
    
    ai_service:
      provider: "openai"
      model: "gpt-4"
      temperature: 0.3
      max_tokens: 2000
    
    capabilities:
      - name: "functional_requirement_extraction"
        confidence_threshold: 0.8
        enabled: true
      - name: "non_functional_requirement_analysis"
        confidence_threshold: 0.7
        enabled: true
    
    prompts:
      functional_analysis: |
        你是一个资深的业务需求分析师...
      non_functional_analysis: |
        你是一个系统架构师...
    
    monitoring:
      health_check_interval: 60  # 秒
      performance_alert_threshold:
        success_rate_min: 0.85
        avg_processing_time_max: 25.0
    
  architecture_design_agent:
    enabled: false  # 暂未启用
    version: "0.9.0"
    # ... 其他配置
```

### Agent管理API
```python
# api/routes/agents.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents():
    """列出所有已注册的Agent"""
    registry = AgentRegistry()
    agents = registry.list_all_agents()
    
    return [
        {
            "name": agent.metadata.name,
            "version": agent.metadata.version,
            "description": agent.metadata.description,
            "capabilities": [cap.name for cap in agent.metadata.capabilities],
            "status": "healthy" if agent.is_healthy else "unhealthy",
            "performance": agent.get_performance_stats()
        }
        for agent in agents
    ]

@router.get("/{agent_name}/health")
async def check_agent_health(agent_name: str):
    """检查Agent健康状态"""
    registry = AgentRegistry()
    agent = registry.get_agent(agent_name)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    is_healthy = await agent.health_check()
    
    return {
        "agent_name": agent_name,
        "is_healthy": is_healthy,
        "performance_stats": agent.get_performance_stats(),
        "last_check": datetime.now().isoformat()
    }

@router.post("/{agent_name}/reload")
async def reload_agent(agent_name: str):
    """重新加载Agent配置"""
    # 实现Agent配置热重载
    pass

@router.delete("/{agent_name}")
async def deactivate_agent(agent_name: str):
    """停用Agent"""
    registry = AgentRegistry()
    agent = registry.get_agent(agent_name)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent.is_active = False
    return {"message": f"Agent {agent_name} deactivated"}
```

---

## 🧪 Agent测试规范

### Agent单元测试
```python
# tests/agents/test_requirement_analysis_agent.py
import pytest
from unittest.mock import AsyncMock, Mock
from digital_employee.agents.specialized.requirement_analysis_agent import RequirementAnalysisAgent
from digital_employee.core.agent_base import TaskRequest, TaskType

class TestRequirementAnalysisAgent:
    
    @pytest.fixture
    def mock_ai_service(self):
        mock_service = Mock()
        mock_service.generate_response = AsyncMock()
        return mock_service
    
    @pytest.fixture
    def agent(self, mock_ai_service):
        return RequirementAnalysisAgent(mock_ai_service)
    
    @pytest.mark.asyncio
    async def test_can_handle_requirement_analysis(self, agent):
        """测试能力评估"""
        # 简单输入
        confidence = agent.can_handle(
            TaskType.REQUIREMENT_ANALYSIS,
            {"user_input": "I need a login system"}
        )
        assert confidence == 0.9
        
        # 复杂输入
        confidence = agent.can_handle(
            TaskType.REQUIREMENT_ANALYSIS,
            {"user_input": "a" * 300}  # 很长的输入
        )
        assert confidence == 0.6
        
        # 不支持的任务类型
        confidence = agent.can_handle(TaskType.CODE_GENERATION)
        assert confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_process_task_success(self, agent, mock_ai_service):
        """测试成功处理任务"""
        # 模拟AI服务响应
        mock_ai_service.generate_response.return_value = Mock(
            content='["用户可以注册账户", "用户可以登录系统"]'
        )
        
        # 创建测试请求
        request = TaskRequest(
            task_id="test-123",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="I need a user management system"
        )
        
        # 执行任务
        response = await agent.process_task(request)
        
        # 验证结果
        assert response.success is True
        assert response.task_id == "test-123"
        assert "functional_requirements" in response.result
        assert len(response.result["functional_requirements"]) > 0
        assert response.confidence_score > 0.5
    
    @pytest.mark.asyncio
    async def test_process_task_ai_failure(self, agent, mock_ai_service):
        """测试AI服务失败的情况"""
        # 模拟AI服务失败
        mock_ai_service.generate_response.side_effect = Exception("API Error")
        
        request = TaskRequest(
            task_id="test-456",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="Test input"
        )
        
        response = await agent.process_task(request)
        
        # 验证错误处理
        assert response.success is False
        assert response.error_message is not None
        assert "API Error" in response.error_message

class TestAgentRegistry:
    """Agent注册表测试"""
    
    def test_register_agent(self):
        registry = AgentRegistry()
        mock_agent = Mock()
        mock_agent.metadata.name = "test_agent"
        mock_agent.metadata.version = "1.0.0"
        mock_agent.metadata.capabilities = []
        
        result = registry.register(mock_agent)
        assert result is True
        
        retrieved_agent = registry.get_agent("test_agent")
        assert retrieved_agent == mock_agent
    
    def test_discover_agents_by_capability(self):
        registry = AgentRegistry()
        
        # 创建mock agent with capability
        mock_agent = Mock()
        mock_agent.metadata.name = "capable_agent"
        mock_agent.metadata.version = "1.0.0"
        mock_capability = Mock()
        mock_capability.name = "test_capability"
        mock_agent.metadata.capabilities = [mock_capability]
        
        registry.register(mock_agent)
        
        # 测试发现
        discovered = registry.discover_agents("test_capability")
        assert len(discovered) == 1
        assert discovered[0] == mock_agent
```

### Agent集成测试
```python
# tests/integration/test_agent_orchestration.py
class TestAgentOrchestration:
    """Agent编排集成测试"""
    
    @pytest.mark.asyncio
    async def test_sequential_workflow(self, test_agents, orchestrator):
        """测试顺序工作流"""
        workflow = [
            {
                "step_id": "analysis",
                "agent": "requirement_analysis_agent",
                "task_type": TaskType.REQUIREMENT_ANALYSIS
            },
            {
                "step_id": "design",
                "agent": "architecture_design_agent", 
                "task_type": TaskType.SOLUTION_DESIGN
            }
        ]
        
        initial_request = TaskRequest(
            task_id="workflow-test-001",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="Build a user management system"
        )
        
        result = await orchestrator.execute_workflow(workflow, initial_request)
        
        assert result.success is True
        assert "functional_requirements" in result.result
        assert "architecture_components" in result.result
    
    @pytest.mark.asyncio
    async def test_parallel_execution(self, test_agents, parallel_orchestrator):
        """测试并行执行"""
        parallel_tasks = [
            {"agent": "requirement_analysis_agent", "task_type": TaskType.REQUIREMENT_ANALYSIS},
            {"agent": "risk_assessment_agent", "task_type": TaskType.GENERAL_INQUIRY}
        ]
        
        initial_request = TaskRequest(
            task_id="parallel-test-001",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="Complex project requirements"
        )
        
        result = await parallel_orchestrator.execute_parallel_tasks(parallel_tasks, initial_request)
        
        assert result.success is True
        # 验证并行结果被正确合并
```

---

## 📋 Agent开发检查清单

### Agent开发完成检查
- [ ] **元数据完整**：name、version、description、capabilities都已定义
- [ ] **能力评估**：实现了准确的`can_handle`方法
- [ ] **错误处理**：包含完整的异常处理和降级逻辑
- [ ] **性能监控**：集成了性能统计和健康检查
- [ ] **AI集成**：正确使用AI服务抽象层
- [ ] **配置管理**：支持外部配置和热重载
- [ ] **日志记录**：关键操作有结构化日志
- [ ] **单元测试**：测试覆盖率 ≥ 85%
- [ ] **集成测试**：与其他Agent的协作测试
- [ ] **负载测试**：并发处理能力验证

### Agent部署检查
- [ ] **注册验证**：正确注册到Agent注册表
- [ ] **健康检查**：健康检查接口正常工作
- [ ] **监控集成**：Prometheus指标正常输出
- [ ] **配置验证**：配置文件语法正确，参数有效
- [ ] **依赖检查**：所有依赖服务可用
- [ ] **权限验证**：必要的API权限已配置
- [ ] **版本兼容**：与现有Agent版本兼容
- [ ] **回滚方案**：部署失败时的回滚策略

---

## 🔄 Agent生命周期管理

### Agent版本管理
```python
class AgentVersionManager:
    """Agent版本管理器"""
    
    def __init__(self):
        self.version_history: Dict[str, List[str]] = {}
        self.rollback_points: Dict[str, str] = {}
    
    def deploy_agent_version(self, agent_name: str, version: str, agent_instance: BaseAgent) -> bool:
        """部署新版本Agent"""
        try:
            # 1. 版本验证
            if not self._validate_version(version):
                raise ValueError(f"Invalid version format: {version}")
            
            # 2. 兼容性检查
            if not self._check_compatibility(agent_name, version):
                raise ValueError(f"Version {version} is not compatible")
            
            # 3. 健康检查
            if not await agent_instance.health_check():
                raise ValueError(f"Agent {agent_name} failed health check")
            
            # 4. 记录当前版本作为回滚点
            current_agent = AgentRegistry().get_agent(agent_name)
            if current_agent:
                self.rollback_points[agent_name] = current_agent.metadata.version
            
            # 5. 注册新版本
            AgentRegistry().register(agent_instance)
            
            # 6. 更新版本历史
            if agent_name not in self.version_history:
                self.version_history[agent_name] = []
            self.version_history[agent_name].append(version)
            
            self.logger.info(f"Successfully deployed {agent_name} version {version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy {agent_name} version {version}: {e}")
            return False
    
    def rollback_agent(self, agent_name: str) -> bool:
        """回滚Agent到上一个版本"""
        try:
            rollback_version = self.rollback_points.get(agent_name)
            if not rollback_version:
                raise ValueError(f"No rollback point found for {agent_name}")
            
            # 实现回滚逻辑
            # 这里需要重新加载旧版本的Agent
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to rollback {agent_name}: {e}")
            return False
```

### Agent停用和清理
```python
class AgentLifecycleManager:
    """Agent生命周期管理"""
    
    async def graceful_shutdown_agent(self, agent_name: str, timeout: int = 30) -> bool:
        """优雅停用Agent"""
        agent = AgentRegistry().get_agent(agent_name)
        if not agent:
            return True  # 已经不存在，认为成功
        
        try:
            # 1. 标记Agent为非活跃状态
            agent.is_active = False
            
            # 2. 等待当前任务完成
            start_time = time.time()
            while agent.current_load > 0 and (time.time() - start_time) < timeout:
                await asyncio.sleep(1)
                self.logger.info(f"Waiting for {agent_name} to finish {agent.current_load} tasks")
            
            # 3. 强制停止（如果超时）
            if agent.current_load > 0:
                self.logger.warning(f"Force stopping {agent_name} with {agent.current_load} active tasks")
            
            # 4. 清理资源
            await self._cleanup_agent_resources(agent)
            
            # 5. 从注册表移除
            AgentRegistry()._agents.pop(agent_name, None)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown {agent_name}: {e}")
            return False
    
    async def _cleanup_agent_resources(self, agent: BaseAgent):
        """清理Agent资源"""
        # 清理AI服务连接
        if hasattr(agent, 'ai_service'):
            await agent.ai_service.cleanup()
        
        # 清理其他资源
        # ...
```

---

*Agent开发和集成规范文档版本：v1.0*  
*创建时间：2025-07-31*  
*维护者：数字员工系统开发团队*
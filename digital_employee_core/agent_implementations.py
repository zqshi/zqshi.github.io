# 数字员工Agent实现示例代码
# 版本: 2.0.0 - 集成Prompt管理系统

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

import aioredis
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from langchain.llms import OpenAI
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

# 导入Prompt管理器
from prompt_manager import PromptManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# 核心数据模型
# ================================

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

# ================================
# Agent基础框架
# ================================

class BaseAgent(ABC):
    """Agent基础类 - 版本2.0.0集成Prompt管理"""
    
    def __init__(self, agent_id: str, role: AgentRole, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        
        # 初始化Prompt管理器
        self.prompt_manager = PromptManager()
        
        # 生成Agent专用prompt
        self.system_prompt = self._generate_system_prompt()
        
        self.constraints = self._load_constraints()
        self.memory = ConversationBufferMemory()
        self.tools = self._initialize_tools()
        
        # 使用自定义prompt初始化LLM
        self.llm = OpenAI(
            temperature=0.7,
            # 可以在这里设置system prompt，具体取决于LangChain版本
        )
        
        self.performance_metrics = {
            'tasks_completed': 0,
            'success_rate': 0.0,
            'avg_response_time': 0.0
        }
        
        # 记录创建日志
        logger.info(f"Agent {self.agent_id} initialized with prompt system v{self.prompt_manager.get_version_info()['version']}")
    
    def _generate_system_prompt(self) -> str:
        """生成Agent系统prompt"""
        try:
            return self.prompt_manager.create_agent_prompt(self.agent_id, self.role.value)
        except Exception as e:
            logger.error(f"Failed to generate system prompt for {self.agent_id}: {str(e)}")
            return f"You are a professional {self.role.value} agent. Please assist users with tasks related to your role."
    
    @abstractmethod
    def _load_constraints(self) -> List[AgentConstraint]:
        """加载Agent约束条件"""
        pass
    
    @abstractmethod
    def _initialize_tools(self) -> List[Tool]:
        """初始化Agent工具"""
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
        """处理任务的主入口 - 版本2.0.0集成任务Prompt"""
        start_time = datetime.now()
        
        try:
            # 任务预处理
            logger.info(f"Agent {self.agent_id} processing task {task.task_id} with prompt system")
            
            # 生成任务专用prompt
            task_prompt = self._generate_task_prompt(task)
            
            # 检查能力
            if not await self.can_handle_task(task):
                return await self._escalate_task(task)
            
            # 执行任务（传入任务prompt）
            result = await self._execute_task(task, task_prompt)
            
            # 验证结果
            validated_result = await self._validate_result(result, task)
            
            # 更新记忆（包含prompt信息）
            self._update_memory(task, validated_result, task_prompt)
            
            # 更新性能指标
            self._update_performance_metrics(start_time, True)
            
            return {
                'status': 'success',
                'result': validated_result,
                'agent_id': self.agent_id,
                'task_id': task.task_id,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'prompt_version': self.prompt_manager.get_version_info()['version']
            }
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            self._update_performance_metrics(start_time, False)
            return {
                'status': 'error',
                'error': str(e),
                'agent_id': self.agent_id,
                'task_id': task.task_id,
                'prompt_version': self.prompt_manager.get_version_info()['version']
            }
    
    def _generate_task_prompt(self, task: Task) -> str:
        """生成任务专用prompt"""
        try:
            task_data = {
                'task_type': task.task_type,
                'priority': task.priority,
                'task_data': str(task.data)
            }
            return self.prompt_manager.create_task_prompt(self.role.value, task.task_type, task_data)
        except Exception as e:
            logger.warning(f"Failed to generate task prompt for {task.task_id}: {str(e)}")
            # 返回基础任务prompt
            return f"Please process the following {task.task_type} task with priority {task.priority}: {task.data}"
    
    @abstractmethod
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行具体任务逻辑 - 版本2.0.0支持任务prompt"""
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
        # 基础验证逻辑
        if result is None:
            raise ValueError("Task result cannot be None")
        return result
    
    def _update_memory(self, task: Task, result: Any, task_prompt: str = None):
        """更新Agent记忆 - 版本2.0.0包含prompt信息"""
        context_input = {
            "input": f"Task: {task.task_type} - {task.data}",
            "task_id": task.task_id,
            "prompt_used": "custom_task_prompt" if task_prompt else "default_prompt"
        }
        
        context_output = {
            "output": str(result),
            "timestamp": datetime.now().isoformat(),
            "agent_version": "2.0.0"
        }
        
        self.memory.save_context(context_input, context_output)
    
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

# ================================
# 具体Agent实现
# ================================

class HRAgent(BaseAgent):
    """人力资源Agent"""
    
    def __init__(self, agent_id: str):
        capabilities = [
            AgentCapability("employee_data_analysis", "员工数据分析", 8, ["database", "analytics"]),
            AgentCapability("recruitment_screening", "招聘筛选", 9, ["resume_parser", "scoring"]),
            AgentCapability("policy_consultation", "政策咨询", 7, ["knowledge_base", "search"])
        ]
        super().__init__(agent_id, AgentRole.HR, capabilities)
    
    def _load_constraints(self) -> List[AgentConstraint]:
        return [
            AgentConstraint(
                "privacy_protection", 
                "不得泄露员工隐私信息",
                lambda task: not self._contains_sensitive_data(task)
            ),
            AgentConstraint(
                "salary_modification",
                "不得直接修改薪资信息",
                lambda task: task.task_type != "salary_modification"
            )
        ]
    
    def _contains_sensitive_data(self, task: Task) -> bool:
        """检查是否包含敏感数据"""
        sensitive_fields = ['ssn', 'salary', 'performance_review']
        return any(field in str(task.data) for field in sensitive_fields)
    
    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="Employee Database Query",
                description="查询员工数据库信息",
                func=self._query_employee_database
            ),
            Tool(
                name="Resume Parser",
                description="解析简历内容",
                func=self._parse_resume
            ),
            Tool(
                name="Policy Search",
                description="搜索人事政策",
                func=self._search_policies
            )
        ]
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行HR相关任务 - 版本2.0.0集成Prompt"""
        # 记录使用的prompt
        if task_prompt:
            logger.info(f"HR Agent using custom task prompt for {task.task_type}")
        
        if task.task_type == "employee_analysis":
            return await self._analyze_employee_data(task.data, task_prompt)
        elif task.task_type == "resume_screening":
            return await self._screen_resume(task.data, task_prompt)
        elif task.task_type == "policy_query":
            return await self._query_policy(task.data, task_prompt)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _analyze_employee_data(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """分析员工数据 - 版本2.0.0支持Prompt增强"""
        employee_id = data.get('employee_id')
        analysis_type = data.get('analysis_type', 'general')
        
        # 如果有自定义task prompt，记录日志
        if task_prompt:
            logger.info(f"Analyzing employee {employee_id} with custom prompt guidance")
        
        # 模拟数据分析过程
        await asyncio.sleep(2)  # 模拟处理时间
        
        return {
            'employee_id': employee_id,
            'analysis_type': analysis_type,
            'performance_score': 8.5,
            'recommendations': [
                "考虑提供更多技能培训机会",
                "建议参与跨部门项目提升协作能力"
            ],
            'risk_factors': ['无明显风险'],
            'analysis_date': datetime.now().isoformat(),
            'prompt_enhanced': task_prompt is not None
        }
    
    async def _screen_resume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """筛选简历"""
        resume_content = data.get('resume_content')
        job_requirements = data.get('job_requirements')
        
        # 模拟简历筛选过程
        await asyncio.sleep(1.5)
        
        return {
            'match_score': 85,
            'matched_skills': ['Python', 'SQL', '项目管理'],
            'missing_skills': ['Kubernetes', '机器学习'],
            'recommendation': 'RECOMMEND',
            'next_steps': ['安排技术面试', '进行背景调查']
        }
    
    async def _query_policy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """查询政策"""
        policy_topic = data.get('topic')
        
        # 模拟政策查询
        await asyncio.sleep(1)
        
        return {
            'topic': policy_topic,
            'relevant_policies': [
                {
                    'policy_name': '员工休假管理办法',
                    'summary': '规定了各类假期的申请流程和审批权限',
                    'effective_date': '2024-01-01'
                }
            ],
            'quick_answer': '年假需要提前15天申请，经直接主管批准后生效。'
        }
    
    def _query_employee_database(self, query: str) -> str:
        """查询员工数据库（工具函数）"""
        return f"Employee database query result for: {query}"
    
    def _parse_resume(self, resume_text: str) -> str:
        """解析简历（工具函数）"""
        return f"Parsed resume data: {len(resume_text)} characters processed"
    
    def _search_policies(self, keyword: str) -> str:
        """搜索政策（工具函数）"""
        return f"Policy search results for: {keyword}"

class FinanceAgent(BaseAgent):
    """财务Agent"""
    
    def __init__(self, agent_id: str):
        capabilities = [
            AgentCapability("financial_analysis", "财务分析", 9, ["excel", "database"]),
            AgentCapability("budget_planning", "预算规划", 8, ["forecasting", "analytics"]),
            AgentCapability("expense_tracking", "费用跟踪", 7, ["erp_system", "reporting"])
        ]
        super().__init__(agent_id, AgentRole.FINANCE, capabilities)
    
    def _load_constraints(self) -> List[AgentConstraint]:
        return [
            AgentConstraint(
                "approval_required",
                "大额交易需要审批",
                lambda task: self._check_transaction_amount(task)
            ),
            AgentConstraint(
                "financial_compliance",
                "必须遵循财务合规要求",
                lambda task: self._validate_compliance(task)
            )
        ]
    
    def _check_transaction_amount(self, task: Task) -> bool:
        """检查交易金额"""
        amount = task.data.get('amount', 0)
        return amount < 10000  # 小于1万的交易可以直接处理
    
    def _validate_compliance(self, task: Task) -> bool:
        """验证合规性"""
        # 简化的合规检查
        return 'illegal' not in str(task.data).lower()
    
    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="Financial Data Query",
                description="查询财务数据",
                func=self._query_financial_data
            ),
            Tool(
                name="Budget Calculator",
                description="预算计算工具",
                func=self._calculate_budget
            ),
            Tool(
                name="Expense Analyzer",
                description="费用分析工具",
                func=self._analyze_expenses
            )
        ]
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行财务相关任务 - 版本2.0.0集成Prompt"""
        # 记录使用的prompt
        if task_prompt:
            logger.info(f"Finance Agent using custom task prompt for {task.task_type}")
        
        if task.task_type == "financial_report":
            return await self._generate_financial_report(task.data, task_prompt)
        elif task.task_type == "budget_analysis":
            return await self._analyze_budget(task.data, task_prompt)
        elif task.task_type == "expense_audit":
            return await self._audit_expenses(task.data, task_prompt)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _generate_financial_report(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """生成财务报告 - 版本2.0.0支持Prompt增强"""
        report_type = data.get('report_type', 'monthly')
        department = data.get('department', 'all')
        
        # 如果有自定义task prompt，记录日志
        if task_prompt:
            logger.info(f"Generating {report_type} financial report with prompt guidance")
        
        # 模拟报告生成
        await asyncio.sleep(3)
        
        return {
            'report_type': report_type,
            'department': department,
            'total_revenue': 1500000,
            'total_expenses': 1200000,
            'profit_margin': 20.0,
            'key_metrics': {
                'revenue_growth': '15%',
                'cost_efficiency': '92%',
                'budget_variance': '-3%'
            },
            'generated_at': datetime.now().isoformat(),
            'prompt_enhanced': task_prompt is not None
        }
    
    async def _analyze_budget(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析预算"""
        budget_period = data.get('period', 'Q1')
        categories = data.get('categories', [])
        
        await asyncio.sleep(2)
        
        return {
            'period': budget_period,
            'total_budget': 500000,
            'allocated_budget': 450000,
            'remaining_budget': 50000,
            'category_breakdown': {
                'personnel': 60,
                'marketing': 20,
                'operations': 15,
                'other': 5
            },
            'recommendations': [
                '建议增加市场营销预算分配',
                '人员成本控制在合理范围内'
            ]
        }
    
    async def _audit_expenses(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """审计费用"""
        period = data.get('period')
        expense_category = data.get('category')
        
        await asyncio.sleep(2.5)
        
        return {
            'audit_period': period,
            'category': expense_category,
            'total_expenses': 85000,
            'flagged_items': [
                {'description': '异常差旅费用', 'amount': 5000, 'risk_level': 'medium'}
            ],
            'compliance_score': 95,
            'audit_status': 'PASSED'
        }
    
    def _query_financial_data(self, query: str) -> str:
        return f"Financial data query result: {query}"
    
    def _calculate_budget(self, parameters: str) -> str:
        return f"Budget calculation result: {parameters}"
    
    def _analyze_expenses(self, data: str) -> str:
        return f"Expense analysis result: {data}"

# ================================
# 任务调度系统
# ================================

class TaskPlannerAgent(BaseAgent):
    """任务规划Agent"""
    
    def __init__(self, agent_id: str):
        capabilities = [
            AgentCapability("task_decomposition", "任务分解", 9, ["nlp", "planning"]),
            AgentCapability("dependency_analysis", "依赖分析", 8, ["graph_analysis"]),
            AgentCapability("priority_optimization", "优先级优化", 7, ["optimization"])
        ]
        super().__init__(agent_id, AgentRole.PLANNER, capabilities)
    
    def _load_constraints(self) -> List[AgentConstraint]:
        return [
            AgentConstraint(
                "complexity_limit",
                "单个任务不超过最大复杂度",
                lambda task: self._check_complexity(task)
            )
        ]
    
    def _check_complexity(self, task: Task) -> bool:
        complexity_score = len(str(task.data)) / 100  # 简化的复杂度计算
        return complexity_score < 10
    
    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="Task Decomposer",
                description="任务分解工具",
                func=self._decompose_task
            ),
            Tool(
                name="Dependency Analyzer",
                description="依赖关系分析",
                func=self._analyze_dependencies
            )
        ]
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行任务规划 - 版本2.0.0集成Prompt"""
        if task_prompt:
            logger.info(f"Task Planner using custom task prompt for {task.task_type}")
        
        if task.task_type == "task_planning":
            return await self._plan_complex_task(task.data, task_prompt)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _plan_complex_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """规划复杂任务"""
        task_description = data.get('description')
        requirements = data.get('requirements', [])
        
        # 模拟任务分解过程
        await asyncio.sleep(2)
        
        subtasks = [
            {
                'subtask_id': 'task_1',
                'description': '需求分析和数据收集',
                'estimated_time': '2小时',
                'required_agent_type': 'analyst',
                'dependencies': [],
                'priority': 'high'
            },
            {
                'subtask_id': 'task_2',
                'description': '数据处理和分析',
                'estimated_time': '4小时',
                'required_agent_type': 'data_analyst',
                'dependencies': ['task_1'],
                'priority': 'high'
            },
            {
                'subtask_id': 'task_3',
                'description': '报告生成和审核',
                'estimated_time': '2小时',
                'required_agent_type': 'report_generator',
                'dependencies': ['task_2'],
                'priority': 'medium'
            }
        ]
        
        return {
            'original_task': task_description,
            'subtasks': subtasks,
            'total_estimated_time': '8小时',
            'execution_plan': {
                'parallel_tasks': ['task_1'],
                'sequential_tasks': [['task_1'], ['task_2'], ['task_3']]
            },
            'resource_requirements': {
                'agents_needed': 3,
                'estimated_cost': 1200
            }
        }
    
    def _decompose_task(self, task_description: str) -> str:
        return f"Task decomposition result for: {task_description}"
    
    def _analyze_dependencies(self, tasks: str) -> str:
        return f"Dependency analysis result: {tasks}"

class TaskSchedulerAgent(BaseAgent):
    """任务调度Agent"""
    
    def __init__(self, agent_id: str, available_agents: Dict[str, BaseAgent]):
        capabilities = [
            AgentCapability("agent_matching", "Agent匹配", 9, ["matching_engine"]),
            AgentCapability("load_balancing", "负载均衡", 8, ["load_balancer"]),
            AgentCapability("performance_monitoring", "性能监控", 7, ["monitoring"])
        ]
        super().__init__(agent_id, AgentRole.SCHEDULER, capabilities)
        self.available_agents = available_agents
        self.task_queue = asyncio.Queue()
    
    def _load_constraints(self) -> List[AgentConstraint]:
        return []
    
    def _initialize_tools(self) -> List[Tool]:
        return [
            Tool(
                name="Agent Matcher",
                description="Agent匹配工具",
                func=self._match_agent
            ),
            Tool(
                name="Load Monitor",
                description="负载监控工具",
                func=self._monitor_load
            )
        ]
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行任务调度 - 版本2.0.0集成Prompt"""
        if task_prompt:
            logger.info(f"Task Scheduler using custom task prompt for {task.task_type}")
        
        if task.task_type == "task_dispatch":
            return await self._dispatch_task(task.data, task_prompt)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _dispatch_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分发任务"""
        target_task = Task(**data['task'])
        
        # 找到合适的Agent
        suitable_agents = []
        for agent_id, agent in self.available_agents.items():
            if await agent.can_handle_task(target_task):
                load_score = self._calculate_load_score(agent)
                suitable_agents.append((agent, load_score))
        
        if not suitable_agents:
            return {
                'status': 'no_suitable_agent',
                'task_id': target_task.task_id
            }
        
        # 选择负载最低的Agent
        selected_agent = min(suitable_agents, key=lambda x: x[1])[0]
        
        # 分发任务
        result = await selected_agent.process_task(target_task)
        
        return {
            'status': 'dispatched',
            'assigned_agent': selected_agent.agent_id,
            'task_result': result
        }
    
    def _calculate_load_score(self, agent: BaseAgent) -> float:
        """计算Agent负载分数"""
        # 简化的负载计算
        return agent.performance_metrics['tasks_completed'] * 0.1
    
    def _match_agent(self, task_requirements: str) -> str:
        return f"Agent matching result: {task_requirements}"
    
    def _monitor_load(self, agent_id: str) -> str:
        return f"Load monitoring result for agent: {agent_id}"

# ================================
# Web API接口
# ================================

app = FastAPI(title="数字员工系统API", version="1.0.0")

# Pydantic模型
class TaskRequest(BaseModel):
    task_type: str
    priority: str
    data: Dict[str, Any]
    deadline: Optional[str] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# 全局Agent实例
agents = {
    'hr_001': HRAgent('hr_001'),
    'finance_001': FinanceAgent('finance_001'),
    'planner_001': TaskPlannerAgent('planner_001'),
}

scheduler = TaskSchedulerAgent('scheduler_001', agents)

@app.post("/api/v1/tasks", response_model=TaskResponse)
async def submit_task(task_request: TaskRequest):
    """提交任务"""
    try:
        task = Task(
            task_id=f"task_{datetime.now().timestamp()}",
            task_type=task_request.task_type,
            priority=task_request.priority,
            data=task_request.data
        )
        
        # 通过调度器分发任务
        dispatch_task = Task(
            task_id=f"dispatch_{task.task_id}",
            task_type="task_dispatch",
            priority="high",
            data={'task': task.__dict__}
        )
        
        result = await scheduler.process_task(dispatch_task)
        
        return TaskResponse(
            task_id=task.task_id,
            status="success",
            result=result
        )
        
    except Exception as e:
        logger.error(f"Task submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """获取Agent状态"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_id]
    return {
        'agent_id': agent_id,
        'role': agent.role.value,
        'status': 'active',
        'capabilities': [cap.name for cap in agent.capabilities],
        'performance_metrics': agent.performance_metrics
    }

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_agents': len(agents)
    }

# ================================
# 启动脚本
# ================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动数字员工系统...")
    logger.info(f"已注册 {len(agents)} 个Agent")
    
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
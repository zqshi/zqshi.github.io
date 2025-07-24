# 简化版Agent实现 - 移除外部依赖
# 版本: 2.0.0 - 统一治理版本

import asyncio
import logging
from typing import Dict, List, Any
from .agent_core import BaseAgent, AgentRole, AgentCapability, AgentConstraint, Task

logger = logging.getLogger(__name__)

# ================================
# 具体Agent实现
# ================================

class HRAgent(BaseAgent):
    """人力资源Agent - 简化版本"""
    
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
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行HR相关任务"""
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
        """分析员工数据"""
        employee_id = data.get('employee_id')
        analysis_type = data.get('analysis_type', 'general')
        
        if task_prompt:
            logger.info(f"Analyzing employee {employee_id} with custom prompt guidance")
        
        # 模拟数据分析过程
        await asyncio.sleep(1)
        
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
    
    async def _screen_resume(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """筛选简历"""
        await asyncio.sleep(1)
        
        return {
            'match_score': 85,
            'matched_skills': ['Python', 'SQL', '项目管理'],
            'missing_skills': ['Kubernetes', '机器学习'],
            'recommendation': 'RECOMMEND',
            'next_steps': ['安排技术面试', '进行背景调查']
        }
    
    async def _query_policy(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """查询政策"""
        policy_topic = data.get('topic')
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

class FinanceAgent(BaseAgent):
    """财务Agent - 简化版本"""
    
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
        return amount < 10000
    
    def _validate_compliance(self, task: Task) -> bool:
        """验证合规性"""
        return 'illegal' not in str(task.data).lower()
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行财务相关任务"""
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
        """生成财务报告"""
        report_type = data.get('report_type', 'monthly')
        department = data.get('department', 'all')
        
        if task_prompt:
            logger.info(f"Generating {report_type} financial report with prompt guidance")
        
        await asyncio.sleep(2)
        
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
    
    async def _analyze_budget(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """分析预算"""
        await asyncio.sleep(1)
        
        return {
            'period': data.get('period', 'Q1'),
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
    
    async def _audit_expenses(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """审计费用"""
        await asyncio.sleep(1)
        
        return {
            'audit_period': data.get('period'),
            'category': data.get('category'),
            'total_expenses': 85000,
            'flagged_items': [
                {'description': '异常差旅费用', 'amount': 5000, 'risk_level': 'medium'}
            ],
            'compliance_score': 95,
            'audit_status': 'PASSED'
        }

class TaskPlannerAgent(BaseAgent):
    """任务规划Agent - 简化版本"""
    
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
        complexity_score = len(str(task.data)) / 100
        return complexity_score < 10
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行任务规划"""
        if task_prompt:
            logger.info(f"Task Planner using custom task prompt for {task.task_type}")
        
        if task.task_type == "task_planning":
            return await self._plan_complex_task(task.data, task_prompt)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _plan_complex_task(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """规划复杂任务"""
        await asyncio.sleep(1)
        
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
            }
        ]
        
        return {
            'original_task': data.get('description'),
            'subtasks': subtasks,
            'total_estimated_time': '6小时',
            'execution_plan': {
                'parallel_tasks': ['task_1'],
                'sequential_tasks': [['task_1'], ['task_2']]
            },
            'resource_requirements': {
                'agents_needed': 2,
                'estimated_cost': 800
            }
        }

class TaskSchedulerAgent(BaseAgent):
    """任务调度Agent - 简化版本"""
    
    def __init__(self, agent_id: str, available_agents: Dict[str, BaseAgent] = None):
        capabilities = [
            AgentCapability("agent_matching", "Agent匹配", 9, ["matching_engine"]),
            AgentCapability("load_balancing", "负载均衡", 8, ["load_balancer"]),
            AgentCapability("performance_monitoring", "性能监控", 7, ["monitoring"])
        ]
        super().__init__(agent_id, AgentRole.SCHEDULER, capabilities)
        self.available_agents = available_agents or {}
    
    def _load_constraints(self) -> List[AgentConstraint]:
        return []
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行任务调度"""
        if task_prompt:
            logger.info(f"Task Scheduler using custom task prompt for {task.task_type}")
        
        if task.task_type == "task_dispatch":
            return await self._dispatch_task(task.data, task_prompt)
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
    
    async def _dispatch_task(self, data: Dict[str, Any], task_prompt: str = None) -> Dict[str, Any]:
        """分发任务"""
        target_task = Task(**data['task'])
        
        # 找到合适的Agent（简化版）
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
        return agent.performance_metrics['tasks_completed'] * 0.1

# 修复datetime导入
from datetime import datetime
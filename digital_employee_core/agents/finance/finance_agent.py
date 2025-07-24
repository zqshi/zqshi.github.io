# Finance Agent实现 - 统一治理版本
# 版本: 2.0.0

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

from ..base import BaseAgent, AgentRole, AgentCapability, AgentConstraint, Task

logger = logging.getLogger(__name__)

class FinanceAgent(BaseAgent):
    """财务Agent - 统一治理版本"""
    
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
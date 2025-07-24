# HR Agent实现 - 统一治理版本
# 版本: 2.0.0

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

from ..base import BaseAgent, AgentRole, AgentCapability, AgentConstraint, Task

logger = logging.getLogger(__name__)

class HRAgent(BaseAgent):
    """人力资源Agent - 统一治理版本"""
    
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
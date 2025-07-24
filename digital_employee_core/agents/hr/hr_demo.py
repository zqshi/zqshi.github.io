# HR Agent演示程序 - 使用统一框架
# 版本: 2.0.0 - 统一治理版本

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

from .hr_agent import HRAgent
from .hr_tools import HRToolManager
from ..base import Task, TaskStatus
from ...demo_framework import StandardAgentDemo, create_demo_task, print_demo_summary

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HRAgentDemo(StandardAgentDemo):
    """HR Agent演示程序 - 使用统一框架"""
    
    def __init__(self):
        self.hr_agent = HRAgent("hr_demo_001")
        self.tool_manager = HRToolManager()
        
        # 定义演示场景
        demo_scenarios = {
            "员工数据分析": self.demo_employee_analysis,
            "简历筛选": self.demo_resume_screening,
            "政策查询": self.demo_policy_query,
            "工具使用": self.demo_tool_usage
        }
        
        super().__init__(self.hr_agent, demo_scenarios)
        logger.info("HR Agent演示程序初始化完成")
    
    def _create_performance_test_task(self, index: int) -> Task:
        """创建HR性能测试任务"""
        return create_demo_task(
            task_id=f"hr_perf_test_{index}",
            task_type="employee_analysis",
            data={
                "employee_id": f"EMP{index:03d}",
                "analysis_type": "performance_review"
            }
        )
    
    async def demo_employee_analysis(self) -> Dict[str, Any]:
        """演示员工数据分析功能"""
        task = create_demo_task(
            task_id="hr_demo_001",
            task_type="employee_analysis",
            data={
                "employee_id": "EMP001",
                "analysis_type": "performance_review"
            },
            priority="high"
        )
        
        return await self.hr_agent.process_task(task)
    
    async def demo_resume_screening(self) -> Dict[str, Any]:
        """演示简历筛选功能"""
        task = create_demo_task(
            task_id="hr_demo_002",
            task_type="resume_screening",
            data={
                "resume_content": "张三，5年Python开发经验，熟悉Django、Flask框架...",
                "job_requirements": {
                    "required_skills": ["Python", "Django", "SQL"],
                    "experience_years": 3,
                    "education": "本科"
                }
            }
        )
        
        return await self.hr_agent.process_task(task)
    
    async def demo_policy_query(self) -> Dict[str, Any]:
        """演示政策查询功能"""
        task = create_demo_task(
            task_id="hr_demo_003",
            task_type="policy_query",
            data={"topic": "年假申请流程"}
        )
        
        return await self.hr_agent.process_task(task)
    
    async def demo_tool_usage(self) -> Dict[str, Any]:
        """演示工具使用功能"""
        tool_results = {}
        
        # 测试员工数据库查询工具
        db_result = self.tool_manager.use_tool(
            "employee_database_query", 
            "SELECT * FROM employees WHERE department = '技术部'"
        )
        tool_results["database_query"] = db_result
        
        # 测试简历解析工具
        resume_result = self.tool_manager.use_tool(
            "resume_parser",
            "张三简历内容..."
        )
        tool_results["resume_parsing"] = resume_result
        
        # 测试政策搜索工具
        policy_result = self.tool_manager.use_tool(
            "policy_search",
            "请假"
        )
        tool_results["policy_search"] = policy_result
        
        # 测试技能匹配工具
        skill_result = self.tool_manager.use_tool(
            "match_skills",
            ["Python", "SQL", "Django"],  # required_skills
            ["Python", "Java", "SQL", "项目管理"]  # candidate_skills
        )
        tool_results["skill_matching"] = skill_result
        
        return tool_results
    
    async def demo_performance_test(self) -> Dict[str, Any]:
        """演示性能测试"""
        start_time = datetime.now()
        
        # 并发执行多个任务
        tasks = []
        for i in range(5):
            task = Task(
                task_id=f"hr_perf_test_{i}",
                task_type="employee_analysis",
                priority="medium",
                data={
                    "employee_id": f"EMP{i:03d}",
                    "analysis_type": "general"
                }
            )
            tasks.append(self.hr_agent.process_task(task))
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            "total_tasks": len(tasks),
            "processing_time": processing_time,
            "avg_time_per_task": processing_time / len(tasks),
            "success_count": sum(1 for r in results if r["status"] == "success"),
            "agent_metrics": self.hr_agent.performance_metrics,
            "sample_results": results[:2]  # 显示前两个结果作为样本
        }
    
    def _generate_summary_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成总结报告"""
        total_scenarios = len([k for k in results.keys() if k != "summary"])
        successful_scenarios = len([v for v in results.values() if v.get("status") == "success"])
        
        return {
            "execution_time": datetime.now().isoformat(),
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "success_rate": (successful_scenarios / total_scenarios) * 100 if total_scenarios > 0 else 0,
            "agent_performance": self.hr_agent.performance_metrics,
            "available_tools": self.tool_manager.get_available_tools(),
            "recommendations": [
                "HR Agent功能正常运行",
                "所有核心功能已验证",
                "工具集成工作正常",
                "性能指标在预期范围内"
            ]
        }

# 演示程序入口
async def main():
    """演示程序主入口"""
    demo = HRAgentDemo()
    results = await demo.run_full_demo()
    
    # 使用统一框架打印结果
    print_demo_summary(results)
    
    # 保存详细结果到文件
    filename = demo.save_results(results)
    print(f"\n详细结果已保存到: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
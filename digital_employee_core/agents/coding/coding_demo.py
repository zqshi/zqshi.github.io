# Coding Agent演示程序 - 使用统一框架
# 版本: 2.0.0 - 统一治理版本

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

from .coding_agent import CodingAgent
from .coding_tools import ProblemType
from ..base import Task, TaskStatus
from ...demo_framework import StandardAgentDemo, create_demo_task, print_demo_summary

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodingAgentDemo(StandardAgentDemo):
    """Coding Agent演示程序 - 使用统一框架"""
    
    def __init__(self):
        self.coding_agent = CodingAgent("coding_demo_001")
        
        # 定义演示场景
        demo_scenarios = {
            "数据处理任务": self.demo_data_processing,
            "API集成任务": self.demo_api_integration,
            "工具创建任务": self.demo_tool_creation,
            "算法设计任务": self.demo_algorithm_design,
            "综合问题解决": self.demo_complex_problem
        }
        
        super().__init__(self.coding_agent, demo_scenarios)
        logger.info("Coding Agent演示程序初始化完成")
    
    def _create_performance_test_task(self, index: int) -> Task:
        """创建Coding性能测试任务"""
        return create_demo_task(
            task_id=f"coding_perf_test_{index}",
            task_type="problem_solving",
            data={
                "problem_description": f"性能测试任务 {index}: 创建一个简单的数据处理函数",
                "context": {"test_index": index},
                "requirements": {"performance_test": True}
            }
        )
    
    async def demo_data_processing(self) -> Dict[str, Any]:
        """演示数据处理功能"""
        task = create_demo_task(
            task_id="coding_demo_data_001",
            task_type="problem_solving",
            data={
                "problem_description": "处理一个包含用户信息的JSON数据，计算平均年龄和统计信息",
                "context": {
                    "sample_data": [
                        {"name": "张三", "age": 25, "city": "北京"},
                        {"name": "李四", "age": 30, "city": "上海"},
                        {"name": "王五", "age": 28, "city": "深圳"}
                    ]
                },
                "requirements": {
                    "output_format": "统计报告",
                    "create_tool": False
                }
            },
            priority="high"
        )
        
        return await self.coding_agent.process_task(task)
    
    async def demo_api_integration(self) -> Dict[str, Any]:
        """演示API集成功能"""
        task = create_demo_task(
            task_id="coding_demo_api_001",
            task_type="problem_solving",
            data={
                "problem_description": "创建一个通用的HTTP API调用工具，支持GET和POST请求",
                "context": {
                    "api_endpoint": "https://httpbin.org/get",
                    "headers": {"User-Agent": "CodingAgent/1.0"}
                },
                "requirements": {
                    "methods": ["GET", "POST"],
                    "error_handling": True,
                    "create_tool": True
                }
            },
            priority="medium"
        )
        
        return await self.coding_agent.process_task(task)
    
    async def demo_tool_creation(self) -> Dict[str, Any]:
        """演示工具创建功能"""
        task = create_demo_task(
            task_id="coding_demo_tool_001", 
            task_type="problem_solving",
            data={
                "problem_description": "创建一个文本处理工具，能够统计文本中的词频和字符数",
                "context": {
                    "sample_text": "这是一个示例文本，用于测试文本处理工具的功能。工具需要能够统计词频。"
                },
                "requirements": {
                    "features": ["词频统计", "字符计数", "去重处理"],
                    "create_tool": True
                }
            }
        )
        
        return await self.coding_agent.process_task(task)
    
    async def demo_algorithm_design(self) -> Dict[str, Any]:
        """演示算法设计功能"""
        task = create_demo_task(
            task_id="coding_demo_algo_001",
            task_type="problem_solving", 
            data={
                "problem_description": "设计并实现一个高效的排序算法，能够处理大量数据",
                "context": {
                    "test_data": [64, 34, 25, 12, 22, 11, 90, 88, 76, 45, 23],
                    "data_size": "medium"
                },
                "requirements": {
                    "algorithm_type": "comparison_based",
                    "time_complexity": "O(n log n)",
                    "include_analysis": True
                }
            }
        )
        
        return await self.coding_agent.process_task(task)
    
    async def demo_complex_problem(self) -> Dict[str, Any]:
        """演示复杂问题解决功能"""
        task = create_demo_task(
            task_id="coding_demo_complex_001",
            task_type="problem_solving",
            data={
                "problem_description": """
                创建一个综合数据处理管道：
                1. 从多个数据源读取数据（JSON、CSV格式）
                2. 清洗和标准化数据格式
                3. 执行数据分析和统计
                4. 生成可视化报告
                5. 输出处理结果
                """,
                "context": {
                    "data_sources": ["user_data.json", "sales_data.csv"],
                    "analysis_type": "comprehensive",
                    "output_formats": ["json", "summary"]
                },
                "requirements": {
                    "pipeline_steps": 5,
                    "error_handling": True,
                    "performance_optimization": True,
                    "create_tool": True
                }
            },
            priority="high"
        )
        
        return await self.coding_agent.process_task(task)

# 演示程序入口
async def main():
    """演示程序主入口"""
    demo = CodingAgentDemo()
    results = await demo.run_full_demo()
    
    # 使用统一框架打印结果
    print_demo_summary(results)
    
    # 显示CodingAgent特有指标
    coding_metrics = demo.coding_agent.coding_metrics
    print(f"\n=== CODING AGENT 专用指标 ===")
    print(f"解决问题数: {coding_metrics['problems_solved']}")
    print(f"创建工具数: {coding_metrics['tools_created']}")
    print(f"代码执行成功率: {coding_metrics['code_execution_success_rate']:.2f}")
    print(f"平均解决时间: {coding_metrics['average_solution_time']:.2f}秒")
    
    # 显示可用工具
    available_tools = demo.coding_agent.tool_manager.get_available_tools()
    if available_tools:
        print(f"\n可用工具: {', '.join(available_tools)}")
    
    # 保存详细结果到文件
    filename = demo.save_results(results)
    print(f"\n详细结果已保存到: {filename}")

if __name__ == "__main__":
    asyncio.run(main())
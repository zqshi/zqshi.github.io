# 统一演示框架
# 版本: 2.0.0 - 统一治理版本

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Type
from abc import ABC, abstractmethod

from .agents.base import BaseAgent, Task, TaskStatus

logger = logging.getLogger(__name__)

class AgentDemoFramework(ABC):
    """统一Agent演示框架基类"""
    
    def __init__(self, agent: BaseAgent, demo_name: str):
        self.agent = agent
        self.demo_name = demo_name
        self.demo_results = []
        self.start_time = None
        self.end_time = None
        logger.info(f"{demo_name}演示框架初始化完成")
    
    async def run_full_demo(self) -> Dict[str, Any]:
        """运行完整演示"""
        self.start_time = datetime.now()
        logger.info(f"开始运行{self.demo_name}完整演示")
        
        results = {
            "demo_info": {
                "name": self.demo_name,
                "agent_id": self.agent.agent_id,
                "agent_role": self.agent.role.value,
                "start_time": self.start_time.isoformat()
            },
            "scenarios": {},
            "performance": {},
            "summary": {}
        }
        
        try:
            # 执行标准演示场景
            scenarios = await self._run_demo_scenarios()
            results["scenarios"] = scenarios
            
            # 执行性能测试
            performance = await self._run_performance_test()
            results["performance"] = performance
            
            # 生成总结报告
            self.end_time = datetime.now()
            summary = self._generate_summary(results)
            results["summary"] = summary
            
            logger.info(f"{self.demo_name}演示执行完成")
            
        except Exception as e:
            logger.error(f"{self.demo_name}演示执行失败: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    @abstractmethod
    async def _run_demo_scenarios(self) -> Dict[str, Any]:
        """运行演示场景 - 子类需要实现"""
        pass
    
    async def _run_performance_test(self) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info(f"开始{self.demo_name}性能测试")
        
        start_time = time.time()
        
        # 并发执行多个标准任务
        tasks = []
        for i in range(5):
            task = self._create_performance_test_task(i)
            tasks.append(self.agent.process_task(task))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 统计结果
        successful_tasks = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        failed_tasks = len(results) - successful_tasks
        
        return {
            "total_tasks": len(tasks),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (successful_tasks / len(tasks)) * 100,
            "total_processing_time": processing_time,
            "avg_time_per_task": processing_time / len(tasks),
            "agent_metrics": self.agent.performance_metrics.copy(),
            "sample_results": [r for r in results[:2] if isinstance(r, dict)]
        }
    
    @abstractmethod
    def _create_performance_test_task(self, index: int) -> Task:
        """创建性能测试任务 - 子类需要实现"""
        pass
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成总结报告"""
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # 统计场景执行情况
        scenarios = results.get("scenarios", {})
        total_scenarios = len(scenarios)
        successful_scenarios = sum(1 for s in scenarios.values() if s.get("status") == "success")
        
        # 性能统计
        performance = results.get("performance", {})
        
        return {
            "execution_time": self.end_time.isoformat(),
            "total_duration": total_duration,
            "scenario_stats": {
                "total": total_scenarios,
                "successful": successful_scenarios,
                "success_rate": (successful_scenarios / total_scenarios) * 100 if total_scenarios > 0 else 0
            },
            "performance_stats": {
                "tasks_processed": performance.get("total_tasks", 0),
                "performance_success_rate": performance.get("success_rate", 0),
                "avg_processing_time": performance.get("avg_time_per_task", 0)
            },
            "agent_final_metrics": self.agent.performance_metrics.copy(),
            "recommendations": self._generate_recommendations(results)
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于成功率的建议
        scenario_success_rate = results.get("summary", {}).get("scenario_stats", {}).get("success_rate", 0)
        if scenario_success_rate >= 90:
            recommendations.append(f"{self.demo_name}功能运行良好，所有核心功能正常")
        elif scenario_success_rate >= 70:
            recommendations.append(f"{self.demo_name}基本功能正常，部分场景需要优化")
        else:
            recommendations.append(f"{self.demo_name}存在较多问题，需要重点关注和修复")
        
        # 基于性能的建议
        perf_success_rate = results.get("performance", {}).get("success_rate", 0)
        avg_time = results.get("performance", {}).get("avg_time_per_task", 0)
        
        if perf_success_rate >= 95:
            recommendations.append("性能测试表现优秀，稳定性良好")
        elif perf_success_rate >= 80:
            recommendations.append("性能表现良好，建议持续监控")
        else:
            recommendations.append("性能存在问题，需要优化处理逻辑")
        
        if avg_time <= 1.0:
            recommendations.append("响应时间优秀")
        elif avg_time <= 3.0:
            recommendations.append("响应时间在可接受范围内")
        else:
            recommendations.append("响应时间较长，建议优化处理效率")
        
        return recommendations
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存演示结果到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.demo_name.lower()}_demo_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"演示结果已保存到: {filename}")
        return filename

class StandardAgentDemo(AgentDemoFramework):
    """标准Agent演示实现"""
    
    def __init__(self, agent: BaseAgent, demo_scenarios: Dict[str, callable]):
        super().__init__(agent, f"{agent.role.value.upper()}_Agent")
        self.demo_scenarios = demo_scenarios
    
    async def _run_demo_scenarios(self) -> Dict[str, Any]:
        """运行预定义的演示场景"""
        results = {}
        
        for scenario_name, scenario_func in self.demo_scenarios.items():
            logger.info(f"执行演示场景: {scenario_name}")
            try:
                result = await scenario_func()
                results[scenario_name] = {
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"场景 '{scenario_name}' 执行成功")
            except Exception as e:
                logger.error(f"场景 '{scenario_name}' 执行失败: {str(e)}")
                results[scenario_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def _create_performance_test_task(self, index: int) -> Task:
        """创建标准性能测试任务"""
        return Task(
            task_id=f"perf_test_{self.agent.agent_id}_{index}",
            task_type="performance_test",
            priority="medium",
            data={
                "test_index": index,
                "test_data": f"Performance test data {index}"
            }
        )

# 演示工具函数
def create_demo_task(task_id: str, task_type: str, data: Dict[str, Any], priority: str = "medium") -> Task:
    """创建演示任务的便捷函数"""
    return Task(
        task_id=task_id,
        task_type=task_type,
        priority=priority,
        data=data
    )

def print_demo_summary(results: Dict[str, Any]):
    """打印演示结果摘要"""
    print("\n" + "="*60)
    print(f"{results.get('demo_info', {}).get('name', 'AGENT')} 演示程序执行结果")
    print("="*60)
    
    # 基本信息
    demo_info = results.get("demo_info", {})
    print(f"\nAgent ID: {demo_info.get('agent_id', 'N/A')}")  
    print(f"Agent 角色: {demo_info.get('agent_role', 'N/A')}")
    print(f"开始时间: {demo_info.get('start_time', 'N/A')}")
    
    # 场景统计
    summary = results.get("summary", {})
    scenario_stats = summary.get("scenario_stats", {})
    print(f"\n场景执行统计:")
    print(f"  总场景数: {scenario_stats.get('total', 0)}")
    print(f"  成功场景数: {scenario_stats.get('successful', 0)}")
    print(f"  成功率: {scenario_stats.get('success_rate', 0):.1f}%")
    
    # 性能统计
    perf_stats = summary.get("performance_stats", {})
    print(f"\n性能测试统计:")
    print(f"  处理任务数: {perf_stats.get('tasks_processed', 0)}")
    print(f"  性能成功率: {perf_stats.get('performance_success_rate', 0):.1f}%")
    print(f"  平均处理时间: {perf_stats.get('avg_processing_time', 0):.2f}秒")
    
    # Agent指标
    agent_metrics = summary.get("agent_final_metrics", {})
    print(f"\nAgent最终指标:")
    print(f"  完成任务数: {agent_metrics.get('tasks_completed', 0)}")
    print(f"  成功率: {agent_metrics.get('success_rate', 0):.2f}")
    print(f"  平均响应时间: {agent_metrics.get('avg_response_time', 0):.2f}秒")
    
    # 建议
    recommendations = summary.get("recommendations", [])
    if recommendations:
        print(f"\n建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    print(f"\n总执行时间: {summary.get('total_duration', 0):.2f}秒")
    print("="*60)
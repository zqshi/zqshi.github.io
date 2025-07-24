"""
CodingAgent演示和测试

展示CodingAgent的核心功能：
1. 数据处理问题解决
2. API集成解决方案
3. 自定义工具创建
4. 算法问题解决
5. 复杂系统集成
6. 与其他Agent的协作

版本: 1.0.0
作者: Digital Employee System Team
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any
import traceback

from .coding_agent_main import CodingAgent
from .agent_integration import (
    create_integrated_agent_system, 
    solve_with_coding_agent,
    EscalationReason
)
from .agent_core import Task, TaskStatus
from .coding_agent import ProblemType

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodingAgentDemo:
    """CodingAgent演示类"""
    
    def __init__(self):
        self.coding_agent = CodingAgent("demo_coding_agent")
        self.test_results = []
        self.demo_scenarios = self._prepare_demo_scenarios()
    
    def _prepare_demo_scenarios(self) -> List[Dict[str, Any]]:
        """准备演示场景"""
        return [
            {
                "name": "数据处理场景",
                "description": "处理CSV数据并生成统计报告",
                "problem_description": "我有一批销售数据，需要计算总销售额、平均订单金额、最佳销售月份",
                "context": {
                    "sample_data": [
                        {"date": "2024-01-15", "amount": 1500, "product": "A"},
                        {"date": "2024-02-20", "amount": 2300, "product": "B"},
                        {"date": "2024-03-10", "amount": 1800, "product": "A"},
                        {"date": "2024-01-25", "amount": 2100, "product": "C"}
                    ]
                },
                "requirements": {
                    "output_format": "json",
                    "create_tool": True,
                    "timeout": 15.0
                },
                "expected_type": ProblemType.DATA_PROCESSING
            },
            {
                "name": "API集成场景", 
                "description": "调用天气API获取多城市天气信息",
                "problem_description": "需要调用天气API获取北京、上海、深圳的当前天气，并格式化输出",
                "context": {
                    "api_url": "https://api.openweathermap.org/data/2.5/weather",
                    "cities": ["Beijing", "Shanghai", "Shenzhen"],
                    "api_key": "demo_key_12345"
                },
                "requirements": {
                    "method": "GET",
                    "format_output": True,
                    "timeout": 20.0
                },
                "expected_type": ProblemType.API_INTEGRATION
            },
            {
                "name": "工具创建场景",
                "description": "创建文本分析工具",
                "problem_description": "创建一个工具函数，能够分析文本的词频、句子数量、平均词长等统计信息",
                "context": {
                    "sample_text": "这是一个示例文本。它包含多个句子和不同的词汇。我们需要分析这些内容。"
                },
                "requirements": {
                    "tool_name": "text_analyzer",
                    "create_tool": True,
                    "include_tests": True,
                    "timeout": 10.0
                },
                "expected_type": ProblemType.TOOL_CREATION
            },
            {
                "name": "算法设计场景",
                "description": "实现快速排序算法",
                "problem_description": "实现一个快速排序算法，能够对数字列表进行排序，并返回排序过程的步骤信息",
                "context": {
                    "test_data": [64, 34, 25, 12, 22, 11, 90, 5]
                },
                "requirements": {
                    "show_steps": True,
                    "include_complexity_analysis": True,
                    "timeout": 15.0
                },
                "expected_type": ProblemType.ALGORITHM_DESIGN
            },
            {
                "name": "系统集成场景",
                "description": "数据库连接和数据同步",
                "problem_description": "创建一个数据同步工具，能够从一个数据源读取数据并写入到另一个数据源",
                "context": {
                    "source_type": "json",
                    "target_type": "csv",
                    "data_mapping": {
                        "id": "ID",
                        "name": "姓名", 
                        "email": "邮箱"
                    }
                },
                "requirements": {
                    "validate_data": True,
                    "create_tool": True,
                    "timeout": 25.0
                },
                "expected_type": ProblemType.SYSTEM_INTEGRATION
            },
            {
                "name": "复杂调试场景",
                "description": "调试性能问题",
                "problem_description": "有一个数据处理脚本运行很慢，需要分析性能瓶颈并提供优化建议",
                "context": {
                    "slow_code": '''
def slow_function(data):
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] > data[j]:
                result.append((data[i], data[j]))
    return result
''',
                    "test_data_size": 1000
                },
                "requirements": {
                    "analyze_complexity": True,
                    "provide_optimized_version": True,
                    "timeout": 20.0
                },
                "expected_type": ProblemType.DEBUGGING
            }
        ]
    
    async def run_complete_demo(self):
        """运行完整演示"""
        print("="*80)
        print("🤖 CodingAgent 完整功能演示")
        print("="*80)
        
        # 1. 系统初始化演示
        print("\n1. 🔧 系统初始化")
        await self._demo_system_initialization()
        
        # 2. 核心功能演示
        print("\n2. 🧠 核心功能演示")
        await self._demo_core_capabilities()
        
        # 3. 场景测试
        print("\n3. 🎯 场景测试")
        await self._demo_scenarios()
        
        # 4. Agent集成演示
        print("\n4. 🔗 Agent集成演示")
        await self._demo_agent_integration()
        
        # 5. 性能分析
        print("\n5. 📊 性能分析")
        self._demo_performance_analysis()
        
        # 6. 总结报告
        print("\n6. 📋 总结报告")
        self._generate_demo_report()
        
        print("\n" + "="*80)
        print("🎉 CodingAgent演示完成！")
        print("="*80)
    
    async def _demo_system_initialization(self):
        """演示系统初始化"""
        print("初始化CodingAgent...")
        
        # 显示Agent能力
        capabilities = [cap.name for cap in self.coding_agent.capabilities]
        print(f"✓ Agent能力: {', '.join(capabilities)}")
        
        # 显示核心组件
        components = {
            "代码执行器": "SecureCodeExecutor",
            "工具管理器": "DynamicToolManager", 
            "问题分析器": "ProblemAnalyzer"
        }
        
        for comp_name, comp_class in components.items():
            print(f"✓ {comp_name}: {comp_class}")
        
        print(f"✓ 安全沙箱: 已启用")
        print(f"✓ 动态工具创建: 已支持")
        print(f"✓ 性能监控: 已启用")
    
    async def _demo_core_capabilities(self):
        """演示核心能力"""
        core_demos = [
            {
                "name": "代码安全验证",
                "demo_func": self._demo_security_validation
            },
            {
                "name": "代码执行环境",
                "demo_func": self._demo_code_execution
            },
            {
                "name": "工具动态创建",
                "demo_func": self._demo_tool_creation
            },
            {
                "name": "问题分析能力",
                "demo_func": self._demo_problem_analysis
            }
        ]
        
        for demo in core_demos:
            print(f"\n📌 {demo['name']}:")
            try:
                await demo["demo_func"]()
                print(f"✅ {demo['name']} 演示成功")
            except Exception as e:
                print(f"❌ {demo['name']} 演示失败: {str(e)}")
    
    async def _demo_security_validation(self):
        """演示安全验证"""
        dangerous_codes = [
            "import os; os.system('rm -rf /')",
            "exec('malicious_code')",
            "open('/etc/passwd', 'r')",
            "__import__('subprocess').call(['ls', '-la'])"
        ]
        
        for code in dangerous_codes:
            from .coding_agent import CodeExecutionContext
            context = CodeExecutionContext(
                execution_id="security_test",
                code=code
            )
            
            security_check = self.coding_agent.code_executor.validate_code_security(code, context)
            
            print(f"  代码: {code[:30]}...")
            print(f"  安全: {'❌ 危险' if not security_check['is_safe'] else '✅ 安全'}")
            if not security_check['is_safe']:
                print(f"  问题: {security_check['issues'][0]}")
    
    async def _demo_code_execution(self):
        """演示代码执行"""
        safe_code = '''
import json
import math

def calculate_circle_area(radius):
    """计算圆的面积"""
    if radius <= 0:
        return {"error": "半径必须大于0"}
    
    area = math.pi * radius ** 2
    return {
        "radius": radius,
        "area": round(area, 2),
        "circumference": round(2 * math.pi * radius, 2)
    }

# 测试函数
result = calculate_circle_area(5)
print(json.dumps(result, indent=2, ensure_ascii=False))
'''
        
        from .coding_agent import CodeExecutionContext
        context = CodeExecutionContext(
            execution_id="demo_execution",
            code=safe_code,
            timeout=5.0
        )
        
        result = self.coding_agent.code_executor.execute_code(context)
        
        print(f"  执行状态: {result['status'].value}")
        print(f"  执行时间: {result['execution_time']:.3f}s")
        print(f"  内存使用: {result['memory_usage']}MB")
        if result['output']:
            print(f"  输出预览: {result['output'][:100]}...")
    
    async def _demo_tool_creation(self):
        """演示工具创建"""
        from .coding_agent import ToolDefinition
        
        tool_code = '''
def string_utilities(text, operation="analyze"):
    """字符串工具函数"""
    if operation == "analyze":
        return {
            "length": len(text),
            "words": len(text.split()),
            "chars": len(text.replace(" ", "")),
            "sentences": text.count(".") + text.count("!") + text.count("?")
        }
    elif operation == "reverse":
        return text[::-1]
    elif operation == "upper":
        return text.upper()
    else:
        return {"error": "不支持的操作"}

# 测试工具
test_result = string_utilities("Hello World! This is a test.", "analyze")
print(f"分析结果: {test_result}")
'''
        
        tool_def = ToolDefinition(
            tool_id="demo_string_tool",
            name="字符串工具",
            description="用于字符串分析和处理的工具",
            function_code=tool_code,
            parameters={"text": "str", "operation": "str"},
            return_type="Dict[str, Any]",
            created_at=time.time(),
            test_cases=[
                {
                    "function": "string_utilities",
                    "args": ["Hello World", "analyze"],
                    "kwargs": {},
                    "expected": None
                }
            ]
        )
        
        creation_result = self.coding_agent.tool_manager.create_tool_from_code(tool_def)
        
        print(f"  工具创建: {'✅ 成功' if creation_result['success'] else '❌ 失败'}")
        if creation_result['success']:
            print(f"  工具ID: {creation_result['tool_id']}")
            print(f"  函数数量: {len(creation_result['functions'])}")
            print(f"  测试结果: {len(creation_result['test_results'])} 个测试")
    
    async def _demo_problem_analysis(self):
        """演示问题分析"""
        test_problems = [
            "我需要处理一个CSV文件，计算销售数据的统计信息",
            "帮我调用一个REST API获取用户信息",
            "创建一个算法来排序大量数据",
            "需要调试一个性能很慢的Python函数"
        ]
        
        for problem in test_problems:
            analysis = self.coding_agent.problem_analyzer.analyze_problem(problem)
            
            print(f"  问题: {problem[:40]}...")
            print(f"  类型: {analysis['primary_type'].value}")
            print(f"  复杂度: {analysis['complexity']}")
            print(f"  预计时间: {analysis['estimated_effort']['estimated_time_minutes']}分钟")
    
    async def _demo_scenarios(self):
        """演示各种场景"""
        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"\n🎯 场景 {i}: {scenario['name']}")
            print(f"描述: {scenario['description']}")
            
            try:
                start_time = time.time()
                
                # 创建任务
                task = Task(
                    task_id=f"demo_scenario_{i}",
                    task_type="demo_task",
                    priority="normal",
                    data=scenario
                )
                
                # 执行任务
                result = await self.coding_agent._execute_task(task)
                
                execution_time = time.time() - start_time
                
                # 记录结果
                test_result = {
                    "scenario": scenario['name'],
                    "status": result.get("status", "unknown"),
                    "execution_time": execution_time,
                    "confidence": result.get("confidence", 0),
                    "created_tools": result.get("created_tools", 0),
                    "problem_type": scenario.get("expected_type", "unknown")
                }
                
                self.test_results.append(test_result)
                
                # 显示结果
                print(f"✅ 执行状态: {result.get('status', 'unknown')}")
                print(f"⏱️  执行时间: {execution_time:.2f}s")
                print(f"🎯 置信度: {result.get('confidence', 0):.2f}")
                
                if result.get("solution"):
                    solution = result["solution"]
                    print(f"🔧 创建工具: {len(solution.created_tools)} 个")
                    print(f"📊 内存使用: {solution.memory_usage}MB")
                
            except Exception as e:
                print(f"❌ 场景执行失败: {str(e)}")
                logger.error(f"场景 {scenario['name']} 执行失败", exc_info=True)
    
    async def _demo_agent_integration(self):
        """演示Agent集成"""
        print("创建集成Agent系统...")
        
        integrated_system = create_integrated_agent_system()
        scheduler = integrated_system["scheduler"]
        
        print(f"✓ 系统组件: {len(integrated_system)} 个")
        print(f"✓ 调度器: {type(scheduler).__name__}")
        print(f"✓ CodingAgent: {integrated_system['coding_agent'].agent_id}")
        
        # 演示任务路由
        test_tasks = [
            {
                "description": "这是一个简单的HR查询任务",
                "task_type": "hr_query",
                "expected_agent": "非CodingAgent"
            },
            {
                "description": "需要编写Python脚本处理数据文件",
                "task_type": "coding_task", 
                "expected_agent": "CodingAgent"
            },
            {
                "description": "超复杂的系统集成问题，需要自定义算法",
                "task_type": "complex_integration",
                "expected_agent": "CodingAgent"
            }
        ]
        
        for i, task_data in enumerate(test_tasks):
            print(f"\n📋 任务 {i+1}: {task_data['description'][:40]}...")
            
            # 创建任务
            task = Task(
                task_id=f"integration_test_{i}",
                task_type=task_data["task_type"],
                priority="normal",
                data={"description": task_data["description"]}
            )
            
            # 分析任务需求
            analysis = scheduler._analyze_task_requirements(task)
            print(f"   分析结果: 复杂度={analysis['estimated_complexity']}, 需要编程={analysis['needs_coding']}")
            
            # 选择Agent
            selected_agent = scheduler._select_best_agent(analysis)
            agent_type = "CodingAgent" if isinstance(selected_agent, CodingAgent) else "其他Agent"
            
            print(f"   分配给: {agent_type}")
            print(f"   预期: {task_data['expected_agent']}")
            print(f"   匹配: {'✅' if ('CodingAgent' in task_data['expected_agent']) == isinstance(selected_agent, CodingAgent) else '⚠️'}")
    
    def _demo_performance_analysis(self):
        """演示性能分析"""
        print("分析CodingAgent性能数据...")
        
        performance_report = self.coding_agent.get_performance_report()
        
        print(f"📊 性能统计:")
        stats = performance_report["performance_stats"]
        print(f"   总解决问题数: {stats['total_problems_solved']}")
        print(f"   成功解决数: {stats['successful_solutions']}")
        print(f"   失败数: {stats['failed_solutions']}")
        print(f"   平均解决时间: {stats['average_solution_time']:.2f}s")
        print(f"   创建工具数: {stats['created_tools_count']}")
        
        success_rate = performance_report.get("success_rate", 0)
        print(f"   成功率: {success_rate:.1%}")
        
        # 分析测试结果
        if self.test_results:
            print(f"\n📈 测试结果分析:")
            total_tests = len(self.test_results)
            successful_tests = len([r for r in self.test_results if r["status"] == "success"])
            
            print(f"   总测试数: {total_tests}")
            print(f"   成功测试: {successful_tests}")
            print(f"   成功率: {successful_tests/total_tests:.1%}")
            
            avg_time = sum(r["execution_time"] for r in self.test_results) / total_tests
            avg_confidence = sum(r["confidence"] for r in self.test_results) / total_tests
            
            print(f"   平均执行时间: {avg_time:.2f}s")
            print(f"   平均置信度: {avg_confidence:.2f}")
    
    def _generate_demo_report(self):
        """生成演示报告"""
        print("生成完整演示报告...")
        
        report = {
            "demo_info": {
                "name": "CodingAgent完整功能演示",
                "version": "1.0.0",
                "timestamp": time.time(),
                "total_scenarios": len(self.demo_scenarios)
            },
            "agent_info": {
                "agent_id": self.coding_agent.agent_id,
                "capabilities": len(self.coding_agent.capabilities),
                "tools_created": len(self.coding_agent.tool_manager.tools_registry)
            },
            "test_results": self.test_results,
            "performance": self.coding_agent.get_performance_report(),
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": len([r for r in self.test_results if r["status"] == "success"]),
                "demo_duration": "完整演示",
                "key_features_demonstrated": [
                    "安全代码执行",
                    "动态工具创建", 
                    "问题智能分析",
                    "多场景解决方案",
                    "Agent系统集成",
                    "性能监控分析"
                ]
            }
        }
        
        print(f"📋 演示报告:")
        print(f"   演示场景: {report['demo_info']['total_scenarios']} 个")
        print(f"   Agent能力: {report['agent_info']['capabilities']} 项")
        print(f"   创建工具: {report['agent_info']['tools_created']} 个")
        print(f"   测试执行: {report['summary']['total_tests']} 个")
        print(f"   成功测试: {report['summary']['successful_tests']} 个")
        
        # 保存报告到Agent历史
        self.demo_report = report
        
        print(f"✅ 演示报告已生成并保存")

# ================================
# 简化演示函数
# ================================

async def run_quick_demo():
    """运行快速演示"""
    print("🚀 CodingAgent 快速演示")
    print("-" * 40)
    
    # 简单问题解决演示
    result = await solve_with_coding_agent(
        "计算1到100的质数，并返回质数列表和统计信息",
        context={"range_start": 1, "range_end": 100},
        requirements={"include_stats": True, "timeout": 10.0}
    )
    
    print(f"问题: {result['problem']}")
    print(f"任务ID: {result['task_id']}")
    
    solution = result['solution']
    print(f"解决状态: {solution.get('status', 'unknown')}")
    print(f"置信度: {solution.get('confidence', 0):.2f}")
    
    if solution.get('solution'):
        sol_info = solution['solution']
        print(f"执行时间: {sol_info.execution_time:.2f}s")
        print(f"创建工具: {len(sol_info.created_tools)} 个")
    
    performance = result['agent_performance']
    print(f"Agent成功率: {performance['success_rate']:.1%}")
    
    print("✅ 快速演示完成")

async def test_coding_agent_basic():
    """基础功能测试"""
    print("🧪 CodingAgent 基础功能测试")
    print("-" * 40)
    
    coding_agent = CodingAgent("test_agent")
    
    # 测试1: 简单数学计算
    task1 = Task(
        task_id="test_math",
        task_type="math_calculation",
        priority="normal",
        data={
            "problem_description": "计算斐波那契数列的前20项",
            "context": {"count": 20},
            "requirements": {"timeout": 5.0}
        }
    )
    
    result1 = await coding_agent._execute_task(task1)
    print(f"数学计算测试: {result1.get('status', 'unknown')}")
    
    # 测试2: 数据处理
    task2 = Task(
        task_id="test_data",
        task_type="data_processing", 
        priority="normal",
        data={
            "problem_description": "分析学生成绩数据，计算平均分、最高分、最低分",
            "context": {
                "sample_data": [85, 92, 78, 96, 88, 75, 91, 83]
            },
            "requirements": {"create_tool": True, "timeout": 8.0}
        }
    )
    
    result2 = await coding_agent._execute_task(task2)
    print(f"数据处理测试: {result2.get('status', 'unknown')}")
    
    # 显示性能报告
    performance = coding_agent.get_performance_report()
    print(f"测试完成 - 成功率: {performance['success_rate']:.1%}")

# ================================
# 主演示入口
# ================================

async def main():
    """主演示函数"""
    print("选择演示模式:")
    print("1. 完整功能演示 (约5-10分钟)")
    print("2. 快速演示 (约1分钟)")
    print("3. 基础功能测试 (约30秒)")
    
    try:
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            demo = CodingAgentDemo()
            await demo.run_complete_demo()
        elif choice == "2":
            await run_quick_demo()
        elif choice == "3":
            await test_coding_agent_basic()
        else:
            print("无效选择，运行快速演示...")
            await run_quick_demo()
            
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"演示执行错误: {e}")
        logger.error("演示执行失败", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
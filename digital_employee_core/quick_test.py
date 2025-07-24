"""
数字员工系统 - 快速功能验证脚本
验证Prompt系统和Agent基础功能
"""

import asyncio
import sys
import traceback
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append('.')

async def test_prompt_system():
    """测试Prompt管理系统"""
    print("=" * 60)
    print("[PROMPT] 测试 Prompt 管理系统")
    print("=" * 60)
    
    try:
        from prompt_manager import PromptManager
        
        pm = PromptManager()
        
        # 1. 测试版本信息
        print("1. 检查版本信息...")
        version_info = pm.get_version_info()
        print(f"   当前版本: {version_info['version']}")
        print(f"   最后更新: {version_info['last_updated']}")
        
        # 2. 测试系统验证
        print("\n2. 验证系统完整性...")
        validation = pm.validate_prompts()
        
        error_count = len(validation['errors'])
        warning_count = len(validation['warnings'])
        
        if error_count == 0:
            print("   [OK] 系统验证通过")
        else:
            print(f"   [ERROR] 发现 {error_count} 个错误:")
            for error in validation['errors']:
                print(f"      - {error}")
        
        if warning_count > 0:
            print(f"   [WARNING] {warning_count} 个警告:")
            for warning in validation['warnings']:
                print(f"      - {warning}")
        
        # 3. 测试Prompt生成
        print("\n3. 测试Agent Prompt生成...")
        
        test_agents = ["hr_agent", "finance_agent"]
        for agent_type in test_agents:
            try:
                prompt = pm.create_agent_prompt(f"test_{agent_type}", agent_type)
                print(f"   [OK] {agent_type}: {len(prompt)} 字符")
            except Exception as e:
                print(f"   [ERROR] {agent_type}: {str(e)}")
        
        # 4. 测试任务Prompt生成
        print("\n4. 测试任务Prompt生成...")
        
        task_data = {
            "employee_id": "TEST001",
            "analysis_type": "performance"
        }
        
        try:
            task_prompt = pm.create_task_prompt("hr_agent", "employee_analysis", task_data)
            print(f"   [OK] 任务Prompt生成成功: {len(task_prompt)} 字符")
        except Exception as e:
            print(f"   [ERROR] 任务Prompt生成失败: {str(e)}")
        
        return error_count == 0
        
    except Exception as e:
        print(f"[ERROR] Prompt系统测试失败: {str(e)}")
        traceback.print_exc()
        return False


async def test_agent_system():
    """测试Agent系统"""
    print("\n" + "=" * 60)
    print("[AGENT] 测试 Agent 系统")
    print("=" * 60)
    
    try:
        from agent_implementations import HRAgent, FinanceAgent, Task, TaskStatus
        
        # 1. 测试Agent初始化
        print("1. 测试Agent初始化...")
        
        try:
            hr_agent = HRAgent("test_hr")
            print("   [OK] HR Agent 初始化成功")
            print(f"      - Agent ID: {hr_agent.agent_id}")
            print(f"      - 角色: {hr_agent.role.value}")
            print(f"      - Prompt长度: {len(hr_agent.system_prompt)} 字符")
        except Exception as e:
            print(f"   [ERROR] HR Agent 初始化失败: {str(e)}")
            return False
        
        try:
            finance_agent = FinanceAgent("test_finance")
            print("   [OK] Finance Agent 初始化成功")
            print(f"      - Agent ID: {finance_agent.agent_id}")
            print(f"      - 角色: {finance_agent.role.value}")
        except Exception as e:
            print(f"   [ERROR] Finance Agent 初始化失败: {str(e)}")
            return False
        
        # 2. 测试任务处理
        print("\n2. 测试任务处理...")
        
        # 创建测试任务
        test_task = Task(
            task_id="test_001",
            task_type="employee_analysis",
            priority="high",
            data={
                "employee_id": "EMP001",
                "analysis_type": "performance_review"
            }
        )
        
        print(f"   创建测试任务: {test_task.task_id}")
        print(f"   任务类型: {test_task.task_type}")
        
        # 执行任务
        try:
            print("   执行HR任务...")
            start_time = datetime.now()
            result = await hr_agent.process_task(test_task)
            end_time = datetime.now()
            
            if result['status'] == 'success':
                print(f"   [OK] 任务执行成功 (耗时: {(end_time - start_time).total_seconds():.2f}s)")
                print(f"      - Prompt版本: {result.get('prompt_version', 'N/A')}")
                print(f"      - 结果包含: {list(result['result'].keys())}")
                
                # 检查结果内容
                task_result = result['result']
                if 'performance_score' in task_result:
                    print(f"      - 绩效评分: {task_result['performance_score']}")
                if 'recommendations' in task_result:
                    print(f"      - 建议数量: {len(task_result['recommendations'])}")
                    
            else:
                print(f"   [ERROR] 任务执行失败: {result.get('error', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"   [ERROR] 任务执行异常: {str(e)}")
            traceback.print_exc()
            return False
        
        # 3. 测试财务Agent
        print("\n3. 测试财务Agent...")
        
        finance_task = Task(
            task_id="test_002",
            task_type="financial_report",
            priority="high",
            data={
                "report_type": "monthly",
                "period": "2024-03",
                "department": "all"
            }
        )
        
        try:
            print("   执行财务任务...")
            result = await finance_agent.process_task(finance_task)
            
            if result['status'] == 'success':
                print("   [OK] 财务任务执行成功")
                task_result = result['result']
                if 'total_revenue' in task_result:
                    print(f"      - 总收入: {task_result['total_revenue']}")
                if 'profit_margin' in task_result:
                    print(f"      - 利润率: {task_result['profit_margin']}%")
            else:
                print(f"   [ERROR] 财务任务执行失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"   [ERROR] 财务任务执行异常: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Agent系统测试失败: {str(e)}")
        traceback.print_exc()
        return False


async def test_integration():
    """测试系统集成"""
    print("\n" + "=" * 60)
    print("[INTEGRATION] 测试系统集成")
    print("=" * 60)
    
    try:
        from test_framework import NaturalLanguageTestFramework
        
        # 创建测试框架
        framework = NaturalLanguageTestFramework()
        
        # 测试框架初始化
        print("1. 测试框架初始化...")
        if framework.agents:
            print(f"   [OK] 初始化了 {len(framework.agents)} 个测试Agent")
            for agent_id in framework.agents:
                print(f"      - {agent_id}")
        else:
            print("   [WARNING] 没有可用的测试Agent")
        
        # 测试用例定义
        print("\n2. 检查测试用例...")
        test_cases = framework.define_test_cases()
        print(f"   [OK] 定义了 {len(test_cases)} 个测试用例")
        
        for tc in test_cases[:3]:  # 只显示前3个
            print(f"      - {tc.id}: {tc.name}")
        
        if len(test_cases) > 3:
            print(f"      ... 还有 {len(test_cases) - 3} 个测试用例")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 集成测试失败: {str(e)}")
        traceback.print_exc()
        return False


async def run_sample_test():
    """运行示例测试"""
    print("\n" + "=" * 60)
    print("[SAMPLE] 运行示例测试")
    print("=" * 60)
    
    try:
        from test_framework import NaturalLanguageTestFramework, TestCase
        
        framework = NaturalLanguageTestFramework()
        
        # 创建一个简单的测试用例
        sample_test = TestCase(
            id="sample_001",
            name="HR员工分析示例",
            description="测试HR Agent分析员工绩效的基础功能",
            agent_type="hr_agent",
            input_data={
                "task_type": "employee_analysis",
                "priority": "high",
                "data": {
                    "employee_id": "SAMPLE001",
                    "analysis_type": "basic_review"
                }
            },
            expected_behavior="返回员工分析结果，包含评分和建议",
            success_criteria=[
                "返回结构化的分析结果",
                "包含绩效评分",
                "提供具体的改进建议"
            ]
        )
        
        print(f"执行测试: {sample_test.name}")
        print(f"描述: {sample_test.description}")
        
        # 执行测试
        result = await framework.run_single_test(sample_test)
        
        if result.success:
            print(f"[OK] 测试通过! (耗时: {result.execution_time:.2f}s)")
            print(f"实际行为: {result.actual_behavior}")
        else:
            print(f"[ERROR] 测试失败! (耗时: {result.execution_time:.2f}s)")
            if result.error_message:
                print(f"错误信息: {result.error_message}")
        
        return result.success
        
    except Exception as e:
        print(f"[ERROR] 示例测试失败: {str(e)}")
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("[TEST] 数字员工系统 - 快速功能验证")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行各项测试
    tests_passed = 0
    total_tests = 4
    
    # 1. Prompt系统测试
    if await test_prompt_system():
        tests_passed += 1
    
    # 2. Agent系统测试
    if await test_agent_system():
        tests_passed += 1
    
    # 3. 集成测试
    if await test_integration():
        tests_passed += 1
    
    # 4. 示例测试
    if await run_sample_test():
        tests_passed += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("[SUMMARY] 验证总结")
    print("=" * 60)
    print(f"总计测试: {total_tests}")
    print(f"通过测试: {tests_passed}")
    print(f"失败测试: {total_tests - tests_passed}")
    print(f"通过率: {(tests_passed / total_tests) * 100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n[SUCCESS] 所有测试通过！系统功能正常！")
        return True
    else:
        print(f"\n[WARNING] {total_tests - tests_passed} 个测试失败，请检查系统配置")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INFO] 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 测试过程中发生未处理异常: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
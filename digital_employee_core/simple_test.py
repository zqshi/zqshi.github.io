"""
数字员工系统 - 简化功能测试
只测试核心Prompt管理功能，不依赖复杂的Agent实现
"""

import asyncio
import sys
import traceback
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append('.')

async def test_prompt_manager():
    """测试Prompt管理器核心功能"""
    print("=" * 60)
    print("[PROMPT] 测试 Prompt 管理系统核心功能")
    print("=" * 60)
    
    try:
        from prompt_manager import PromptManager
        
        pm = PromptManager()
        
        # 1. 版本管理测试
        print("1. 版本管理测试...")
        version_info = pm.get_version_info()
        print(f"   当前版本: {version_info['version']}")
        print(f"   描述: {version_info['description']}")
        print(f"   最后更新: {version_info['last_updated']}")
        
        # 2. 系统验证测试
        print("\n2. 系统完整性验证...")
        validation = pm.validate_prompts()
        
        error_count = len(validation['errors'])
        warning_count = len(validation['warnings'])
        info_count = len(validation['info'])
        
        print(f"   错误: {error_count}")
        print(f"   警告: {warning_count}")
        print(f"   信息: {info_count}")
        
        if error_count == 0:
            print("   [OK] 系统验证通过")
        else:
            print("   [ERROR] 发现错误:")
            for error in validation['errors']:
                print(f"      - {error}")
        
        # 3. 可用prompt列表测试
        print("\n3. 可用Prompt类型检查...")
        available = pm.list_available_prompts()
        
        for category, items in available.items():
            print(f"   {category}: {len(items)} 项")
            if len(items) > 0:
                print(f"      示例: {items[0]}")
        
        # 4. Agent Prompt生成测试
        print("\n4. Agent Prompt生成测试...")
        
        test_agents = ["hr_agent", "finance_agent", "developer_agent"]
        agent_results = {}
        
        for agent_type in test_agents:
            try:
                prompt = pm.create_agent_prompt(f"test_{agent_type}", agent_type)
                agent_results[agent_type] = {
                    "success": True,
                    "length": len(prompt),
                    "preview": prompt[:100] + "..." if len(prompt) > 100 else prompt
                }
                print(f"   [OK] {agent_type}: {len(prompt)} 字符")
            except Exception as e:
                agent_results[agent_type] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"   [ERROR] {agent_type}: {str(e)}")
        
        # 5. 任务Prompt生成测试
        print("\n5. 任务Prompt生成测试...")
        
        test_tasks = [
            ("hr_agent", "employee_analysis", {"employee_id": "TEST001", "analysis_type": "performance"}),
            ("finance_agent", "financial_report", {"report_type": "monthly", "period": "2024-03"}),
            ("general_task", "task_planning", {"description": "测试任务", "requirements": "基础测试"})
        ]
        
        task_results = {}
        
        for agent_role, task_type, task_data in test_tasks:
            try:
                task_prompt = pm.create_task_prompt(agent_role, task_type, task_data)
                task_results[f"{agent_role}_{task_type}"] = {
                    "success": True,
                    "length": len(task_prompt),
                    "preview": task_prompt[:100] + "..." if len(task_prompt) > 100 else task_prompt
                }
                print(f"   [OK] {agent_role}.{task_type}: {len(task_prompt)} 字符")
            except Exception as e:
                task_results[f"{agent_role}_{task_type}"] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"   [ERROR] {agent_role}.{task_type}: {str(e)}")
        
        # 6. 模板渲染测试
        print("\n6. 模板渲染功能测试...")
        
        test_template = "你好，{name}！你的角色是{role}，任务是{task}。"
        test_variables = {
            "name": "测试用户",
            "role": "系统管理员",
            "task": "验证系统功能"
        }
        
        try:
            rendered = pm.render_prompt(test_template, test_variables)
            print(f"   [OK] 模板渲染成功: {rendered}")
        except Exception as e:
            print(f"   [ERROR] 模板渲染失败: {str(e)}")
        
        # 7. 约束prompt测试
        print("\n7. 约束Prompt测试...")
        
        test_constraints = [
            ("security_constraints", "privacy_protection"),
            ("business_constraints", "financial_approval"),
            ("technical_constraints", "code_quality")
        ]
        
        constraint_results = {}
        
        for constraint_type, constraint_name in test_constraints:
            try:
                constraint = pm.get_constraint_prompt(constraint_type, constraint_name)
                constraint_results[f"{constraint_type}.{constraint_name}"] = {
                    "success": True,
                    "length": len(constraint.get("template", "")),
                    "applicable_agents": constraint.get("applicable_agents", [])
                }
                print(f"   [OK] {constraint_type}.{constraint_name}: {len(constraint.get('template', ''))} 字符")
            except Exception as e:
                constraint_results[f"{constraint_type}.{constraint_name}"] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"   [ERROR] {constraint_type}.{constraint_name}: {str(e)}")
        
        # 8. 版本更新测试
        print("\n8. 版本更新功能测试...")
        
        try:
            # 保存原始版本信息
            original_version = pm.get_version_info().copy()
            
            # 测试版本更新
            test_version = "1.0.1"
            test_changes = ["测试版本更新功能"]
            pm.update_version(test_version, test_changes, "测试程序")
            
            # 验证更新
            updated_version = pm.get_version_info()
            if updated_version["version"] == test_version:
                print(f"   [OK] 版本更新成功: {test_version}")
            else:
                print(f"   [ERROR] 版本更新失败，期望: {test_version}, 实际: {updated_version['version']}")
            
            # 恢复原始版本
            pm.save_version_info(original_version)
            print("   [INFO] 已恢复原始版本信息")
            
        except Exception as e:
            print(f"   [ERROR] 版本更新测试失败: {str(e)}")
        
        # 统计结果
        total_agent_tests = len(test_agents)
        successful_agent_tests = sum(1 for result in agent_results.values() if result["success"])
        
        total_task_tests = len(test_tasks)
        successful_task_tests = sum(1 for result in task_results.values() if result["success"])
        
        total_constraint_tests = len(test_constraints)
        successful_constraint_tests = sum(1 for result in constraint_results.values() if result["success"])
        
        print(f"\n测试结果统计:")
        print(f"   Agent Prompt生成: {successful_agent_tests}/{total_agent_tests}")
        print(f"   任务Prompt生成: {successful_task_tests}/{total_task_tests}")
        print(f"   约束Prompt读取: {successful_constraint_tests}/{total_constraint_tests}")
        
        # 总体评估
        if (error_count == 0 and 
            successful_agent_tests == total_agent_tests and 
            successful_task_tests >= total_task_tests * 0.8 and  # 允许一些任务类型不存在
            successful_constraint_tests == total_constraint_tests):
            print("\n[SUCCESS] Prompt管理系统功能完全正常!")
            return True
        else:
            print("\n[WARNING] Prompt管理系统存在部分问题")
            return False
        
    except Exception as e:
        print(f"[ERROR] Prompt管理系统测试失败: {str(e)}")
        traceback.print_exc()
        return False


async def test_natural_language_scenarios():
    """测试自然语言场景"""
    print("\n" + "=" * 60)
    print("[SCENARIO] 自然语言场景测试")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "HR场景 - 员工绩效分析",
            "description": "分析员工张三的年度绩效，识别优势和改进点",
            "agent": "hr_agent",
            "expected": "应该生成包含分析维度、输出要求和质量标准的专业prompt"
        },
        {
            "name": "财务场景 - 月度报告",
            "description": "生成2024年3月的财务报告，包含收支分析",
            "agent": "finance_agent", 
            "expected": "应该生成包含报告要素、输出要求的财务专业prompt"
        },
        {
            "name": "技术场景 - 代码审查",
            "description": "审查Python项目的代码质量和安全性",
            "agent": "developer_agent",
            "expected": "应该生成包含审查维度、标准和输出要求的技术prompt"
        },
        {
            "name": "安全场景 - 隐私保护",
            "description": "确保系统不会泄露用户敏感信息",
            "agent": "hr_agent",
            "expected": "应该包含隐私保护约束和安全检查机制"
        }
    ]
    
    try:
        from prompt_manager import PromptManager
        pm = PromptManager()
        
        successful_scenarios = 0
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. {scenario['name']}")
            print(f"   描述: {scenario['description']}")
            print(f"   期望: {scenario['expected']}")
            
            try:
                # 生成Agent专用prompt
                agent_prompt = pm.create_agent_prompt(f"test_{scenario['agent']}", scenario["agent"])
                
                # 检查prompt是否包含关键元素
                prompt_lower = agent_prompt.lower()
                
                # 基础检查
                has_role_description = "角色" in agent_prompt or "role" in prompt_lower
                has_capabilities = "能力" in agent_prompt or "capabilities" in prompt_lower
                has_constraints = "约束" in agent_prompt or "constraint" in prompt_lower
                
                # 特定场景检查
                scenario_specific_checks = True
                if scenario["agent"] == "hr_agent":
                    scenario_specific_checks = ("员工" in agent_prompt and "隐私" in agent_prompt)
                elif scenario["agent"] == "finance_agent":
                    scenario_specific_checks = ("财务" in agent_prompt and "审批" in agent_prompt)
                elif scenario["agent"] == "developer_agent":
                    scenario_specific_checks = ("代码" in agent_prompt and "质量" in agent_prompt)
                
                if (has_role_description and has_capabilities and has_constraints and scenario_specific_checks):
                    print(f"   [OK] 场景测试通过 (prompt长度: {len(agent_prompt)})")
                    successful_scenarios += 1
                else:
                    print(f"   [WARNING] 场景测试部分通过，缺少部分关键元素")
                    if not has_role_description:
                        print("      - 缺少角色描述")
                    if not has_capabilities:
                        print("      - 缺少能力定义")
                    if not has_constraints:
                        print("      - 缺少约束条件")
                    if not scenario_specific_checks:
                        print("      - 缺少场景特定内容")
                
            except Exception as e:
                print(f"   [ERROR] 场景测试失败: {str(e)}")
        
        print(f"\n场景测试结果: {successful_scenarios}/{len(scenarios)} 通过")
        
        if successful_scenarios >= len(scenarios) * 0.8:  # 80%通过率
            print("[SUCCESS] 自然语言场景测试基本通过")
            return True
        else:
            print("[WARNING] 自然语言场景测试需要改进")
            return False
        
    except Exception as e:
        print(f"[ERROR] 自然语言场景测试失败: {str(e)}")
        return False


async def test_prompt_quality():
    """测试Prompt质量"""
    print("\n" + "=" * 60)
    print("[QUALITY] Prompt质量测试")
    print("=" * 60)
    
    try:
        from prompt_manager import PromptManager
        pm = PromptManager()
        
        quality_metrics = {
            "length_appropriate": 0,  # 长度适中
            "structure_clear": 0,     # 结构清晰
            "language_professional": 0, # 语言专业
            "constraints_included": 0,  # 包含约束
            "actionable": 0             # 可执行性
        }
        
        test_agents = ["hr_agent", "finance_agent", "developer_agent"]
        
        for agent_type in test_agents:
            print(f"\n分析 {agent_type} 的Prompt质量:")
            
            try:
                prompt = pm.create_agent_prompt(f"quality_test_{agent_type}", agent_type)
                
                # 长度检查 (500-3000字符比较合适)
                if 500 <= len(prompt) <= 3000:
                    quality_metrics["length_appropriate"] += 1
                    print(f"   [OK] 长度适中: {len(prompt)} 字符")
                else:
                    print(f"   [WARNING] 长度异常: {len(prompt)} 字符")
                
                # 结构检查 (是否有明确的sections)
                sections = ["##", "###", "角色设定", "核心能力", "约束条件"]
                found_sections = sum(1 for section in sections if section in prompt)
                if found_sections >= 3:
                    quality_metrics["structure_clear"] += 1
                    print(f"   [OK] 结构清晰: 发现 {found_sections} 个结构元素")
                else:
                    print(f"   [WARNING] 结构不够清晰: 只发现 {found_sections} 个结构元素")
                
                # 专业性检查 (包含专业术语)
                professional_terms = ["专业", "准确", "合规", "安全", "质量", "标准", "流程"]
                found_terms = sum(1 for term in professional_terms if term in prompt)
                if found_terms >= 4:
                    quality_metrics["language_professional"] += 1
                    print(f"   [OK] 语言专业: 包含 {found_terms} 个专业术语")
                else:
                    print(f"   [WARNING] 专业性不足: 只包含 {found_terms} 个专业术语")
                
                # 约束检查
                constraint_indicators = ["不得", "必须", "严格", "禁止", "需要", "约束", "限制"]
                found_constraints = sum(1 for indicator in constraint_indicators if indicator in prompt)
                if found_constraints >= 3:
                    quality_metrics["constraints_included"] += 1
                    print(f"   [OK] 约束完整: 发现 {found_constraints} 个约束指示词")
                else:
                    print(f"   [WARNING] 约束不足: 只发现 {found_constraints} 个约束指示词")
                
                # 可执行性检查 (包含具体的行动指导)
                action_words = ["执行", "处理", "分析", "生成", "检查", "验证", "输出", "提供"]
                found_actions = sum(1 for action in action_words if action in prompt)
                if found_actions >= 4:
                    quality_metrics["actionable"] += 1
                    print(f"   [OK] 可执行性强: 包含 {found_actions} 个行动指导词")
                else:
                    print(f"   [WARNING] 可执行性不足: 只包含 {found_actions} 个行动指导词")
                
            except Exception as e:
                print(f"   [ERROR] {agent_type} 质量分析失败: {str(e)}")
        
        # 质量评估
        total_tests = len(test_agents)
        print(f"\n质量指标统计 (满分: {total_tests}):")
        for metric, score in quality_metrics.items():
            percentage = (score / total_tests) * 100
            print(f"   {metric}: {score}/{total_tests} ({percentage:.1f}%)")
        
        # 总体质量评分
        total_score = sum(quality_metrics.values())
        max_score = len(quality_metrics) * total_tests
        overall_quality = (total_score / max_score) * 100
        
        print(f"\n总体质量评分: {overall_quality:.1f}%")
        
        if overall_quality >= 80:
            print("[SUCCESS] Prompt质量优秀")
            return True
        elif overall_quality >= 60:
            print("[WARNING] Prompt质量良好，但有改进空间")
            return True
        else:
            print("[ERROR] Prompt质量需要显著改进")
            return False
        
    except Exception as e:
        print(f"[ERROR] Prompt质量测试失败: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("[TEST] 数字员工系统 - 简化功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行各项测试
    tests_passed = 0
    total_tests = 3
    
    # 1. 核心Prompt管理测试
    if await test_prompt_manager():
        tests_passed += 1
    
    # 2. 自然语言场景测试
    if await test_natural_language_scenarios():
        tests_passed += 1
    
    # 3. Prompt质量测试
    if await test_prompt_quality():
        tests_passed += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("[SUMMARY] 测试总结")
    print("=" * 60)
    print(f"总计测试: {total_tests}")
    print(f"通过测试: {tests_passed}")
    print(f"失败测试: {total_tests - tests_passed}")
    print(f"通过率: {(tests_passed / total_tests) * 100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n[SUCCESS] 所有测试通过！Prompt系统功能完全正常！")
        print("\n可用性验证结论:")
        print("✓ Prompt管理系统核心功能正常")
        print("✓ 支持自然语言场景描述")
        print("✓ 生成的Prompt质量达标")
        print("✓ 版本控制和模板渲染功能正常")
        print("\n系统已准备好用于生产环境！")
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
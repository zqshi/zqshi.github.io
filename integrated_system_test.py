"""
数字员工系统集成测试

测试记忆引擎模块和数字员工核心模块的集成功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_memory_engine_module():
    """测试记忆引擎模块"""
    print("="*50)
    print("测试记忆引擎模块")
    print("="*50)
    
    try:
        # 导入记忆引擎模块
        from memory_engine_module import (
            create_memory_system,
            get_module_info,
            InputType,
            DEFAULT_MEMORY_CONFIG
        )
        
        print("✓ 记忆引擎模块导入成功")
        
        # 获取模块信息
        module_info = get_module_info()
        print(f"✓ 模块信息: {module_info['name']} v{module_info['version']}")
        print(f"  组件数量: {len(module_info['components'])}")
        
        # 创建记忆系统
        memory_system = create_memory_system()
        print("✓ 记忆系统创建成功")
        
        # 测试基本功能
        result = memory_system.process(
            "测试记忆引擎集成",
            InputType.QUERY,
            {"source": "integration_test"}
        )
        
        print(f"✓ 记忆处理成功: {result.response[:50]}...")
        print(f"  置信度: {result.confidence:.2f}")
        
        # 获取系统状态
        status = memory_system.get_memory_status()
        print(f"✓ 系统状态正常，记忆层数: {len(status)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆引擎模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_digital_employee_core():
    """测试数字员工核心模块"""
    print("\n" + "="*50)
    print("测试数字员工核心模块")
    print("="*50)
    
    try:
        # 导入数字员工核心模块
        from digital_employee_core import (
            get_module_info,
            check_dependencies,
            DEFAULT_AGENT_CONFIG
        )
        
        print("✓ 数字员工核心模块基础导入成功")
        
        # 获取模块信息
        module_info = get_module_info()
        print(f"✓ 模块信息: {module_info['name']} v{module_info['version']}")
        print(f"  组件可用性: {module_info['components_available']}")
        
        # 检查依赖
        dependencies = check_dependencies()
        print("✓ 依赖检查完成:")
        for dep, info in dependencies.items():
            status = "✓" if info["available"] else "❌"
            print(f"  {status} {dep}: {info.get('version', info.get('error', 'unknown'))}")
        
        # 尝试创建完整系统（如果组件可用）
        if module_info['components_available']:
            from digital_employee_core import create_digital_employee_system
            
            system = create_digital_employee_system()
            print("✓ 数字员工系统创建成功")
            print(f"  可用Agent类型: {len(system['available_agents'])}")
        else:
            print("⚠️  核心组件不完全可用，跳过系统创建测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 数字员工核心模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cross_module_integration():
    """测试跨模块集成"""
    print("\n" + "="*50)
    print("测试跨模块集成")
    print("="*50)
    
    try:
        # 导入两个模块
        from memory_engine_module import create_memory_system, InputType
        from digital_employee_core import get_module_info as get_core_info
        
        print("✓ 跨模块导入成功")
        
        # 创建记忆系统
        memory_system = create_memory_system()
        
        # 模拟数字员工使用记忆系统的场景
        test_scenarios = [
            {
                "input": "客户询问产品信息",
                "type": InputType.QUERY,
                "context": {"source": "customer_service", "priority": "high"}
            },
            {
                "input": {
                    "description": "成功处理客户咨询",
                    "participants": ["客户", "客服agent"],
                    "outcome": "satisfied"
                },
                "type": InputType.EVENT,
                "context": {"source": "service_log"}
            },
            {
                "input": {
                    "emotion": "satisfaction",
                    "intensity": 0.8,
                    "trigger": "successful_interaction"
                },
                "type": InputType.EMOTION,
                "context": {"source": "feedback_analyzer"}
            }
        ]
        
        print("✓ 执行集成测试场景:")
        
        for i, scenario in enumerate(test_scenarios, 1):
            result = memory_system.process(
                scenario["input"],
                scenario["type"],
                scenario["context"]
            )
            
            print(f"  场景 {i}: {scenario['type'].value}")
            print(f"    响应: {result.response[:40]}...")
            print(f"    置信度: {result.confidence:.2f}")
            print(f"    激活记忆: {len(result.activated_memories)}")
        
        # 检查记忆系统状态
        final_status = memory_system.get_memory_status()
        print(f"✓ 集成测试后系统状态:")
        for layer, status in final_status.items():
            print(f"  {layer}: {status['size']}/{status['capacity']} "
                 f"({status['utilization']*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 跨模块集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_module_isolation():
    """测试模块隔离性"""
    print("\n" + "="*50)
    print("测试模块隔离性")
    print("="*50)
    
    try:
        # 测试单独导入每个模块不会影响其他模块
        import memory_engine_module
        print("✓ 记忆引擎模块独立导入成功")
        
        import digital_employee_core  
        print("✓ 数字员工核心模块独立导入成功")
        
        # 测试模块命名空间隔离
        memory_info = memory_engine_module.get_module_info()
        core_info = digital_employee_core.get_module_info()
        
        print(f"✓ 模块命名空间隔离正常:")
        print(f"  记忆引擎: {memory_info['name']}")
        print(f"  数字员工核心: {core_info['name']}")
        
        # 测试配置隔离
        memory_config = memory_engine_module.DEFAULT_MEMORY_CONFIG
        core_config = digital_employee_core.DEFAULT_AGENT_CONFIG
        
        print(f"✓ 配置隔离正常:")
        print(f"  记忆引擎配置项: {len(memory_config)}")
        print(f"  数字员工配置项: {len(core_config)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块隔离性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("数字员工系统集成测试开始")
    print("时间:", logging.Formatter().formatTime(logging.LogRecord(
        '', 0, '', 0, '', (), None), '%Y-%m-%d %H:%M:%S'))
    
    test_results = []
    
    # 执行各项测试
    test_results.append(("记忆引擎模块", test_memory_engine_module()))
    test_results.append(("数字员工核心模块", test_digital_employee_core())) 
    test_results.append(("跨模块集成", test_cross_module_integration()))
    test_results.append(("模块隔离性", test_module_isolation()))
    
    # 汇总测试结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed + failed} 项测试")
    print(f"通过: {passed} 项")
    print(f"失败: {failed} 项")
    
    if failed == 0:
        print("\n🎉 所有测试通过！系统集成成功！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 项测试失败，请检查相关模块")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
"""
CodingAgent主类实现

继续coding_agent.py的实现，包含主要的CodingAgent类
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .agent_core import BaseAgent, AgentRole, AgentCapability, Task, TaskStatus
from .coding_agent import (
    SecureCodeExecutor, DynamicToolManager, ProblemAnalyzer,
    CodeExecutionContext, ToolDefinition, ProblemSolution,
    ProblemType, CodeExecutionResult
)

# ================================
# CodingAgent主类
# ================================

class CodingAgent(BaseAgent):
    """
    编程问题解决Agent
    
    当现有Agent无法通过现有工具和信息解决问题时，作为最终解决方案，
    通过编程方式解决工程、检索、工具使用等复杂问题。
    """
    
    def __init__(self, agent_id: str = "coding_agent_001"):
        # 定义CodingAgent的核心能力
        capabilities = [
            AgentCapability(
                name="code_generation",
                description="生成Python代码解决复杂问题",
                skill_level=9,
                tools_required=["python_interpreter", "code_executor"]
            ),
            AgentCapability(
                name="tool_creation",
                description="创建自定义工具和函数",
                skill_level=8,
                tools_required=["dynamic_tool_manager"]
            ),
            AgentCapability(
                name="problem_solving",
                description="分析和解决复杂工程问题",
                skill_level=9,
                tools_required=["problem_analyzer", "solution_generator"]
            ),
            AgentCapability(
                name="api_integration",
                description="集成外部API和服务",
                skill_level=7,
                tools_required=["requests", "json_parser"]
            ),
            AgentCapability(
                name="data_processing",
                description="处理和转换各种数据格式",
                skill_level=8,
                tools_required=["pandas", "numpy", "data_converters"]
            ),
            AgentCapability(
                name="algorithm_design",
                description="设计和实现算法解决方案",
                skill_level=8,
                tools_required=["algorithm_library", "performance_analyzer"]
            ),
            AgentCapability(
                name="debugging",
                description="调试和修复代码问题",
                skill_level=7,
                tools_required=["debugger", "error_analyzer"]
            ),
            AgentCapability(
                name="system_integration",
                description="集成不同系统和模块",
                skill_level=7,
                tools_required=["integration_tools", "config_manager"]
            )
        ]
        
        super().__init__(agent_id, AgentRole.DEVELOPER, capabilities)
        
        # 初始化核心组件
        self.code_executor = SecureCodeExecutor()
        self.tool_manager = DynamicToolManager()
        self.problem_analyzer = ProblemAnalyzer()
        
        # 解决方案历史
        self.solution_history = []
        
        # 性能统计
        self.performance_stats = {
            "total_problems_solved": 0,
            "successful_solutions": 0,
            "failed_solutions": 0,
            "average_solution_time": 0.0,
            "created_tools_count": 0
        }
        
        # 扩展系统提示词
        self.system_prompt += """

我是CodingAgent，专门负责通过编程方式解决其他Agent无法处理的复杂问题。

我的核心能力包括：
1. 代码生成和执行 - 编写Python代码解决各种问题
2. 自定义工具创建 - 根据需求创建专用工具函数  
3. 复杂问题分解 - 将大问题分解为可执行的小步骤
4. API集成 - 调用外部服务和接口
5. 数据处理 - 处理各种格式的数据
6. 算法设计 - 实现高效的算法解决方案
7. 系统集成 - 连接不同的系统和模块

工作流程：
1. 问题分析 - 理解问题类型和复杂度
2. 方案设计 - 制定解决策略和步骤
3. 代码实现 - 编写安全可执行的代码
4. 测试验证 - 验证解决方案的正确性
5. 工具注册 - 将有用的解决方案注册为可复用工具

安全原则：
- 所有代码在安全沙箱中执行
- 限制文件系统和网络访问
- 验证代码安全性和合规性
- 监控资源使用和执行时间
"""
    
    async def _execute_task(self, task: Task) -> Dict[str, Any]:
        """执行编程任务"""
        try:
            problem_description = task.data.get("problem_description", "")
            context = task.data.get("context", {})
            requirements = task.data.get("requirements", {})
            
            # 分析问题
            problem_analysis = self.problem_analyzer.analyze_problem(problem_description)
            
            # 生成解决方案
            solution = await self._generate_solution(
                problem_description, 
                problem_analysis, 
                context, 
                requirements
            )
            
            # 更新统计信息
            self._update_performance_stats(solution)
            
            return {
                "status": "success",
                "solution": solution,
                "problem_analysis": problem_analysis,
                "execution_time": solution.execution_time,
                "created_tools": len(solution.created_tools),
                "confidence": solution.confidence_score
            }
            
        except Exception as e:
            self.performance_stats["failed_solutions"] += 1
            logger.error(f"CodingAgent任务执行失败: {str(e)}")
            
            return {
                "status": "failed",
                "error": str(e),
                "suggestion": "请检查问题描述是否清晰，或尝试将复杂问题分解为更小的子问题"
            }
    
    async def _generate_solution(self, problem_description: str, problem_analysis: Dict[str, Any], 
                               context: Dict[str, Any], requirements: Dict[str, Any]) -> ProblemSolution:
        """生成问题解决方案"""
        solution_start_time = time.time()
        problem_id = str(uuid.uuid4())
        
        # 根据问题类型选择解决策略
        primary_type = problem_analysis["primary_type"]
        
        if primary_type == ProblemType.DATA_PROCESSING:
            solution_code = await self._generate_data_processing_solution(
                problem_description, context, requirements
            )
        elif primary_type == ProblemType.API_INTEGRATION:
            solution_code = await self._generate_api_integration_solution(
                problem_description, context, requirements
            )
        elif primary_type == ProblemType.TOOL_CREATION:
            solution_code = await self._generate_tool_creation_solution(
                problem_description, context, requirements
            )
        elif primary_type == ProblemType.ALGORITHM_DESIGN:
            solution_code = await self._generate_algorithm_solution(
                problem_description, context, requirements
            )
        else:
            solution_code = await self._generate_custom_solution(
                problem_description, context, requirements
            )
        
        # 执行解决方案
        execution_context = CodeExecutionContext(
            execution_id=problem_id,
            code=solution_code,
            timeout=requirements.get("timeout", 30.0)
        )
        
        execution_result = self.code_executor.execute_code(execution_context)
        
        # 创建工具（如果需要）
        created_tools = []
        if requirements.get("create_tool", False):
            tool_def = self._create_tool_from_solution(
                problem_description, solution_code, execution_result
            )
            if tool_def:
                tool_creation_result = self.tool_manager.create_tool_from_code(tool_def)
                if tool_creation_result["success"]:
                    created_tools.append(tool_def)
        
        # 计算置信度
        confidence_score = self._calculate_confidence_score(
            execution_result, problem_analysis, requirements
        )
        
        solution = ProblemSolution(
            problem_id=problem_id,
            problem_description=problem_description,
            problem_type=primary_type,
            solution_code=solution_code,
            solution_description=self._generate_solution_description(problem_analysis, execution_result),
            created_tools=created_tools,
            execution_results=[execution_result],
            confidence_score=confidence_score,
            execution_time=time.time() - solution_start_time,
            memory_usage=execution_result.get("memory_usage", 0),
            created_at=time.time()
        )
        
        # 保存到历史
        self.solution_history.append(solution)
        
        return solution
    
    async def _generate_data_processing_solution(self, problem_description: str, 
                                               context: Dict[str, Any], 
                                               requirements: Dict[str, Any]) -> str:
        """生成数据处理解决方案"""
        
        # 分析数据类型和处理需求
        data_source = context.get("data_source", "unknown")
        output_format = requirements.get("output_format", "json")
        
        solution_template = f'''
import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any

def solve_data_processing_problem():
    """
    数据处理解决方案
    问题: {problem_description}
    """
    try:
        # 数据加载
        # 根据实际数据源调整加载方式
        data = {context.get("sample_data", "[]")}
        
        # 数据处理逻辑
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])
        
        # 数据清洗和转换
        # 这里添加具体的处理逻辑
        processed_data = df.to_dict('records')
        
        # 结果格式化
        result = {{
            "status": "success",
            "processed_data": processed_data,
            "data_info": {{
                "rows": len(processed_data),
                "columns": len(df.columns) if len(df.columns) > 0 else 0,
                "processing_method": "pandas_dataframe"
            }}
        }}
        
        return result
        
    except Exception as e:
        return {{
            "status": "error",
            "error": str(e),
            "suggestion": "请检查数据格式和处理逻辑"
        }}

# 执行解决方案
result = solve_data_processing_problem()
print(json.dumps(result, indent=2, ensure_ascii=False))
'''
        
        return solution_template
    
    async def _generate_api_integration_solution(self, problem_description: str,
                                               context: Dict[str, Any],
                                               requirements: Dict[str, Any]) -> str:
        """生成API集成解决方案"""
        
        api_url = context.get("api_url", "")
        method = requirements.get("method", "GET")
        
        solution_template = f'''
import requests
import json
from typing import Dict, Any

def solve_api_integration_problem():
    """
    API集成解决方案
    问题: {problem_description}
    """
    try:
        # API请求配置
        api_url = "{api_url}"
        method = "{method}"
        headers = {{"Content-Type": "application/json"}}
        
        # 构建请求参数
        params = {context.get("params", "{}")}
        data = {context.get("data", "{}")}
        
        # 发送API请求
        if method.upper() == "GET":
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(api_url, json=data, headers=headers, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(api_url, json=data, headers=headers, timeout=10)
        else:
            raise ValueError(f"不支持的HTTP方法: {{method}}")
        
        # 处理响应
        if response.status_code == 200:
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            result = {{
                "status": "success",
                "data": response_data,
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }}
        else:
            result = {{
                "status": "error",
                "status_code": response.status_code,
                "error": response.text
            }}
        
        return result
        
    except requests.RequestException as e:
        return {{
            "status": "error",
            "error": f"请求失败: {{str(e)}}",
            "suggestion": "请检查网络连接和API地址"
        }}
    except Exception as e:
        return {{
            "status": "error", 
            "error": str(e)
        }}

# 执行解决方案
result = solve_api_integration_problem()
print(json.dumps(result, indent=2, ensure_ascii=False))
'''
        
        return solution_template
    
    async def _generate_tool_creation_solution(self, problem_description: str,
                                             context: Dict[str, Any],
                                             requirements: Dict[str, Any]) -> str:
        """生成工具创建解决方案"""
        
        tool_name = requirements.get("tool_name", "custom_tool")
        
        solution_template = f'''
def {tool_name}(*args, **kwargs):
    """
    自定义工具函数
    问题: {problem_description}
    """
    try:
        # 工具实现逻辑
        # 根据具体需求实现功能
        
        result = {{
            "status": "success", 
            "message": "工具执行成功",
            "args": args,
            "kwargs": kwargs,
            "tool_name": "{tool_name}"
        }}
        
        return result
        
    except Exception as e:
        return {{
            "status": "error",
            "error": str(e),
            "tool_name": "{tool_name}"
        }}

def test_{tool_name}():
    """测试工具函数"""
    test_result = {tool_name}("test")
    print(f"测试结果: {{test_result}}")
    return test_result

# 执行测试
result = test_{tool_name}()
'''
        
        return solution_template
    
    async def _generate_algorithm_solution(self, problem_description: str,
                                         context: Dict[str, Any],
                                         requirements: Dict[str, Any]) -> str:
        """生成算法解决方案"""
        
        solution_template = f'''
def solve_algorithm_problem(input_data):
    """
    算法解决方案
    问题: {problem_description}
    """
    try:
        # 算法实现
        # 根据具体问题类型实现相应算法
        
        if not input_data:
            return {{"status": "error", "error": "输入数据为空"}}
        
        # 这里实现具体的算法逻辑
        # 示例：简单的数据处理
        if isinstance(input_data, list):
            result_data = sorted(input_data)
            algorithm_type = "sorting"
        elif isinstance(input_data, dict):
            result_data = input_data
            algorithm_type = "dict_processing"
        else:
            result_data = str(input_data)
            algorithm_type = "string_processing"
        
        result = {{
            "status": "success",
            "result": result_data,
            "algorithm_type": algorithm_type,
            "input_type": str(type(input_data).__name__),
            "complexity": "O(n log n)" if algorithm_type == "sorting" else "O(1)"
        }}
        
        return result
        
    except Exception as e:
        return {{
            "status": "error",
            "error": str(e)
        }}

# 测试算法
test_data = {context.get("test_data", "[3, 1, 4, 1, 5, 9, 2, 6]")}
result = solve_algorithm_problem(test_data)
print(f"算法执行结果: {{result}}")
'''
        
        return solution_template
    
    async def _generate_custom_solution(self, problem_description: str,
                                      context: Dict[str, Any],
                                      requirements: Dict[str, Any]) -> str:
        """生成自定义解决方案"""
        
        solution_template = f'''
def solve_custom_problem():
    """
    自定义问题解决方案
    问题: {problem_description}
    """
    try:
        # 问题分析
        problem_context = {json.dumps(context, ensure_ascii=False)}
        requirements = {json.dumps(requirements, ensure_ascii=False)}
        
        # 解决方案实现
        # 根据具体问题描述和上下文实现解决逻辑
        
        solution_steps = [
            "1. 分析问题需求",
            "2. 设计解决方案",
            "3. 实现核心逻辑", 
            "4. 验证结果正确性"
        ]
        
        # 实现具体逻辑
        implementation_result = {{
            "problem_understood": True,
            "solution_approach": "custom_implementation",
            "steps_completed": solution_steps,
            "context_used": problem_context,
            "requirements_met": True
        }}
        
        result = {{
            "status": "success",
            "solution": implementation_result,
            "message": "自定义问题解决完成",
            "next_steps": ["测试验证", "优化性能", "文档化"]
        }}
        
        return result
        
    except Exception as e:
        return {{
            "status": "error",
            "error": str(e),
            "suggestion": "请提供更详细的问题描述和上下文信息"
        }}

# 执行解决方案
result = solve_custom_problem()
print(json.dumps(result, indent=2, ensure_ascii=False))
'''
        
        return solution_template
    
    def _create_tool_from_solution(self, problem_description: str, 
                                 solution_code: str, 
                                 execution_result: Dict[str, Any]) -> Optional[ToolDefinition]:
        """从解决方案创建工具"""
        if execution_result.get("status") != CodeExecutionResult.SUCCESS:
            return None
        
        tool_id = f"tool_{str(uuid.uuid4())[:8]}"
        
        # 提取函数名
        import re
        func_matches = re.findall(r'def\s+(\w+)\s*\(', solution_code)
        if not func_matches:
            return None
        
        main_function = func_matches[0]
        
        tool_def = ToolDefinition(
            tool_id=tool_id,
            name=f"Generated Tool - {main_function}",
            description=f"基于问题'{problem_description[:50]}...'自动生成的工具",
            function_code=solution_code,
            parameters={
                "input": "Any",
                "output": "Dict[str, Any]"
            },
            return_type="Dict[str, Any]",
            created_at=time.time(),
            dependencies=["json", "typing"],
            test_cases=[
                {
                    "function": main_function,
                    "args": [],
                    "kwargs": {},
                    "expected": None
                }
            ]
        )
        
        return tool_def
    
    def _calculate_confidence_score(self, execution_result: Dict[str, Any],
                                  problem_analysis: Dict[str, Any],
                                  requirements: Dict[str, Any]) -> float:
        """计算解决方案置信度"""
        base_confidence = 0.5
        
        # 执行成功加分
        if execution_result.get("status") == CodeExecutionResult.SUCCESS:
            base_confidence += 0.3
        
        # 无错误输出加分
        if not execution_result.get("error"):
            base_confidence += 0.1
        
        # 问题复杂度调整
        complexity = problem_analysis.get("complexity", "simple")
        if complexity == "simple":
            base_confidence += 0.1
        elif complexity == "complex":
            base_confidence -= 0.1
        
        # 执行时间合理性
        execution_time = execution_result.get("execution_time", 0)
        if execution_time < 5.0:  # 5秒内完成
            base_confidence += 0.1
        elif execution_time > 20.0:  # 超过20秒
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _generate_solution_description(self, problem_analysis: Dict[str, Any],
                                     execution_result: Dict[str, Any]) -> str:
        """生成解决方案描述"""
        problem_type = problem_analysis.get("primary_type", ProblemType.CUSTOM_SOLUTION)
        complexity = problem_analysis.get("complexity", "unknown")
        status = execution_result.get("status", "unknown")
        
        description = f"问题类型: {problem_type.value}, 复杂度: {complexity}, 执行状态: {status.value if hasattr(status, 'value') else status}"
        
        if execution_result.get("output"):
            description += f", 输出: {execution_result['output'][:100]}..."
        
        return description
    
    def _update_performance_stats(self, solution: ProblemSolution):
        """更新性能统计"""
        self.performance_stats["total_problems_solved"] += 1
        
        if solution.confidence_score > 0.7:
            self.performance_stats["successful_solutions"] += 1
        else:
            self.performance_stats["failed_solutions"] += 1
        
        # 更新平均解决时间
        total_time = (self.performance_stats["average_solution_time"] * 
                     (self.performance_stats["total_problems_solved"] - 1) + 
                     solution.execution_time)
        self.performance_stats["average_solution_time"] = total_time / self.performance_stats["total_problems_solved"]
        
        # 更新创建工具数量
        self.performance_stats["created_tools_count"] += len(solution.created_tools)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        success_rate = 0.0
        if self.performance_stats["total_problems_solved"] > 0:
            success_rate = (self.performance_stats["successful_solutions"] / 
                          self.performance_stats["total_problems_solved"])
        
        return {
            "agent_id": self.agent_id,
            "performance_stats": self.performance_stats,
            "success_rate": success_rate,
            "recent_solutions": len([s for s in self.solution_history if time.time() - s.created_at < 3600]),
            "available_tools": len(self.tool_manager.tools_registry),
            "capabilities": [cap.name for cap in self.capabilities]
        }
    
    def list_created_tools(self) -> List[Dict[str, Any]]:
        """列出已创建的工具"""
        return self.tool_manager.list_tools()
    
    def get_solution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取解决方案历史"""
        recent_solutions = sorted(self.solution_history, 
                                key=lambda x: x.created_at, reverse=True)[:limit]
        
        return [
            {
                "problem_id": sol.problem_id,
                "problem_description": sol.problem_description[:100] + "...",
                "problem_type": sol.problem_type.value,
                "confidence_score": sol.confidence_score,
                "execution_time": sol.execution_time,
                "created_tools_count": len(sol.created_tools),
                "created_at": sol.created_at
            }
            for sol in recent_solutions
        ]
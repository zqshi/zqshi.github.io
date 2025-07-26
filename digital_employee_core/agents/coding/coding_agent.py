# Coding Agent实现 - 统一治理版本
# 版本: 2.0.0

import asyncio
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any

from ..base import BaseAgent, AgentRole, AgentCapability, AgentConstraint, Task
from .coding_tools import (
    SecureCodeExecutor, DynamicToolManager, ProblemAnalyzer,
    CodeExecutionContext, ToolDefinition, ProblemSolution,
    ProblemType, CodeExecutionResult
)

logger = logging.getLogger(__name__)

class CodingAgent(BaseAgent):
    """编程问题解决Agent - 统一治理版本"""
    
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
                tools_required=["problem_analyzer"]
            ),
            AgentCapability(
                name="data_processing",
                description="处理各种格式的数据",
                skill_level=8,
                tools_required=["pandas", "numpy"]
            ),
            AgentCapability(
                name="api_integration",
                description="调用和集成外部API",
                skill_level=7,
                tools_required=["requests", "json"]
            ),
            AgentCapability(
                name="algorithm_design",
                description="设计和实现算法",
                skill_level=8,
                tools_required=["python_interpreter"]
            )
        ]
        
        super().__init__(agent_id, AgentRole.DEVELOPER, capabilities)
        
        # 初始化CodingAgent特有组件
        self.code_executor = SecureCodeExecutor()
        self.tool_manager = DynamicToolManager()
        self.problem_analyzer = ProblemAnalyzer()
        
        # CodingAgent特有的性能指标
        self.coding_metrics = {
            "problems_solved": 0,
            "tools_created": 0,
            "code_execution_success_rate": 0.0,
            "average_solution_time": 0.0
        }
        
        logger.info(f"CodingAgent {agent_id} 初始化完成")
    
    def _load_constraints(self) -> List[AgentConstraint]:
        return [
            AgentConstraint(
                "code_safety",
                "执行的代码必须安全，不得包含恶意操作",
                lambda task: self._validate_code_safety(task)
            ),
            AgentConstraint(
                "execution_timeout",
                "代码执行不得超过时间限制",
                lambda task: True  # 由执行器控制超时
            ),
            AgentConstraint(
                "resource_limits", 
                "不得超过资源使用限制",
                lambda task: True  # 由执行器控制资源
            )
        ]
    
    def _validate_code_safety(self, task: Task) -> bool:
        """验证代码安全性"""
        # 基本安全检查
        if 'problem_description' in task.data:
            description = task.data['problem_description']
            dangerous_keywords = ['rm -rf', 'del *', 'format', 'system', 'eval', 'exec']
            return not any(keyword in description.lower() for keyword in dangerous_keywords)
        return True
    
    async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
        """执行编程任务"""
        try:
            if task_prompt:
                logger.info(f"Coding Agent using custom task prompt for {task.task_type}")
            
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
            
            # 更新编程专用指标
            self.coding_metrics["problems_solved"] += 1
            
            return {
                "solution": solution,
                "problem_analysis": problem_analysis,
                "execution_context": {
                    "agent_id": self.agent_id,
                    "task_id": task.task_id,
                    "coding_metrics": self.coding_metrics.copy()
                }
            }
            
        except Exception as e:
            logger.error(f"编程任务执行失败: {str(e)}")
            raise
    
    async def _generate_solution(self, problem_description: str, analysis: Dict[str, Any],
                               context: Dict[str, Any], requirements: Dict[str, Any]) -> ProblemSolution:
        """生成问题解决方案"""
        start_time = datetime.now()
        
        try:
            # 根据问题类型生成代码
            problem_type = analysis.get("problem_type", ProblemType.SYSTEM_INTEGRATION)
            
            if problem_type == ProblemType.DATA_PROCESSING:
                solution_code = await self._generate_data_processing_solution(problem_description, context)
            elif problem_type == ProblemType.API_INTEGRATION:
                solution_code = await self._generate_api_integration_solution(problem_description, context)
            elif problem_type == ProblemType.TOOL_CREATION:
                solution_code = await self._generate_tool_creation_solution(problem_description, context)
            elif problem_type == ProblemType.ALGORITHM_DESIGN:
                solution_code = await self._generate_algorithm_solution(problem_description, context)
            else:
                solution_code = await self._generate_general_solution(problem_description, context)
            
            # 执行代码验证
            execution_result = await self.code_executor.execute_code(solution_code, context)
            
            # 创建解决方案对象
            solution = ProblemSolution(
                problem_description=problem_description,
                solution_code=solution_code,
                explanation=self._generate_explanation(problem_type, solution_code),
                test_cases=[],
                performance_metrics={
                    "execution_success": execution_result.success,
                    "execution_time": execution_result.execution_time,
                    "solution_generation_time": (datetime.now() - start_time).total_seconds()
                }
            )
            
            # 如果执行成功，可能创建可复用工具
            if execution_result.success and requirements.get("create_tool", False):
                tool_created = await self._create_reusable_tool(solution)
                if tool_created:
                    self.coding_metrics["tools_created"] += 1
            
            return solution
            
        except Exception as e:
            logger.error(f"解决方案生成失败: {str(e)}")
            # 返回错误解决方案
            return ProblemSolution(
                problem_description=problem_description,
                solution_code=f"# 错误: {str(e)}",
                explanation=f"解决方案生成过程中出现错误: {str(e)}",
                performance_metrics={
                    "execution_success": False,
                    "error": str(e)
                }
            )
    
    async def _generate_data_processing_solution(self, description: str, context: Dict[str, Any]) -> str:
        """生成数据处理解决方案"""
        return '''
import pandas as pd
import json

# 数据处理解决方案
def process_data(data):
    """处理数据的通用函数"""
    if isinstance(data, str):
        # 假设是文件路径或JSON字符串
        try:
            # 尝试作为JSON处理
            data = json.loads(data)
        except:
            # 假设是CSV文件路径
            data = pd.read_csv(data)
    
    # 基本数据处理
    if isinstance(data, pd.DataFrame):
        result = data.describe()
        print("数据统计信息:")
        print(result)
        return result
    else:
        print("处理的数据:", data)
        return data

# 执行数据处理
result = process_data("test_data")
print("处理完成")
'''
    
    async def _generate_api_integration_solution(self, description: str, context: Dict[str, Any]) -> str:
        """生成API集成解决方案"""
        return '''
import requests
import json

def call_api(url, method="GET", data=None, headers=None):
    """通用API调用函数"""
    try:
        if headers is None:
            headers = {"Content-Type": "application/json"}
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.request(method, url, json=data, headers=headers)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"API调用失败: {e}")
        return None

# 示例API调用
result = call_api("https://httpbin.org/get")
print("API调用结果:", result)
'''
    
    async def _generate_tool_creation_solution(self, description: str, context: Dict[str, Any]) -> str:
        """生成工具创建解决方案"""
        return '''
def create_utility_tool(*args, **kwargs):
    """创建的通用工具函数"""
    print("工具执行中...")
    print("参数:", args)
    print("关键字参数:", kwargs)
    
    # 工具逻辑
    result = {"status": "success", "message": "工具执行完成"}
    return result

# 测试工具
tool_result = create_utility_tool("test", value=42)
print("工具结果:", tool_result)
'''
    
    async def _generate_algorithm_solution(self, description: str, context: Dict[str, Any]) -> str:
        """生成算法解决方案"""
        return '''
def algorithm_solution(data):
    """算法解决方案"""
    if not data:
        return []
    
    # 示例排序算法
    if isinstance(data, list):
        # 快速排序实现
        if len(data) <= 1:
            return data
        
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        
        return algorithm_solution(left) + middle + algorithm_solution(right)
    
    return data

# 测试算法
test_data = [3, 6, 8, 10, 1, 2, 1]
sorted_data = algorithm_solution(test_data)
print("原数据:", test_data)
print("排序结果:", sorted_data)
'''
    
    async def _generate_general_solution(self, description: str, context: Dict[str, Any]) -> str:
        """生成通用解决方案"""
        return '''
def general_solution():
    """通用问题解决方案"""
    print("正在分析问题...")
    
    # 基本问题解决逻辑
    steps = [
        "1. 问题理解",
        "2. 方案设计", 
        "3. 实施解决",
        "4. 结果验证"
    ]
    
    for step in steps:
        print(step)
    
    result = {
        "status": "completed",
        "steps_executed": len(steps),
        "message": "问题解决完成"
    }
    
    return result

# 执行解决方案
solution_result = general_solution()
print("解决方案执行结果:", solution_result)
'''
    
    def _generate_explanation(self, problem_type: ProblemType, solution_code: str) -> str:
        """生成解决方案说明"""
        explanations = {
            ProblemType.DATA_PROCESSING: "这个解决方案使用pandas库处理数据，包含数据读取、处理和分析功能。",
            ProblemType.API_INTEGRATION: "这个解决方案提供了通用的API调用功能，支持GET/POST等HTTP方法。",
            ProblemType.TOOL_CREATION: "这个解决方案创建了一个可复用的工具函数，可以处理各种参数输入。",
            ProblemType.ALGORITHM_DESIGN: "这个解决方案实现了快速排序算法，展示了分治法的应用。",
            ProblemType.DEBUGGING: "这个解决方案包含了调试和错误处理的最佳实践。",
            ProblemType.SYSTEM_INTEGRATION: "这个解决方案提供了系统集成的通用框架。"
        }
        
        base_explanation = explanations.get(problem_type, "这是一个通用的问题解决方案。")
        
        # 分析代码特征
        code_features = []
        if "import pandas" in solution_code:
            code_features.append("使用了pandas进行数据处理")
        if "import requests" in solution_code:
            code_features.append("包含HTTP请求功能")
        if "def " in solution_code:
            func_count = solution_code.count("def ")
            code_features.append(f"定义了{func_count}个函数")
        
        if code_features:
            base_explanation += " 具体特征: " + "、".join(code_features) + "。"
        
        return base_explanation
    
    async def _create_reusable_tool(self, solution: ProblemSolution) -> bool:
        """创建可复用工具"""
        try:
            # 从解决方案代码中提取主函数
            code_lines = solution.solution_code.strip().split('\n')
            
            # 找到函数定义
            for i, line in enumerate(code_lines):
                if line.strip().startswith('def ') and not line.strip().startswith('def algorithm_solution'):
                    # 提取函数名
                    func_name = line.split('def ')[1].split('(')[0].strip()
                    
                    # 创建工具
                    tool_created = self.tool_manager.create_tool_from_code(
                        name=func_name,
                        description=f"从问题解决方案中创建的工具: {solution.problem_description[:100]}",
                        code=solution.solution_code,
                        parameters={"generated_from": "problem_solution"}
                    )
                    
                    if tool_created:
                        logger.info(f"成功创建可复用工具: {func_name}")
                        return True
                    break
            
            return False
            
        except Exception as e:
            logger.error(f"创建可复用工具失败: {str(e)}")
            return False
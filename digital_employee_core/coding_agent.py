"""
CodingAgent - 编程问题解决Agent

当现有Agent无法通过现有工具和信息解决问题时，CodingAgent作为最终解决方案，
通过编程方式解决工程、检索、工具使用等复杂问题。

核心能力：
- 代码生成和执行
- 自定义工具创建
- 复杂问题分解和解决
- 安全代码执行环境
- 工具库动态扩展

版本: 1.0.0
作者: Digital Employee System Team
"""

import ast
import sys
import os
import subprocess
import tempfile
import uuid
import json
import time
import logging
import traceback
import inspect
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import threading
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from io import StringIO
import importlib.util
import pickle

# 安全相关
import re
import hashlib
from pathlib import Path

# 导入基础Agent框架
from .agent_implementations import BaseAgent, AgentRole, AgentCapability, Task, TaskStatus

logger = logging.getLogger(__name__)

# ================================
# 核心数据模型
# ================================

class CodeExecutionResult(Enum):
    """代码执行结果状态"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    SECURITY_VIOLATION = "security_violation"
    COMPILATION_ERROR = "compilation_error"

class ProblemType(Enum):
    """问题类型分类"""
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration"
    TOOL_CREATION = "tool_creation"
    ALGORITHM_DESIGN = "algorithm_design"
    SYSTEM_INTEGRATION = "system_integration"
    DEBUGGING = "debugging"
    OPTIMIZATION = "optimization"
    CUSTOM_SOLUTION = "custom_solution"

@dataclass
class CodeExecutionContext:
    """代码执行上下文"""
    execution_id: str
    code: str
    language: str = "python"
    timeout: float = 30.0
    memory_limit: int = 128  # MB
    allowed_imports: List[str] = None
    restricted_functions: List[str] = None
    workspace_path: str = None
    
    def __post_init__(self):
        if self.allowed_imports is None:
            self.allowed_imports = [
                'json', 'math', 'datetime', 'collections', 'itertools',
                'os', 'sys', 'pathlib', 'typing', 'dataclasses',
                'requests', 'pandas', 'numpy', 'sqlite3', 'csv',
                'logging', 'time', 'uuid', 're', 'hashlib'
            ]
        if self.restricted_functions is None:
            self.restricted_functions = [
                'exec', 'eval', 'compile', '__import__', 'open',
                'input', 'raw_input', 'file', 'execfile', 'reload'
            ]
        if self.workspace_path is None:
            self.workspace_path = tempfile.mkdtemp(prefix=f"coding_agent_{self.execution_id}_")

@dataclass
class ToolDefinition:
    """工具定义"""
    tool_id: str
    name: str
    description: str
    function_code: str
    parameters: Dict[str, Any]
    return_type: str
    created_at: float
    version: str = "1.0.0"
    dependencies: List[str] = None
    test_cases: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.test_cases is None:
            self.test_cases = []

@dataclass
class ProblemSolution:
    """问题解决方案"""
    problem_id: str
    problem_description: str
    problem_type: ProblemType
    solution_code: str
    solution_description: str
    created_tools: List[ToolDefinition]
    execution_results: List[Dict[str, Any]]
    confidence_score: float
    execution_time: float
    memory_usage: int
    created_at: float

# ================================
# 安全代码执行环境
# ================================

class SecureCodeExecutor:
    """安全代码执行器"""
    
    def __init__(self):
        self.execution_history = []
        self.created_functions = {}
        
    def validate_code_security(self, code: str, context: CodeExecutionContext) -> Dict[str, Any]:
        """验证代码安全性"""
        security_issues = []
        
        # 检查危险函数调用
        for restricted_func in context.restricted_functions:
            if re.search(rf'\b{restricted_func}\s*\(', code):
                security_issues.append(f"使用了受限函数: {restricted_func}")
        
        # 检查文件系统操作
        file_operations = ['open', 'file', 'write', 'delete', 'remove', 'unlink']
        for op in file_operations:
            if re.search(rf'\b{op}\s*\(', code):
                security_issues.append(f"包含文件系统操作: {op}")
        
        # 检查网络操作
        network_patterns = [
            r'import\s+socket', r'from\s+socket', r'urllib', r'http\.client',
            r'subprocess', r'os\.system', r'os\.popen'
        ]
        for pattern in network_patterns:
            if re.search(pattern, code):
                security_issues.append(f"包含网络或系统调用: {pattern}")
        
        # 检查导入限制
        import_pattern = r'import\s+(\w+)|from\s+(\w+)\s+import'
        imports = re.findall(import_pattern, code)
        for imp in imports:
            module = imp[0] or imp[1]
            if module and module not in context.allowed_imports:
                security_issues.append(f"导入了未授权模块: {module}")
        
        return {
            "is_safe": len(security_issues) == 0,
            "issues": security_issues,
            "risk_level": "high" if security_issues else "low"
        }
    
    def execute_code(self, context: CodeExecutionContext) -> Dict[str, Any]:
        """执行代码"""
        start_time = time.time()
        
        # 安全性验证
        security_check = self.validate_code_security(context.code, context)
        if not security_check["is_safe"]:
            return {
                "status": CodeExecutionResult.SECURITY_VIOLATION,
                "error": f"安全检查失败: {'; '.join(security_check['issues'])}",
                "output": "",
                "execution_time": 0,
                "memory_usage": 0
            }
        
        # 创建执行环境
        execution_globals = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'bool': bool, 'type': type, 'isinstance': isinstance,
                'hasattr': hasattr, 'getattr': getattr, 'setattr': setattr,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'map': map, 'filter': filter, 'sorted': sorted,
                'max': max, 'min': min, 'sum': sum, 'any': any, 'all': all,
                'print': print, 'repr': repr, 'abs': abs, 'round': round
            }
        }
        
        # 添加允许的模块
        for module_name in context.allowed_imports:
            try:
                module = __import__(module_name)
                execution_globals[module_name] = module
            except ImportError:
                logger.warning(f"无法导入模块: {module_name}")
        
        # 捕获输出
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            # 使用超时执行
            with self._timeout(context.timeout):
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # 编译代码
                    compiled_code = compile(context.code, '<string>', 'exec')
                    
                    # 执行代码
                    exec(compiled_code, execution_globals)
            
            execution_time = time.time() - start_time
            
            # 提取返回值（如果有的话）
            result_value = execution_globals.get('result', None)
            
            return {
                "status": CodeExecutionResult.SUCCESS,
                "output": stdout_capture.getvalue(),
                "error": stderr_capture.getvalue(),
                "result": result_value,
                "execution_time": execution_time,
                "memory_usage": self._estimate_memory_usage(),
                "globals": {k: v for k, v in execution_globals.items() 
                           if not k.startswith('__') and callable(v)}
            }
            
        except SyntaxError as e:
            return {
                "status": CodeExecutionResult.COMPILATION_ERROR,
                "error": f"语法错误: {str(e)}",
                "output": stdout_capture.getvalue(),
                "execution_time": time.time() - start_time,
                "memory_usage": 0
            }
            
        except TimeoutError:
            return {
                "status": CodeExecutionResult.TIMEOUT,
                "error": f"执行超时 (>{context.timeout}s)",
                "output": stdout_capture.getvalue(),
                "execution_time": context.timeout,
                "memory_usage": 0
            }
            
        except Exception as e:
            return {
                "status": CodeExecutionResult.ERROR,
                "error": f"运行时错误: {str(e)}\n{traceback.format_exc()}",
                "output": stdout_capture.getvalue(),
                "execution_time": time.time() - start_time,
                "memory_usage": 0
            }
    
    @contextmanager
    def _timeout(self, seconds):
        """超时上下文管理器"""
        def timeout_handler():
            raise TimeoutError()
        
        timer = threading.Timer(seconds, timeout_handler)
        timer.start()
        try:
            yield
        finally:
            timer.cancel()
    
    def _estimate_memory_usage(self) -> int:
        """估算内存使用量 (简化实现)"""
        import psutil
        process = psutil.Process(os.getpid())
        return int(process.memory_info().rss / 1024 / 1024)  # MB

# ================================
# 动态工具管理器
# ================================

class DynamicToolManager:
    """动态工具管理器"""
    
    def __init__(self):
        self.tools_registry = {}
        self.tool_dependencies = {}
        
    def create_tool_from_code(self, tool_def: ToolDefinition) -> Dict[str, Any]:
        """从代码创建工具"""
        try:
            # 创建执行上下文
            context = CodeExecutionContext(
                execution_id=f"tool_{tool_def.tool_id}",
                code=tool_def.function_code,
                timeout=10.0
            )
            
            # 执行工具代码
            executor = SecureCodeExecutor()
            result = executor.execute_code(context)
            
            if result["status"] == CodeExecutionResult.SUCCESS:
                # 提取创建的函数
                tool_functions = result.get("globals", {})
                
                if tool_functions:
                    # 注册工具
                    self.tools_registry[tool_def.tool_id] = {
                        "definition": tool_def,
                        "functions": tool_functions,
                        "created_at": time.time()
                    }
                    
                    # 运行测试用例
                    test_results = self._run_tool_tests(tool_def, tool_functions)
                    
                    return {
                        "success": True,
                        "tool_id": tool_def.tool_id,
                        "functions": list(tool_functions.keys()),
                        "test_results": test_results
                    }
                else:
                    return {
                        "success": False,
                        "error": "未找到可用的工具函数"
                    }
            else:
                return {
                    "success": False,
                    "error": result["error"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"工具创建失败: {str(e)}"
            }
    
    def _run_tool_tests(self, tool_def: ToolDefinition, functions: Dict[str, Callable]) -> List[Dict[str, Any]]:
        """运行工具测试"""
        if not tool_def.test_cases:
            return []
        
        test_results = []
        for i, test_case in enumerate(tool_def.test_cases):
            try:
                func_name = test_case.get("function")
                if func_name in functions:
                    func = functions[func_name]
                    args = test_case.get("args", [])
                    kwargs = test_case.get("kwargs", {})
                    expected = test_case.get("expected")
                    
                    result = func(*args, **kwargs)
                    
                    test_results.append({
                        "test_id": i,
                        "function": func_name,
                        "passed": result == expected if expected is not None else True,
                        "result": result,
                        "expected": expected
                    })
                else:
                    test_results.append({
                        "test_id": i,
                        "function": func_name,
                        "passed": False,
                        "error": f"函数 {func_name} 不存在"
                    })
            except Exception as e:
                test_results.append({
                    "test_id": i,
                    "passed": False,
                    "error": str(e)
                })
        
        return test_results
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """获取工具"""
        return self.tools_registry.get(tool_id)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return [
            {
                "tool_id": tool_id,
                "name": tool_data["definition"].name,
                "description": tool_data["definition"].description,
                "functions": list(tool_data["functions"].keys()),
                "created_at": tool_data["created_at"]
            }
            for tool_id, tool_data in self.tools_registry.items()
        ]

# ================================
# 问题分析器
# ================================

class ProblemAnalyzer:
    """问题分析器"""
    
    def __init__(self):
        self.problem_patterns = {
            ProblemType.DATA_PROCESSING: [
                r'数据处理', r'数据分析', r'清洗数据', r'转换格式',
                r'pandas', r'numpy', r'csv', r'json', r'excel'
            ],
            ProblemType.API_INTEGRATION: [
                r'API', r'接口', r'调用', r'requests', r'http',
                r'REST', r'GraphQL', r'webhook'
            ],
            ProblemType.TOOL_CREATION: [
                r'创建工具', r'自定义函数', r'工具函数', r'辅助函数'
            ],
            ProblemType.ALGORITHM_DESIGN: [
                r'算法', r'排序', r'搜索', r'优化', r'计算',
                r'递归', r'动态规划', r'贪心'
            ],
            ProblemType.SYSTEM_INTEGRATION: [
                r'系统集成', r'模块集成', r'服务集成', r'数据库连接'
            ],
            ProblemType.DEBUGGING: [
                r'调试', r'错误', r'bug', r'异常', r'问题排查'
            ],
            ProblemType.OPTIMIZATION: [
                r'优化', r'性能', r'效率', r'速度', r'内存'
            ]
        }
    
    def analyze_problem(self, problem_description: str) -> Dict[str, Any]:
        """分析问题类型和复杂度"""
        problem_description_lower = problem_description.lower()
        
        # 识别问题类型
        detected_types = []
        for problem_type, patterns in self.problem_patterns.items():
            for pattern in patterns:
                if re.search(pattern, problem_description_lower):
                    detected_types.append(problem_type)
                    break
        
        if not detected_types:
            detected_types = [ProblemType.CUSTOM_SOLUTION]
        
        # 评估复杂度
        complexity_indicators = {
            'simple': ['简单', '基础', '直接', '快速'],
            'medium': ['复杂', '多步', '集成', '处理'],
            'complex': ['复杂系统', '多模块', '高性能', '大规模', '企业级']
        }
        
        complexity = 'simple'
        for level, indicators in complexity_indicators.items():
            if any(indicator in problem_description_lower for indicator in indicators):
                complexity = level
        
        # 提取关键信息
        key_entities = self._extract_key_entities(problem_description)
        
        return {
            "problem_types": detected_types,
            "primary_type": detected_types[0] if detected_types else ProblemType.CUSTOM_SOLUTION,
            "complexity": complexity,
            "key_entities": key_entities,
            "estimated_effort": self._estimate_effort(complexity, len(detected_types)),
            "recommended_approach": self._recommend_approach(detected_types[0] if detected_types else ProblemType.CUSTOM_SOLUTION)
        }
    
    def _extract_key_entities(self, text: str) -> List[str]:
        """提取关键实体"""
        # 简化的实体提取
        entities = []
        
        # 提取技术栈
        tech_patterns = [
            r'\b(python|javascript|java|c\+\+|sql|html|css)\b',
            r'\b(pandas|numpy|requests|flask|django|fastapi)\b',
            r'\b(mysql|postgresql|mongodb|redis|sqlite)\b',
            r'\b(api|rest|graphql|json|xml|csv|excel)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text.lower())
            entities.extend(matches)
        
        return list(set(entities))
    
    def _estimate_effort(self, complexity: str, type_count: int) -> Dict[str, Any]:
        """估算工作量"""
        base_time = {
            'simple': 5,    # 5分钟
            'medium': 15,   # 15分钟  
            'complex': 45   # 45分钟
        }
        
        estimated_time = base_time[complexity] * (1 + type_count * 0.3)
        
        return {
            "estimated_time_minutes": int(estimated_time),
            "complexity_level": complexity,
            "confidence": 0.7 if complexity == 'simple' else 0.6 if complexity == 'medium' else 0.5
        }
    
    def _recommend_approach(self, problem_type: ProblemType) -> Dict[str, Any]:
        """推荐解决方案"""
        approaches = {
            ProblemType.DATA_PROCESSING: {
                "strategy": "数据管道方法",
                "tools": ["pandas", "numpy"],
                "steps": ["数据加载", "清洗验证", "转换处理", "结果输出"]
            },
            ProblemType.API_INTEGRATION: {
                "strategy": "API客户端方法", 
                "tools": ["requests", "json"],
                "steps": ["接口分析", "请求构建", "响应处理", "错误处理"]
            },
            ProblemType.TOOL_CREATION: {
                "strategy": "函数式设计",
                "tools": ["typing", "dataclasses"],
                "steps": ["需求分析", "接口设计", "实现编码", "测试验证"]
            },
            ProblemType.ALGORITHM_DESIGN: {
                "strategy": "分治算法",
                "tools": ["math", "collections"],
                "steps": ["问题分解", "算法设计", "复杂度分析", "优化实现"]
            }
        }
        
        return approaches.get(problem_type, {
            "strategy": "自定义解决方案",
            "tools": ["根据需求确定"],
            "steps": ["问题分析", "方案设计", "编码实现", "测试验证"]
        })
# Coding Agent工具管理器
# 版本: 2.0.0 - 统一治理版本

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

logger = logging.getLogger(__name__)

# ================================
# 核心数据模型  
# ================================

class ProblemType(Enum):
    DATA_PROCESSING = "data_processing"
    API_INTEGRATION = "api_integration" 
    TOOL_CREATION = "tool_creation"
    ALGORITHM_DESIGN = "algorithm_design"
    DEBUGGING = "debugging"
    SYSTEM_INTEGRATION = "system_integration"

@dataclass
class CodeExecutionContext:
    """代码执行上下文配置"""
    timeout: int = 30
    max_memory_mb: int = 256
    allowed_imports: List[str] = None
    forbidden_patterns: List[str] = None
    sandbox_enabled: bool = True
    log_execution: bool = True
    
    def __post_init__(self):
        if self.allowed_imports is None:
            self.allowed_imports = [
                'json', 'csv', 'datetime', 'math', 'random', 'urllib', 'requests',
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'sqlite3', 're'
            ]
        
        if self.forbidden_patterns is None:
            self.forbidden_patterns = [
                r'import\s+os\s*\.\s*system',
                r'subprocess\.',
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__',
                r'open\s*\(',
                r'file\s*\(',
                r'input\s*\(',
                r'raw_input\s*\('
            ]

@dataclass
class CodeExecutionResult:
    """代码执行结果"""
    success: bool
    output: str
    error: str = ""
    execution_time: float = 0.0
    memory_used: int = 0
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    function: callable
    parameters: Dict[str, Any]
    examples: List[str] = None
    tags: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = time.strftime('%Y-%m-%d %H:%M:%S')

@dataclass
class ProblemSolution:
    """问题解决方案"""
    problem_description: str
    solution_code: str
    explanation: str
    test_cases: List[Dict[str, Any]] = None
    performance_metrics: Dict[str, Any] = None
    created_tools: List[ToolDefinition] = None
    
    def __post_init__(self):
        if self.test_cases is None:
            self.test_cases = []
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.created_tools is None:
            self.created_tools = []

# ================================
# 安全代码执行器
# ================================

class SecureCodeExecutor:
    """安全代码执行器"""
    
    def __init__(self, context: CodeExecutionContext = None):
        self.context = context or CodeExecutionContext()
        self.execution_history = []
        logger.info("安全代码执行器初始化完成")
    
    async def execute_code(self, code: str, context_vars: Dict[str, Any] = None) -> CodeExecutionResult:
        """安全执行代码"""
        start_time = time.time()
        
        try:
            # 1. 安全检查
            security_check = self._security_check(code)
            if not security_check["safe"]:
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error=f"安全检查失败: {security_check['reason']}",
                    execution_time=time.time() - start_time
                )
            
            # 2. 准备执行环境
            execution_globals = self._prepare_execution_environment(context_vars or {})
            
            # 3. 执行代码
            result = await self._execute_in_sandbox(code, execution_globals)
            
            # 4. 记录执行历史
            self.execution_history.append({
                "code": code,
                "result": result,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return result
            
        except Exception as e:
            logger.error(f"代码执行失败: {str(e)}")
            return CodeExecutionResult(
                success=False,
                output="",
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _security_check(self, code: str) -> Dict[str, Any]:
        """安全检查"""
        # 检查禁用模式
        for pattern in self.context.forbidden_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return {
                    "safe": False,
                    "reason": f"代码包含禁用模式: {pattern}"
                }
        
        # 检查导入语句
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in self.context.allowed_imports:
                            return {
                                "safe": False,
                                "reason": f"不允许导入模块: {alias.name}"
                            }
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in self.context.allowed_imports:
                        return {
                            "safe": False,
                            "reason": f"不允许从模块导入: {node.module}"
                        }
        except SyntaxError as e:
            return {
                "safe": False,
                "reason": f"语法错误: {str(e)}"
            }
        
        return {"safe": True}
    
    def _prepare_execution_environment(self, context_vars: Dict[str, Any]) -> Dict[str, Any]:
        """准备执行环境"""
        # 基础安全环境
        execution_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sorted': sorted,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'type': type,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr
            }
        }
        
        # 添加允许的模块
        for module_name in self.context.allowed_imports:
            try:
                module = __import__(module_name)
                execution_globals[module_name] = module
            except ImportError:
                logger.warning(f"无法导入模块: {module_name}")
        
        # 添加上下文变量
        execution_globals.update(context_vars)
        
        return execution_globals
    
    async def _execute_in_sandbox(self, code: str, execution_globals: Dict[str, Any]) -> CodeExecutionResult:
        """在沙箱中执行代码"""
        start_time = time.time()
        
        # 捕获输出
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # 编译代码
                compiled_code = compile(code, '<sandbox>', 'exec')
                
                # 执行代码
                exec(compiled_code, execution_globals)
            
            execution_time = time.time() - start_time
            
            return CodeExecutionResult(
                success=True,
                output=stdout_capture.getvalue(),
                error=stderr_capture.getvalue(),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return CodeExecutionResult(
                success=False,
                output=stdout_capture.getvalue(),
                error=f"{type(e).__name__}: {str(e)}\\n{traceback.format_exc()}",
                execution_time=execution_time
            )

# ================================
# 动态工具管理器
# ================================

class DynamicToolManager:
    """动态工具管理器"""
    
    def __init__(self):
        self.tools = {}
        self.tool_usage_stats = {}
        logger.info("动态工具管理器初始化完成")
    
    def register_tool(self, tool: ToolDefinition) -> bool:
        """注册工具"""
        try:
            # 验证工具函数
            if not callable(tool.function):
                raise ValueError("工具函数必须是可调用对象")
            
            # 注册工具
            self.tools[tool.name] = tool
            self.tool_usage_stats[tool.name] = {
                "usage_count": 0,
                "success_count": 0,
                "last_used": None
            }
            
            logger.info(f"工具 '{tool.name}' 注册成功")
            return True
            
        except Exception as e:
            logger.error(f"工具注册失败: {str(e)}")
            return False
    
    def use_tool(self, tool_name: str, *args, **kwargs) -> Any:
        """使用工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        
        tool = self.tools[tool_name]
        
        try:
            # 更新使用统计
            self.tool_usage_stats[tool_name]["usage_count"] += 1
            self.tool_usage_stats[tool_name]["last_used"] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 执行工具函数
            result = tool.function(*args, **kwargs)
            
            # 更新成功统计
            self.tool_usage_stats[tool_name]["success_count"] += 1
            
            logger.info(f"工具 '{tool_name}' 执行成功")
            return result
            
        except Exception as e:
            logger.error(f"工具 '{tool_name}' 执行失败: {str(e)}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取工具信息"""
        if tool_name not in self.tools:
            return None
        
        tool = self.tools[tool_name]
        stats = self.tool_usage_stats[tool_name]
        
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "examples": tool.examples,
            "tags": tool.tags,
            "created_at": tool.created_at,
            "usage_stats": stats
        }
    
    def create_tool_from_code(self, name: str, description: str, code: str, 
                            parameters: Dict[str, Any] = None) -> bool:
        """从代码创建工具"""
        try:
            # 创建函数
            exec_globals = {}
            exec(code, exec_globals)
            
            # 找到定义的函数
            tool_function = None
            for key, value in exec_globals.items():
                if callable(value) and not key.startswith('__'):
                    tool_function = value
                    break
            
            if tool_function is None:
                raise ValueError("代码中未找到可用函数")
            
            # 创建工具定义
            tool = ToolDefinition(
                name=name,
                description=description,
                function=tool_function,
                parameters=parameters or {},
                tags=["custom", "generated"]
            )
            
            return self.register_tool(tool)
            
        except Exception as e:
            logger.error(f"从代码创建工具失败: {str(e)}")
            return False

# ================================
# 问题分析器
# ================================

class ProblemAnalyzer:
    """问题分析器"""
    
    def __init__(self):
        self.analysis_history = []
        logger.info("问题分析器初始化完成")
    
    def analyze_problem(self, problem_description: str) -> Dict[str, Any]:
        """分析问题"""
        try:
            analysis = {
                "problem_type": self._classify_problem_type(problem_description),
                "complexity_level": self._assess_complexity(problem_description),
                "required_skills": self._identify_required_skills(problem_description),
                "suggested_approach": self._suggest_approach(problem_description),
                "key_entities": self._extract_key_entities(problem_description),
                "estimated_effort": self._estimate_effort(problem_description)
            }
            
            # 记录分析历史
            self.analysis_history.append({
                "problem": problem_description,
                "analysis": analysis,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return analysis
            
        except Exception as e:
            logger.error(f"问题分析失败: {str(e)}")
            return {
                "error": str(e),
                "problem_type": ProblemType.DEBUGGING,
                "complexity_level": 1,
                "required_skills": [],
                "suggested_approach": "错误分析",
                "key_entities": [],
                "estimated_effort": "unknown"
            }
    
    def _classify_problem_type(self, description: str) -> ProblemType:
        """分类问题类型"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ['数据', 'data', '处理', 'process', 'csv', 'json']):
            return ProblemType.DATA_PROCESSING
        elif any(keyword in description_lower for keyword in ['api', '接口', 'request', 'http', 'rest']):
            return ProblemType.API_INTEGRATION
        elif any(keyword in description_lower for keyword in ['工具', 'tool', '函数', 'function']):
            return ProblemType.TOOL_CREATION
        elif any(keyword in description_lower for keyword in ['算法', '排序', 'algorithm', 'sort']):
            return ProblemType.ALGORITHM_DESIGN
        elif any(keyword in description_lower for keyword in ['错误', 'error', 'bug', '调试', 'debug']):
            return ProblemType.DEBUGGING
        else:
            return ProblemType.SYSTEM_INTEGRATION
    
    def _assess_complexity(self, description: str) -> int:
        """评估复杂度 (1-10)"""
        complexity_indicators = {
            'simple': ['简单', 'basic', '基础', 'easy'],
            'medium': ['复杂', 'complex', '多步骤', 'multiple'],
            'hard': ['困难', 'difficult', '高级', 'advanced', '优化', 'optimize']
        }
        
        description_lower = description.lower()
        
        if any(indicator in description_lower for indicator in complexity_indicators['hard']):
            return 8
        elif any(indicator in description_lower for indicator in complexity_indicators['medium']):
            return 5
        else:
            return 3
    
    def _identify_required_skills(self, description: str) -> List[str]:
        """识别所需技能"""
        skill_keywords = {
            'python': ['python', 'py'],
            'data_analysis': ['数据分析', 'data analysis', 'pandas', 'numpy'],
            'web_scraping': ['爬虫', 'scraping', 'requests', 'beautifulsoup'],
            'api_integration': ['api', '接口', 'rest', 'json'],
            'database': ['数据库', 'database', 'sql', 'sqlite'],
            'file_processing': ['文件', 'file', 'csv', 'excel'],
            'algorithm': ['算法', 'algorithm', '排序', 'sort']
        }
        
        description_lower = description.lower()
        required_skills = []
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                required_skills.append(skill)
        
        return required_skills or ['general_programming']
    
    def _suggest_approach(self, description: str) -> str:
        """建议解决方法"""
        problem_type = self._classify_problem_type(description)
        
        approach_map = {
            ProblemType.DATA_PROCESSING: "1. 数据读取和清洗 2. 数据处理和转换 3. 结果输出",
            ProblemType.API_INTEGRATION: "1. API调用设计 2. 数据格式处理 3. 错误处理和重试",
            ProblemType.TOOL_CREATION: "1. 功能设计 2. 代码实现 3. 测试和优化",
            ProblemType.ALGORITHM_DESIGN: "1. 算法分析 2. 数据结构选择 3. 性能优化",
            ProblemType.DEBUGGING: "1. 错误重现 2. 问题定位 3. 解决方案实施",
            ProblemType.SYSTEM_INTEGRATION: "1. 系统分析 2. 接口设计 3. 集成测试"
        }
        
        return approach_map.get(problem_type, "1. 问题分析 2. 方案设计 3. 实施验证")
    
    def _extract_key_entities(self, text: str) -> List[str]:
        """提取关键实体"""
        # 简化的关键词提取
        import re
        
        # 提取可能的文件名、URL、技术名词等
        entities = []
        
        # 文件名模式
        file_patterns = re.findall(r'[\w\-_]+\.[a-zA-Z]{2,4}', text)
        entities.extend(file_patterns)
        
        # URL模式
        url_patterns = re.findall(r'https?://[\w\-\._~:/?#[\]@!$&\'()*+,;=]+', text)
        entities.extend(url_patterns)
        
        # 技术关键词
        tech_keywords = ['python', 'pandas', 'numpy', 'requests', 'json', 'csv', 'sql', 'api']
        for keyword in tech_keywords:
            if keyword.lower() in text.lower():
                entities.append(keyword)
        
        return list(set(entities))[:10]  # 限制返回数量
    
    def _estimate_effort(self, description: str) -> str:
        """估算工作量"""
        complexity = self._assess_complexity(description)
        required_skills = self._identify_required_skills(description)
        
        if complexity >= 7 or len(required_skills) >= 4:
            return "high (2-4 hours)"
        elif complexity >= 4 or len(required_skills) >= 2:
            return "medium (30min-2hours)"
        else:
            return "low (5-30min)"
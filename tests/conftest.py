"""
AI系统测试配置文件
专业的测试环境配置和固定装置
"""

import pytest
import asyncio
import json
import os
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock
from dataclasses import dataclass

from digital_employee.core.ai_service import (
    AIService, AIResponse, AIMessage, AIProvider,
    OpenAIService, AnthropicService, LocalAIService,
    AIServiceManager
)


@dataclass
class MockAIResponse:
    """标准化的Mock AI响应"""
    content: str
    model: str = "mock-model"
    usage_tokens: int = 100
    confidence_score: float = 0.85
    error: str = None


class DeterministicAIService(AIService):
    """确定性AI服务 - 用于单元测试"""
    
    def __init__(self, response_map: Dict[str, str] = None):
        super().__init__("deterministic-test-model")
        self.response_map = response_map or {}
        self.default_responses = {
            "requirement_analysis": {
                "functional_requirements": ["用户管理", "数据处理", "API接口"],
                "non_functional_requirements": ["性能要求", "安全要求", "可用性要求"],
                "assumptions": ["假设用户规模中等", "假设使用标准技术栈"]
            },
            "solution_design": {
                "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis"],
                "architecture_components": ["API网关", "业务服务", "数据层", "缓存层"]
            },
            "code_generation": {
                "code_example": """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.post("/users/")
async def create_user(user: User):
    # 创建用户逻辑
    return {"message": "用户创建成功", "user": user}
"""
            }
        }
    
    def _sanitize_input(self, user_input: str) -> str:
        """安全过滤用户输入"""
        # 移除潜在的恶意内容
        dangerous_patterns = [
            "drop table", "script", "javascript", "onclick", 
            "onerror", "onload", "eval", "exec", "../", 
            "passwd", "shadow", "hosts"
        ]
        
        safe_input = user_input
        for pattern in dangerous_patterns:
            safe_input = safe_input.replace(pattern, "[FILTERED]")
            safe_input = safe_input.replace(pattern.upper(), "[FILTERED]")
        
        # 移除控制字符
        safe_input = ''.join(char for char in safe_input if ord(char) >= 32 or char in '\n\r\t')
        
        return safe_input
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AIResponse:
        """基于输入内容返回确定性响应"""
        
        user_input = ""
        for msg in messages:
            if msg.role == "user":
                user_input = msg.content.lower()
                break
        
        # 尝试从响应映射中查找
        for key, response in self.response_map.items():
            if key.lower() in user_input:
                return AIResponse(
                    content=response,
                    model=self.model,
                    usage_tokens=100,
                    confidence_score=0.9
                )
        
        # 使用默认响应模式
        if "需求分析" in user_input or "requirement" in user_input or "电商系统" in user_input or "博客系统" in user_input:
            content = json.dumps(self.default_responses["requirement_analysis"], ensure_ascii=False, indent=2)
        elif "方案设计" in user_input or "solution" in user_input or "架构" in user_input:
            content = json.dumps(self.default_responses["solution_design"], ensure_ascii=False, indent=2)
        elif "代码生成" in user_input or "code" in user_input or "API接口" in user_input:
            content = json.dumps(self.default_responses["code_generation"], ensure_ascii=False, indent=2)
        else:
            # 为其他情况提供更详细的默认响应，同时进行安全过滤
            safe_input = self._sanitize_input(user_input)
            content = json.dumps({
                "response_type": "general_analysis",
                "analysis": f"针对技术需求的分析",
                "recommendations": ["进一步澄清需求", "制定实施计划", "评估技术方案"],
                "confidence_level": "medium",
                "original_request_length": len(user_input)
            }, ensure_ascii=False, indent=2)
        
        self.request_count += 1
        
        return AIResponse(
            content=content,
            model=self.model,
            usage_tokens=100,
            confidence_score=0.85
        )


class QualityMetricsCollector:
    """质量指标收集器"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置指标"""
        self.response_times = []
        self.success_count = 0
        self.failure_count = 0
        self.confidence_scores = []
        self.token_usage = []
        self.error_types = {}
    
    def record_response(self, response_time: float, success: bool, 
                       confidence_score: float = None, tokens: int = None, 
                       error_type: str = None):
        """记录响应指标"""
        self.response_times.append(response_time)
        
        if success:
            self.success_count += 1
            if confidence_score:
                self.confidence_scores.append(confidence_score)
            if tokens:
                self.token_usage.append(tokens)
        else:
            self.failure_count += 1
            if error_type:
                self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取质量指标"""
        total_requests = self.success_count + self.failure_count
        
        if not total_requests:
            return {"message": "无数据"}
        
        return {
            "total_requests": total_requests,
            "success_rate": self.success_count / total_requests,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "p95_response_time": sorted(self.response_times)[int(len(self.response_times) * 0.95)] if self.response_times else 0,
            "avg_confidence_score": sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0,
            "avg_token_usage": sum(self.token_usage) / len(self.token_usage) if self.token_usage else 0,
            "error_distribution": self.error_types
        }


# 全局质量指标收集器
quality_metrics = QualityMetricsCollector()


@pytest.fixture
def deterministic_ai_service():
    """确定性AI服务固定装置"""
    return DeterministicAIService()


@pytest.fixture
def mock_ai_service():
    """Mock AI服务固定装置"""
    service = Mock(spec=AIService)
    service.model = "mock-model"
    service.request_count = 0
    service.total_tokens = 0
    
    async def mock_generate_response(messages, temperature=0.7, max_tokens=2000):
        service.request_count += 1
        service.total_tokens += 100
        
        return AIResponse(
            content="Mock AI响应",
            model=service.model,
            usage_tokens=100,
            confidence_score=0.8
        )
    
    service.generate_response = AsyncMock(side_effect=mock_generate_response)
    service.get_statistics.return_value = {
        "provider": "MockService",
        "model": "mock-model",
        "request_count": 0,
        "total_tokens": 0
    }
    
    return service


@pytest.fixture
def ai_service_manager():
    """AI服务管理器固定装置"""
    manager = AIServiceManager()
    
    # 注册确定性服务作为主要服务
    deterministic_service = DeterministicAIService()
    manager.register_service(AIProvider.LOCAL, deterministic_service, is_primary=True)
    
    return manager


@pytest.fixture
def quality_collector():
    """质量指标收集器固定装置"""
    quality_metrics.reset()
    return quality_metrics


@pytest.fixture(scope="session")
def event_loop():
    """提供事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 测试数据集
STANDARD_TEST_CASES = {
    "requirement_analysis": [
        {
            "input": "我需要一个支持1000并发用户的电商系统",
            "expected_keywords": ["functional_requirements", "non_functional_requirements", "用户管理", "数据处理"],
            "min_confidence": 0.7
        },
        {
            "input": "开发一个简单的博客系统",
            "expected_keywords": ["functional_requirements", "用户管理", "数据处理"],
            "min_confidence": 0.7
        }
    ],
    "solution_design": [
        {
            "input": "设计一个微服务架构的Web应用",
            "expected_keywords": ["tech_stack", "architecture_components", "python", "fastapi"],
            "min_confidence": 0.7
        }
    ],
    "code_generation": [
        {
            "input": "生成一个用户注册的API接口",
            "expected_keywords": ["code_example", "fastapi", "user", "app"],
            "min_confidence": 0.6
        }
    ]
}


@pytest.fixture
def test_cases():
    """标准测试用例固定装置"""
    return STANDARD_TEST_CASES


# 性能测试基准
PERFORMANCE_BENCHMARKS = {
    "response_time_threshold": 5.0,  # 5秒响应时间阈值
    "p95_response_time_threshold": 8.0,  # P95响应时间阈值
    "min_success_rate": 0.95,  # 最低成功率95%
    "min_confidence_score": 0.7,  # 最低置信度70%
    "max_concurrent_requests": 10  # 最大并发请求数
}


@pytest.fixture
def performance_benchmarks():
    """性能基准固定装置"""
    return PERFORMANCE_BENCHMARKS


# 安全测试数据
SECURITY_TEST_INPUTS = [
    "'; DROP TABLE users; --",  # SQL注入尝试
    "<script>alert('xss')</script>",  # XSS尝试
    "../../etc/passwd",  # 路径遍历尝试
    "A" * 10000,  # 超长输入
    "\x00\x01\x02",  # 控制字符
    "{{7*7}}",  # 模板注入尝试
]


@pytest.fixture
def security_test_inputs():
    """安全测试输入固定装置"""
    return SECURITY_TEST_INPUTS
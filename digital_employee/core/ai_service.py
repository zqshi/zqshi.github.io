"""
AI服务抽象层
统一的LLM调用接口，支持多厂商切换
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import httpx

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI服务提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class AIMessage:
    """AI消息格式"""
    role: str  # system, user, assistant
    content: str


@dataclass
class AIResponse:
    """AI响应格式"""
    content: str
    model: str
    usage_tokens: int = 0
    confidence_score: float = 0.8
    error: Optional[str] = None


class AIService(ABC):
    """AI服务抽象基类"""
    
    def __init__(self, model: str, api_key: str = None):
        self.model = model
        self.api_key = api_key
        self.request_count = 0
        self.total_tokens = 0
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AIResponse:
        """生成AI响应"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            "provider": type(self).__name__,
            "model": self.model,
            "request_count": self.request_count,
            "total_tokens": self.total_tokens
        }


class OpenAIService(AIService):
    """OpenAI API服务"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(model, api_key)
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AIResponse:
        """调用OpenAI API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return AIResponse(
                        content="",
                        model=self.model,
                        error=error_msg
                    )
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage_tokens = data.get("usage", {}).get("total_tokens", 0)
                
                # 更新统计
                self.request_count += 1
                self.total_tokens += usage_tokens
                
                return AIResponse(
                    content=content,
                    model=self.model,
                    usage_tokens=usage_tokens,
                    confidence_score=0.85  # OpenAI通常质量较高
                )
                
        except Exception as e:
            error_msg = f"OpenAI API调用失败: {str(e)}"
            logger.error(error_msg)
            return AIResponse(
                content="",
                model=self.model,
                error=error_msg
            )


class AnthropicService(AIService):
    """Anthropic Claude API服务"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(model, api_key)
        self.base_url = "https://api.anthropic.com/v1"
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AIResponse:
        """调用Anthropic API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                
                # 分离系统消息和用户消息
                system_message = ""
                user_messages = []
                
                for msg in messages:
                    if msg.role == "system":
                        system_message = msg.content
                    else:
                        user_messages.append({"role": msg.role, "content": msg.content})
                
                payload = {
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": user_messages
                }
                
                if system_message:
                    payload["system"] = system_message
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return AIResponse(
                        content="",
                        model=self.model,
                        error=error_msg
                    )
                
                data = response.json()
                content = data["content"][0]["text"]
                usage_tokens = data.get("usage", {}).get("total_tokens", 0)
                
                # 更新统计
                self.request_count += 1
                self.total_tokens += usage_tokens
                
                return AIResponse(
                    content=content,
                    model=self.model,
                    usage_tokens=usage_tokens,
                    confidence_score=0.88  # Claude质量通常很高
                )
                
        except Exception as e:
            error_msg = f"Anthropic API调用失败: {str(e)}"
            logger.error(error_msg)
            return AIResponse(
                content="",
                model=self.model,
                error=error_msg
            )


class LocalAIService(AIService):
    """本地AI服务（备用降级方案）"""
    
    def __init__(self, model: str = "local-fallback"):
        super().__init__(model)
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AIResponse:
        """本地降级响应"""
        
        # 简单的规则基础响应（作为备用）
        user_input = ""
        for msg in messages:
            if msg.role == "user":
                user_input = msg.content
                break
        
        if "需求分析" in user_input or "requirement" in user_input.lower():
            content = """
            基于您的输入，我识别出以下需求：
            
            功能性需求：
            - 用户管理功能
            - 数据处理功能
            - 接口服务功能
            
            非功能性需求：
            - 性能要求
            - 安全要求
            - 可用性要求
            
            建议进一步澄清：
            - 具体的业务场景
            - 用户规模预期
            - 技术栈偏好
            """
        elif "方案设计" in user_input or "solution" in user_input.lower():
            content = """
            基于需求分析，建议的技术方案：
            
            架构设计：
            - 前后端分离架构
            - 微服务模式
            - 容器化部署
            
            技术栈选择：
            - 后端：Python/FastAPI
            - 前端：React/Vue
            - 数据库：PostgreSQL
            - 缓存：Redis
            """
        else:
            content = f"我理解您的询问：{user_input}\n\n这是本地降级响应，建议配置外部AI服务以获得更好的体验。"
        
        await asyncio.sleep(0.1)  # 模拟处理时间
        
        self.request_count += 1
        
        return AIResponse(
            content=content,
            model=self.model,
            usage_tokens=0,
            confidence_score=0.5  # 本地响应置信度较低
        )


class AIServiceManager:
    """AI服务管理器 - 支持多厂商和故障转移"""
    
    def __init__(self):
        self.services: Dict[AIProvider, AIService] = {}
        self.primary_provider: Optional[AIProvider] = None
        self.fallback_providers: List[AIProvider] = []
    
    def register_service(self, provider: AIProvider, service: AIService, is_primary: bool = False):
        """注册AI服务"""
        self.services[provider] = service
        if is_primary:
            self.primary_provider = provider
        else:
            self.fallback_providers.append(provider)
        
        logger.info(f"注册AI服务: {provider.value}, 模型: {service.model}")
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AIResponse:
        """生成响应，支持自动故障转移"""
        
        # 尝试主要服务
        if self.primary_provider and self.primary_provider in self.services:
            try:
                response = await self.services[self.primary_provider].generate_response(
                    messages, temperature, max_tokens
                )
                if not response.error:
                    return response
                else:
                    logger.warning(f"主要服务失败: {response.error}")
            except Exception as e:
                logger.error(f"主要服务异常: {str(e)}")
        
        # 尝试备用服务
        for provider in self.fallback_providers:
            if provider in self.services:
                try:
                    logger.info(f"尝试备用服务: {provider.value}")
                    response = await self.services[provider].generate_response(
                        messages, temperature, max_tokens
                    )
                    if not response.error:
                        return response
                    else:
                        logger.warning(f"备用服务失败: {response.error}")
                except Exception as e:
                    logger.error(f"备用服务异常: {str(e)}")
        
        # 所有服务都失败，返回错误
        return AIResponse(
            content="",
            model="none",
            error="所有AI服务都不可用"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取所有服务统计"""
        stats = {}
        for provider, service in self.services.items():
            stats[provider.value] = service.get_statistics()
        return stats


# 全局AI服务管理器实例
ai_manager = AIServiceManager()


def initialize_ai_services(config: Dict[str, Any]):
    """初始化AI服务配置"""
    
    # 注册OpenAI服务
    if config.get("openai", {}).get("api_key"):
        openai_service = OpenAIService(
            api_key=config["openai"]["api_key"],
            model=config["openai"].get("model", "gpt-4o-mini")
        )
        ai_manager.register_service(AIProvider.OPENAI, openai_service, is_primary=True)
    
    # 注册Anthropic服务
    if config.get("anthropic", {}).get("api_key"):
        anthropic_service = AnthropicService(
            api_key=config["anthropic"]["api_key"],
            model=config["anthropic"].get("model", "claude-3-sonnet-20240229")
        )
        ai_manager.register_service(AIProvider.ANTHROPIC, anthropic_service)
    
    # 始终注册本地降级服务
    local_service = LocalAIService()
    ai_manager.register_service(AIProvider.LOCAL, local_service)
    
    logger.info("AI服务初始化完成")


# 便捷函数
async def generate_ai_response(
    system_prompt: str,
    user_input: str,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> AIResponse:
    """便捷的AI响应生成函数"""
    messages = [
        AIMessage(role="system", content=system_prompt),
        AIMessage(role="user", content=user_input)
    ]
    
    return await ai_manager.generate_response(messages, temperature, max_tokens)
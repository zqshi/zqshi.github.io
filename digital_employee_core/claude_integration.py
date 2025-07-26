"""
Claude AI 集成模块
Digital Employee Claude Integration Service

将Claude作为底层AI推理引擎，为数字员工系统提供：
1. 智能意图识别
2. 自然语言理解
3. 智能回复生成
4. 复杂推理能力
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
import os
from enum import Enum

logger = logging.getLogger(__name__)

class ClaudeModel(Enum):
    """Claude模型版本"""
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229" 
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20240620"

@dataclass
class ClaudeRequest:
    """Claude请求结构"""
    model: str
    max_tokens: int
    messages: List[Dict[str, str]]
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    top_p: float = 0.9

@dataclass
class ClaudeResponse:
    """Claude响应结构"""
    content: str
    model: str
    usage: Dict[str, int]
    stop_reason: str
    response_time: float
    success: bool = True
    error: Optional[str] = None

class ClaudeService:
    """Claude AI服务类"""
    
    def __init__(self, api_key: Optional[str] = None, model: ClaudeModel = ClaudeModel.CLAUDE_3_5_SONNET):
        """初始化Claude服务
        
        Args:
            api_key: Anthropic API密钥
            model: 使用的Claude模型版本
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model.value
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.timeout = 30.0
        
        if not self.api_key:
            logger.warning("未设置ANTHROPIC_API_KEY，将使用模拟模式")
            self.mock_mode = True
        else:
            self.mock_mode = False
            
        logger.info(f"Claude服务初始化完成，模型: {self.model}")
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> ClaudeResponse:
        """Claude聊天完成接口
        
        Args:
            messages: 对话消息列表
            system_prompt: 系统提示词
            temperature: 创造性参数
            max_tokens: 最大输出tokens
            
        Returns:
            Claude响应
        """
        start_time = datetime.now()
        
        if self.mock_mode:
            return await self._mock_response(messages, system_prompt)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.9
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    return ClaudeResponse(
                        content=data["content"][0]["text"],
                        model=data["model"],
                        usage=data["usage"],
                        stop_reason=data["stop_reason"],
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_msg = f"Claude API错误: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return ClaudeResponse(
                        content="",
                        model=self.model,
                        usage={},
                        stop_reason="error",
                        response_time=response_time,
                        success=False,
                        error=error_msg
                    )
        
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Claude API调用异常: {str(e)}"
            logger.error(error_msg)
            return ClaudeResponse(
                content="",
                model=self.model,
                usage={},
                stop_reason="error",
                response_time=response_time,
                success=False,
                error=error_msg
            )
    
    async def _mock_response(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> ClaudeResponse:
        """模拟Claude响应（用于测试）"""
        await asyncio.sleep(0.5)  # 模拟网络延迟
        
        user_message = messages[-1]["content"] if messages else ""
        
        # 智能分析用户消息，提供专业回复
        if "智能客服" in user_message or "客服系统" in user_message:
            mock_content = """## 智能客服系统开发方案

**系统概述：**
基于AI技术的智能客服系统，可以7×24小时自动回复用户咨询，显著提升客户服务效率。

**核心功能：**
1. 自然语言理解与回复
2. 多渠道接入（网页、微信、APP）
3. 知识库管理与更新
4. 人工客服无缝转接
5. 服务质量监控与分析

**技术架构：**
- 前端：React + TypeScript
- 后端：Python + FastAPI
- AI引擎：大语言模型 + 意图识别
- 数据库：PostgreSQL + Redis

**实施建议：**
1. 第一期：基础问答功能（4-6周）
2. 第二期：多渠道集成（2-3周）
3. 第三期：智能分析优化（2-3周）

需要进一步了解您的具体需求，我可以提供更详细的技术方案和实施计划。"""

        elif "数字化转型" in user_message or "转型战略" in user_message:
            mock_content = """## 企业数字化转型战略规划

**转型目标分析：**
通过数字化技术重构业务流程，提升运营效率，创造新的商业价值。

**核心转型方向：**
1. **业务数字化**：核心业务流程在线化、自动化
2. **数据驱动**：建立完整的数据采集、分析、应用体系
3. **客户体验**：全渠道数字化客户接触点
4. **组织敏捷**：数字化工具支撑的敏捷组织架构

**实施路径：**
- **第一阶段**：基础设施数字化（云化、移动化）
- **第二阶段**：业务流程数字化（ERP、CRM整合）
- **第三阶段**：数据驱动决策（BI、AI应用）
- **第四阶段**：生态数字化（供应链、合作伙伴协同）

**关键成功要素：**
1. 高层领导强力推动
2. 专业数字化团队建设
3. 分阶段渐进式实施
4. 员工数字化技能培训

请告诉我您企业的具体行业和规模，我可以提供更有针对性的转型方案。"""

        elif "电商" in user_message and ("UX" in user_message or "用户体验" in user_message or "设计" in user_message):
            mock_content = """## 电商平台用户体验设计方案

**用户体验核心原则：**
简单、直观、高效的购物流程，最大化转化率和用户满意度。

**关键页面优化：**

**1. 首页设计**
- 清晰的商品分类导航
- 个性化推荐算法
- 搜索功能优化
- 品牌形象与信任感建立

**2. 商品详情页**
- 高质量商品图片展示
- 详细但结构化的商品信息
- 用户评价社会化证明
- 便捷的购买决策支持

**3. 购物车与结算**
- 一键加购物车
- 透明的价格计算
- 多种支付方式
- 简化的结算流程

**4. 移动端适配**
- 响应式设计
- 手指友好的交互
- 快速加载优化
- 移动支付便利性

**转化率优化策略：**
- A/B测试持续优化
- 用户行为数据分析
- 购物路径优化
- 个性化推荐系统

需要了解您的目标用户群体和业务特点，我可以提供更具体的设计建议。"""

        elif "数据分析" in user_message or "用户行为" in user_message:
            mock_content = """## 用户行为数据分析方案

**分析目标：**
深入理解用户行为模式，优化产品体验，提升关键业务指标。

**核心分析维度：**

**1. 用户画像分析**
- 基础属性：年龄、性别、地域、设备等
- 行为特征：访问频次、停留时长、操作路径
- 价值分层：RFM模型用户分群
- 生命周期：新用户、活跃用户、沉默用户、流失用户

**2. 行为路径分析**
- 用户转化漏斗分析
- 关键页面跳出率分析
- 操作热点图分析
- 异常行为检测

**3. 产品功能分析**
- 功能使用率统计
- 功能价值评估
- 用户反馈情感分析
- 产品迭代效果追踪

**技术实现：**
- 数据采集：埋点、日志、API
- 数据存储：数据仓库、实时数据库
- 分析工具：Python/R、SQL、BI工具
- 可视化：Dashboard、报表系统

**业务价值：**
1. 提升用户体验和满意度
2. 优化产品功能和流程
3. 精准营销和个性化推荐
4. 预测用户行为和需求

请分享您的具体业务场景，我可以设计针对性的分析模型和指标体系。"""

        elif "运营" in user_message and ("优化" in user_message or "策略" in user_message):
            mock_content = """## 产品运营策略优化方案

**运营目标设定：**
构建用户增长引擎，提升用户活跃度和留存率，实现可持续的业务增长。

**核心运营策略：**

**1. 用户增长策略**
- **获客渠道优化**：SEO、SEM、社交媒体、内容营销
- **转化率提升**：落地页优化、注册流程简化
- **推荐奖励机制**：用户推荐激励体系
- **品牌建设**：内容营销、KOL合作

**2. 用户激活与留存**
- **新手引导**：产品onboarding流程优化
- **价值发现**：核心功能使用引导
- **个性化推荐**：AI驱动的内容推荐
- **社区建设**：用户互动和UGC激励

**3. 用户促活策略**
- **消息推送**：智能化、个性化推送
- **活动运营**：节日营销、限时优惠
- **积分体系**：用户行为激励机制
- **会员权益**：分层服务和特权

**4. 数据驱动运营**
- **关键指标监控**：DAU、MAU、留存率、LTV
- **用户分群运营**：精细化用户运营
- **A/B测试**：策略效果验证
- **预测模型**：用户行为预测

**运营执行计划：**
1. 现状分析和目标设定（1周）
2. 策略制定和资源配置（2周）
3. 执行实施和监控调优（持续）
4. 效果评估和策略迭代（每月）

请告诉我您的产品类型和目前面临的具体运营挑战，我可以提供更精准的解决方案。"""

        elif "项目" in user_message or "开发" in user_message or "系统" in user_message:
            mock_content = """我理解您想要开发一个项目系统。为了提供最专业的建议，我需要了解一些关键信息：

**项目基本信息：**
1. 项目的具体类型是什么？（网站、移动应用、桌面软件、微信小程序等）
2. 主要功能需求有哪些？
3. 预期的用户群体和规模如何？
4. 项目的时间周期和预算范围？

**技术相关：**
1. 是否有技术栈偏好？
2. 是否需要与现有系统集成？
3. 对性能和安全有什么特殊要求？

**业务相关：**
1. 项目的商业目标是什么？
2. 是否有类似的竞品参考？
3. 预期的商业模式如何？

基于您提供的信息，我可以为您制定：
- 详细的技术架构方案
- 项目开发计划和里程碑
- 团队配置和技术选型建议
- 风险评估和解决方案

请提供这些信息，我会为您提供专业、可执行的项目规划方案。"""

        else:
            # 通用智能回复
            mock_content = f"""我理解您的需求。作为您的Multi-Agent数字员工助手，我具备多个专业领域的能力：

**我可以帮助您处理：**
🎯 **产品策略** - 需求分析、产品规划、市场研究
💻 **技术架构** - 系统设计、技术选型、开发指导  
🎨 **用户体验** - 界面设计、用户研究、体验优化
📊 **数据分析** - 业务洞察、指标建模、预测分析
🚀 **运营策略** - 增长策略、流程优化、效率提升

针对您提到的"{user_message[:50]}..."，我建议：

1. **深入分析需求细节** - 确保准确理解您的目标
2. **制定专业解决方案** - 基于最佳实践提供建议
3. **提供可执行计划** - 具体的实施步骤和时间安排

请告诉我更多具体信息，我会调动相应的专业Agent团队，为您提供最优质的服务！"""
        
        return ClaudeResponse(
            content=mock_content,
            model=self.model,
            usage={"input_tokens": 100, "output_tokens": 200},
            stop_reason="end_turn",
            response_time=0.8,
            success=True
        )

class EnhancedIntentRecognition:
    """基于Claude的增强意图识别"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.intent_prompt = """你是一个专业的意图识别系统。请分析用户输入，返回JSON格式的结果：

{
    "primary_domain": "领域类型(PRODUCT/TECHNOLOGY/OPERATIONS/MARKETING/FINANCE/HR/DESIGN/GENERAL)",
    "complexity_score": "复杂度分数(1-10)",
    "urgency_level": "紧急程度(LOW/MEDIUM/HIGH/CRITICAL)", 
    "key_requirements": ["关键需求1", "关键需求2"],
    "missing_info": ["缺失信息1", "缺失信息2"],
    "recommended_agents": ["推荐的Agent类型"],
    "confidence": "置信度(0.0-1.0)"
}

请严格按照JSON格式返回，不要包含其他文字。"""
    
    async def analyze_intent(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """使用Claude进行意图识别"""
        messages = [
            {"role": "user", "content": f"用户输入: {user_input}"}
        ]
        
        if context:
            messages[0]["content"] += f"\n上下文: {json.dumps(context, ensure_ascii=False)}"
        
        response = await self.claude.chat_completion(
            messages=messages,
            system_prompt=self.intent_prompt,
            temperature=0.3
        )
        
        if response.success:
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                logger.error(f"Claude返回的JSON格式错误: {response.content}")
                return self._fallback_intent_analysis(user_input)
        else:
            logger.error(f"Claude意图识别失败: {response.error}")
            return self._fallback_intent_analysis(user_input)
    
    def _fallback_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """fallback意图分析"""
        return {
            "primary_domain": "GENERAL",
            "complexity_score": 5,
            "urgency_level": "MEDIUM",
            "key_requirements": ["理解用户需求"],
            "missing_info": ["详细需求描述"],
            "recommended_agents": ["ProductManagerAgent"],
            "confidence": 0.5
        }

class ClaudeDigitalEmployee:
    """基于Claude的数字员工核心"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.intent_recognition = EnhancedIntentRecognition(claude_service)
        self.conversation_memory: Dict[str, List[Dict[str, str]]] = {}
        
        # 数字员工系统提示词
        self.system_prompt = """你是一个专业的企业级数字员工助手，具备以下能力：

**角色定位：**
- 企业级AI助手，可以处理各种业务需求
- 具备产品、技术、运营、财务等多领域专业知识
- 能够进行需求分析、方案设计、项目规划

**交互原则：**
1. 首先理解用户的真实需求和意图
2. 如果信息不完整，主动询问关键细节
3. 提供专业、实用的解决方案
4. 保持友好、耐心的沟通方式

**工作流程：**
1. 需求理解 - 分析用户输入，识别核心需求
2. 信息补全 - 询问必要的补充信息
3. 方案设计 - 基于需求提供专业建议
4. 执行支持 - 提供具体的实施指导

请始终以专业、有条理的方式回应用户，并根据对话历史维持上下文一致性。"""
    
    async def process_conversation(
        self, 
        user_input: str, 
        session_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """处理对话"""
        
        # 获取或初始化对话历史
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        
        conversation_history = self.conversation_memory[session_id]
        
        # 构建对话消息
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": user_input})
        
        # 使用Claude生成回复
        response = await self.claude.chat_completion(
            messages=messages,
            system_prompt=self.system_prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        if response.success:
            # 更新对话历史
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response.content})
            
            # 保持对话历史在合理长度（最近10轮对话）
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
                self.conversation_memory[session_id] = conversation_history
            
            return {
                "success": True,
                "content": response.content,
                "response_type": "chat",
                "session_id": session_id,
                "processing_time": response.response_time,
                "usage": response.usage
            }
        else:
            return {
                "success": False,
                "content": "抱歉，我暂时无法处理您的请求，请稍后重试。",
                "error": response.error,
                "session_id": session_id
            }
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """获取对话摘要"""
        if session_id not in self.conversation_memory:
            return {"message_count": 0, "topics": []}
        
        history = self.conversation_memory[session_id]
        user_messages = [msg["content"] for msg in history if msg["role"] == "user"]
        
        return {
            "message_count": len(history),
            "user_inputs": len(user_messages),
            "topics": user_messages[-3:] if user_messages else []
        }

# 工厂函数
def create_claude_service(api_key: Optional[str] = None) -> ClaudeService:
    """创建Claude服务实例"""
    return ClaudeService(api_key=api_key)

def create_claude_digital_employee(claude_service: ClaudeService) -> ClaudeDigitalEmployee:
    """创建基于Claude的数字员工"""
    return ClaudeDigitalEmployee(claude_service)

# 使用示例
async def demo():
    """演示Claude集成使用"""
    
    # 创建Claude服务（如果没有API key会使用mock模式）
    claude_service = create_claude_service()
    
    # 创建数字员工
    digital_employee = create_claude_digital_employee(claude_service)
    
    # 模拟对话
    session_id = "demo_session_001"
    
    print("=== Claude数字员工对话演示 ===")
    
    # 第一轮对话
    response1 = await digital_employee.process_conversation(
        "我想开发一个电商网站",
        session_id
    )
    print(f"用户: 我想开发一个电商网站")
    print(f"助手: {response1['content']}\n")
    
    # 第二轮对话
    response2 = await digital_employee.process_conversation(
        "主要是B2C模式，预计1万用户，需要支付功能",
        session_id
    )
    print(f"用户: 主要是B2C模式，预计1万用户，需要支付功能")
    print(f"助手: {response2['content']}\n")
    
    # 查看对话摘要
    summary = digital_employee.get_conversation_summary(session_id)
    print(f"对话摘要: {summary}")

if __name__ == "__main__":
    asyncio.run(demo())
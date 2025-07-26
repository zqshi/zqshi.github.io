"""
智能意图识别系统
Intent Recognition System

基于用户输入智能识别意图并制定执行流程
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """意图类型"""
    PRODUCT_DEVELOPMENT = "product_development"  # 产品开发
    SYSTEM_ARCHITECTURE = "system_architecture"  # 系统架构
    UX_DESIGN = "ux_design"  # 用户体验设计
    DATA_ANALYSIS = "data_analysis"  # 数据分析
    BUSINESS_STRATEGY = "business_strategy"  # 商业策略
    TECHNICAL_CONSULTATION = "technical_consultation"  # 技术咨询
    GENERAL_INQUIRY = "general_inquiry"  # 一般询问

class ProcessStage(Enum):
    """处理阶段"""
    INTENT_RECOGNITION = "intent_recognition"  # 意图识别
    REQUIREMENT_ANALYSIS = "requirement_analysis"  # 需求分析
    AGENT_SELECTION = "agent_selection"  # Agent选择
    ARCHITECTURE_DESIGN = "architecture_design"  # 架构设计
    PRODUCT_DESIGN = "product_design"  # 产品方案设计
    UX_DESIGN = "ux_design"  # UX设计
    QA_TESTING = "qa_testing"  # QA测试
    RESULT_DELIVERY = "result_delivery"  # 结果交付

class AgentRole(Enum):
    """Agent角色"""
    ORCHESTRATOR = "orchestrator"  # 编排器
    PRODUCT_MANAGER = "product_manager"  # 产品经理
    TECH_LEAD = "tech_lead"  # 技术负责人
    UX_DESIGNER = "ux_designer"  # UX设计师
    DATA_ANALYST = "data_analyst"  # 数据分析师
    QA_ENGINEER = "qa_engineer"  # QA工程师
    BUSINESS_ANALYST = "business_analyst"  # 业务分析师

@dataclass
class IntentRecognitionResult:
    """意图识别结果"""
    intent_type: IntentType
    confidence: float
    required_stages: List[ProcessStage]
    required_agents: List[AgentRole]
    estimated_complexity: int  # 1-10
    reasoning: str
    extracted_requirements: List[str]
    missing_information: List[str]

@dataclass
class ProcessFlow:
    """处理流程"""
    flow_id: str
    user_input: str
    intent_result: IntentRecognitionResult
    current_stage: ProcessStage
    completed_stages: List[ProcessStage] = field(default_factory=list)
    stage_results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class SmartIntentRecognizer:
    """智能意图识别器"""
    
    def __init__(self, claude_service):
        self.claude = claude_service
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_intent_patterns(self) -> Dict[str, Dict[str, Any]]:
        """加载意图识别模式"""
        return {
            "product_development": {
                "keywords": ["开发", "系统", "平台", "应用", "软件", "APP", "网站", "产品"],
                "stages": [
                    ProcessStage.INTENT_RECOGNITION,
                    ProcessStage.REQUIREMENT_ANALYSIS,
                    ProcessStage.AGENT_SELECTION,
                    ProcessStage.ARCHITECTURE_DESIGN,
                    ProcessStage.PRODUCT_DESIGN,
                    ProcessStage.UX_DESIGN,
                    ProcessStage.QA_TESTING,
                    ProcessStage.RESULT_DELIVERY
                ],
                "agents": [AgentRole.ORCHESTRATOR, AgentRole.PRODUCT_MANAGER, AgentRole.TECH_LEAD, AgentRole.UX_DESIGNER, AgentRole.QA_ENGINEER]
            },
            "system_architecture": {
                "keywords": ["架构", "设计", "技术选型", "数据库", "服务器", "云平台", "微服务"],
                "stages": [
                    ProcessStage.INTENT_RECOGNITION,
                    ProcessStage.REQUIREMENT_ANALYSIS,
                    ProcessStage.ARCHITECTURE_DESIGN,
                    ProcessStage.QA_TESTING,
                    ProcessStage.RESULT_DELIVERY
                ],
                "agents": [AgentRole.TECH_LEAD, AgentRole.QA_ENGINEER]
            },
            "ux_design": {
                "keywords": ["用户体验", "界面设计", "交互设计", "UI", "UX", "原型", "用户研究"],
                "stages": [
                    ProcessStage.INTENT_RECOGNITION,
                    ProcessStage.REQUIREMENT_ANALYSIS,
                    ProcessStage.UX_DESIGN,
                    ProcessStage.RESULT_DELIVERY
                ],
                "agents": [AgentRole.UX_DESIGNER, AgentRole.PRODUCT_MANAGER]
            },
            "data_analysis": {
                "keywords": ["数据分析", "用户行为", "指标", "统计", "报表", "洞察", "预测"],
                "stages": [
                    ProcessStage.INTENT_RECOGNITION,
                    ProcessStage.REQUIREMENT_ANALYSIS,
                    ProcessStage.RESULT_DELIVERY
                ],
                "agents": [AgentRole.DATA_ANALYST, AgentRole.BUSINESS_ANALYST]
            },
            "business_strategy": {
                "keywords": ["商业模式", "战略", "运营", "增长", "市场", "竞争", "转型"],
                "stages": [
                    ProcessStage.INTENT_RECOGNITION,
                    ProcessStage.REQUIREMENT_ANALYSIS,
                    ProcessStage.RESULT_DELIVERY
                ],
                "agents": [AgentRole.BUSINESS_ANALYST, AgentRole.PRODUCT_MANAGER]
            }
        }
    
    async def recognize_intent(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> IntentRecognitionResult:
        """智能意图识别"""
        logger.info(f"开始意图识别: {user_input[:100]}...")
        
        # 构建意图识别提示词
        intent_prompt = f"""
你是一个专业的意图识别系统。请分析用户输入，识别其真实意图并制定处理流程。

用户输入: {user_input}
上下文: {json.dumps(context or {}, ensure_ascii=False)}

可用的意图类型：
1. product_development - 产品开发（开发系统、应用、平台等）
2. system_architecture - 系统架构（技术架构设计、技术选型等）
3. ux_design - 用户体验设计（界面设计、交互设计等）
4. data_analysis - 数据分析（用户行为分析、指标分析等）
5. business_strategy - 商业策略（商业模式、运营策略等）
6. technical_consultation - 技术咨询（技术问题解答等）
7. general_inquiry - 一般询问（简单问题等）

请严格按照以下JSON格式返回分析结果：
{{
    "intent_type": "意图类型",
    "confidence": 置信度(0.0-1.0),
    "estimated_complexity": 复杂度评分(1-10),
    "reasoning": "分析推理过程",
    "extracted_requirements": ["提取的需求1", "提取的需求2"],
    "missing_information": ["缺失的信息1", "缺失的信息2"]
}}

只返回JSON，不要其他内容。
"""
        
        try:
            # 使用Claude进行意图识别
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": intent_prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            if response.success:
                # 解析Claude的响应
                result_data = json.loads(response.content)
                
                # 根据意图类型确定流程
                intent_type = IntentType(result_data.get("intent_type", "general_inquiry"))
                pattern = self.intent_patterns.get(intent_type.value, self.intent_patterns["product_development"])
                
                return IntentRecognitionResult(
                    intent_type=intent_type,
                    confidence=result_data.get("confidence", 0.5),
                    required_stages=pattern["stages"],
                    required_agents=pattern["agents"],
                    estimated_complexity=result_data.get("estimated_complexity", 5),
                    reasoning=result_data.get("reasoning", "智能识别结果"),
                    extracted_requirements=result_data.get("extracted_requirements", []),
                    missing_information=result_data.get("missing_information", [])
                )
            else:
                logger.error(f"Claude意图识别失败: {response.error}")
                return self._fallback_intent_recognition(user_input)
                
        except Exception as e:
            logger.error(f"意图识别异常: {str(e)}")
            return self._fallback_intent_recognition(user_input)
    
    def _fallback_intent_recognition(self, user_input: str) -> IntentRecognitionResult:
        """备用意图识别（基于关键词）"""
        user_lower = user_input.lower()
        
        # 简单的关键词匹配
        for intent_key, pattern in self.intent_patterns.items():
            if any(keyword in user_input for keyword in pattern["keywords"]):
                intent_type = IntentType(intent_key)
                return IntentRecognitionResult(
                    intent_type=intent_type,
                    confidence=0.6,
                    required_stages=pattern["stages"],
                    required_agents=pattern["agents"],
                    estimated_complexity=5,
                    reasoning=f"基于关键词匹配识别为{intent_type.value}",
                    extracted_requirements=[user_input],
                    missing_information=["需要更多具体信息"]
                )
        
        # 默认为产品开发
        pattern = self.intent_patterns["product_development"]
        return IntentRecognitionResult(
            intent_type=IntentType.PRODUCT_DEVELOPMENT,
            confidence=0.4,
            required_stages=pattern["stages"],
            required_agents=pattern["agents"],
            estimated_complexity=5,
            reasoning="默认识别为产品开发需求",
            extracted_requirements=[user_input],
            missing_information=["需要明确具体需求"]
        )

class ProcessOrchestrator:
    """流程编排器"""
    
    def __init__(self, claude_service):
        self.claude = claude_service
        self.intent_recognizer = SmartIntentRecognizer(claude_service)
        self.active_flows: Dict[str, ProcessFlow] = {}
    
    async def create_process_flow(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ProcessFlow:
        """创建处理流程"""
        import uuid
        
        # 意图识别
        intent_result = await self.intent_recognizer.recognize_intent(user_input, context)
        
        # 创建流程
        flow = ProcessFlow(
            flow_id=f"flow_{uuid.uuid4().hex[:8]}",
            user_input=user_input,
            intent_result=intent_result,
            current_stage=ProcessStage.INTENT_RECOGNITION
        )
        
        # 记录意图识别结果
        flow.stage_results["intent_recognition"] = {
            "intent_type": intent_result.intent_type.value,
            "confidence": intent_result.confidence,
            "reasoning": intent_result.reasoning,
            "extracted_requirements": intent_result.extracted_requirements,
            "missing_information": intent_result.missing_information
        }
        
        flow.completed_stages.append(ProcessStage.INTENT_RECOGNITION)
        
        # 保存流程
        self.active_flows[flow.flow_id] = flow
        
        logger.info(f"创建流程 {flow.flow_id}: {intent_result.intent_type.value}, 置信度: {intent_result.confidence}")
        
        return flow
    
    async def advance_flow(self, flow_id: str) -> Optional[ProcessFlow]:
        """推进流程到下一阶段"""
        if flow_id not in self.active_flows:
            return None
        
        flow = self.active_flows[flow_id]
        current_index = flow.intent_result.required_stages.index(flow.current_stage)
        
        # 检查是否有下一阶段
        if current_index + 1 < len(flow.intent_result.required_stages):
            flow.current_stage = flow.intent_result.required_stages[current_index + 1]
            flow.updated_at = datetime.now()
            logger.info(f"流程 {flow_id} 推进到: {flow.current_stage.value}")
        
        return flow
    
    def get_flow_status(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """获取流程状态"""
        if flow_id not in self.active_flows:
            return None
        
        flow = self.active_flows[flow_id]
        
        return {
            "flow_id": flow.flow_id,
            "intent_type": flow.intent_result.intent_type.value,
            "current_stage": flow.current_stage.value,
            "progress": len(flow.completed_stages) / len(flow.intent_result.required_stages),
            "completed_stages": [stage.value for stage in flow.completed_stages],
            "remaining_stages": [stage.value for stage in flow.intent_result.required_stages[len(flow.completed_stages):]],
            "stage_results": flow.stage_results,
            "created_at": flow.created_at.isoformat(),
            "updated_at": flow.updated_at.isoformat()
        }

# 工厂函数
def create_intent_recognizer(claude_service) -> SmartIntentRecognizer:
    """创建意图识别器"""
    return SmartIntentRecognizer(claude_service)

def create_process_orchestrator(claude_service) -> ProcessOrchestrator:
    """创建流程编排器"""
    return ProcessOrchestrator(claude_service)

# 使用示例
async def demo_intent_recognition():
    """演示意图识别"""
    from .claude_integration import create_claude_service
    
    claude_service = create_claude_service()
    orchestrator = create_process_orchestrator(claude_service)
    
    # 测试不同类型的输入
    test_inputs = [
        "我想开发一个智能客服系统",
        "设计一个电商平台的用户体验",
        "分析用户行为数据趋势",
        "制定数字化转型战略"
    ]
    
    for user_input in test_inputs:
        print(f"\n用户输入: {user_input}")
        flow = await orchestrator.create_process_flow(user_input)
        status = orchestrator.get_flow_status(flow.flow_id)
        print(f"识别结果: {status}")

if __name__ == "__main__":
    asyncio.run(demo_intent_recognition())
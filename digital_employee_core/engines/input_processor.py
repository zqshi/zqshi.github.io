"""
智能输入处理器 - 流程引擎入口
Input Processor - Flow Engine Entry Point

实现EARS需求：EARS-001至EARS-004
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..claude_integration import ClaudeService

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """意图类型"""
    PRODUCT_DEVELOPMENT = "product_development"
    TECHNICAL_ANALYSIS = "technical_analysis"
    BUSINESS_ANALYSIS = "business_analysis"
    DESIGN_REQUEST = "design_request"
    CODE_GENERATION = "code_generation"
    PROBLEM_SOLVING = "problem_solving"
    CONSULTATION = "consultation"
    UNKNOWN = "unknown"

class ComplexityLevel(Enum):
    """复杂度等级"""
    SIMPLE = "simple"          # 单Agent可处理
    MODERATE = "moderate"      # 需要2-3个Agent
    COMPLEX = "complex"        # 需要多Agent协作
    ENTERPRISE = "enterprise"  # 需要完整工作流

class ExecutionMode(Enum):
    """执行模式"""
    SINGLE_AGENT = "single_agent"
    MULTI_AGENT_PARALLEL = "multi_agent_parallel"
    MULTI_AGENT_SEQUENTIAL = "multi_agent_sequential"
    COLLABORATIVE_WORKSHOP = "collaborative_workshop"

@dataclass
class IntentAnalysis:
    """意图分析结果"""
    intent_type: IntentType
    confidence: float
    keywords: List[str]
    domain: str
    entities: Dict[str, Any]
    ambiguity_score: float
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplexityEvaluation:
    """复杂度评估结果"""
    level: ComplexityLevel
    score: float  # 0-100
    factors: Dict[str, float]
    reasoning: str
    estimated_duration: str
    required_agents: List[str]
    processing_time: float

@dataclass
class ProcessingPlan:
    """处理计划"""
    intent: IntentAnalysis
    complexity: ComplexityEvaluation
    execution_mode: ExecutionMode
    estimated_duration: str
    required_agents: List[str]
    priority: int
    risks: List[str]
    success_criteria: List[str]
    created_at: datetime = field(default_factory=datetime.now)

class IntentAnalyzer:
    """意图分析器"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        # 意图识别提示词
        self.intent_analysis_prompt = """
你是一个专业的意图分析师，负责分析用户输入的意图和需求。

请分析以下用户输入，识别其意图类型、领域、关键信息和潜在歧义：

用户输入: {user_input}

请返回JSON格式的分析结果：
{{
    "intent_type": "product_development/technical_analysis/business_analysis/design_request/code_generation/problem_solving/consultation/unknown",
    "confidence": 0.85,
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "domain": "技术领域/业务领域/设计领域等",
    "entities": {{
        "技术栈": ["Python", "FastAPI"],
        "业务对象": ["用户", "订单"],
        "时间限制": "2周"
    }},
    "ambiguity_score": 0.3,
    "reasoning": "分析推理过程"
}}

意图类型说明：
- product_development: 产品开发需求
- technical_analysis: 技术分析和解决方案
- business_analysis: 业务分析和咨询
- design_request: 设计需求（UI/UX）
- code_generation: 代码生成需求
- problem_solving: 问题解决
- consultation: 一般咨询

只返回JSON，不要其他内容。
"""

    async def analyze(self, user_input: str, context: Dict[str, Any] = None) -> IntentAnalysis:
        """
        分析用户意图
        实现EARS-001和EARS-002
        """
        start_time = time.time()
        
        try:
            # 构建分析提示词
            prompt = self.intent_analysis_prompt.format(user_input=user_input)
            
            # 如果有上下文，添加到提示词中
            if context:
                prompt += f"\n\n上下文信息:\n{json.dumps(context, ensure_ascii=False, indent=2)}"
            
            # 调用Claude进行意图分析
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            processing_time = time.time() - start_time
            
            if response.success:
                try:
                    # 解析JSON响应
                    analysis_data = json.loads(response.content)
                    
                    return IntentAnalysis(
                        intent_type=IntentType(analysis_data.get("intent_type", "unknown")),
                        confidence=analysis_data.get("confidence", 0.5),
                        keywords=analysis_data.get("keywords", []),
                        domain=analysis_data.get("domain", "未知"),
                        entities=analysis_data.get("entities", {}),
                        ambiguity_score=analysis_data.get("ambiguity_score", 0.5),
                        processing_time=processing_time,
                        metadata={
                            "reasoning": analysis_data.get("reasoning", ""),
                            "user_input": user_input,
                            "context": context or {}
                        }
                    )
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"意图分析响应解析失败: {e}")
                    # 返回默认分析结果
                    return self._create_default_analysis(user_input, processing_time)
            else:
                logger.error(f"Claude意图分析失败: {response.error}")
                return self._create_default_analysis(user_input, processing_time)
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"意图分析异常: {str(e)}")
            return self._create_default_analysis(user_input, processing_time)
    
    def _create_default_analysis(self, user_input: str, processing_time: float) -> IntentAnalysis:
        """创建默认分析结果"""
        return IntentAnalysis(
            intent_type=IntentType.UNKNOWN,
            confidence=0.3,
            keywords=[],
            domain="未知",
            entities={},
            ambiguity_score=0.8,
            processing_time=processing_time,
            metadata={"user_input": user_input, "fallback": True}
        )

class ComplexityEvaluator:
    """复杂度评估器"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        self.complexity_evaluation_prompt = """
你是一个专业的复杂度评估专家，负责评估任务的复杂度等级。

请评估以下任务的复杂度：

意图分析结果:
- 意图类型: {intent_type}
- 置信度: {confidence}
- 领域: {domain}
- 关键词: {keywords}
- 实体: {entities}

请返回JSON格式的复杂度评估：
{{
    "level": "simple/moderate/complex/enterprise",
    "score": 75,
    "factors": {{
        "technical_complexity": 0.8,
        "business_complexity": 0.6,
        "integration_complexity": 0.4,
        "time_complexity": 0.7
    }},
    "reasoning": "评估理由",
    "estimated_duration": "2-4小时",
    "required_agents": ["agent1", "agent2"]
}}

复杂度等级标准：
- simple (0-25): 单一专业领域，1个Agent可处理
- moderate (26-50): 涉及2-3个领域，需要2-3个Agent
- complex (51-75): 多领域综合问题，需要深度协作
- enterprise (76-100): 企业级复杂项目，需要全流程协作

可用Agent类型:
- requirements_analyst: 需求分析师
- product_manager: 产品经理
- architect: 架构师
- ux_designer: UX设计师
- project_manager: 项目经理
- coding_agent: 编程Agent
- quality_assurance: 质量保证

只返回JSON，不要其他内容。
"""

    async def evaluate(self, intent_analysis: IntentAnalysis) -> ComplexityEvaluation:
        """
        评估任务复杂度
        实现EARS-003
        """
        start_time = time.time()
        
        try:
            # 构建评估提示词
            prompt = self.complexity_evaluation_prompt.format(
                intent_type=intent_analysis.intent_type.value,
                confidence=intent_analysis.confidence,
                domain=intent_analysis.domain,
                keywords=intent_analysis.keywords,
                entities=json.dumps(intent_analysis.entities, ensure_ascii=False)
            )
            
            # 调用Claude进行复杂度评估
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800
            )
            
            processing_time = time.time() - start_time
            
            if response.success:
                try:
                    # 解析JSON响应
                    eval_data = json.loads(response.content)
                    
                    return ComplexityEvaluation(
                        level=ComplexityLevel(eval_data.get("level", "moderate")),
                        score=eval_data.get("score", 50),
                        factors=eval_data.get("factors", {}),
                        reasoning=eval_data.get("reasoning", "自动评估"),
                        estimated_duration=eval_data.get("estimated_duration", "未知"),
                        required_agents=eval_data.get("required_agents", []),
                        processing_time=processing_time
                    )
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"复杂度评估响应解析失败: {e}")
                    return self._create_default_evaluation(processing_time)
            else:
                logger.error(f"Claude复杂度评估失败: {response.error}")
                return self._create_default_evaluation(processing_time)
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"复杂度评估异常: {str(e)}")
            return self._create_default_evaluation(processing_time)
    
    def _create_default_evaluation(self, processing_time: float) -> ComplexityEvaluation:
        """创建默认评估结果"""
        return ComplexityEvaluation(
            level=ComplexityLevel.MODERATE,
            score=50,
            factors={"technical_complexity": 0.5, "business_complexity": 0.5},
            reasoning="默认中等复杂度",
            estimated_duration="2-4小时",
            required_agents=["product_manager"],
            processing_time=processing_time
        )

class InputProcessor:
    """
    智能输入处理器 - 流程引擎入口
    实现EARS-001至EARS-004
    """
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.intent_analyzer = IntentAnalyzer(claude_service)
        self.complexity_evaluator = ComplexityEvaluator(claude_service)
        
        # 执行模式决策规则
        self.execution_mode_rules = {
            ComplexityLevel.SIMPLE: ExecutionMode.SINGLE_AGENT,
            ComplexityLevel.MODERATE: ExecutionMode.MULTI_AGENT_PARALLEL,
            ComplexityLevel.COMPLEX: ExecutionMode.MULTI_AGENT_SEQUENTIAL,
            ComplexityLevel.ENTERPRISE: ExecutionMode.COLLABORATIVE_WORKSHOP
        }
    
    async def process_user_request(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None
    ) -> ProcessingPlan:
        """
        处理用户请求，生成处理计划
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            ProcessingPlan: 处理计划
        """
        logger.info(f"开始处理用户请求: {user_input[:100]}...")
        
        try:
            # 1. 意图识别与分类 (EARS-001, EARS-002)
            intent_analysis = await self.intent_analyzer.analyze(user_input, context)
            logger.info(f"意图识别完成: {intent_analysis.intent_type.value}, 置信度: {intent_analysis.confidence}")
            
            # 2. 复杂度评估 (EARS-003)
            complexity = await self.complexity_evaluator.evaluate(intent_analysis)
            logger.info(f"复杂度评估完成: {complexity.level.value}, 评分: {complexity.score}")
            
            # 3. 执行模式决策 (EARS-004)
            execution_mode = self.decide_execution_mode(complexity)
            logger.info(f"执行模式决策: {execution_mode.value}")
            
            # 4. 生成处理计划
            processing_plan = ProcessingPlan(
                intent=intent_analysis,
                complexity=complexity,
                execution_mode=execution_mode,
                estimated_duration=self.estimate_duration(complexity),
                required_agents=self.identify_required_agents(intent_analysis),
                priority=self._calculate_priority(intent_analysis, complexity),
                risks=self._identify_risks(complexity),
                success_criteria=self._define_success_criteria(intent_analysis)
            )
            
            logger.info(f"处理计划生成完成，预估时长: {processing_plan.estimated_duration}")
            return processing_plan
            
        except Exception as e:
            logger.error(f"用户请求处理失败: {str(e)}")
            # 返回默认处理计划
            return self._create_fallback_plan(user_input, context)
    
    def decide_execution_mode(self, complexity: ComplexityEvaluation) -> ExecutionMode:
        """
        决策执行模式
        实现EARS-004
        """
        # 基于复杂度等级决定执行模式
        base_mode = self.execution_mode_rules.get(complexity.level, ExecutionMode.SINGLE_AGENT)
        
        # 根据具体因子进行微调
        factors = complexity.factors
        
        # 如果技术复杂度很高，倾向于顺序执行
        if factors.get("technical_complexity", 0) > 0.8:
            if base_mode == ExecutionMode.MULTI_AGENT_PARALLEL:
                return ExecutionMode.MULTI_AGENT_SEQUENTIAL
        
        # 如果集成复杂度很高，需要协作工作坊
        if factors.get("integration_complexity", 0) > 0.9:
            return ExecutionMode.COLLABORATIVE_WORKSHOP
        
        return base_mode
    
    def estimate_duration(self, complexity: ComplexityEvaluation) -> str:
        """估算处理时长"""
        if complexity.estimated_duration != "未知":
            return complexity.estimated_duration
        
        # 基于复杂度等级估算
        duration_mapping = {
            ComplexityLevel.SIMPLE: "30分钟-1小时",
            ComplexityLevel.MODERATE: "1-3小时", 
            ComplexityLevel.COMPLEX: "4-8小时",
            ComplexityLevel.ENTERPRISE: "1-3天"
        }
        
        return duration_mapping.get(complexity.level, "2-4小时")
    
    def identify_required_agents(self, intent_analysis: IntentAnalysis) -> List[str]:
        """识别所需的Agent"""
        agents = []
        
        # 基于意图类型决定Agent
        agent_mapping = {
            IntentType.PRODUCT_DEVELOPMENT: ["requirements_analyst", "product_manager", "architect", "coding_agent"],
            IntentType.TECHNICAL_ANALYSIS: ["architect", "coding_agent"],
            IntentType.BUSINESS_ANALYSIS: ["requirements_analyst", "product_manager"],
            IntentType.DESIGN_REQUEST: ["ux_designer", "product_manager"],
            IntentType.CODE_GENERATION: ["coding_agent", "quality_assurance"],
            IntentType.PROBLEM_SOLVING: ["architect", "coding_agent"],
            IntentType.CONSULTATION: ["product_manager"],
            IntentType.UNKNOWN: ["product_manager"]
        }
        
        base_agents = agent_mapping.get(intent_analysis.intent_type, ["product_manager"])
        agents.extend(base_agents)
        
        # 根据实体信息添加特定Agent
        entities = intent_analysis.entities
        
        if "项目管理" in str(entities) or "进度" in str(entities):
            agents.append("project_manager")
        
        if "测试" in str(entities) or "质量" in str(entities):
            agents.append("quality_assurance")
        
        # 去重并返回
        return list(set(agents))
    
    def _calculate_priority(self, intent: IntentAnalysis, complexity: ComplexityEvaluation) -> int:
        """计算优先级 1-10"""
        priority = 5  # 基础优先级
        
        # 基于置信度调整
        if intent.confidence > 0.8:
            priority += 1
        elif intent.confidence < 0.5:
            priority -= 1
        
        # 基于复杂度调整
        if complexity.level == ComplexityLevel.ENTERPRISE:
            priority += 2
        elif complexity.level == ComplexityLevel.SIMPLE:
            priority -= 1
        
        # 基于歧义度调整
        if intent.ambiguity_score > 0.7:
            priority -= 2
        
        return max(1, min(10, priority))
    
    def _identify_risks(self, complexity: ComplexityEvaluation) -> List[str]:
        """识别风险"""
        risks = []
        
        factors = complexity.factors
        
        if factors.get("technical_complexity", 0) > 0.8:
            risks.append("技术实现复杂度高，可能需要更多时间")
        
        if factors.get("integration_complexity", 0) > 0.7:
            risks.append("集成复杂度高，Agent协作可能产生冲突")
        
        if complexity.score > 80:
            risks.append("整体复杂度很高，建议分阶段实施")
        
        if not risks:
            risks.append("无明显风险")
        
        return risks
    
    def _define_success_criteria(self, intent: IntentAnalysis) -> List[str]:
        """定义成功标准"""
        criteria = []
        
        # 基于意图类型定义标准
        if intent.intent_type == IntentType.CODE_GENERATION:
            criteria.extend([
                "代码质量评分≥8.0/10",
                "测试覆盖率≥80%", 
                "代码符合规范要求"
            ])
        elif intent.intent_type == IntentType.DESIGN_REQUEST:
            criteria.extend([
                "设计方案完整性≥90%",
                "用户体验评分≥4.0/5.0",
                "设计符合可访问性标准"
            ])
        elif intent.intent_type == IntentType.PRODUCT_DEVELOPMENT:
            criteria.extend([
                "需求理解准确率≥85%",
                "用户故事INVEST符合率≥95%",
                "验收标准可测试性≥95%"
            ])
        else:
            criteria.extend([
                "用户满意度≥4.0/5.0",
                "解决方案完整性≥90%",
                "响应时间满足要求"
            ])
        
        return criteria
    
    def _create_fallback_plan(self, user_input: str, context: Dict[str, Any]) -> ProcessingPlan:
        """创建默认处理计划"""
        fallback_intent = IntentAnalysis(
            intent_type=IntentType.UNKNOWN,
            confidence=0.3,
            keywords=[],
            domain="未知",
            entities={},
            ambiguity_score=0.8,
            processing_time=0.1,
            metadata={"fallback": True}
        )
        
        fallback_complexity = ComplexityEvaluation(
            level=ComplexityLevel.MODERATE,
            score=50,
            factors={"unknown": 0.5},
            reasoning="请求处理失败，使用默认复杂度",
            estimated_duration="1-2小时",
            required_agents=["product_manager"],
            processing_time=0.1
        )
        
        return ProcessingPlan(
            intent=fallback_intent,
            complexity=fallback_complexity,
            execution_mode=ExecutionMode.SINGLE_AGENT,
            estimated_duration="1-2小时",
            required_agents=["product_manager"],
            priority=3,
            risks=["请求处理失败，可能需要人工介入"],
            success_criteria=["基本回复用户需求"]
        )

# 工厂函数
def create_input_processor(claude_service: ClaudeService) -> InputProcessor:
    """创建输入处理器"""
    return InputProcessor(claude_service)

# 使用示例
async def demo_input_processor():
    """演示输入处理器"""
    from ..claude_integration import create_claude_service
    
    claude_service = create_claude_service()
    processor = create_input_processor(claude_service)
    
    test_inputs = [
        "我想开发一个电商网站，需要用户注册、商品展示、购物车和支付功能",
        "帮我写一个Python函数计算斐波那契数列",
        "分析一下我们公司的数字化转型策略，制定未来3年的发展规划"
    ]
    
    for user_input in test_inputs:
        print(f"\n测试输入: {user_input}")
        
        plan = await processor.process_user_request(user_input)
        
        print(f"意图类型: {plan.intent.intent_type.value}")
        print(f"复杂度: {plan.complexity.level.value}")
        print(f"执行模式: {plan.execution_mode.value}")
        print(f"所需Agent: {plan.required_agents}")
        print(f"预估时长: {plan.estimated_duration}")
        print(f"优先级: {plan.priority}/10")

if __name__ == "__main__":
    asyncio.run(demo_input_processor())
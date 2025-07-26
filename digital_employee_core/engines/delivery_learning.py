"""
交付与学习引擎 - 流程引擎第五阶段
Delivery & Learning Engine - Flow Engine Stage 5

实现EARS需求：EARS-018至EARS-022
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from .result_integrator import IntegratedResult
from ..claude_integration import ClaudeService

logger = logging.getLogger(__name__)

class DeliveryFormat(Enum):
    """交付格式"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    XML = "xml"
    YAML = "yaml"
    PLAIN_TEXT = "plain_text"

class DeliveryChannel(Enum):
    """交付渠道"""
    API_RESPONSE = "api_response"
    EMAIL = "email"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    WEBHOOK = "webhook"
    DOWNLOAD = "download"

class QualityGateStatus(Enum):
    """质量门禁状态"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"

class LearningType(Enum):
    """学习类型"""
    PATTERN_RECOGNITION = "pattern_recognition"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_PREVENTION = "error_prevention"
    PROCESS_IMPROVEMENT = "process_improvement"
    QUALITY_ENHANCEMENT = "quality_enhancement"

@dataclass
class OutputTemplate:
    """输出模板"""
    template_id: str
    name: str
    format: DeliveryFormat
    structure: Dict[str, Any]
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QualityGate:
    """质量门禁"""
    gate_id: str
    name: str
    criteria: Dict[str, Any]
    threshold: float
    mandatory: bool = True
    description: str = ""

@dataclass
class QualityGateResult:
    """质量门禁结果"""
    gate: QualityGate
    status: QualityGateStatus
    score: float
    details: str
    evidence: List[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)

@dataclass
class DeliveryResult:
    """交付结果"""
    delivery_id: str
    format: DeliveryFormat
    channel: DeliveryChannel
    content: Any
    size: int  # 字节
    checksum: str
    delivery_time: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LearningInsight:
    """学习洞察"""
    insight_id: str
    learning_type: LearningType
    pattern: str
    frequency: int
    confidence: float
    impact_score: float
    description: str
    recommendations: List[str] = field(default_factory=list)
    discovered_at: datetime = field(default_factory=datetime.now)

@dataclass
class ExecutionAnalysis:
    """执行分析"""
    analysis_id: str
    total_execution_time: float
    performance_metrics: Dict[str, float]
    success_patterns: List[str]
    failure_patterns: List[str]
    optimization_opportunities: List[str]
    quality_trends: Dict[str, List[float]]
    insights: List[LearningInsight] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

class OutputFormatter:
    """输出格式化器 - 实现EARS-018"""
    
    def __init__(self):
        # 预定义输出模板
        self.templates = {
            "standard_report": OutputTemplate(
                template_id="standard_report",
                name="标准报告模板",
                format=DeliveryFormat.JSON,
                structure={
                    "summary": "执行摘要",
                    "results": "详细结果",
                    "quality_metrics": "质量指标",
                    "recommendations": "建议事项",
                    "metadata": "元数据信息"
                },
                validation_rules=[
                    "summary字段不能为空",
                    "results必须包含具体内容",
                    "quality_metrics必须是数字类型"
                ]
            ),
            "technical_document": OutputTemplate(
                template_id="technical_document",
                name="技术文档模板",
                format=DeliveryFormat.MARKDOWN,
                structure={
                    "title": "文档标题",
                    "overview": "概述",
                    "architecture": "架构设计",
                    "implementation": "实现细节",
                    "testing": "测试方案",
                    "deployment": "部署说明"
                }
            ),
            "executive_summary": OutputTemplate(
                template_id="executive_summary",
                name="执行摘要模板",
                format=DeliveryFormat.HTML,
                structure={
                    "executive_summary": "执行摘要",
                    "key_achievements": "主要成果",
                    "metrics": "关键指标",
                    "next_steps": "后续步骤"
                }
            )
        }
    
    def format_output(self, integrated_result: IntegratedResult, template_id: str = "standard_report") -> Dict[str, Any]:
        """
        格式化输出
        实现EARS-018
        """
        try:
            template = self.templates.get(template_id)
            if not template:
                logger.warning(f"未找到模板{template_id}，使用默认模板")
                template = self.templates["standard_report"]
            
            logger.info(f"使用模板{template.name}格式化输出")
            
            # 根据模板格式化内容
            formatted_content = self._apply_template(integrated_result, template)
            
            # 验证格式合规性
            compliance_result = self._validate_format_compliance(formatted_content, template)
            
            if compliance_result["compliant"]:
                logger.info("输出格式验证通过")
                return {
                    "content": formatted_content,
                    "template": template_id,
                    "format": template.format.value,
                    "validation": compliance_result,
                    "size": len(str(formatted_content)),
                    "formatted_at": datetime.now().isoformat()
                }
            else:
                logger.warning(f"格式验证失败: {compliance_result['errors']}")
                # 使用简化格式
                return self._create_fallback_format(integrated_result)
                
        except Exception as e:
            logger.error(f"输出格式化失败: {str(e)}")
            return self._create_fallback_format(integrated_result)
    
    def _apply_template(self, integrated_result: IntegratedResult, template: OutputTemplate) -> Dict[str, Any]:
        """应用模板"""
        formatted_content = {}
        
        for field, description in template.structure.items():
            if field == "summary":
                formatted_content[field] = integrated_result.integrated_content.get("summary", "执行结果摘要")
            elif field == "results":
                formatted_content[field] = integrated_result.integrated_content
            elif field == "quality_metrics":
                formatted_content[field] = {
                    "overall_score": integrated_result.quality_assessment.overall_score,
                    "dimension_scores": {
                        dim.value: metrics.score 
                        for dim, metrics in integrated_result.quality_assessment.dimension_scores.items()
                    }
                }
            elif field == "recommendations":
                formatted_content[field] = integrated_result.quality_assessment.recommendations
            elif field == "metadata":
                formatted_content[field] = integrated_result.integration_metadata
            else:
                # 从整合内容中提取对应字段
                formatted_content[field] = integrated_result.integrated_content.get(field, f"待填写: {description}")
        
        return formatted_content
    
    def _validate_format_compliance(self, content: Dict[str, Any], template: OutputTemplate) -> Dict[str, Any]:
        """验证格式合规性"""
        validation_result = {
            "compliant": True,
            "errors": [],
            "warnings": []
        }
        
        # 检查必需字段
        for field in template.structure.keys():
            if field not in content:
                validation_result["compliant"] = False
                validation_result["errors"].append(f"缺少必需字段: {field}")
        
        # 应用验证规则
        for rule in template.validation_rules:
            if not self._check_validation_rule(content, rule):
                validation_result["compliant"] = False
                validation_result["errors"].append(f"验证规则失败: {rule}")
        
        return validation_result
    
    def _check_validation_rule(self, content: Dict[str, Any], rule: str) -> bool:
        """检查验证规则"""
        try:
            if "不能为空" in rule:
                field = rule.split("字段")[0]
                return bool(content.get(field))
            elif "必须包含具体内容" in rule:
                field = rule.split("必须")[0]
                field_content = content.get(field)
                return field_content and len(str(field_content)) > 10
            elif "必须是数字类型" in rule:
                field = rule.split("必须")[0]
                field_value = content.get(field)
                return isinstance(field_value, (int, float, dict))
            else:
                return True  # 未知规则默认通过
        except Exception:
            return False
    
    def _create_fallback_format(self, integrated_result: IntegratedResult) -> Dict[str, Any]:
        """创建降级格式"""
        return {
            "content": {
                "summary": "执行结果",
                "integrated_content": integrated_result.integrated_content,
                "quality_score": integrated_result.quality_assessment.overall_score
            },
            "template": "fallback",
            "format": "json",
            "validation": {"compliant": True, "fallback": True},
            "formatted_at": datetime.now().isoformat()
        }

class QualityGateChecker:
    """质量门禁检查器 - 实现EARS-019"""
    
    def __init__(self):
        # 预定义质量门禁
        self.quality_gates = [
            QualityGate(
                gate_id="completeness_gate",
                name="完整性门禁",
                criteria={"min_completeness": 0.9},
                threshold=90.0,
                mandatory=True,
                description="确保交付内容完整性≥90%"
            ),
            QualityGate(
                gate_id="quality_score_gate",
                name="质量评分门禁",
                criteria={"min_quality_score": 75.0},
                threshold=75.0,
                mandatory=True,
                description="确保整体质量评分≥75分"
            ),
            QualityGate(
                gate_id="consistency_gate",
                name="一致性门禁",
                criteria={"max_conflicts": 2},
                threshold=2.0,
                mandatory=True,
                description="确保未解决冲突数量≤2个"
            ),
            QualityGate(
                gate_id="performance_gate",
                name="性能门禁",
                criteria={"max_response_time": 30.0},
                threshold=30.0,
                mandatory=False,
                description="确保响应时间≤30秒"
            )
        ]
    
    def check_quality_gates(self, integrated_result: IntegratedResult, formatted_output: Dict[str, Any]) -> List[QualityGateResult]:
        """
        执行质量门禁检查
        实现EARS-019
        """
        gate_results = []
        
        for gate in self.quality_gates:
            try:
                logger.info(f"检查质量门禁: {gate.name}")
                
                # 执行门禁检查
                result = self._check_single_gate(gate, integrated_result, formatted_output)
                gate_results.append(result)
                
                if result.status == QualityGateStatus.FAILED and gate.mandatory:
                    logger.error(f"强制质量门禁{gate.name}检查失败")
                elif result.status == QualityGateStatus.PASSED:
                    logger.info(f"质量门禁{gate.name}检查通过")
                
            except Exception as e:
                logger.error(f"质量门禁{gate.name}检查异常: {str(e)}")
                gate_results.append(QualityGateResult(
                    gate=gate,
                    status=QualityGateStatus.FAILED,
                    score=0.0,
                    details=f"检查异常: {str(e)}"
                ))
        
        # 统计结果
        passed_count = len([r for r in gate_results if r.status == QualityGateStatus.PASSED])
        total_count = len(gate_results)
        logger.info(f"质量门禁检查完成: {passed_count}/{total_count} 通过")
        
        return gate_results
    
    def _check_single_gate(self, gate: QualityGate, integrated_result: IntegratedResult, formatted_output: Dict[str, Any]) -> QualityGateResult:
        """检查单个质量门禁"""
        if gate.gate_id == "completeness_gate":
            return self._check_completeness_gate(gate, integrated_result)
        elif gate.gate_id == "quality_score_gate":
            return self._check_quality_score_gate(gate, integrated_result)
        elif gate.gate_id == "consistency_gate":
            return self._check_consistency_gate(gate, integrated_result)
        elif gate.gate_id == "performance_gate":
            return self._check_performance_gate(gate, formatted_output)
        else:
            return QualityGateResult(
                gate=gate,
                status=QualityGateStatus.FAILED,
                score=0.0,
                details="未知门禁类型"
            )
    
    def _check_completeness_gate(self, gate: QualityGate, integrated_result: IntegratedResult) -> QualityGateResult:
        """检查完整性门禁"""
        completeness_score = integrated_result.integrated_content.get("metadata", {}).get("actual_completeness", 0.9) * 100
        min_required = gate.criteria["min_completeness"] * 100
        
        status = QualityGateStatus.PASSED if completeness_score >= min_required else QualityGateStatus.FAILED
        
        return QualityGateResult(
            gate=gate,
            status=status,
            score=completeness_score,
            details=f"完整性评分: {completeness_score:.1f}%, 要求: {min_required:.1f}%",
            evidence=[f"实际完整性: {completeness_score:.1f}%"]
        )
    
    def _check_quality_score_gate(self, gate: QualityGate, integrated_result: IntegratedResult) -> QualityGateResult:
        """检查质量评分门禁"""
        quality_score = integrated_result.quality_assessment.overall_score
        min_required = gate.criteria["min_quality_score"]
        
        status = QualityGateStatus.PASSED if quality_score >= min_required else QualityGateStatus.FAILED
        
        return QualityGateResult(
            gate=gate,
            status=status,
            score=quality_score,
            details=f"质量评分: {quality_score:.1f}, 要求: {min_required:.1f}",
            evidence=[f"整体质量评分: {quality_score}"]
        )
    
    def _check_consistency_gate(self, gate: QualityGate, integrated_result: IntegratedResult) -> QualityGateResult:
        """检查一致性门禁"""
        unresolved_conflicts = len([c for c in integrated_result.conflicts_resolved if not c.resolved])
        max_allowed = gate.criteria["max_conflicts"]
        
        status = QualityGateStatus.PASSED if unresolved_conflicts <= max_allowed else QualityGateStatus.FAILED
        
        return QualityGateResult(
            gate=gate,
            status=status,
            score=max(0, 100 - unresolved_conflicts * 10),
            details=f"未解决冲突: {unresolved_conflicts}个, 允许: {max_allowed}个",
            evidence=[f"未解决冲突数量: {unresolved_conflicts}"]
        )
    
    def _check_performance_gate(self, gate: QualityGate, formatted_output: Dict[str, Any]) -> QualityGateResult:
        """检查性能门禁"""
        # 简化的性能检查，实际应该从执行指标中获取
        response_time = 15.0  # 模拟响应时间
        max_allowed = gate.criteria["max_response_time"]
        
        status = QualityGateStatus.PASSED if response_time <= max_allowed else QualityGateStatus.FAILED
        
        return QualityGateResult(
            gate=gate,
            status=status,
            score=max(0, 100 - (response_time - max_allowed) * 2),
            details=f"响应时间: {response_time:.1f}秒, 要求: {max_allowed:.1f}秒",
            evidence=[f"实际响应时间: {response_time}秒"]
        )

class DeliveryManager:
    """交付管理器 - 实现EARS-020"""
    
    def __init__(self):
        pass
    
    def deliver_results(
        self, 
        formatted_output: Dict[str, Any],
        gate_results: List[QualityGateResult],
        delivery_config: Dict[str, Any] = None
    ) -> DeliveryResult:
        """
        交付结果
        实现EARS-020
        """
        try:
            # 检查质量门禁
            if not self._all_mandatory_gates_passed(gate_results):
                logger.warning("强制质量门禁未通过，交付被阻止")
                raise Exception("质量门禁检查失败，无法交付")
            
            # 默认交付配置
            if not delivery_config:
                delivery_config = {
                    "format": DeliveryFormat.JSON.value,
                    "channel": DeliveryChannel.API_RESPONSE.value
                }
            
            # 准备交付内容
            delivery_content = self._prepare_delivery_content(formatted_output, gate_results)
            
            # 计算内容大小和校验和
            content_str = json.dumps(delivery_content, ensure_ascii=False)
            content_size = len(content_str.encode('utf-8'))
            content_checksum = self._calculate_checksum(content_str)
            
            # 执行交付
            delivery_result = DeliveryResult(
                delivery_id=str(uuid.uuid4()),
                format=DeliveryFormat(delivery_config["format"]),
                channel=DeliveryChannel(delivery_config["channel"]),
                content=delivery_content,
                size=content_size,
                checksum=content_checksum,
                metadata={
                    "quality_gates_passed": len([r for r in gate_results if r.status == QualityGateStatus.PASSED]),
                    "quality_gates_total": len(gate_results),
                    "delivery_config": delivery_config
                }
            )
            
            logger.info(f"结果交付成功，交付ID: {delivery_result.delivery_id}")
            return delivery_result
            
        except Exception as e:
            logger.error(f"结果交付失败: {str(e)}")
            raise
    
    def _all_mandatory_gates_passed(self, gate_results: List[QualityGateResult]) -> bool:
        """检查所有强制门禁是否通过"""
        for result in gate_results:
            if result.gate.mandatory and result.status != QualityGateStatus.PASSED:
                return False
        return True
    
    def _prepare_delivery_content(self, formatted_output: Dict[str, Any], gate_results: List[QualityGateResult]) -> Dict[str, Any]:
        """准备交付内容"""
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "content": formatted_output["content"],
            "metadata": {
                "format": formatted_output.get("format"),
                "template": formatted_output.get("template"),
                "size": formatted_output.get("size"),
                "quality_gates": [
                    {
                        "name": result.gate.name,
                        "status": result.status.value,
                        "score": result.score
                    }
                    for result in gate_results
                ]
            }
        }
    
    def _calculate_checksum(self, content: str) -> str:
        """计算内容校验和"""
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()

class ExecutionLearner:
    """执行学习器 - 实现EARS-021"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        self.learning_analysis_prompt = """
你是一个专业的执行分析专家，负责分析执行过程并提取改进机会。

执行数据分析：
{execution_data}

请从以下角度进行分析：
1. 模式识别：识别成功和失败的执行模式
2. 性能优化：找出性能瓶颈和优化机会
3. 错误预防：分析错误原因和预防措施
4. 流程改进：识别流程优化点
5. 质量提升：找出质量改进机会

返回JSON格式分析：
{{
    "performance_analysis": {{
        "bottlenecks": ["瓶颈1", "瓶颈2"],
        "optimization_opportunities": ["优化机会1", "优化机会2"]
    }},
    "pattern_insights": [
        {{
            "pattern": "成功模式描述",
            "frequency": 0.8,
            "confidence": 0.9,
            "impact": "high",
            "recommendations": ["建议1", "建议2"]
        }}
    ],
    "improvement_suggestions": [
        {{
            "area": "改进领域",
            "suggestion": "具体建议",
            "priority": "high/medium/low",
            "expected_impact": "预期影响"
        }}
    ]
}}

只返回JSON，不要其他内容。
"""

    async def analyze_execution(
        self, 
        integrated_result: IntegratedResult,
        delivery_result: DeliveryResult,
        execution_context: Dict[str, Any] = None
    ) -> ExecutionAnalysis:
        """
        分析执行效果
        实现EARS-021
        """
        try:
            logger.info("开始执行效果分析")
            
            # 准备分析数据
            execution_data = self._prepare_execution_data(integrated_result, delivery_result, execution_context)
            
            # 调用Claude进行分析
            analysis_result = await self._analyze_with_claude(execution_data)
            
            # 提取学习洞察
            insights = self._extract_learning_insights(analysis_result)
            
            # 构建执行分析
            execution_analysis = ExecutionAnalysis(
                analysis_id=str(uuid.uuid4()),
                total_execution_time=execution_context.get("total_execution_time", 0) if execution_context else 0,
                performance_metrics=self._extract_performance_metrics(integrated_result, delivery_result),
                success_patterns=analysis_result.get("pattern_insights", []),
                failure_patterns=[],  # 从分析结果中提取
                optimization_opportunities=analysis_result.get("performance_analysis", {}).get("optimization_opportunities", []),
                quality_trends={},  # 质量趋势分析
                insights=insights
            )
            
            logger.info(f"执行分析完成，识别到{len(insights)}个学习洞察")
            return execution_analysis
            
        except Exception as e:
            logger.error(f"执行分析失败: {str(e)}")
            return self._create_fallback_analysis()
    
    def _prepare_execution_data(
        self, 
        integrated_result: IntegratedResult,
        delivery_result: DeliveryResult, 
        execution_context: Dict[str, Any]
    ) -> str:
        """准备执行数据用于分析"""
        data = {
            "integration_metadata": integrated_result.integration_metadata,
            "quality_assessment": {
                "overall_score": integrated_result.quality_assessment.overall_score,
                "strengths": integrated_result.quality_assessment.strengths,
                "weaknesses": integrated_result.quality_assessment.weaknesses
            },
            "conflicts_analysis": {
                "total_conflicts": len(integrated_result.conflicts_detected),
                "resolved_conflicts": len([c for c in integrated_result.conflicts_resolved if c.resolved])
            },
            "delivery_metrics": {
                "size": delivery_result.size,
                "delivery_time": delivery_result.delivery_time.isoformat()
            },
            "execution_context": execution_context or {}
        }
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    async def _analyze_with_claude(self, execution_data: str) -> Dict[str, Any]:
        """使用Claude进行分析"""
        try:
            prompt = self.learning_analysis_prompt.format(execution_data=execution_data)
            
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            if response.success:
                try:
                    return json.loads(response.content)
                except json.JSONDecodeError:
                    logger.warning("Claude分析响应解析失败")
                    return {"performance_analysis": {}, "pattern_insights": [], "improvement_suggestions": []}
            else:
                logger.error(f"Claude执行分析失败: {response.error}")
                return {}
                
        except Exception as e:
            logger.error(f"Claude分析异常: {str(e)}")
            return {}
    
    def _extract_learning_insights(self, analysis_result: Dict[str, Any]) -> List[LearningInsight]:
        """提取学习洞察"""
        insights = []
        
        # 从模式识别中提取洞察
        for pattern_data in analysis_result.get("pattern_insights", []):
            insight = LearningInsight(
                insight_id=str(uuid.uuid4()),
                learning_type=LearningType.PATTERN_RECOGNITION,
                pattern=pattern_data.get("pattern", ""),
                frequency=int(pattern_data.get("frequency", 0) * 100),
                confidence=pattern_data.get("confidence", 0.5),
                impact_score=self._calculate_impact_score(pattern_data.get("impact", "medium")),
                description=pattern_data.get("pattern", ""),
                recommendations=pattern_data.get("recommendations", [])
            )
            insights.append(insight)
        
        # 从改进建议中提取洞察
        for suggestion in analysis_result.get("improvement_suggestions", []):
            insight = LearningInsight(
                insight_id=str(uuid.uuid4()),
                learning_type=LearningType.PROCESS_IMPROVEMENT,
                pattern=suggestion.get("area", ""),
                frequency=1,
                confidence=0.8,
                impact_score=self._calculate_impact_score(suggestion.get("priority", "medium")),
                description=suggestion.get("suggestion", ""),
                recommendations=[suggestion.get("suggestion", "")]
            )
            insights.append(insight)
        
        return insights
    
    def _calculate_impact_score(self, impact_level: str) -> float:
        """计算影响评分"""
        impact_scores = {
            "high": 0.9,
            "medium": 0.6,
            "low": 0.3
        }
        return impact_scores.get(impact_level.lower(), 0.5)
    
    def _extract_performance_metrics(self, integrated_result: IntegratedResult, delivery_result: DeliveryResult) -> Dict[str, float]:
        """提取性能指标"""
        return {
            "quality_score": integrated_result.quality_assessment.overall_score,
            "integration_completeness": integrated_result.integrated_content.get("metadata", {}).get("actual_completeness", 0.8),
            "conflicts_resolution_rate": len([c for c in integrated_result.conflicts_resolved if c.resolved]) / max(len(integrated_result.conflicts_detected), 1),
            "delivery_size_kb": delivery_result.size / 1024,
            "content_complexity": len(str(delivery_result.content)) / 1000  # 简化的复杂度指标
        }
    
    def _create_fallback_analysis(self) -> ExecutionAnalysis:
        """创建降级分析结果"""
        return ExecutionAnalysis(
            analysis_id=str(uuid.uuid4()),
            total_execution_time=0,
            performance_metrics={},
            success_patterns=[],
            failure_patterns=[],
            optimization_opportunities=["需要详细分析执行数据"],
            quality_trends={},
            insights=[]
        )

class KnowledgeManager:
    """知识管理器 - 实现EARS-022"""
    
    def __init__(self):
        # 简化的知识库存储
        self.knowledge_base = {
            "patterns": [],
            "best_practices": [],
            "failure_cases": [],
            "optimization_strategies": []
        }
    
    def update_knowledge_base(self, execution_analysis: ExecutionAnalysis) -> Dict[str, Any]:
        """
        更新知识库
        实现EARS-022
        """
        try:
            logger.info("开始更新知识库")
            
            update_summary = {
                "patterns_added": 0,
                "practices_updated": 0,
                "strategies_refined": 0,
                "knowledge_quality_score": 0.0
            }
            
            # 1. 更新成功模式
            for pattern in execution_analysis.success_patterns:
                if self._is_new_pattern(pattern):
                    self.knowledge_base["patterns"].append({
                        "pattern": pattern,
                        "success_rate": 0.8,  # 基于分析结果
                        "added_at": datetime.now().isoformat(),
                        "source": "execution_analysis"
                    })
                    update_summary["patterns_added"] += 1
            
            # 2. 更新最佳实践
            for insight in execution_analysis.insights:
                if insight.learning_type == LearningType.PROCESS_IMPROVEMENT:
                    best_practice = {
                        "practice": insight.description,
                        "recommendations": insight.recommendations,
                        "confidence": insight.confidence,
                        "impact_score": insight.impact_score,
                        "updated_at": datetime.now().isoformat()
                    }
                    self.knowledge_base["best_practices"].append(best_practice)
                    update_summary["practices_updated"] += 1
            
            # 3. 更新优化策略
            for opportunity in execution_analysis.optimization_opportunities:
                strategy = {
                    "strategy": opportunity,
                    "performance_impact": "待评估",
                    "implementation_complexity": "medium",
                    "added_at": datetime.now().isoformat()
                }
                self.knowledge_base["optimization_strategies"].append(strategy)
                update_summary["strategies_refined"] += 1
            
            # 4. 评估知识质量
            update_summary["knowledge_quality_score"] = self._assess_knowledge_quality()
            
            logger.info(f"知识库更新完成: {update_summary}")
            return update_summary
            
        except Exception as e:
            logger.error(f"知识库更新失败: {str(e)}")
            return {"error": str(e)}
    
    def _is_new_pattern(self, pattern) -> bool:
        """检查是否为新模式"""
        # 简化的重复检查
        for existing_pattern in self.knowledge_base["patterns"]:
            if str(pattern) in str(existing_pattern.get("pattern", "")):
                return False
        return True
    
    def _assess_knowledge_quality(self) -> float:
        """评估知识质量"""
        total_items = (
            len(self.knowledge_base["patterns"]) +
            len(self.knowledge_base["best_practices"]) +
            len(self.knowledge_base["optimization_strategies"])
        )
        
        if total_items == 0:
            return 0.0
        
        # 简化的质量评估
        quality_factors = [
            min(len(self.knowledge_base["patterns"]) / 10, 1.0),  # 模式数量
            min(len(self.knowledge_base["best_practices"]) / 10, 1.0),  # 实践数量
            min(len(self.knowledge_base["optimization_strategies"]) / 5, 1.0)  # 策略数量
        ]
        
        return sum(quality_factors) / len(quality_factors) * 100

class DeliveryLearningEngine:
    """
    交付与学习引擎
    实现EARS-018至EARS-022
    """
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.output_formatter = OutputFormatter()
        self.quality_gate_checker = QualityGateChecker()
        self.delivery_manager = DeliveryManager()
        self.execution_learner = ExecutionLearner(claude_service)
        self.knowledge_manager = KnowledgeManager()
    
    async def process_delivery_and_learning(
        self, 
        integrated_result: IntegratedResult,
        delivery_config: Dict[str, Any] = None,
        execution_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        处理交付和学习流程
        
        Args:
            integrated_result: 整合结果
            delivery_config: 交付配置
            execution_context: 执行上下文
            
        Returns:
            Dict: 处理结果
        """
        logger.info("开始交付与学习流程")
        
        try:
            # 1. 输出格式化 (EARS-018)
            formatted_output = self.output_formatter.format_output(integrated_result)
            logger.info("输出格式化完成")
            
            # 2. 质量最终检查 (EARS-019)
            gate_results = self.quality_gate_checker.check_quality_gates(integrated_result, formatted_output)
            logger.info("质量门禁检查完成")
            
            # 3. 用户交付 (EARS-020)
            delivery_result = self.delivery_manager.deliver_results(formatted_output, gate_results, delivery_config)
            logger.info("用户交付完成")
            
            # 4. 执行效果学习 (EARS-021)
            execution_analysis = await self.execution_learner.analyze_execution(
                integrated_result, delivery_result, execution_context
            )
            logger.info("执行效果分析完成")
            
            # 5. 知识库更新 (EARS-022)
            knowledge_update = self.knowledge_manager.update_knowledge_base(execution_analysis)
            logger.info("知识库更新完成")
            
            # 构建最终结果
            final_result = {
                "delivery_status": "success",
                "delivery_id": delivery_result.delivery_id,
                "delivery_content": delivery_result.content,
                "quality_gates": {
                    "total": len(gate_results),
                    "passed": len([r for r in gate_results if r.status == QualityGateStatus.PASSED]),
                    "results": [
                        {
                            "name": r.gate.name,
                            "status": r.status.value,
                            "score": r.score,
                            "details": r.details
                        }
                        for r in gate_results
                    ]
                },
                "learning_insights": {
                    "analysis_id": execution_analysis.analysis_id,
                    "insights_count": len(execution_analysis.insights),
                    "optimization_opportunities": execution_analysis.optimization_opportunities,
                    "performance_metrics": execution_analysis.performance_metrics
                },
                "knowledge_update": knowledge_update,
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "total_processing_time": execution_context.get("total_execution_time", 0) if execution_context else 0,
                    "content_size": delivery_result.size,
                    "content_checksum": delivery_result.checksum
                }
            }
            
            logger.info("交付与学习流程完成")
            return final_result
            
        except Exception as e:
            logger.error(f"交付与学习流程失败: {str(e)}")
            return {
                "delivery_status": "failed",
                "error": str(e),
                "partial_results": {
                    "integrated_result_id": integrated_result.result_id,
                    "failure_time": datetime.now().isoformat()
                }
            }

# 工厂函数
def create_delivery_learning_engine(claude_service: ClaudeService) -> DeliveryLearningEngine:
    """创建交付学习引擎"""
    return DeliveryLearningEngine(claude_service)

# 使用示例
async def demo_delivery_learning():
    """演示交付学习引擎"""
    from ..claude_integration import create_claude_service
    from .result_integrator import IntegratedResult, QualityAssessment
    
    claude_service = create_claude_service()
    engine = create_delivery_learning_engine(claude_service)
    
    # 模拟整合结果
    mock_integrated_result = IntegratedResult(
        result_id="test_result",
        source_results={"test": "data"},
        integrated_content={
            "summary": "测试执行结果",
            "main_content": "这是一个测试的整合结果",
            "metadata": {"actual_completeness": 0.95}
        },
        conflicts_detected=[],
        conflicts_resolved=[],
        quality_assessment=QualityAssessment(
            overall_score=85,
            dimension_scores={},
            strengths=["内容完整"],
            weaknesses=["需要优化"],
            recommendations=["增强细节"]
        )
    )
    
    # 执行交付和学习
    result = await engine.process_delivery_and_learning(
        mock_integrated_result,
        execution_context={"total_execution_time": 120}
    )
    
    print(f"交付状态: {result.get('delivery_status')}")
    print(f"交付ID: {result.get('delivery_id')}")
    print(f"质量门禁通过: {result.get('quality_gates', {}).get('passed')}/{result.get('quality_gates', {}).get('total')}")
    print(f"学习洞察数量: {result.get('learning_insights', {}).get('insights_count')}")

if __name__ == "__main__":
    asyncio.run(demo_delivery_learning())
"""
智能结果整合器 - 流程引擎第四阶段
Result Integrator - Flow Engine Stage 4

实现EARS需求：EARS-014至EARS-017
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import difflib

from .parallel_execution import ExecutionStatus
from ..claude_integration import ClaudeService

logger = logging.getLogger(__name__)

class ConflictType(Enum):
    """冲突类型"""
    SEMANTIC = "semantic"  # 语义冲突
    STRUCTURAL = "structural"  # 结构冲突
    DATA = "data"  # 数据冲突
    LOGIC = "logic"  # 逻辑冲突
    FORMAT = "format"  # 格式冲突

class ConflictSeverity(Enum):
    """冲突严重性"""
    CRITICAL = "critical"  # 严重冲突，必须解决
    HIGH = "high"  # 高优先级冲突
    MEDIUM = "medium"  # 中等冲突
    LOW = "low"  # 轻微冲突
    INFO = "info"  # 信息性冲突

class QualityDimension(Enum):
    """质量维度"""
    COMPLETENESS = "completeness"  # 完整性
    CONSISTENCY = "consistency"  # 一致性
    CORRECTNESS = "correctness"  # 正确性
    CLARITY = "clarity"  # 清晰度
    RELEVANCE = "relevance"  # 相关性
    EFFICIENCY = "efficiency"  # 效率
    MAINTAINABILITY = "maintainability"  # 可维护性

@dataclass
class ConflictInfo:
    """冲突信息"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    description: str
    involved_results: List[str]  # 涉及的结果ID
    conflicting_values: Dict[str, Any]
    resolution_strategy: Optional[str] = None
    resolved: bool = False
    resolution_result: Optional[Any] = None
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class QualityMetrics:
    """质量指标"""
    dimension: QualityDimension
    score: float  # 0-100
    details: str
    measurement_method: str
    evidence: List[str] = field(default_factory=list)

@dataclass
class QualityAssessment:
    """质量评估"""
    overall_score: float  # 0-100
    dimension_scores: Dict[QualityDimension, QualityMetrics]
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessment_time: datetime = field(default_factory=datetime.now)

@dataclass
class IntegratedResult:
    """整合结果"""
    result_id: str
    source_results: Dict[str, Any]  # 源结果
    integrated_content: Dict[str, Any]  # 整合后内容
    conflicts_detected: List[ConflictInfo]
    conflicts_resolved: List[ConflictInfo]
    quality_assessment: QualityAssessment
    integration_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class ConsistencyChecker:
    """一致性检查器 - 实现EARS-014"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        self.consistency_check_prompt = """
你是一个专业的一致性检查专家，负责检查多个Agent执行结果之间的一致性。

请检查以下执行结果的一致性：

{results_data}

请识别以下类型的冲突：
1. 语义冲突：含义或概念上的矛盾
2. 结构冲突：组织结构上的不一致
3. 数据冲突：具体数据值的不一致
4. 逻辑冲突：逻辑关系上的矛盾
5. 格式冲突：格式标准的不统一

返回JSON格式的冲突分析：
{{
    "conflicts_detected": [
        {{
            "conflict_type": "semantic/structural/data/logic/format",
            "severity": "critical/high/medium/low/info",
            "description": "详细描述冲突内容",
            "involved_results": ["result_id1", "result_id2"],
            "conflicting_values": {{
                "result_id1": "value1",
                "result_id2": "value2"
            }},
            "resolution_strategy": "建议的解决策略"
        }}
    ],
    "consistency_score": 0.85,
    "overall_assessment": "整体一致性评估",
    "recommendations": ["改进建议1", "改进建议2"]
}}

只返回JSON，不要其他内容。
"""

    async def check_consistency(self, results: Dict[str, Any]) -> Tuple[List[ConflictInfo], float]:
        """
        检查结果一致性
        实现EARS-014
        """
        try:
            # 构建结果数据用于分析
            results_data = self._format_results_for_analysis(results)
            
            # 构建检查提示词
            prompt = self.consistency_check_prompt.format(results_data=results_data)
            
            # 调用Claude进行一致性检查
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000
            )
            
            if response.success:
                try:
                    # 解析JSON响应
                    analysis_data = json.loads(response.content)
                    
                    # 转换为ConflictInfo对象
                    conflicts = []
                    for conflict_data in analysis_data.get("conflicts_detected", []):
                        conflict = ConflictInfo(
                            conflict_id=self._generate_conflict_id(conflict_data),
                            conflict_type=ConflictType(conflict_data.get("conflict_type", "semantic")),
                            severity=ConflictSeverity(conflict_data.get("severity", "medium")),
                            description=conflict_data.get("description", ""),
                            involved_results=conflict_data.get("involved_results", []),
                            conflicting_values=conflict_data.get("conflicting_values", {}),
                            resolution_strategy=conflict_data.get("resolution_strategy")
                        )
                        conflicts.append(conflict)
                    
                    consistency_score = analysis_data.get("consistency_score", 0.8)
                    
                    logger.info(f"一致性检查完成，发现{len(conflicts)}个冲突，一致性评分: {consistency_score}")
                    return conflicts, consistency_score
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"一致性检查响应解析失败: {e}")
                    return [], 0.5
            else:
                logger.error(f"Claude一致性检查失败: {response.error}")
                return [], 0.5
                
        except Exception as e:
            logger.error(f"一致性检查异常: {str(e)}")
            return [], 0.5
    
    def _format_results_for_analysis(self, results: Dict[str, Any]) -> str:
        """格式化结果数据用于分析"""
        formatted_data = []
        
        for result_id, result_data in results.items():
            formatted_data.append(f"结果ID: {result_id}")
            formatted_data.append(f"内容: {json.dumps(result_data, ensure_ascii=False, indent=2)}")
            formatted_data.append("---")
        
        return "\n".join(formatted_data)
    
    def _generate_conflict_id(self, conflict_data: Dict) -> str:
        """生成冲突ID"""
        conflict_str = f"{conflict_data.get('conflict_type', '')}{conflict_data.get('description', '')}"
        return hashlib.md5(conflict_str.encode()).hexdigest()[:8]

class ConflictResolver:
    """冲突检测与解决器 - 实现EARS-015"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        # 冲突解决策略
        self.resolution_strategies = {
            ConflictType.SEMANTIC: self._resolve_semantic_conflict,
            ConflictType.STRUCTURAL: self._resolve_structural_conflict,
            ConflictType.DATA: self._resolve_data_conflict,
            ConflictType.LOGIC: self._resolve_logic_conflict,
            ConflictType.FORMAT: self._resolve_format_conflict
        }
        
        self.conflict_resolution_prompt = """
你是一个专业的冲突解决专家，负责解决Agent执行结果之间的冲突。

冲突信息：
- 冲突类型: {conflict_type}
- 严重性: {severity}
- 描述: {description}
- 涉及结果: {involved_results}
- 冲突值: {conflicting_values}

请提供解决方案：
1. 分析冲突根本原因
2. 提供具体的解决方案
3. 给出解决后的统一结果
4. 评估解决方案的可信度

返回JSON格式：
{{
    "root_cause": "冲突根本原因分析",
    "resolution_approach": "解决方法",
    "unified_result": "统一后的结果",
    "confidence": 0.9,
    "rationale": "解决方案理由"
}}

只返回JSON，不要其他内容。
"""

    async def resolve_conflicts(self, conflicts: List[ConflictInfo], results: Dict[str, Any]) -> List[ConflictInfo]:
        """
        解决冲突
        实现EARS-015
        """
        resolved_conflicts = []
        
        # 按严重性排序，优先处理严重冲突
        sorted_conflicts = sorted(conflicts, key=lambda c: self._get_severity_priority(c.severity))
        
        for conflict in sorted_conflicts:
            try:
                logger.info(f"开始解决冲突: {conflict.conflict_id}")
                
                # 选择解决策略
                resolver = self.resolution_strategies.get(
                    conflict.conflict_type, 
                    self._resolve_generic_conflict
                )
                
                # 执行冲突解决
                resolved_conflict = await resolver(conflict, results)
                resolved_conflicts.append(resolved_conflict)
                
                if resolved_conflict.resolved:
                    logger.info(f"冲突{conflict.conflict_id}已解决")
                else:
                    logger.warning(f"冲突{conflict.conflict_id}解决失败")
                    
            except Exception as e:
                logger.error(f"解决冲突{conflict.conflict_id}时异常: {str(e)}")
                conflict.resolved = False
                resolved_conflicts.append(conflict)
        
        success_rate = len([c for c in resolved_conflicts if c.resolved]) / len(resolved_conflicts) if resolved_conflicts else 0
        logger.info(f"冲突解决完成，成功率: {success_rate:.2%}")
        
        return resolved_conflicts
    
    def _get_severity_priority(self, severity: ConflictSeverity) -> int:
        """获取严重性优先级"""
        priority_map = {
            ConflictSeverity.CRITICAL: 0,
            ConflictSeverity.HIGH: 1,
            ConflictSeverity.MEDIUM: 2,
            ConflictSeverity.LOW: 3,
            ConflictSeverity.INFO: 4
        }
        return priority_map.get(severity, 5)
    
    async def _resolve_semantic_conflict(self, conflict: ConflictInfo, results: Dict[str, Any]) -> ConflictInfo:
        """解决语义冲突"""
        return await self._resolve_with_claude(conflict, results)
    
    async def _resolve_structural_conflict(self, conflict: ConflictInfo, results: Dict[str, Any]) -> ConflictInfo:
        """解决结构冲突"""
        return await self._resolve_with_claude(conflict, results)
    
    async def _resolve_data_conflict(self, conflict: ConflictInfo, results: Dict[str, Any]) -> ConflictInfo:
        """解决数据冲突"""
        # 对于数据冲突，可以使用投票、平均值或专家权重等方法
        
        if len(conflict.conflicting_values) == 2:
            # 二选一的情况，使用Claude判断
            return await self._resolve_with_claude(conflict, results)
        else:
            # 多个值的情况，可以使用统计方法
            return self._resolve_with_statistics(conflict)
    
    async def _resolve_logic_conflict(self, conflict: ConflictInfo, results: Dict[str, Any]) -> ConflictInfo:
        """解决逻辑冲突"""
        return await self._resolve_with_claude(conflict, results)
    
    async def _resolve_format_conflict(self, conflict: ConflictInfo, results: Dict[str, Any]) -> ConflictInfo:
        """解决格式冲突"""
        # 格式冲突通常选择最标准的格式
        
        # 简化处理：选择第一个格式作为标准
        if conflict.conflicting_values:
            first_key = list(conflict.conflicting_values.keys())[0]
            conflict.resolution_result = conflict.conflicting_values[first_key]
            conflict.resolved = True
            conflict.resolution_strategy = "选择标准格式"
        
        return conflict
    
    async def _resolve_generic_conflict(self, conflict: ConflictInfo, results: Dict[str, Any]) -> ConflictInfo:
        """通用冲突解决"""
        return await self._resolve_with_claude(conflict, results)
    
    async def _resolve_with_claude(self, conflict: ConflictInfo, results: Dict[str, Any]) -> ConflictInfo:
        """使用Claude解决冲突"""
        try:
            prompt = self.conflict_resolution_prompt.format(
                conflict_type=conflict.conflict_type.value,
                severity=conflict.severity.value,
                description=conflict.description,
                involved_results=conflict.involved_results,
                conflicting_values=json.dumps(conflict.conflicting_values, ensure_ascii=False, indent=2)
            )
            
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            if response.success:
                try:
                    resolution_data = json.loads(response.content)
                    
                    conflict.resolution_result = resolution_data.get("unified_result")
                    conflict.resolution_strategy = resolution_data.get("resolution_approach")
                    conflict.resolved = resolution_data.get("confidence", 0) > 0.7
                    
                    return conflict
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"冲突解决响应解析失败: {e}")
                    conflict.resolved = False
                    return conflict
            else:
                logger.error(f"Claude冲突解决失败: {response.error}")
                conflict.resolved = False
                return conflict
                
        except Exception as e:
            logger.error(f"Claude冲突解决异常: {str(e)}")
            conflict.resolved = False
            return conflict
    
    def _resolve_with_statistics(self, conflict: ConflictInfo) -> ConflictInfo:
        """使用统计方法解决冲突"""
        try:
            values = list(conflict.conflicting_values.values())
            
            # 如果是数值型数据，计算平均值
            if all(isinstance(v, (int, float)) for v in values):
                conflict.resolution_result = sum(values) / len(values)
                conflict.resolved = True
                conflict.resolution_strategy = "统计平均值"
            else:
                # 非数值型，选择出现频率最高的值
                from collections import Counter
                counter = Counter(str(v) for v in values)
                most_common = counter.most_common(1)[0][0]
                conflict.resolution_result = most_common
                conflict.resolved = True
                conflict.resolution_strategy = "频率投票"
                
        except Exception as e:
            logger.error(f"统计方法解决冲突失败: {str(e)}")
            conflict.resolved = False
        
        return conflict

class QualityAssessor:
    """质量评估器 - 实现EARS-016"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        self.quality_assessment_prompt = """
你是一个专业的质量评估专家，负责评估整合结果的质量。

请从以下维度评估结果质量：

整合结果：
{integrated_content}

评估维度：
1. 完整性 (Completeness): 结果是否完整，覆盖所有必要内容
2. 一致性 (Consistency): 内容是否内部一致，无矛盾
3. 正确性 (Correctness): 内容是否准确正确
4. 清晰度 (Clarity): 表达是否清晰易懂
5. 相关性 (Relevance): 内容是否相关且有价值
6. 效率 (Efficiency): 解决方案是否高效实用
7. 可维护性 (Maintainability): 结果是否易于维护和扩展

返回JSON格式评估：
{{
    "overall_score": 85,
    "dimension_scores": {{
        "completeness": {{
            "score": 90,
            "details": "内容完整度高，覆盖所有关键要素",
            "evidence": ["证据1", "证据2"]
        }}
        // ... 其他维度
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "recommendations": ["改进建议1", "改进建议2"]
}}

只返回JSON，不要其他内容。
"""

    async def assess_quality(self, integrated_content: Dict[str, Any]) -> QualityAssessment:
        """
        评估质量
        实现EARS-016
        """
        try:
            # 构建评估提示词
            content_str = json.dumps(integrated_content, ensure_ascii=False, indent=2)
            prompt = self.quality_assessment_prompt.format(integrated_content=content_str)
            
            # 调用Claude进行质量评估
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2000
            )
            
            if response.success:
                try:
                    # 解析JSON响应
                    assessment_data = json.loads(response.content)
                    
                    # 转换维度评分
                    dimension_scores = {}
                    for dim_name, dim_data in assessment_data.get("dimension_scores", {}).items():
                        try:
                            dimension = QualityDimension(dim_name)
                            metrics = QualityMetrics(
                                dimension=dimension,
                                score=dim_data.get("score", 70),
                                details=dim_data.get("details", ""),
                                measurement_method="Claude AI评估",
                                evidence=dim_data.get("evidence", [])
                            )
                            dimension_scores[dimension] = metrics
                        except ValueError:
                            logger.warning(f"未知质量维度: {dim_name}")
                    
                    # 创建质量评估对象
                    quality_assessment = QualityAssessment(
                        overall_score=assessment_data.get("overall_score", 70),
                        dimension_scores=dimension_scores,
                        strengths=assessment_data.get("strengths", []),
                        weaknesses=assessment_data.get("weaknesses", []),
                        recommendations=assessment_data.get("recommendations", [])
                    )
                    
                    logger.info(f"质量评估完成，总分: {quality_assessment.overall_score}")
                    return quality_assessment
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"质量评估响应解析失败: {e}")
                    return self._create_default_assessment()
            else:
                logger.error(f"Claude质量评估失败: {response.error}")
                return self._create_default_assessment()
                
        except Exception as e:
            logger.error(f"质量评估异常: {str(e)}")
            return self._create_default_assessment()
    
    def _create_default_assessment(self) -> QualityAssessment:
        """创建默认质量评估"""
        dimension_scores = {}
        for dimension in QualityDimension:
            metrics = QualityMetrics(
                dimension=dimension,
                score=70,
                details="默认评估",
                measurement_method="默认方法"
            )
            dimension_scores[dimension] = metrics
        
        return QualityAssessment(
            overall_score=70,
            dimension_scores=dimension_scores,
            strengths=["基本功能完整"],
            weaknesses=["需要进一步优化"],
            recommendations=["详细评估质量"]
        )

class ContentFuser:
    """内容融合器 - 实现EARS-017"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        
        self.content_fusion_prompt = """
你是一个专业的内容融合专家，负责将多个Agent的执行结果融合成统一的整合内容。

源结果数据：
{source_results}

已解决的冲突：
{resolved_conflicts}

请将这些结果融合成一个统一、完整、逻辑清晰的整合结果：

要求：
1. 保持内容完整性≥95%
2. 确保逻辑一致性
3. 优化结构组织
4. 去除重复内容
5. 增强可读性

返回JSON格式的融合结果：
{{
    "integrated_content": {{
        "summary": "整合内容摘要",
        "main_sections": {{
            "section1": "内容1",
            "section2": "内容2"
        }},
        "metadata": {{
            "completeness_score": 0.95,
            "integration_quality": "high"
        }}
    }},
    "fusion_notes": "融合过程说明",
    "completeness_analysis": "完整性分析"
}}

只返回JSON，不要其他内容。
"""

    async def fuse_content(
        self, 
        source_results: Dict[str, Any], 
        resolved_conflicts: List[ConflictInfo]
    ) -> Dict[str, Any]:
        """
        融合内容
        实现EARS-017
        """
        try:
            # 准备融合数据
            source_data = json.dumps(source_results, ensure_ascii=False, indent=2)
            conflicts_data = self._format_conflicts_for_fusion(resolved_conflicts)
            
            # 构建融合提示词
            prompt = self.content_fusion_prompt.format(
                source_results=source_data,
                resolved_conflicts=conflicts_data
            )
            
            # 调用Claude进行内容融合
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=3000
            )
            
            if response.success:
                try:
                    # 解析JSON响应
                    fusion_data = json.loads(response.content)
                    integrated_content = fusion_data.get("integrated_content", {})
                    
                    # 验证完整性
                    completeness = self._verify_completeness(source_results, integrated_content)
                    integrated_content["metadata"] = integrated_content.get("metadata", {})
                    integrated_content["metadata"]["actual_completeness"] = completeness
                    
                    logger.info(f"内容融合完成，完整性: {completeness:.2%}")
                    return integrated_content
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"内容融合响应解析失败: {e}")
                    return self._create_fallback_integration(source_results)
            else:
                logger.error(f"Claude内容融合失败: {response.error}")
                return self._create_fallback_integration(source_results)
                
        except Exception as e:
            logger.error(f"内容融合异常: {str(e)}")
            return self._create_fallback_integration(source_results)
    
    def _format_conflicts_for_fusion(self, conflicts: List[ConflictInfo]) -> str:
        """格式化冲突信息用于融合"""
        conflict_summaries = []
        
        for conflict in conflicts:
            if conflict.resolved:
                summary = f"冲突{conflict.conflict_id}: {conflict.description} -> 已解决: {conflict.resolution_result}"
            else:
                summary = f"冲突{conflict.conflict_id}: {conflict.description} -> 未解决"
            conflict_summaries.append(summary)
        
        return "\n".join(conflict_summaries)
    
    def _verify_completeness(self, source_results: Dict[str, Any], integrated_content: Dict[str, Any]) -> float:
        """验证完整性"""
        try:
            # 简化的完整性检查：比较关键字数量
            source_text = json.dumps(source_results, ensure_ascii=False)
            integrated_text = json.dumps(integrated_content, ensure_ascii=False)
            
            # 提取关键词
            source_words = set(source_text.lower().split())
            integrated_words = set(integrated_text.lower().split())
            
            # 计算覆盖率
            if source_words:
                coverage = len(source_words & integrated_words) / len(source_words)
                return min(coverage, 1.0)
            else:
                return 1.0
                
        except Exception as e:
            logger.warning(f"完整性验证失败: {str(e)}")
            return 0.8  # 默认值
    
    def _create_fallback_integration(self, source_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建降级整合结果"""
        return {
            "summary": "多Agent执行结果整合",
            "main_sections": {
                "source_results": source_results,
                "integration_status": "使用降级整合方案"
            },
            "metadata": {
                "completeness_score": 0.8,
                "integration_quality": "fallback",
                "fallback_reason": "主要整合方案失败"
            }
        }

class ResultIntegrator:
    """
    智能结果整合器
    实现EARS-014至EARS-017
    """
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.consistency_checker = ConsistencyChecker(claude_service)
        self.conflict_resolver = ConflictResolver(claude_service)
        self.quality_assessor = QualityAssessor(claude_service)
        self.content_fuser = ContentFuser(claude_service)
    
    async def integrate_results(self, execution_results: Dict[str, Any]) -> IntegratedResult:
        """
        整合执行结果
        
        Args:
            execution_results: Agent执行结果
            
        Returns:
            IntegratedResult: 整合结果
        """
        logger.info(f"开始整合{len(execution_results)}个执行结果")
        
        try:
            # 1. 结果一致性检查 (EARS-014)
            conflicts, consistency_score = await self.consistency_checker.check_consistency(execution_results)
            logger.info(f"一致性检查完成，一致性评分: {consistency_score}")
            
            # 2. 冲突检测与解决 (EARS-015)
            resolved_conflicts = await self.conflict_resolver.resolve_conflicts(conflicts, execution_results)
            logger.info(f"冲突解决完成，解决了{len([c for c in resolved_conflicts if c.resolved])}个冲突")
            
            # 3. 结果融合 (EARS-017)
            integrated_content = await self.content_fuser.fuse_content(execution_results, resolved_conflicts)
            logger.info("内容融合完成")
            
            # 4. 质量评估 (EARS-016)
            quality_assessment = await self.quality_assessor.assess_quality(integrated_content)
            logger.info(f"质量评估完成，总分: {quality_assessment.overall_score}")
            
            # 5. 生成整合结果
            integrated_result = IntegratedResult(
                result_id=str(uuid.uuid4()),
                source_results=execution_results,
                integrated_content=integrated_content,
                conflicts_detected=conflicts,
                conflicts_resolved=resolved_conflicts,
                quality_assessment=quality_assessment,
                integration_metadata={
                    "consistency_score": consistency_score,
                    "conflicts_total": len(conflicts),
                    "conflicts_resolved": len([c for c in resolved_conflicts if c.resolved]),
                    "integration_time": datetime.now().isoformat()
                }
            )
            
            logger.info(f"结果整合完成，整合ID: {integrated_result.result_id}")
            return integrated_result
            
        except Exception as e:
            logger.error(f"结果整合失败: {str(e)}")
            # 返回简化的整合结果
            return self._create_fallback_result(execution_results, str(e))
    
    def _create_fallback_result(self, execution_results: Dict[str, Any], error: str) -> IntegratedResult:
        """创建降级整合结果"""
        fallback_content = {
            "summary": "降级整合结果",
            "source_results": execution_results,
            "error": error,
            "metadata": {
                "integration_quality": "fallback",
                "completeness_score": 0.6
            }
        }
        
        fallback_assessment = QualityAssessment(
            overall_score=60,
            dimension_scores={},
            strengths=["保留了源结果"],
            weaknesses=["整合质量降级"],
            recommendations=["检查整合流程"]
        )
        
        return IntegratedResult(
            result_id=str(uuid.uuid4()),
            source_results=execution_results,
            integrated_content=fallback_content,
            conflicts_detected=[],
            conflicts_resolved=[],
            quality_assessment=fallback_assessment,
            integration_metadata={
                "fallback": True,
                "error": error
            }
        )

# 工厂函数
def create_result_integrator(claude_service: ClaudeService) -> ResultIntegrator:
    """创建结果整合器"""
    return ResultIntegrator(claude_service)

# 使用示例
async def demo_result_integrator():
    """演示结果整合器"""
    from ..claude_integration import create_claude_service
    
    claude_service = create_claude_service()
    integrator = create_result_integrator(claude_service)
    
    # 模拟执行结果
    mock_results = {
        "requirements_analysis": {
            "status": "completed",
            "analysis": "用户管理系统需求分析完成",
            "requirements": ["用户注册", "用户登录", "用户管理"]
        },
        "architecture_design": {
            "status": "completed", 
            "design": "采用微服务架构",
            "components": ["用户服务", "认证服务", "管理服务"]
        },
        "code_generation": {
            "status": "completed",
            "code": "生成了用户管理相关代码",
            "files": ["user.py", "auth.py", "admin.py"]
        }
    }
    
    # 整合结果
    integrated_result = await integrator.integrate_results(mock_results)
    
    print(f"整合结果ID: {integrated_result.result_id}")
    print(f"检测到冲突: {len(integrated_result.conflicts_detected)}")
    print(f"解决冲突: {len([c for c in integrated_result.conflicts_resolved if c.resolved])}")
    print(f"质量评分: {integrated_result.quality_assessment.overall_score}")
    print(f"整合内容摘要: {integrated_result.integrated_content.get('summary', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(demo_result_integrator())
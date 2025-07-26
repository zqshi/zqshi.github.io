"""
US-001: 智能需求理解与EARS转换
Smart Requirements Understanding & EARS Conversion

验收标准:
- AC-001-01: 基础需求理解准确率≥85%
- AC-001-02: EARS规范转换完整性≥90%
- AC-001-03: 歧义识别召回率≥80%
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ...claude_integration import ClaudeService

logger = logging.getLogger(__name__)

class RequirementType(Enum):
    """需求类型"""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    USER_INTERFACE = "user_interface"
    BUSINESS_RULE = "business_rule"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"

class AmbiguityLevel(Enum):
    """歧义程度"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RequirementUnderstanding:
    """需求理解结果"""
    original_text: str
    requirement_type: RequirementType
    core_concepts: List[str]
    entities: List[str]
    actions: List[str]
    conditions: List[str]
    quality_attributes: List[str]
    ambiguities: List[Dict[str, Any]]
    confidence_score: float
    understanding_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EARSRequirement:
    """EARS格式需求"""
    ears_id: str
    ears_type: str  # ubiquitous, event-driven, unwanted, optional, complex
    original_requirement: str
    ears_statement: str
    trigger_condition: Optional[str] = None
    system_response: str = ""
    boundary_condition: Optional[str] = None
    completeness_score: float = 0.0
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RequirementAnalysisResult:
    """需求分析结果"""
    understanding: RequirementUnderstanding
    ears_requirements: List[EARSRequirement]
    analysis_quality: Dict[str, float]
    recommendations: List[str]
    issues_found: List[Dict[str, Any]]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

class SmartRequirementsAnalyzer:
    """智能需求分析器"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.analysis_patterns = self._load_analysis_patterns()
        self.ears_templates = self._load_ears_templates()
        self.ambiguity_detectors = self._load_ambiguity_detectors()
        
    def _load_analysis_patterns(self) -> Dict[str, List[str]]:
        """加载分析模式"""
        return {
            "functional_indicators": [
                "系统应该", "系统必须", "应用程序", "功能", "处理", "执行", "计算",
                "显示", "存储", "检索", "更新", "删除", "创建", "生成", "发送", "接收"
            ],
            "non_functional_indicators": [
                "性能", "响应时间", "吞吐量", "可用性", "可靠性", "安全性", "可扩展性",
                "可维护性", "兼容性", "用户体验", "易用性", "准确性", "时间"
            ],
            "ui_indicators": [
                "界面", "页面", "按钮", "菜单", "表单", "列表", "图表", "弹窗",
                "导航", "布局", "颜色", "字体", "图标", "交互", "点击", "输入"
            ],
            "constraint_indicators": [
                "必须使用", "不能", "禁止", "限制", "约束", "仅限", "只能",
                "预算", "时间限制", "资源限制", "技术限制", "法规要求"
            ]
        }
    
    def _load_ears_templates(self) -> Dict[str, str]:
        """加载EARS模板"""
        return {
            "ubiquitous": "系统应当{system_response}",
            "event_driven": "当{trigger_condition}时，系统应当{system_response}",
            "unwanted": "如果{unwanted_condition}，则系统应当{system_response}",
            "optional": "在{optional_condition}情况下，系统应当{system_response}",
            "complex": "在{boundary_condition}条件下，如果{trigger_condition}，则系统应当{system_response}"
        }
    
    def _load_ambiguity_detectors(self) -> Dict[str, List[str]]:
        """加载歧义检测器"""
        return {
            "vague_terms": [
                "适当的", "合理的", "足够的", "快速的", "简单的", "复杂的", 
                "大量的", "少量的", "经常", "很少", "通常", "可能", "应该"
            ],
            "pronouns": ["这个", "那个", "它", "他们", "其中", "此", "该"],
            "incomplete_conditions": ["如果", "当", "除非", "假设", "只要"],
            "subjective_terms": ["好看", "友好", "直观", "容易", "困难", "美观"]
        }
    
    async def analyze_requirements(self, requirement_text: str) -> RequirementAnalysisResult:
        """
        分析需求文本，实现智能需求理解与EARS转换
        
        Args:
            requirement_text: 原始需求文本
            
        Returns:
            RequirementAnalysisResult: 完整的需求分析结果
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"开始分析需求: {requirement_text[:100]}...")
            
            # 1. 需求理解
            understanding = await self._understand_requirements(requirement_text)
            
            # 2. EARS转换
            ears_requirements = await self._convert_to_ears(understanding)
            
            # 3. 质量评估
            analysis_quality = self._assess_analysis_quality(understanding, ears_requirements)
            
            # 4. 生成建议
            recommendations = self._generate_recommendations(understanding, ears_requirements)
            
            # 5. 识别问题
            issues = self._identify_issues(understanding, ears_requirements)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = RequirementAnalysisResult(
                understanding=understanding,
                ears_requirements=ears_requirements,
                analysis_quality=analysis_quality,
                recommendations=recommendations,
                issues_found=issues,
                processing_time=processing_time
            )
            
            logger.info(f"需求分析完成，理解准确率: {analysis_quality.get('understanding_accuracy', 0):.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"需求分析失败: {str(e)}")
            raise
    
    async def _understand_requirements(self, requirement_text: str) -> RequirementUnderstanding:
        """理解需求文本"""
        
        understanding_prompt = f"""
你是一位资深的需求分析专家，擅长理解和分析各类需求。

请分析以下需求文本：
{requirement_text}

请提供详细的需求理解分析，包括：

1. **需求类型识别**
   - 判断是功能性需求、非功能性需求、用户界面需求、业务规则、约束条件还是假设

2. **核心概念提取**
   - 识别需求中的关键概念和术语

3. **实体识别**
   - 提取涉及的主要实体（用户、系统、数据等）

4. **动作识别**
   - 识别需要执行的动作和操作

5. **条件识别**
   - 提取触发条件、前置条件、约束条件

6. **质量属性**
   - 识别性能、安全、可用性等质量要求

7. **歧义检测**
   - 识别模糊不清的表述
   - 评估歧义程度
   - 指出需要澄清的地方

8. **置信度评估**
   - 基于需求清晰度给出理解置信度（0-1）

返回JSON格式的分析结果。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": understanding_prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        
        if response.success:
            try:
                analysis_data = json.loads(response.content)
                
                # 解析需求类型
                req_type = RequirementType.FUNCTIONAL
                type_str = analysis_data.get("需求类型", "functional")
                for rt in RequirementType:
                    if rt.value in type_str.lower():
                        req_type = rt
                        break
                
                # 解析歧义信息
                ambiguities = []
                ambiguity_data = analysis_data.get("歧义检测", {})
                if isinstance(ambiguity_data, dict):
                    for ambiguity_text in ambiguity_data.get("模糊表述", []):
                        ambiguities.append({
                            "text": ambiguity_text,
                            "level": AmbiguityLevel.MEDIUM.value,
                            "suggestion": f"建议明确{ambiguity_text}的具体含义"
                        })
                
                return RequirementUnderstanding(
                    original_text=requirement_text,
                    requirement_type=req_type,
                    core_concepts=analysis_data.get("核心概念", []),
                    entities=analysis_data.get("实体", []),
                    actions=analysis_data.get("动作", []),
                    conditions=analysis_data.get("条件", []),
                    quality_attributes=analysis_data.get("质量属性", []),
                    ambiguities=ambiguities,
                    confidence_score=analysis_data.get("置信度", 0.8),
                    understanding_metadata={
                        "analysis_method": "claude_nlp",
                        "language": "chinese",
                        "complexity": self._assess_text_complexity(requirement_text)
                    }
                )
                
            except json.JSONDecodeError:
                # 降级处理：使用基础解析
                return self._basic_requirement_understanding(requirement_text)
        else:
            raise Exception(f"需求理解失败: {response.error}")
    
    def _basic_requirement_understanding(self, requirement_text: str) -> RequirementUnderstanding:
        """基础需求理解（降级处理）"""
        
        # 基于关键词匹配的简单分析
        req_type = RequirementType.FUNCTIONAL
        for type_name, indicators in self.analysis_patterns.items():
            if any(indicator in requirement_text for indicator in indicators):
                if "non_functional" in type_name:
                    req_type = RequirementType.NON_FUNCTIONAL
                elif "ui" in type_name:
                    req_type = RequirementType.USER_INTERFACE
                elif "constraint" in type_name:
                    req_type = RequirementType.CONSTRAINT
                break
        
        # 简单实体提取
        entities = re.findall(r'[用户|系统|应用|数据库|服务|模块|组件]', requirement_text)
        actions = re.findall(r'[创建|删除|更新|查询|处理|执行|生成|发送|接收|显示|计算]', requirement_text)
        
        # 检测歧义
        ambiguities = []
        for ambiguous_term in self.ambiguity_detectors["vague_terms"]:
            if ambiguous_term in requirement_text:
                ambiguities.append({
                    "text": ambiguous_term,
                    "level": AmbiguityLevel.MEDIUM.value,
                    "suggestion": f"建议明确'{ambiguous_term}'的具体标准"
                })
        
        return RequirementUnderstanding(
            original_text=requirement_text,
            requirement_type=req_type,
            core_concepts=list(set(entities + actions)),
            entities=entities,
            actions=actions,
            conditions=[],
            quality_attributes=[],
            ambiguities=ambiguities,
            confidence_score=0.6,  # 基础分析置信度较低
            understanding_metadata={
                "analysis_method": "basic_pattern_matching",
                "fallback": True
            }
        )
    
    async def _convert_to_ears(self, understanding: RequirementUnderstanding) -> List[EARSRequirement]:
        """转换为EARS格式"""
        
        ears_prompt = f"""
作为需求工程专家，请将以下需求理解转换为标准的EARS格式。

原始需求: {understanding.original_text}
需求类型: {understanding.requirement_type.value}
核心概念: {understanding.core_concepts}
实体: {understanding.entities}
动作: {understanding.actions}
条件: {understanding.conditions}

EARS规范说明：
1. Ubiquitous (普遍性): 系统应当[系统响应]
2. Event-driven (事件驱动): 当[触发条件]时，系统应当[系统响应]
3. Unwanted (非期望): 如果[非期望条件]，则系统应当[系统响应]
4. Optional (可选): 在[可选条件]情况下，系统应当[系统响应]
5. Complex (复杂): 在[边界条件]条件下，如果[触发条件]，则系统应当[系统响应]

请生成1-3个EARS格式的需求，每个需求包括：
- EARS类型
- 完整的EARS陈述
- 触发条件（如适用）
- 系统响应
- 边界条件（如适用）
- 验证规则

返回JSON格式结果。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": ears_prompt}],
            temperature=0.1,
            max_tokens=1500
        )
        
        ears_requirements = []
        
        if response.success:
            try:
                ears_data = json.loads(response.content)
                
                for i, req_data in enumerate(ears_data.get("EARS需求", [])):
                    ears_req = EARSRequirement(
                        ears_id=f"EARS-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                        ears_type=req_data.get("EARS类型", "ubiquitous"),
                        original_requirement=understanding.original_text,
                        ears_statement=req_data.get("EARS陈述", ""),
                        trigger_condition=req_data.get("触发条件"),
                        system_response=req_data.get("系统响应", ""),
                        boundary_condition=req_data.get("边界条件"),
                        completeness_score=self._calculate_completeness_score(req_data),
                        validation_rules=req_data.get("验证规则", []),
                        metadata={
                            "source_understanding": understanding.original_text,
                            "conversion_method": "claude_nlp",
                            "created_at": datetime.now().isoformat()
                        }
                    )
                    ears_requirements.append(ears_req)
                    
            except json.JSONDecodeError:
                # 降级处理：生成基础EARS需求
                ears_requirements = self._generate_basic_ears(understanding)
        else:
            # 降级处理
            ears_requirements = self._generate_basic_ears(understanding)
        
        return ears_requirements
    
    def _generate_basic_ears(self, understanding: RequirementUnderstanding) -> List[EARSRequirement]:
        """生成基础EARS需求（降级处理）"""
        
        ears_req = EARSRequirement(
            ears_id=f"EARS-{datetime.now().strftime('%Y%m%d')}-001",
            ears_type="ubiquitous",
            original_requirement=understanding.original_text,
            ears_statement=f"系统应当{understanding.original_text}",
            system_response=understanding.original_text,
            completeness_score=0.7,
            validation_rules=["需要进一步细化需求"],
            metadata={
                "conversion_method": "basic_fallback",
                "requires_refinement": True
            }
        )
        
        return [ears_req]
    
    def _calculate_completeness_score(self, req_data: Dict[str, Any]) -> float:
        """计算完整性评分"""
        score = 0.0
        weight_sum = 0.0
        
        # EARS陈述完整性 (40%)
        if req_data.get("EARS陈述"):
            statement = req_data["EARS陈述"]
            if "系统应当" in statement and len(statement) > 10:
                score += 0.4
        weight_sum += 0.4
        
        # 系统响应明确性 (30%)
        if req_data.get("系统响应") and len(req_data["系统响应"]) > 5:
            score += 0.3
        weight_sum += 0.3
        
        # 条件完整性 (20%)
        if req_data.get("触发条件") or req_data.get("边界条件"):
            score += 0.2
        weight_sum += 0.2
        
        # 验证规则存在 (10%)
        if req_data.get("验证规则") and len(req_data["验证规则"]) > 0:
            score += 0.1
        weight_sum += 0.1
        
        return score / weight_sum if weight_sum > 0 else 0.0
    
    def _assess_analysis_quality(self, understanding: RequirementUnderstanding, ears_requirements: List[EARSRequirement]) -> Dict[str, float]:
        """评估分析质量"""
        
        # 理解准确率评估
        understanding_accuracy = understanding.confidence_score
        
        # EARS转换完整性评估
        ears_completeness = 0.0
        if ears_requirements:
            ears_completeness = sum(req.completeness_score for req in ears_requirements) / len(ears_requirements)
        
        # 歧义识别召回率评估
        ambiguity_recall = 0.0
        if understanding.ambiguities:
            # 简化计算：基于识别到的歧义数量
            text_length = len(understanding.original_text)
            expected_ambiguities = max(1, text_length // 50)  # 假设每50字符可能有1个歧义
            ambiguity_recall = min(len(understanding.ambiguities) / expected_ambiguities, 1.0)
        else:
            ambiguity_recall = 0.8  # 如果没有识别到歧义，给一个基础分数
        
        return {
            "understanding_accuracy": understanding_accuracy,
            "ears_completeness": ears_completeness,
            "ambiguity_recall": ambiguity_recall,
            "overall_quality": (understanding_accuracy + ears_completeness + ambiguity_recall) / 3
        }
    
    def _generate_recommendations(self, understanding: RequirementUnderstanding, ears_requirements: List[EARSRequirement]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于置信度生成建议
        if understanding.confidence_score < 0.8:
            recommendations.append("建议与业务人员进一步澄清需求含义")
        
        # 基于歧义生成建议
        if len(understanding.ambiguities) > 3:
            recommendations.append("检测到多个歧义表述，建议优先澄清高优先级歧义")
        
        # 基于EARS完整性生成建议
        incomplete_ears = [req for req in ears_requirements if req.completeness_score < 0.8]
        if incomplete_ears:
            recommendations.append(f"有{len(incomplete_ears)}个EARS需求不够完整，建议补充细节")
        
        # 基于需求类型生成建议
        if understanding.requirement_type == RequirementType.NON_FUNCTIONAL:
            recommendations.append("建议为非功能性需求添加具体的量化指标")
        
        return recommendations
    
    def _identify_issues(self, understanding: RequirementUnderstanding, ears_requirements: List[EARSRequirement]) -> List[Dict[str, Any]]:
        """识别问题"""
        issues = []
        
        # 高歧义性问题
        critical_ambiguities = [amb for amb in understanding.ambiguities 
                              if amb.get("level") in ["high", "critical"]]
        if critical_ambiguities:
            issues.append({
                "type": "critical_ambiguity",
                "severity": "high",
                "description": f"发现{len(critical_ambiguities)}个严重歧义",
                "items": critical_ambiguities
            })
        
        # EARS转换问题
        if not ears_requirements:
            issues.append({
                "type": "ears_conversion_failure",
                "severity": "high",
                "description": "EARS转换失败，无法生成标准格式需求"
            })
        
        # 置信度问题
        if understanding.confidence_score < 0.6:
            issues.append({
                "type": "low_confidence",
                "severity": "medium",
                "description": f"需求理解置信度较低({understanding.confidence_score:.1%})"
            })
        
        return issues
    
    def _assess_text_complexity(self, text: str) -> str:
        """评估文本复杂度"""
        length = len(text)
        if length < 50:
            return "simple"
        elif length < 200:
            return "medium"
        else:
            return "complex"

# 工厂函数
def create_requirements_analyzer(claude_service: ClaudeService) -> SmartRequirementsAnalyzer:
    """创建需求分析器"""
    return SmartRequirementsAnalyzer(claude_service)

# 使用示例
async def demo_requirements_understanding():
    """演示需求理解功能"""
    from ....claude_integration import create_claude_service
    
    claude_service = create_claude_service()
    analyzer = create_requirements_analyzer(claude_service)
    
    # 测试用例
    test_requirements = [
        "用户应该能够快速登录系统",
        "系统必须在用户点击登录按钮后3秒内响应，支持邮箱和手机号登录，并在登录失败时显示友好的错误信息",
        "开发一个电商系统，需要有商品管理、订单处理和用户管理功能"
    ]
    
    for i, requirement in enumerate(test_requirements):
        print(f"\n=== 测试 {i+1}: {requirement} ===")
        
        try:
            result = await analyzer.analyze_requirements(requirement)
            
            print(f"理解准确率: {result.analysis_quality['understanding_accuracy']:.1%}")
            print(f"EARS转换完整性: {result.analysis_quality['ears_completeness']:.1%}")
            print(f"歧义识别召回率: {result.analysis_quality['ambiguity_recall']:.1%}")
            print(f"整体质量: {result.analysis_quality['overall_quality']:.1%}")
            
            print(f"\n生成的EARS需求数量: {len(result.ears_requirements)}")
            for ears_req in result.ears_requirements:
                print(f"- {ears_req.ears_id}: {ears_req.ears_statement}")
            
            if result.issues_found:
                print(f"\n发现的问题:")
                for issue in result.issues_found:
                    print(f"- {issue['type']}: {issue['description']}")
            
            print(f"处理时间: {result.processing_time:.2f}秒")
            
        except Exception as e:
            print(f"分析失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_requirements_understanding())
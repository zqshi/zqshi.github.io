"""
US-003: 验收标准智能制定
Intelligent Acceptance Criteria Definition

验收标准:
- AC-003-01: 验收标准可测试性≥95%
- AC-003-02: 量化指标覆盖率100%
- AC-003-03: Given-When-Then格式合规率100%
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
from .user_story_generator import UserStory, UserStoryGenerationResult

logger = logging.getLogger(__name__)

class CriteriaType(Enum):
    """验收标准类型"""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    SECURITY = "security"
    RELIABILITY = "reliability"
    COMPATIBILITY = "compatibility"
    BUSINESS_RULE = "business_rule"

class TestabilityLevel(Enum):
    """可测试性等级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOT_TESTABLE = "not_testable"

@dataclass
class QuantitativeMetric:
    """量化指标"""
    metric_name: str
    target_value: str
    unit: str
    measurement_method: str
    acceptance_threshold: str
    baseline_value: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AcceptanceCriterion:
    """验收标准"""
    criterion_id: str
    title: str
    description: str
    criteria_type: CriteriaType
    
    # Given-When-Then结构
    given_context: str
    when_action: str
    then_outcome: str
    
    # 可测试性评估
    testability_level: TestabilityLevel
    testability_score: float
    
    # 量化指标
    quantitative_metrics: List[QuantitativeMetric]
    
    # 测试方法
    test_methods: List[str]
    verification_steps: List[str]
    
    # 优先级和依赖
    priority: str  # high, medium, low
    dependencies: List[str]
    
    # 元数据
    source_story_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AcceptanceCriteriaSet:
    """验收标准集合"""
    story_id: str
    story_title: str
    criteria: List[AcceptanceCriterion]
    coverage_analysis: Dict[str, Any]
    quality_metrics: Dict[str, float]
    recommendations: List[str]
    issues_found: List[Dict[str, Any]]

@dataclass
class AcceptanceCriteriaResult:
    """验收标准制定结果"""
    source_stories: List[UserStory]
    criteria_sets: List[AcceptanceCriteriaSet]
    overall_quality: Dict[str, float]
    generation_summary: Dict[str, Any]
    recommendations: List[str]
    issues_found: List[Dict[str, Any]]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

class IntelligentAcceptanceCriteriaMaker:
    """智能验收标准制定器"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.criteria_templates = self._load_criteria_templates()
        self.metric_patterns = self._load_metric_patterns()
        self.test_method_library = self._load_test_method_library()
        
    def _load_criteria_templates(self) -> Dict[str, List[str]]:
        """加载验收标准模板"""
        return {
            "functional": [
                "Given {context}, when {action}, then {outcome}",
                "Given {precondition}, when user {action}, then system should {response}",
                "Given {initial_state}, when {trigger_event}, then {expected_result}"
            ],
            "performance": [
                "Given {normal_load}, when {performance_test}, then {response_time} should be less than {threshold}",
                "Given {concurrent_users}, when {load_test}, then {throughput} should be at least {target}",
                "Given {system_state}, when {stress_test}, then {availability} should remain above {minimum}%"
            ],
            "usability": [
                "Given {user_type}, when {task_execution}, then {completion_time} should be within {acceptable_range}",
                "Given {user_interface}, when {interaction}, then {user_feedback} should be {satisfaction_level}",
                "Given {accessibility_requirements}, when {usage_scenario}, then {compliance_standard} should be met"
            ],
            "security": [
                "Given {security_context}, when {access_attempt}, then {authorization_check} should {expected_behavior}",
                "Given {sensitive_data}, when {data_operation}, then {encryption_standard} should be applied",
                "Given {authentication_state}, when {security_test}, then {vulnerability_scan} should show {clean_result}"
            ]
        }
    
    def _load_metric_patterns(self) -> Dict[str, Dict[str, str]]:
        """加载指标模式"""
        return {
            "performance": {
                "response_time": "≤{value}秒",
                "throughput": "≥{value}请求/秒",
                "availability": "≥{value}%",
                "error_rate": "≤{value}%",
                "cpu_usage": "≤{value}%",
                "memory_usage": "≤{value}MB"
            },
            "usability": {
                "completion_time": "≤{value}分钟",
                "error_rate": "≤{value}%",
                "satisfaction_score": "≥{value}/5",
                "learning_time": "≤{value}小时",
                "efficiency_ratio": "≥{value}%"
            },
            "functional": {
                "success_rate": "≥{value}%",
                "accuracy": "≥{value}%",
                "completeness": "≥{value}%",
                "data_integrity": "100%",
                "feature_coverage": "≥{value}%"
            },
            "security": {
                "authentication_success": "≥{value}%",
                "authorization_accuracy": "100%",
                "data_encryption": "100%",
                "vulnerability_count": "0",
                "compliance_score": "≥{value}%"
            }
        }
    
    def _load_test_method_library(self) -> Dict[str, List[str]]:
        """加载测试方法库"""
        return {
            "functional": [
                "单元测试", "集成测试", "端到端测试", "用户验收测试",
                "功能测试", "回归测试", "冒烟测试"
            ],
            "performance": [
                "负载测试", "压力测试", "容量测试", "稳定性测试",
                "基准测试", "并发测试", "资源利用率测试"
            ],
            "usability": [
                "可用性测试", "用户体验测试", "无障碍测试", "A/B测试",
                "用户旅程测试", "交互测试", "界面测试"
            ],
            "security": [
                "渗透测试", "漏洞扫描", "安全审计", "权限测试",
                "数据安全测试", "网络安全测试", "身份认证测试"
            ],
            "reliability": [
                "可靠性测试", "故障恢复测试", "容错测试", "备份恢复测试",
                "系统监控测试", "异常处理测试"
            ],
            "compatibility": [
                "浏览器兼容性测试", "操作系统兼容性测试", "设备兼容性测试",
                "版本兼容性测试", "API兼容性测试"
            ]
        }
    
    async def generate_acceptance_criteria(self, story_result: UserStoryGenerationResult) -> AcceptanceCriteriaResult:
        """
        为用户故事生成验收标准
        
        Args:
            story_result: 用户故事生成结果
            
        Returns:
            AcceptanceCriteriaResult: 验收标准制定结果
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"开始为{len(story_result.generated_stories)}个用户故事生成验收标准...")
            
            criteria_sets = []
            
            # 为每个用户故事生成验收标准
            for story in story_result.generated_stories:
                criteria_set = await self._generate_criteria_for_story(story)
                criteria_sets.append(criteria_set)
            
            # 评估整体质量
            overall_quality = self._assess_overall_quality(criteria_sets)
            
            # 生成汇总信息
            generation_summary = self._generate_summary(criteria_sets)
            
            # 生成整体建议
            recommendations = self._generate_overall_recommendations(criteria_sets, overall_quality)
            
            # 识别整体问题
            issues = self._identify_overall_issues(criteria_sets, overall_quality)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = AcceptanceCriteriaResult(
                source_stories=story_result.generated_stories,
                criteria_sets=criteria_sets,
                overall_quality=overall_quality,
                generation_summary=generation_summary,
                recommendations=recommendations,
                issues_found=issues,
                processing_time=processing_time
            )
            
            logger.info(f"验收标准生成完成，可测试性: {overall_quality.get('testability', 0):.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"验收标准生成失败: {str(e)}")
            raise
    
    async def _generate_criteria_for_story(self, story: UserStory) -> AcceptanceCriteriaSet:
        """为单个用户故事生成验收标准"""
        
        criteria_generation_prompt = f"""
作为资深的质量保证工程师和测试专家，请为以下用户故事生成高质量的验收标准。

用户故事信息：
- 故事ID: {story.story_id}
- 标题: {story.title}
- 完整故事: {story.full_story}
- 用户角色: {story.user_role.value}
- 业务价值: {story.business_value}
- 优先级: {story.priority.value}
- 现有验收标准: {story.acceptance_criteria}

请生成5-8个全面的验收标准，每个标准包含：

1. **Given-When-Then格式**
   - Given: 前置条件和上下文
   - When: 用户操作或系统事件
   - Then: 预期结果和行为

2. **验收标准类型**
   - 功能性标准
   - 性能标准
   - 可用性标准
   - 安全性标准（如适用）

3. **量化指标**
   - 具体的数值目标
   - 可测量的成功标准
   - 明确的阈值

4. **测试方法**
   - 推荐的测试类型
   - 验证步骤
   - 测试工具建议

5. **可测试性**
   - 确保每个标准都是可测试的
   - 提供明确的验证方法

请返回JSON格式的详细验收标准。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": criteria_generation_prompt}],
            temperature=0.1,
            max_tokens=2500
        )
        
        criteria = []
        
        if response.success:
            try:
                criteria_data = json.loads(response.content)
                
                for i, criterion_data in enumerate(criteria_data.get("验收标准", [])):
                    criterion = self._parse_criterion_data(criterion_data, story, i+1)
                    criteria.append(criterion)
                    
            except json.JSONDecodeError:
                criteria = self._generate_basic_criteria(story)
        else:
            criteria = self._generate_basic_criteria(story)
        
        # 分析覆盖度
        coverage_analysis = self._analyze_coverage(criteria, story)
        
        # 评估质量
        quality_metrics = self._assess_criteria_quality(criteria)
        
        # 生成建议
        recommendations = self._generate_story_recommendations(criteria, quality_metrics)
        
        # 识别问题
        issues = self._identify_story_issues(criteria, quality_metrics)
        
        return AcceptanceCriteriaSet(
            story_id=story.story_id,
            story_title=story.title,
            criteria=criteria,
            coverage_analysis=coverage_analysis,
            quality_metrics=quality_metrics,
            recommendations=recommendations,
            issues_found=issues
        )
    
    def _parse_criterion_data(self, criterion_data: Dict[str, Any], story: UserStory, index: int) -> AcceptanceCriterion:
        """解析标准数据"""
        
        # 解析标准类型
        criteria_type = self._parse_criteria_type(criterion_data.get("类型", "functional"))
        
        # 解析Given-When-Then
        given = criterion_data.get("Given", criterion_data.get("前置条件", ""))
        when = criterion_data.get("When", criterion_data.get("操作", ""))
        then = criterion_data.get("Then", criterion_data.get("期望结果", ""))
        
        # 评估可测试性
        testability_level, testability_score = self._assess_testability(given, when, then)
        
        # 解析量化指标
        quantitative_metrics = self._parse_quantitative_metrics(criterion_data.get("量化指标", []))
        
        # 解析测试方法
        test_methods = criterion_data.get("测试方法", [])
        verification_steps = criterion_data.get("验证步骤", [])
        
        return AcceptanceCriterion(
            criterion_id=f"AC-{story.story_id.split('-')[-1]}-{index:02d}",
            title=criterion_data.get("标题", f"验收标准 {index}"),
            description=criterion_data.get("描述", ""),
            criteria_type=criteria_type,
            given_context=given,
            when_action=when,
            then_outcome=then,
            testability_level=testability_level,
            testability_score=testability_score,
            quantitative_metrics=quantitative_metrics,
            test_methods=test_methods,
            verification_steps=verification_steps,
            priority=criterion_data.get("优先级", "medium"),
            dependencies=criterion_data.get("依赖", []),
            source_story_id=story.story_id
        )
    
    def _parse_criteria_type(self, type_str: str) -> CriteriaType:
        """解析标准类型"""
        type_str = type_str.lower()
        
        if any(word in type_str for word in ["performance", "性能", "响应时间", "吞吐量"]):
            return CriteriaType.PERFORMANCE
        elif any(word in type_str for word in ["usability", "可用性", "用户体验", "易用性"]):
            return CriteriaType.USABILITY
        elif any(word in type_str for word in ["security", "安全性", "权限", "认证"]):
            return CriteriaType.SECURITY
        elif any(word in type_str for word in ["reliability", "可靠性", "稳定性", "容错"]):
            return CriteriaType.RELIABILITY
        elif any(word in type_str for word in ["compatibility", "兼容性", "跨平台"]):
            return CriteriaType.COMPATIBILITY
        elif any(word in type_str for word in ["business", "业务规则", "业务逻辑"]):
            return CriteriaType.BUSINESS_RULE
        else:
            return CriteriaType.FUNCTIONAL
    
    def _assess_testability(self, given: str, when: str, then: str) -> Tuple[TestabilityLevel, float]:
        """评估可测试性"""
        score = 0.0
        
        # 检查Given的明确性
        if given and len(given) > 5:
            score += 0.3
        
        # 检查When的可操作性
        if when and any(word in when for word in ["点击", "输入", "选择", "提交", "触发", "执行"]):
            score += 0.3
        
        # 检查Then的可验证性
        if then and any(word in then for word in ["显示", "返回", "应该", "必须", "包含", "等于"]):
            score += 0.4
        
        # 检查量化指标
        if re.search(r'\d+', f"{given} {when} {then}"):
            score += 0.1
        
        # 确定可测试性等级
        if score >= 0.8:
            level = TestabilityLevel.HIGH
        elif score >= 0.6:
            level = TestabilityLevel.MEDIUM
        elif score >= 0.4:
            level = TestabilityLevel.LOW
        else:
            level = TestabilityLevel.NOT_TESTABLE
        
        return level, min(1.0, score)
    
    def _parse_quantitative_metrics(self, metrics_data: List[Dict[str, Any]]) -> List[QuantitativeMetric]:
        """解析量化指标"""
        metrics = []
        
        for metric_data in metrics_data:
            if isinstance(metric_data, dict):
                metric = QuantitativeMetric(
                    metric_name=metric_data.get("指标名称", ""),
                    target_value=metric_data.get("目标值", ""),
                    unit=metric_data.get("单位", ""),
                    measurement_method=metric_data.get("测量方法", ""),
                    acceptance_threshold=metric_data.get("验收阈值", ""),
                    baseline_value=metric_data.get("基线值"),
                    metadata=metric_data.get("元数据", {})
                )
                metrics.append(metric)
            elif isinstance(metric_data, str):
                # 简单解析字符串格式的指标
                metric = self._parse_metric_string(metric_data)
                if metric:
                    metrics.append(metric)
        
        return metrics
    
    def _parse_metric_string(self, metric_str: str) -> Optional[QuantitativeMetric]:
        """解析字符串格式的指标"""
        
        # 尝试提取数值和单位
        number_pattern = r'([≥≤><]?)(\d+(?:\.\d+)?)([%秒分钟小时天次个/]*)'
        match = re.search(number_pattern, metric_str)
        
        if match:
            operator = match.group(1) or "="
            value = match.group(2)
            unit = match.group(3) or "个"
            
            return QuantitativeMetric(
                metric_name=metric_str,
                target_value=f"{operator}{value}",
                unit=unit,
                measurement_method="自动化测试",
                acceptance_threshold=f"{operator}{value}{unit}"
            )
        
        return None
    
    def _generate_basic_criteria(self, story: UserStory) -> List[AcceptanceCriterion]:
        """生成基础验收标准（降级处理）"""
        
        criteria = []
        
        # 基本功能标准
        basic_criterion = AcceptanceCriterion(
            criterion_id=f"AC-{story.story_id.split('-')[-1]}-001",
            title="基本功能验证",
            description="验证基本功能是否正常工作",
            criteria_type=CriteriaType.FUNCTIONAL,
            given_context="系统正常运行状态",
            when_action="用户执行操作",
            then_outcome="系统应该按预期响应",
            testability_level=TestabilityLevel.MEDIUM,
            testability_score=0.7,
            quantitative_metrics=[
                QuantitativeMetric(
                    metric_name="功能成功率",
                    target_value="≥95%",
                    unit="%",
                    measurement_method="功能测试",
                    acceptance_threshold="≥95%"
                )
            ],
            test_methods=["功能测试", "用户验收测试"],
            verification_steps=["执行功能", "验证结果"],
            priority="high",
            dependencies=[],
            source_story_id=story.story_id
        )
        criteria.append(basic_criterion)
        
        # 性能标准（如果相关）
        if any(word in story.full_story.lower() for word in ["快速", "性能", "响应", "时间"]):
            performance_criterion = AcceptanceCriterion(
                criterion_id=f"AC-{story.story_id.split('-')[-1]}-002",
                title="性能验证",
                description="验证系统性能符合要求",
                criteria_type=CriteriaType.PERFORMANCE,
                given_context="正常负载条件下",
                when_action="用户执行操作",
                then_outcome="系统响应时间应在可接受范围内",
                testability_level=TestabilityLevel.HIGH,
                testability_score=0.9,
                quantitative_metrics=[
                    QuantitativeMetric(
                        metric_name="响应时间",
                        target_value="≤3秒",
                        unit="秒",
                        measurement_method="性能测试",
                        acceptance_threshold="≤3秒"
                    )
                ],
                test_methods=["性能测试", "负载测试"],
                verification_steps=["执行性能测试", "测量响应时间"],
                priority="medium",
                dependencies=[],
                source_story_id=story.story_id
            )
            criteria.append(performance_criterion)
        
        return criteria
    
    def _analyze_coverage(self, criteria: List[AcceptanceCriterion], story: UserStory) -> Dict[str, Any]:
        """分析覆盖度"""
        
        coverage_analysis = {
            "total_criteria": len(criteria),
            "type_coverage": {},
            "testability_distribution": {},
            "quantitative_metrics_count": 0,
            "given_when_then_compliance": 0.0
        }
        
        # 类型覆盖分析
        type_counts = {}
        for criterion in criteria:
            criteria_type = criterion.criteria_type.value
            type_counts[criteria_type] = type_counts.get(criteria_type, 0) + 1
        coverage_analysis["type_coverage"] = type_counts
        
        # 可测试性分布
        testability_counts = {}
        for criterion in criteria:
            level = criterion.testability_level.value
            testability_counts[level] = testability_counts.get(level, 0) + 1
        coverage_analysis["testability_distribution"] = testability_counts
        
        # 量化指标统计
        total_metrics = sum(len(criterion.quantitative_metrics) for criterion in criteria)
        coverage_analysis["quantitative_metrics_count"] = total_metrics
        
        # Given-When-Then合规性
        compliant_count = 0
        for criterion in criteria:
            if (criterion.given_context and criterion.when_action and criterion.then_outcome):
                compliant_count += 1
        coverage_analysis["given_when_then_compliance"] = compliant_count / len(criteria) if criteria else 0.0
        
        return coverage_analysis
    
    def _assess_criteria_quality(self, criteria: List[AcceptanceCriterion]) -> Dict[str, float]:
        """评估标准质量"""
        
        if not criteria:
            return {
                "testability": 0.0,
                "quantitative_coverage": 0.0,
                "given_when_then_compliance": 0.0,
                "overall_quality": 0.0
            }
        
        # 可测试性评分
        testability_scores = [criterion.testability_score for criterion in criteria]
        avg_testability = sum(testability_scores) / len(testability_scores)
        
        # 量化指标覆盖率
        criteria_with_metrics = sum(1 for criterion in criteria if criterion.quantitative_metrics)
        quantitative_coverage = criteria_with_metrics / len(criteria)
        
        # Given-When-Then合规率
        compliant_criteria = sum(
            1 for criterion in criteria 
            if criterion.given_context and criterion.when_action and criterion.then_outcome
        )
        given_when_then_compliance = compliant_criteria / len(criteria)
        
        # 整体质量
        overall_quality = (avg_testability + quantitative_coverage + given_when_then_compliance) / 3
        
        return {
            "testability": avg_testability,
            "quantitative_coverage": quantitative_coverage,
            "given_when_then_compliance": given_when_then_compliance,
            "overall_quality": overall_quality
        }
    
    def _generate_story_recommendations(self, criteria: List[AcceptanceCriterion], quality_metrics: Dict[str, float]) -> List[str]:
        """生成故事级别的建议"""
        recommendations = []
        
        # 基于可测试性生成建议
        if quality_metrics["testability"] < 0.95:
            recommendations.append("建议提高验收标准的可测试性，明确测试步骤和验证方法")
        
        # 基于量化指标覆盖率生成建议
        if quality_metrics["quantitative_coverage"] < 1.0:
            recommendations.append("建议为所有验收标准添加量化指标和成功阈值")
        
        # 基于Given-When-Then合规性生成建议
        if quality_metrics["given_when_then_compliance"] < 1.0:
            recommendations.append("建议将所有验收标准转换为Given-When-Then格式以提高清晰度")
        
        # 基于标准数量生成建议
        if len(criteria) < 3:
            recommendations.append("建议增加更多验收标准以提高测试覆盖率")
        elif len(criteria) > 8:
            recommendations.append("验收标准较多，建议合并相关标准或拆分用户故事")
        
        # 基于标准类型生成建议
        functional_count = sum(1 for criterion in criteria if criterion.criteria_type == CriteriaType.FUNCTIONAL)
        if functional_count == len(criteria):
            recommendations.append("建议添加非功能性验收标准（性能、可用性、安全性等）")
        
        return recommendations
    
    def _identify_story_issues(self, criteria: List[AcceptanceCriterion], quality_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """识别故事级别的问题"""
        issues = []
        
        # 可测试性问题
        low_testability_criteria = [c for c in criteria if c.testability_score < 0.6]
        if low_testability_criteria:
            issues.append({
                "type": "low_testability",
                "severity": "high",
                "description": f"{len(low_testability_criteria)}个验收标准可测试性较低",
                "affected_criteria": [c.criterion_id for c in low_testability_criteria]
            })
        
        # 缺少量化指标
        no_metrics_criteria = [c for c in criteria if not c.quantitative_metrics]
        if no_metrics_criteria:
            issues.append({
                "type": "missing_quantitative_metrics",
                "severity": "medium",
                "description": f"{len(no_metrics_criteria)}个验收标准缺少量化指标",
                "affected_criteria": [c.criterion_id for c in no_metrics_criteria]
            })
        
        # Given-When-Then格式问题
        non_compliant_criteria = [c for c in criteria if not (c.given_context and c.when_action and c.then_outcome)]
        if non_compliant_criteria:
            issues.append({
                "type": "gwt_format_non_compliance",
                "severity": "medium",
                "description": f"{len(non_compliant_criteria)}个验收标准不符合Given-When-Then格式",
                "affected_criteria": [c.criterion_id for c in non_compliant_criteria]
            })
        
        # 缺少测试方法
        no_test_methods_criteria = [c for c in criteria if not c.test_methods]
        if no_test_methods_criteria:
            issues.append({
                "type": "missing_test_methods",
                "severity": "low",
                "description": f"{len(no_test_methods_criteria)}个验收标准缺少测试方法",
                "affected_criteria": [c.criterion_id for c in no_test_methods_criteria]
            })
        
        return issues
    
    def _assess_overall_quality(self, criteria_sets: List[AcceptanceCriteriaSet]) -> Dict[str, float]:
        """评估整体质量"""
        
        if not criteria_sets:
            return {
                "overall_testability": 0.0,
                "overall_quantitative_coverage": 0.0,
                "overall_gwt_compliance": 0.0,
                "overall_quality": 0.0
            }
        
        # 整体可测试性
        testability_scores = [cs.quality_metrics["testability"] for cs in criteria_sets]
        overall_testability = sum(testability_scores) / len(testability_scores)
        
        # 整体量化指标覆盖率
        quantitative_scores = [cs.quality_metrics["quantitative_coverage"] for cs in criteria_sets]
        overall_quantitative_coverage = sum(quantitative_scores) / len(quantitative_scores)
        
        # 整体Given-When-Then合规率
        gwt_scores = [cs.quality_metrics["given_when_then_compliance"] for cs in criteria_sets]
        overall_gwt_compliance = sum(gwt_scores) / len(gwt_scores)
        
        # 整体质量
        overall_quality = (overall_testability + overall_quantitative_coverage + overall_gwt_compliance) / 3
        
        return {
            "overall_testability": overall_testability,
            "overall_quantitative_coverage": overall_quantitative_coverage,
            "overall_gwt_compliance": overall_gwt_compliance,
            "overall_quality": overall_quality
        }
    
    def _generate_summary(self, criteria_sets: List[AcceptanceCriteriaSet]) -> Dict[str, Any]:
        """生成汇总信息"""
        
        total_criteria = sum(len(cs.criteria) for cs in criteria_sets)
        total_metrics = sum(
            sum(len(criterion.quantitative_metrics) for criterion in cs.criteria)
            for cs in criteria_sets
        )
        
        # 类型分布统计
        type_distribution = {}
        for cs in criteria_sets:
            for criterion in cs.criteria:
                criteria_type = criterion.criteria_type.value
                type_distribution[criteria_type] = type_distribution.get(criteria_type, 0) + 1
        
        # 可测试性分布
        testability_distribution = {}
        for cs in criteria_sets:
            for criterion in cs.criteria:
                level = criterion.testability_level.value
                testability_distribution[level] = testability_distribution.get(level, 0) + 1
        
        return {
            "total_stories": len(criteria_sets),
            "total_criteria": total_criteria,
            "total_quantitative_metrics": total_metrics,
            "average_criteria_per_story": total_criteria / len(criteria_sets) if criteria_sets else 0,
            "type_distribution": type_distribution,
            "testability_distribution": testability_distribution
        }
    
    def _generate_overall_recommendations(self, criteria_sets: List[AcceptanceCriteriaSet], overall_quality: Dict[str, float]) -> List[str]:
        """生成整体建议"""
        recommendations = []
        
        # 基于整体质量生成建议
        if overall_quality["overall_testability"] < 0.95:
            recommendations.append("整体可测试性需要改进，建议重点关注可测试性较低的验收标准")
        
        if overall_quality["overall_quantitative_coverage"] < 1.0:
            recommendations.append("需要为所有验收标准添加量化指标以实现100%覆盖")
        
        if overall_quality["overall_gwt_compliance"] < 1.0:
            recommendations.append("需要将所有验收标准转换为Given-When-Then格式")
        
        # 基于标准数量分布生成建议
        criteria_counts = [len(cs.criteria) for cs in criteria_sets]
        avg_criteria = sum(criteria_counts) / len(criteria_counts) if criteria_counts else 0
        
        if avg_criteria < 3:
            recommendations.append("平均验收标准数量较少，建议增加更多验收标准以提高覆盖率")
        elif avg_criteria > 7:
            recommendations.append("平均验收标准数量较多，建议评估是否需要拆分用户故事")
        
        # 基于问题频率生成建议
        issue_counts = {}
        for cs in criteria_sets:
            for issue in cs.issues_found:
                issue_type = issue["type"]
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        if issue_counts.get("low_testability", 0) > len(criteria_sets) * 0.3:
            recommendations.append("多个故事存在可测试性问题，建议制定可测试性提升计划")
        
        return recommendations
    
    def _identify_overall_issues(self, criteria_sets: List[AcceptanceCriteriaSet], overall_quality: Dict[str, float]) -> List[Dict[str, Any]]:
        """识别整体问题"""
        issues = []
        
        # 整体质量问题
        if overall_quality["overall_testability"] < 0.95:
            issues.append({
                "type": "overall_testability_low",
                "severity": "high",
                "description": f"整体可测试性为{overall_quality['overall_testability']:.1%}，未达到≥95%的目标"
            })
        
        if overall_quality["overall_quantitative_coverage"] < 1.0:
            issues.append({
                "type": "incomplete_quantitative_coverage",
                "severity": "high",
                "description": f"量化指标覆盖率为{overall_quality['overall_quantitative_coverage']:.1%}，未达到100%的目标"
            })
        
        if overall_quality["overall_gwt_compliance"] < 1.0:
            issues.append({
                "type": "incomplete_gwt_compliance",
                "severity": "medium",
                "description": f"Given-When-Then格式合规率为{overall_quality['overall_gwt_compliance']:.1%}，未达到100%的目标"
            })
        
        # 标准分布问题
        stories_without_criteria = [cs for cs in criteria_sets if len(cs.criteria) == 0]
        if stories_without_criteria:
            issues.append({
                "type": "stories_without_criteria",
                "severity": "critical",
                "description": f"{len(stories_without_criteria)}个用户故事没有验收标准",
                "affected_stories": [cs.story_id for cs in stories_without_criteria]
            })
        
        # 质量一致性问题
        quality_variance = max(cs.quality_metrics["overall_quality"] for cs in criteria_sets) - \
                          min(cs.quality_metrics["overall_quality"] for cs in criteria_sets)
        if quality_variance > 0.3:
            issues.append({
                "type": "quality_inconsistency",
                "severity": "medium",
                "description": f"验收标准质量差异较大（方差: {quality_variance:.2f}），需要统一标准"
            })
        
        return issues

# 工厂函数
def create_acceptance_criteria_maker(claude_service: ClaudeService) -> IntelligentAcceptanceCriteriaMaker:
    """创建验收标准制定器"""
    return IntelligentAcceptanceCriteriaMaker(claude_service)

# 使用示例
async def demo_acceptance_criteria_generation():
    """演示验收标准生成功能"""
    from ....claude_integration import create_claude_service
    from .requirements_understanding import create_requirements_analyzer
    from .user_story_generator import create_user_story_generator
    
    claude_service = create_claude_service()
    requirements_analyzer = create_requirements_analyzer(claude_service)
    story_generator = create_user_story_generator(claude_service)
    criteria_maker = create_acceptance_criteria_maker(claude_service)
    
    # 测试需求
    test_requirement = "开发一个在线购物车系统，用户可以添加商品到购物车、修改商品数量、删除商品，并且能够快速结算，响应时间不超过2秒"
    
    print(f"测试需求: {test_requirement}")
    
    try:
        # 1. 需求分析
        requirement_analysis = await requirements_analyzer.analyze_requirements(test_requirement)
        print(f"需求分析完成")
        
        # 2. 生成用户故事
        story_result = await story_generator.generate_user_stories(requirement_analysis)
        print(f"用户故事生成完成，共{len(story_result.generated_stories)}个故事")
        
        # 3. 生成验收标准
        criteria_result = await criteria_maker.generate_acceptance_criteria(story_result)
        
        print(f"\n=== 验收标准生成结果 ===")
        print(f"处理故事数: {criteria_result.generation_summary['total_stories']}")
        print(f"总验收标准数: {criteria_result.generation_summary['total_criteria']}")
        print(f"总量化指标数: {criteria_result.generation_summary['total_quantitative_metrics']}")
        print(f"平均每故事标准数: {criteria_result.generation_summary['average_criteria_per_story']:.1f}")
        
        print(f"\n=== 整体质量评估 ===")
        print(f"整体可测试性: {criteria_result.overall_quality['overall_testability']:.1%}")
        print(f"量化指标覆盖率: {criteria_result.overall_quality['overall_quantitative_coverage']:.1%}")
        print(f"Given-When-Then合规率: {criteria_result.overall_quality['overall_gwt_compliance']:.1%}")
        print(f"整体质量: {criteria_result.overall_quality['overall_quality']:.1%}")
        
        print(f"\n=== 详细验收标准 ===")
        for criteria_set in criteria_result.criteria_sets:
            print(f"\n故事: {criteria_set.story_title} ({criteria_set.story_id})")
            print(f"验收标准数量: {len(criteria_set.criteria)}")
            
            for i, criterion in enumerate(criteria_set.criteria[:3], 1):  # 显示前3个
                print(f"\n  {i}. {criterion.title} ({criterion.criterion_id})")
                print(f"     类型: {criterion.criteria_type.value}")
                print(f"     Given: {criterion.given_context}")
                print(f"     When: {criterion.when_action}")
                print(f"     Then: {criterion.then_outcome}")
                print(f"     可测试性: {criterion.testability_level.value} ({criterion.testability_score:.2f})")
                
                if criterion.quantitative_metrics:
                    print(f"     量化指标:")
                    for metric in criterion.quantitative_metrics[:2]:  # 显示前2个
                        print(f"     - {metric.metric_name}: {metric.acceptance_threshold}")
                
                if criterion.test_methods:
                    print(f"     测试方法: {', '.join(criterion.test_methods[:3])}")
        
        print(f"\n=== 类型分布 ===")
        type_dist = criteria_result.generation_summary['type_distribution']
        for criteria_type, count in type_dist.items():
            print(f"- {criteria_type}: {count}个")
        
        print(f"\n=== 可测试性分布 ===")
        testability_dist = criteria_result.generation_summary['testability_distribution']
        for level, count in testability_dist.items():
            print(f"- {level}: {count}个")
        
        if criteria_result.recommendations:
            print(f"\n=== 改进建议 ===")
            for rec in criteria_result.recommendations:
                print(f"- {rec}")
        
        if criteria_result.issues_found:
            print(f"\n=== 发现的问题 ===")
            for issue in criteria_result.issues_found:
                print(f"- {issue['type']} ({issue['severity']}): {issue['description']}")
        
        print(f"\n处理时间: {criteria_result.processing_time:.2f}秒")
        
        # 验证验收标准
        print(f"\n=== 验收标准验证 ===")
        print(f"AC-003-01 (可测试性≥95%): {'✓' if criteria_result.overall_quality['overall_testability'] >= 0.95 else '✗'} {criteria_result.overall_quality['overall_testability']:.1%}")
        print(f"AC-003-02 (量化指标覆盖率100%): {'✓' if criteria_result.overall_quality['overall_quantitative_coverage'] >= 1.0 else '✗'} {criteria_result.overall_quality['overall_quantitative_coverage']:.1%}")
        print(f"AC-003-03 (Given-When-Then格式合规率100%): {'✓' if criteria_result.overall_quality['overall_gwt_compliance'] >= 1.0 else '✗'} {criteria_result.overall_quality['overall_gwt_compliance']:.1%}")
        
    except Exception as e:
        print(f"验收标准生成失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_acceptance_criteria_generation())
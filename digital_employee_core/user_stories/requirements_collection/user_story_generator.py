"""
US-002: 用户故事自动生成
Automated User Story Generation

验收标准:
- AC-002-01: 用户故事INVEST符合率≥95%
- AC-002-02: 业务价值映射准确率≥90%
- AC-002-03: 故事边界清晰度评分≥4.5/5.0
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
from .requirements_understanding import RequirementAnalysisResult, EARSRequirement

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """用户角色"""
    END_USER = "end_user"
    ADMIN = "admin"
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    MANAGER = "manager"
    DEVELOPER = "developer"
    SYSTEM = "system"
    STAKEHOLDER = "stakeholder"

class BusinessValue(Enum):
    """业务价值类型"""
    EFFICIENCY = "efficiency"
    COST_REDUCTION = "cost_reduction"
    REVENUE_INCREASE = "revenue_increase"
    USER_SATISFACTION = "user_satisfaction"
    COMPLIANCE = "compliance"
    COMPETITIVE_ADVANTAGE = "competitive_advantage"
    RISK_MITIGATION = "risk_mitigation"
    INNOVATION = "innovation"

class StoryPriority(Enum):
    """故事优先级"""
    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"
    COULD_HAVE = "could_have"
    WONT_HAVE = "wont_have"

@dataclass
class INVESTCriteria:
    """INVEST原则评估"""
    independent: float  # 独立性 0-1
    negotiable: float   # 可协商性 0-1
    valuable: float     # 价值性 0-1
    estimable: float    # 可估算性 0-1
    small: float        # 适当大小 0-1
    testable: float     # 可测试性 0-1
    overall_score: float = 0.0
    
    def __post_init__(self):
        scores = [self.independent, self.negotiable, self.valuable, 
                 self.estimable, self.small, self.testable]
        self.overall_score = sum(scores) / len(scores)

@dataclass
class BusinessValueMapping:
    """业务价值映射"""
    value_type: BusinessValue
    description: str
    impact_level: str  # high, medium, low
    measurable_outcomes: List[str]
    stakeholders: List[str]
    confidence_score: float

@dataclass
class StoryBoundary:
    """故事边界定义"""
    included_features: List[str]
    excluded_features: List[str]
    assumptions: List[str]
    dependencies: List[str]
    constraints: List[str]
    clarity_score: float

@dataclass
class UserStory:
    """用户故事"""
    story_id: str
    title: str
    user_role: UserRole
    user_goal: str
    business_value: str
    full_story: str
    
    # INVEST评估
    invest_criteria: INVESTCriteria
    
    # 业务价值映射
    business_value_mapping: BusinessValueMapping
    
    # 故事边界
    story_boundary: StoryBoundary
    
    # 优先级和估算
    priority: StoryPriority
    story_points: Optional[int] = None
    effort_estimate: Optional[str] = None
    
    # 验收标准
    acceptance_criteria: List[str] = field(default_factory=list)
    
    # 元数据
    source_requirement: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserStoryGenerationResult:
    """用户故事生成结果"""
    source_analysis: RequirementAnalysisResult
    generated_stories: List[UserStory]
    generation_quality: Dict[str, float]
    epic_structure: Dict[str, Any]
    recommendations: List[str]
    issues_found: List[Dict[str, Any]]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

class AutomatedUserStoryGenerator:
    """自动化用户故事生成器"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.role_templates = self._load_role_templates()
        self.value_templates = self._load_value_templates()
        self.story_patterns = self._load_story_patterns()
        
    def _load_role_templates(self) -> Dict[str, List[str]]:
        """加载角色模板"""
        return {
            "business_context": [
                "客户", "用户", "管理员", "员工", "经理", "主管", "操作员", "审核员"
            ],
            "technical_context": [
                "开发者", "测试人员", "运维人员", "架构师", "产品经理"
            ],
            "system_context": [
                "系统", "应用程序", "服务", "组件", "模块"
            ]
        }
    
    def _load_value_templates(self) -> Dict[BusinessValue, str]:
        """加载价值模板"""
        return {
            BusinessValue.EFFICIENCY: "提高工作效率和生产力",
            BusinessValue.COST_REDUCTION: "降低运营成本和资源消耗",
            BusinessValue.REVENUE_INCREASE: "增加收入和商业机会",
            BusinessValue.USER_SATISFACTION: "提升用户体验和满意度",
            BusinessValue.COMPLIANCE: "确保合规性和标准遵循",
            BusinessValue.COMPETITIVE_ADVANTAGE: "获得竞争优势",
            BusinessValue.RISK_MITIGATION: "降低业务风险",
            BusinessValue.INNOVATION: "推动创新和技术进步"
        }
    
    def _load_story_patterns(self) -> Dict[str, str]:
        """加载故事模式"""
        return {
            "basic": "作为{role}，我希望{goal}，以便{value}",
            "detailed": "作为{role}，我希望能够{goal}，这样我就可以{value}",
            "contextual": "在{context}情况下，作为{role}，我需要{goal}，从而{value}"
        }
    
    async def generate_user_stories(self, requirement_analysis: RequirementAnalysisResult) -> UserStoryGenerationResult:
        """
        基于需求分析结果生成用户故事
        
        Args:
            requirement_analysis: 需求分析结果
            
        Returns:
            UserStoryGenerationResult: 用户故事生成结果
        """
        start_time = datetime.now()
        
        try:
            logger.info("开始生成用户故事...")
            
            # 1. 识别用户角色和目标
            user_roles_goals = await self._identify_roles_and_goals(requirement_analysis)
            
            # 2. 生成用户故事
            user_stories = await self._generate_stories(requirement_analysis, user_roles_goals)
            
            # 3. INVEST评估
            await self._evaluate_invest_criteria(user_stories)
            
            # 4. 业务价值映射
            await self._map_business_values(user_stories, requirement_analysis)
            
            # 5. 定义故事边界
            await self._define_story_boundaries(user_stories)
            
            # 6. 评估生成质量
            generation_quality = self._assess_generation_quality(user_stories)
            
            # 7. 构建Epic结构
            epic_structure = self._build_epic_structure(user_stories)
            
            # 8. 生成建议
            recommendations = self._generate_recommendations(user_stories, generation_quality)
            
            # 9. 识别问题
            issues = self._identify_issues(user_stories, generation_quality)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = UserStoryGenerationResult(
                source_analysis=requirement_analysis,
                generated_stories=user_stories,
                generation_quality=generation_quality,
                epic_structure=epic_structure,
                recommendations=recommendations,
                issues_found=issues,
                processing_time=processing_time
            )
            
            logger.info(f"用户故事生成完成，生成{len(user_stories)}个故事，INVEST符合率: {generation_quality.get('invest_compliance', 0):.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"用户故事生成失败: {str(e)}")
            raise
    
    async def _identify_roles_and_goals(self, requirement_analysis: RequirementAnalysisResult) -> Dict[str, Any]:
        """识别用户角色和目标"""
        
        role_identification_prompt = f"""
作为产品经理专家，请分析以下需求并识别用户角色和目标。

需求分析结果：
- 原始需求: {requirement_analysis.understanding.original_text}
- 核心概念: {requirement_analysis.understanding.core_concepts}
- 实体: {requirement_analysis.understanding.entities}
- 动作: {requirement_analysis.understanding.actions}

请识别：

1. **主要用户角色**
   - 识别所有相关的用户类型
   - 为每个角色定义明确的特征和职责

2. **用户目标**
   - 每个角色想要实现什么目标
   - 目标的优先级和重要性

3. **用户场景**
   - 用户在什么情况下使用系统
   - 典型的使用流程

4. **价值期望**
   - 用户期望获得什么价值
   - 解决什么问题

返回JSON格式的分析结果。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": role_identification_prompt}],
            temperature=0.2,
            max_tokens=1500
        )
        
        if response.success:
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return self._basic_role_identification(requirement_analysis)
        else:
            return self._basic_role_identification(requirement_analysis)
    
    def _basic_role_identification(self, requirement_analysis: RequirementAnalysisResult) -> Dict[str, Any]:
        """基础角色识别（降级处理）"""
        
        # 基于实体识别用户角色
        entities = requirement_analysis.understanding.entities
        roles = []
        
        if any(entity in ["用户", "客户", "顾客"] for entity in entities):
            roles.append("用户")
        if any(entity in ["管理员", "管理", "admin"] for entity in entities):
            roles.append("管理员")
        if any(entity in ["系统", "应用", "程序"] for entity in entities):
            roles.append("系统用户")
        
        if not roles:
            roles = ["用户"]  # 默认角色
        
        return {
            "主要用户角色": [{"角色": role, "描述": f"{role}使用系统"} for role in roles],
            "用户目标": requirement_analysis.understanding.actions,
            "用户场景": ["基本使用场景"],
            "价值期望": ["满足业务需求"]
        }
    
    async def _generate_stories(self, requirement_analysis: RequirementAnalysisResult, roles_goals: Dict[str, Any]) -> List[UserStory]:
        """生成用户故事"""
        
        story_generation_prompt = f"""
作为资深产品经理，请基于以下信息生成高质量的用户故事。

需求信息：
- 原始需求: {requirement_analysis.understanding.original_text}
- 需求类型: {requirement_analysis.understanding.requirement_type.value}

用户角色信息：
{json.dumps(roles_goals, ensure_ascii=False, indent=2)}

EARS需求：
{[ears.ears_statement for ears in requirement_analysis.ears_requirements]}

请生成2-5个用户故事，每个故事包含：

1. **故事结构** (遵循标准格式)
   - "作为[角色]，我希望[功能]，以便[价值]"

2. **故事详情**
   - 明确的标题
   - 具体的用户角色
   - 清晰的功能描述
   - 明确的业务价值

3. **验收标准**
   - 3-5个可测试的验收标准
   - 使用Given-When-Then格式

4. **优先级评估**
   - 基于MoSCoW模型的优先级

返回JSON格式的故事列表。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": story_generation_prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        
        user_stories = []
        
        if response.success:
            try:
                stories_data = json.loads(response.content)
                
                for i, story_data in enumerate(stories_data.get("用户故事", [])):
                    # 解析用户角色
                    role_text = story_data.get("用户角色", "用户")
                    user_role = self._parse_user_role(role_text)
                    
                    # 解析优先级
                    priority_text = story_data.get("优先级", "should_have")
                    priority = self._parse_priority(priority_text)
                    
                    # 创建用户故事
                    story = UserStory(
                        story_id=f"US-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                        title=story_data.get("标题", f"用户故事 {i+1}"),
                        user_role=user_role,
                        user_goal=story_data.get("功能描述", ""),
                        business_value=story_data.get("业务价值", ""),
                        full_story=story_data.get("完整故事", ""),
                        invest_criteria=INVESTCriteria(0.8, 0.8, 0.8, 0.8, 0.8, 0.8),  # 初始值
                        business_value_mapping=BusinessValueMapping(
                            value_type=BusinessValue.USER_SATISFACTION,
                            description="",
                            impact_level="medium",
                            measurable_outcomes=[],
                            stakeholders=[],
                            confidence_score=0.8
                        ),
                        story_boundary=StoryBoundary(
                            included_features=[],
                            excluded_features=[],
                            assumptions=[],
                            dependencies=[],
                            constraints=[],
                            clarity_score=4.0
                        ),
                        priority=priority,
                        acceptance_criteria=story_data.get("验收标准", []),
                        source_requirement=requirement_analysis.understanding.original_text
                    )
                    user_stories.append(story)
                    
            except json.JSONDecodeError:
                user_stories = self._generate_basic_stories(requirement_analysis, roles_goals)
        else:
            user_stories = self._generate_basic_stories(requirement_analysis, roles_goals)
        
        return user_stories
    
    def _generate_basic_stories(self, requirement_analysis: RequirementAnalysisResult, roles_goals: Dict[str, Any]) -> List[UserStory]:
        """生成基础用户故事（降级处理）"""
        
        stories = []
        roles = roles_goals.get("主要用户角色", [{"角色": "用户"}])
        
        for i, role_info in enumerate(roles[:3]):  # 最多3个故事
            role_name = role_info.get("角色", "用户")
            user_role = self._parse_user_role(role_name)
            
            story = UserStory(
                story_id=f"US-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}",
                title=f"{role_name}使用系统功能",
                user_role=user_role,
                user_goal=requirement_analysis.understanding.original_text,
                business_value="满足业务需求",
                full_story=f"作为{role_name}，我希望{requirement_analysis.understanding.original_text}，以便满足业务需求",
                invest_criteria=INVESTCriteria(0.7, 0.7, 0.7, 0.7, 0.7, 0.7),
                business_value_mapping=BusinessValueMapping(
                    value_type=BusinessValue.USER_SATISFACTION,
                    description="基本业务需求满足",
                    impact_level="medium",
                    measurable_outcomes=[],
                    stakeholders=[role_name],
                    confidence_score=0.6
                ),
                story_boundary=StoryBoundary(
                    included_features=[],
                    excluded_features=[],
                    assumptions=[],
                    dependencies=[],
                    constraints=[],
                    clarity_score=3.5
                ),
                priority=StoryPriority.SHOULD_HAVE,
                acceptance_criteria=["功能正常工作", "用户能够使用"],
                source_requirement=requirement_analysis.understanding.original_text
            )
            stories.append(story)
        
        return stories
    
    def _parse_user_role(self, role_text: str) -> UserRole:
        """解析用户角色"""
        role_text = role_text.lower()
        
        if any(word in role_text for word in ["管理员", "admin", "管理"]):
            return UserRole.ADMIN
        elif any(word in role_text for word in ["客户", "顾客", "customer"]):
            return UserRole.CUSTOMER
        elif any(word in role_text for word in ["员工", "employee", "职员"]):
            return UserRole.EMPLOYEE
        elif any(word in role_text for word in ["经理", "manager", "主管"]):
            return UserRole.MANAGER
        elif any(word in role_text for word in ["开发", "developer", "程序员"]):
            return UserRole.DEVELOPER
        elif any(word in role_text for word in ["系统", "system"]):
            return UserRole.SYSTEM
        else:
            return UserRole.END_USER
    
    def _parse_priority(self, priority_text: str) -> StoryPriority:
        """解析优先级"""
        priority_text = priority_text.lower()
        
        if any(word in priority_text for word in ["must", "必须", "critical", "关键"]):
            return StoryPriority.MUST_HAVE
        elif any(word in priority_text for word in ["should", "应该", "重要"]):
            return StoryPriority.SHOULD_HAVE
        elif any(word in priority_text for word in ["could", "可以", "可选"]):
            return StoryPriority.COULD_HAVE
        else:
            return StoryPriority.SHOULD_HAVE
    
    async def _evaluate_invest_criteria(self, user_stories: List[UserStory]):
        """评估INVEST原则"""
        
        for story in user_stories:
            # 独立性评估
            independent = self._evaluate_independence(story)
            
            # 可协商性评估
            negotiable = self._evaluate_negotiability(story)
            
            # 价值性评估
            valuable = self._evaluate_value(story)
            
            # 可估算性评估
            estimable = self._evaluate_estimability(story)
            
            # 大小适当性评估
            small = self._evaluate_size(story)
            
            # 可测试性评估
            testable = self._evaluate_testability(story)
            
            story.invest_criteria = INVESTCriteria(
                independent=independent,
                negotiable=negotiable,
                valuable=valuable,
                estimable=estimable,
                small=small,
                testable=testable
            )
    
    def _evaluate_independence(self, story: UserStory) -> float:
        """评估独立性"""
        # 简化评估：检查是否包含依赖关键词
        dependency_keywords = ["依赖", "需要", "基于", "前提", "条件"]
        full_text = f"{story.full_story} {' '.join(story.acceptance_criteria)}"
        
        dependency_count = sum(1 for keyword in dependency_keywords if keyword in full_text)
        return max(0.3, 1.0 - dependency_count * 0.2)
    
    def _evaluate_negotiability(self, story: UserStory) -> float:
        """评估可协商性"""
        # 检查是否过于具体或限制性
        restrictive_keywords = ["必须", "只能", "仅限", "禁止", "不允许"]
        full_text = f"{story.full_story} {' '.join(story.acceptance_criteria)}"
        
        restriction_count = sum(1 for keyword in restrictive_keywords if keyword in full_text)
        return max(0.4, 1.0 - restriction_count * 0.15)
    
    def _evaluate_value(self, story: UserStory) -> float:
        """评估价值性"""
        # 检查是否明确表达了价值
        if story.business_value and len(story.business_value) > 10:
            return 0.9
        elif "以便" in story.full_story or "从而" in story.full_story:
            return 0.8
        else:
            return 0.6
    
    def _evaluate_estimability(self, story: UserStory) -> float:
        """评估可估算性"""
        # 检查故事的明确性和具体性
        clarity_indicators = len(story.acceptance_criteria)
        if clarity_indicators >= 3:
            return 0.9
        elif clarity_indicators >= 1:
            return 0.7
        else:
            return 0.5
    
    def _evaluate_size(self, story: UserStory) -> float:
        """评估大小适当性"""
        # 基于故事描述长度和复杂度
        story_length = len(story.full_story)
        criteria_count = len(story.acceptance_criteria)
        
        if story_length < 100 and criteria_count <= 5:
            return 0.9
        elif story_length < 200 and criteria_count <= 8:
            return 0.7
        else:
            return 0.5
    
    def _evaluate_testability(self, story: UserStory) -> float:
        """评估可测试性"""
        # 检查验收标准的质量
        if not story.acceptance_criteria:
            return 0.3
        
        testable_count = 0
        for criteria in story.acceptance_criteria:
            if any(word in criteria for word in ["Given", "When", "Then", "如果", "当", "那么"]):
                testable_count += 1
        
        return min(1.0, testable_count / len(story.acceptance_criteria) + 0.3)
    
    async def _map_business_values(self, user_stories: List[UserStory], requirement_analysis: RequirementAnalysisResult):
        """映射业务价值"""
        
        for story in user_stories:
            # 基于故事内容识别业务价值类型
            value_type = self._identify_business_value_type(story)
            
            # 评估影响程度
            impact_level = self._assess_impact_level(story)
            
            # 生成可测量结果
            measurable_outcomes = self._generate_measurable_outcomes(story, value_type)
            
            # 识别利益相关者
            stakeholders = self._identify_stakeholders(story)
            
            story.business_value_mapping = BusinessValueMapping(
                value_type=value_type,
                description=story.business_value,
                impact_level=impact_level,
                measurable_outcomes=measurable_outcomes,
                stakeholders=stakeholders,
                confidence_score=0.8
            )
    
    def _identify_business_value_type(self, story: UserStory) -> BusinessValue:
        """识别业务价值类型"""
        full_text = f"{story.full_story} {story.business_value}".lower()
        
        if any(word in full_text for word in ["效率", "快速", "节省时间", "自动化"]):
            return BusinessValue.EFFICIENCY
        elif any(word in full_text for word in ["成本", "费用", "节约", "降低"]):
            return BusinessValue.COST_REDUCTION
        elif any(word in full_text for word in ["收入", "盈利", "销售", "营收"]):
            return BusinessValue.REVENUE_INCREASE
        elif any(word in full_text for word in ["用户体验", "满意度", "友好", "便利"]):
            return BusinessValue.USER_SATISFACTION
        elif any(word in full_text for word in ["合规", "规范", "标准", "法规"]):
            return BusinessValue.COMPLIANCE
        elif any(word in full_text for word in ["竞争", "优势", "领先", "差异化"]):
            return BusinessValue.COMPETITIVE_ADVANTAGE
        elif any(word in full_text for word in ["风险", "安全", "稳定", "可靠"]):
            return BusinessValue.RISK_MITIGATION
        elif any(word in full_text for word in ["创新", "新功能", "技术", "升级"]):
            return BusinessValue.INNOVATION
        else:
            return BusinessValue.USER_SATISFACTION
    
    def _assess_impact_level(self, story: UserStory) -> str:
        """评估影响程度"""
        if story.priority == StoryPriority.MUST_HAVE:
            return "high"
        elif story.priority == StoryPriority.SHOULD_HAVE:
            return "medium"
        else:
            return "low"
    
    def _generate_measurable_outcomes(self, story: UserStory, value_type: BusinessValue) -> List[str]:
        """生成可测量结果"""
        outcomes = []
        
        if value_type == BusinessValue.EFFICIENCY:
            outcomes = ["处理时间减少", "操作步骤简化", "自动化程度提升"]
        elif value_type == BusinessValue.USER_SATISFACTION:
            outcomes = ["用户满意度评分", "使用频率提升", "用户反馈改善"]
        elif value_type == BusinessValue.COST_REDUCTION:
            outcomes = ["运营成本降低", "人力资源节约", "维护费用减少"]
        else:
            outcomes = ["关键指标改善", "目标达成率提升"]
        
        return outcomes
    
    def _identify_stakeholders(self, story: UserStory) -> List[str]:
        """识别利益相关者"""
        stakeholders = [story.user_role.value]
        
        # 基于故事内容识别其他利益相关者
        full_text = f"{story.full_story} {story.business_value}".lower()
        
        if any(word in full_text for word in ["管理", "经理", "主管"]):
            stakeholders.append("management")
        if any(word in full_text for word in ["客户", "顾客"]):
            stakeholders.append("customers")
        if any(word in full_text for word in ["员工", "团队"]):
            stakeholders.append("employees")
        if any(word in full_text for word in ["开发", "技术"]):
            stakeholders.append("development_team")
        
        return list(set(stakeholders))
    
    async def _define_story_boundaries(self, user_stories: List[UserStory]):
        """定义故事边界"""
        
        for story in user_stories:
            # 基于验收标准定义包含功能
            included_features = self._extract_included_features(story)
            
            # 识别排除功能
            excluded_features = self._identify_excluded_features(story)
            
            # 识别假设
            assumptions = self._identify_assumptions(story)
            
            # 识别依赖
            dependencies = self._identify_dependencies(story)
            
            # 识别约束
            constraints = self._identify_constraints(story)
            
            # 评估清晰度
            clarity_score = self._assess_boundary_clarity(story)
            
            story.story_boundary = StoryBoundary(
                included_features=included_features,
                excluded_features=excluded_features,
                assumptions=assumptions,
                dependencies=dependencies,
                constraints=constraints,
                clarity_score=clarity_score
            )
    
    def _extract_included_features(self, story: UserStory) -> List[str]:
        """提取包含的功能"""
        features = []
        
        # 从验收标准中提取功能
        for criteria in story.acceptance_criteria:
            # 简单的功能提取
            if "能够" in criteria or "可以" in criteria:
                features.append(criteria)
        
        # 从故事描述中提取
        if "希望" in story.full_story:
            goal_part = story.full_story.split("希望")[1].split("以便")[0] if "以便" in story.full_story else story.full_story.split("希望")[1]
            features.append(goal_part.strip())
        
        return features
    
    def _identify_excluded_features(self, story: UserStory) -> List[str]:
        """识别排除的功能"""
        excluded = []
        
        # 查找明确排除的内容
        for criteria in story.acceptance_criteria:
            if "不包括" in criteria or "不支持" in criteria or "排除" in criteria:
                excluded.append(criteria)
        
        return excluded
    
    def _identify_assumptions(self, story: UserStory) -> List[str]:
        """识别假设"""
        assumptions = []
        
        # 查找假设相关的表述
        assumption_keywords = ["假设", "假定", "前提", "基于"]
        full_text = f"{story.full_story} {' '.join(story.acceptance_criteria)}"
        
        for keyword in assumption_keywords:
            if keyword in full_text:
                assumptions.append(f"基于{keyword}的条件")
        
        return assumptions
    
    def _identify_dependencies(self, story: UserStory) -> List[str]:
        """识别依赖"""
        dependencies = []
        
        # 查找依赖相关的表述
        dependency_keywords = ["依赖", "需要", "要求", "基于"]
        full_text = f"{story.full_story} {' '.join(story.acceptance_criteria)}"
        
        for keyword in dependency_keywords:
            if keyword in full_text:
                dependencies.append(f"依赖于{keyword}的条件")
        
        return dependencies
    
    def _identify_constraints(self, story: UserStory) -> List[str]:
        """识别约束"""
        constraints = []
        
        # 查找约束相关的表述
        constraint_keywords = ["限制", "约束", "不能", "禁止", "仅限"]
        full_text = f"{story.full_story} {' '.join(story.acceptance_criteria)}"
        
        for keyword in constraint_keywords:
            if keyword in full_text:
                constraints.append(f"受{keyword}的限制")
        
        return constraints
    
    def _assess_boundary_clarity(self, story: UserStory) -> float:
        """评估边界清晰度"""
        score = 3.0  # 基础分数
        
        # 有明确的验收标准 +1分
        if len(story.acceptance_criteria) >= 3:
            score += 1.0
        elif len(story.acceptance_criteria) >= 1:
            score += 0.5
        
        # 有明确的包含功能 +0.5分
        if story.story_boundary and story.story_boundary.included_features:
            score += 0.5
        
        # 有明确的排除功能 +0.5分
        if story.story_boundary and story.story_boundary.excluded_features:
            score += 0.5
        
        return min(5.0, score)
    
    def _assess_generation_quality(self, user_stories: List[UserStory]) -> Dict[str, float]:
        """评估生成质量"""
        
        if not user_stories:
            return {
                "invest_compliance": 0.0,
                "business_value_mapping_accuracy": 0.0,
                "boundary_clarity": 0.0,
                "overall_quality": 0.0
            }
        
        # INVEST符合率
        invest_scores = [story.invest_criteria.overall_score for story in user_stories]
        invest_compliance = sum(invest_scores) / len(invest_scores)
        
        # 业务价值映射准确率
        value_mapping_scores = [story.business_value_mapping.confidence_score for story in user_stories]
        business_value_mapping_accuracy = sum(value_mapping_scores) / len(value_mapping_scores)
        
        # 故事边界清晰度
        boundary_scores = [story.story_boundary.clarity_score for story in user_stories]
        boundary_clarity = sum(boundary_scores) / len(boundary_scores) / 5.0  # 标准化到0-1
        
        # 整体质量
        overall_quality = (invest_compliance + business_value_mapping_accuracy + boundary_clarity) / 3
        
        return {
            "invest_compliance": invest_compliance,
            "business_value_mapping_accuracy": business_value_mapping_accuracy,
            "boundary_clarity": boundary_clarity,
            "overall_quality": overall_quality
        }
    
    def _build_epic_structure(self, user_stories: List[UserStory]) -> Dict[str, Any]:
        """构建Epic结构"""
        
        # 按业务价值类型分组
        epics_by_value = {}
        for story in user_stories:
            value_type = story.business_value_mapping.value_type
            if value_type not in epics_by_value:
                epics_by_value[value_type] = []
            epics_by_value[value_type].append(story)
        
        # 构建Epic结构
        epic_structure = {
            "total_stories": len(user_stories),
            "epics": [],
            "priority_distribution": {},
            "value_distribution": {}
        }
        
        for value_type, stories in epics_by_value.items():
            epic = {
                "epic_name": f"{value_type.value}_epic",
                "value_type": value_type.value,
                "stories": [story.story_id for story in stories],
                "story_count": len(stories),
                "estimated_effort": sum(story.story_points or 5 for story in stories),
                "priority": self._calculate_epic_priority(stories)
            }
            epic_structure["epics"].append(epic)
        
        # 统计优先级分布
        priority_counts = {}
        for story in user_stories:
            priority = story.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        epic_structure["priority_distribution"] = priority_counts
        
        # 统计价值分布
        value_counts = {}
        for story in user_stories:
            value_type = story.business_value_mapping.value_type.value
            value_counts[value_type] = value_counts.get(value_type, 0) + 1
        epic_structure["value_distribution"] = value_counts
        
        return epic_structure
    
    def _calculate_epic_priority(self, stories: List[UserStory]) -> str:
        """计算Epic优先级"""
        priority_weights = {
            StoryPriority.MUST_HAVE: 4,
            StoryPriority.SHOULD_HAVE: 3,
            StoryPriority.COULD_HAVE: 2,
            StoryPriority.WONT_HAVE: 1
        }
        
        total_weight = sum(priority_weights[story.priority] for story in stories)
        avg_weight = total_weight / len(stories)
        
        if avg_weight >= 3.5:
            return "high"
        elif avg_weight >= 2.5:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, user_stories: List[UserStory], quality: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于INVEST符合率生成建议
        if quality["invest_compliance"] < 0.95:
            recommendations.append("建议优化用户故事的INVEST符合性，特别关注独立性和可测试性")
        
        # 基于业务价值映射准确率生成建议
        if quality["business_value_mapping_accuracy"] < 0.90:
            recommendations.append("建议明确每个用户故事的业务价值和可测量结果")
        
        # 基于边界清晰度生成建议
        if quality["boundary_clarity"] < 0.90:
            recommendations.append("建议为用户故事添加更明确的边界定义和验收标准")
        
        # 基于故事数量生成建议
        if len(user_stories) < 2:
            recommendations.append("建议分解需求为更多的用户故事以提高可管理性")
        elif len(user_stories) > 5:
            recommendations.append("建议合并相关的用户故事或将其组织为Epic")
        
        # 基于优先级分布生成建议
        must_have_count = sum(1 for story in user_stories if story.priority == StoryPriority.MUST_HAVE)
        if must_have_count == 0:
            recommendations.append("建议至少有一个Must-Have优先级的用户故事")
        elif must_have_count > len(user_stories) * 0.6:
            recommendations.append("Must-Have故事过多，建议重新评估优先级")
        
        return recommendations
    
    def _identify_issues(self, user_stories: List[UserStory], quality: Dict[str, float]) -> List[Dict[str, Any]]:
        """识别问题"""
        issues = []
        
        # INVEST符合率问题
        poor_invest_stories = [story for story in user_stories if story.invest_criteria.overall_score < 0.8]
        if poor_invest_stories:
            issues.append({
                "type": "poor_invest_compliance",
                "severity": "medium",
                "description": f"{len(poor_invest_stories)}个用户故事INVEST符合率较低",
                "affected_stories": [story.story_id for story in poor_invest_stories]
            })
        
        # 边界清晰度问题
        unclear_stories = [story for story in user_stories if story.story_boundary.clarity_score < 4.0]
        if unclear_stories:
            issues.append({
                "type": "unclear_boundaries",
                "severity": "medium",
                "description": f"{len(unclear_stories)}个用户故事边界不够清晰",
                "affected_stories": [story.story_id for story in unclear_stories]
            })
        
        # 验收标准缺失问题
        no_criteria_stories = [story for story in user_stories if not story.acceptance_criteria]
        if no_criteria_stories:
            issues.append({
                "type": "missing_acceptance_criteria",
                "severity": "high",
                "description": f"{len(no_criteria_stories)}个用户故事缺少验收标准",
                "affected_stories": [story.story_id for story in no_criteria_stories]
            })
        
        # 业务价值缺失问题
        no_value_stories = [story for story in user_stories if not story.business_value or len(story.business_value) < 5]
        if no_value_stories:
            issues.append({
                "type": "unclear_business_value",
                "severity": "medium",
                "description": f"{len(no_value_stories)}个用户故事业务价值不明确",
                "affected_stories": [story.story_id for story in no_value_stories]
            })
        
        return issues

# 工厂函数
def create_user_story_generator(claude_service: ClaudeService) -> AutomatedUserStoryGenerator:
    """创建用户故事生成器"""
    return AutomatedUserStoryGenerator(claude_service)

# 使用示例
async def demo_user_story_generation():
    """演示用户故事生成功能"""
    from ....claude_integration import create_claude_service
    from .requirements_understanding import create_requirements_analyzer
    
    claude_service = create_claude_service()
    requirements_analyzer = create_requirements_analyzer(claude_service)
    story_generator = create_user_story_generator(claude_service)
    
    # 测试需求
    test_requirement = "开发一个在线图书管理系统，用户可以浏览图书、借阅图书、归还图书，管理员可以管理图书信息和用户信息"
    
    print(f"测试需求: {test_requirement}")
    
    try:
        # 1. 先进行需求分析
        requirement_analysis = await requirements_analyzer.analyze_requirements(test_requirement)
        print(f"需求分析完成，理解准确率: {requirement_analysis.analysis_quality['understanding_accuracy']:.1%}")
        
        # 2. 生成用户故事
        story_result = await story_generator.generate_user_stories(requirement_analysis)
        
        print(f"\n=== 用户故事生成结果 ===")
        print(f"生成故事数量: {len(story_result.generated_stories)}")
        print(f"INVEST符合率: {story_result.generation_quality['invest_compliance']:.1%}")
        print(f"业务价值映射准确率: {story_result.generation_quality['business_value_mapping_accuracy']:.1%}")
        print(f"边界清晰度: {story_result.generation_quality['boundary_clarity']:.1%}")
        print(f"整体质量: {story_result.generation_quality['overall_quality']:.1%}")
        
        print(f"\n=== 生成的用户故事 ===")
        for i, story in enumerate(story_result.generated_stories, 1):
            print(f"\n{i}. {story.title} ({story.story_id})")
            print(f"   {story.full_story}")
            print(f"   优先级: {story.priority.value}")
            print(f"   INVEST评分: {story.invest_criteria.overall_score:.2f}")
            print(f"   边界清晰度: {story.story_boundary.clarity_score:.1f}/5.0")
            if story.acceptance_criteria:
                print(f"   验收标准:")
                for criteria in story.acceptance_criteria[:3]:  # 显示前3个
                    print(f"   - {criteria}")
        
        print(f"\n=== Epic结构 ===")
        epic_structure = story_result.epic_structure
        print(f"总故事数: {epic_structure['total_stories']}")
        print(f"Epic数量: {len(epic_structure['epics'])}")
        print(f"优先级分布: {epic_structure['priority_distribution']}")
        
        if story_result.recommendations:
            print(f"\n=== 改进建议 ===")
            for rec in story_result.recommendations:
                print(f"- {rec}")
        
        if story_result.issues_found:
            print(f"\n=== 发现的问题 ===")
            for issue in story_result.issues_found:
                print(f"- {issue['type']}: {issue['description']}")
        
        print(f"\n处理时间: {story_result.processing_time:.2f}秒")
        
        # 验证验收标准
        print(f"\n=== 验收标准验证 ===")
        print(f"AC-002-01 (INVEST符合率≥95%): {'✓' if story_result.generation_quality['invest_compliance'] >= 0.95 else '✗'} {story_result.generation_quality['invest_compliance']:.1%}")
        print(f"AC-002-02 (业务价值映射准确率≥90%): {'✓' if story_result.generation_quality['business_value_mapping_accuracy'] >= 0.90 else '✗'} {story_result.generation_quality['business_value_mapping_accuracy']:.1%}")
        print(f"AC-002-03 (边界清晰度≥4.5/5.0): {'✓' if story_result.generation_quality['boundary_clarity'] >= 0.90 else '✗'} {story_result.generation_quality['boundary_clarity']:.1f}")
        
    except Exception as e:
        print(f"用户故事生成失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_user_story_generation())
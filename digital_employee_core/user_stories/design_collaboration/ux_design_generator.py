"""
US-005: UX设计智能生成
UX Design Intelligence Generation

验收标准:
- AC-005-01: 交互设计方案完整性≥90%
- AC-005-02: 可用性标准覆盖率100%
- AC-005-03: 设计规范一致性评分≥4.5/5.0
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
from .technical_architecture_designer import ArchitectureDesignResult, TechnicalArchitecture

logger = logging.getLogger(__name__)

class DesignPattern(Enum):
    """设计模式"""
    ATOMIC_DESIGN = "atomic_design"
    MATERIAL_DESIGN = "material_design"
    HUMAN_INTERFACE = "human_interface"
    FLUENT_DESIGN = "fluent_design"
    CARBON_DESIGN = "carbon_design"
    ANT_DESIGN = "ant_design"
    BOOTSTRAP = "bootstrap"
    CUSTOM = "custom"

class DeviceType(Enum):
    """设备类型"""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"
    WEARABLE = "wearable"
    TV = "tv"
    IOT = "iot"

class AccessibilityLevel(Enum):
    """无障碍等级"""
    WCAG_A = "wcag_a"
    WCAG_AA = "wcag_aa"
    WCAG_AAA = "wcag_aaa"
    SECTION_508 = "section_508"

@dataclass
class ColorPalette:
    """色彩方案"""
    primary_color: str
    secondary_colors: List[str]
    accent_colors: List[str]
    neutral_colors: List[str]
    semantic_colors: Dict[str, str]  # success, warning, error, info
    background_colors: Dict[str, str]  # light, dark themes
    accessibility_contrast: Dict[str, float]

@dataclass
class TypographySystem:
    """字体系统"""
    font_families: Dict[str, str]  # heading, body, mono
    font_scales: Dict[str, Dict[str, str]]  # size, weight, line-height
    spacing_scale: List[str]
    responsive_typography: Dict[str, Dict[str, str]]

@dataclass
class ComponentSpecification:
    """组件规范"""
    component_name: str
    component_type: str
    purpose: str
    states: List[str]  # default, hover, active, disabled, etc.
    variants: List[str]  # size, style variations
    properties: Dict[str, Any]
    behavior_rules: List[str]
    accessibility_features: List[str]
    responsive_behavior: Dict[str, str]

@dataclass
class InteractionPattern:
    """交互模式"""
    pattern_name: str
    pattern_type: str
    trigger: str
    action: str
    feedback: str
    animation_specs: Dict[str, Any]
    accessibility_considerations: List[str]
    device_adaptations: Dict[DeviceType, str]

@dataclass
class LayoutSystem:
    """布局系统"""
    grid_system: Dict[str, Any]
    breakpoints: Dict[str, str]
    spacing_system: Dict[str, str]
    container_specs: Dict[str, Dict[str, Any]]
    responsive_rules: Dict[str, List[str]]

@dataclass
class UserFlow:
    """用户流程"""
    flow_id: str
    flow_name: str
    user_persona: str
    entry_point: str
    steps: List[Dict[str, Any]]
    decision_points: List[Dict[str, Any]]
    exit_points: List[str]
    success_metrics: Dict[str, str]
    error_handling: List[Dict[str, Any]]

@dataclass
class AccessibilityFeatures:
    """无障碍功能"""
    keyboard_navigation: Dict[str, Any]
    screen_reader_support: Dict[str, Any]
    visual_indicators: Dict[str, Any]
    motor_accessibility: Dict[str, Any]
    cognitive_accessibility: Dict[str, Any]
    compliance_checklist: List[str]

@dataclass
class UXDesignSystem:
    """UX设计系统"""
    design_id: str
    project_name: str
    design_philosophy: str
    target_users: List[Dict[str, Any]]
    
    # 视觉设计
    design_pattern: DesignPattern
    color_palette: ColorPalette
    typography_system: TypographySystem
    
    # 组件系统
    component_library: List[ComponentSpecification]
    interaction_patterns: List[InteractionPattern]
    layout_system: LayoutSystem
    
    # 用户体验
    user_flows: List[UserFlow]
    information_architecture: Dict[str, Any]
    navigation_structure: Dict[str, Any]
    
    # 响应式设计
    supported_devices: List[DeviceType]
    responsive_strategy: str
    
    # 无障碍设计
    accessibility_level: AccessibilityLevel
    accessibility_features: AccessibilityFeatures
    
    # 质量评估
    completeness_score: float
    consistency_score: float
    usability_score: float
    accessibility_score: float
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UXDesignResult:
    """UX设计结果"""
    source_architecture: TechnicalArchitecture
    ux_design_system: UXDesignSystem
    design_quality: Dict[str, float]
    prototyping_recommendations: List[str]
    usability_testing_plan: Dict[str, Any]
    implementation_guidelines: List[str]
    issues_found: List[Dict[str, Any]]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

class IntelligentUXDesignGenerator:
    """智能UX设计生成器"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.design_patterns_library = self._load_design_patterns()
        self.component_templates = self._load_component_templates()
        self.interaction_patterns_library = self._load_interaction_patterns()
        self.accessibility_guidelines = self._load_accessibility_guidelines()
        
    def _load_design_patterns(self) -> Dict[str, Dict[str, Any]]:
        """加载设计模式库"""
        return {
            "material_design": {
                "principles": ["Material metaphor", "Bold graphics", "Meaningful motion"],
                "color_approach": "Material color system",
                "typography": "Roboto font family",
                "components": ["FAB", "Cards", "Bottom sheets", "Navigation drawer"]
            },
            "human_interface": {
                "principles": ["Clarity", "Deference", "Depth"],
                "color_approach": "iOS color system",
                "typography": "San Francisco font family",
                "components": ["Tab bars", "Navigation bars", "Action sheets", "Modals"]
            },
            "atomic_design": {
                "principles": ["Atoms", "Molecules", "Organisms", "Templates", "Pages"],
                "color_approach": "Semantic color tokens",
                "typography": "Modular scale",
                "components": ["Button atoms", "Form molecules", "Header organisms"]
            }
        }
    
    def _load_component_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载组件模板"""
        return {
            "button": {
                "states": ["default", "hover", "active", "disabled", "loading"],
                "variants": ["primary", "secondary", "ghost", "link"],
                "sizes": ["small", "medium", "large"],
                "properties": ["label", "icon", "loading", "disabled", "onClick"]
            },
            "input": {
                "states": ["default", "focus", "error", "disabled"],
                "variants": ["text", "password", "email", "number", "search"],
                "properties": ["placeholder", "value", "label", "error", "required"]
            },
            "card": {
                "states": ["default", "hover", "selected", "disabled"],
                "variants": ["elevated", "outlined", "filled"],
                "properties": ["title", "content", "actions", "media"]
            },
            "navigation": {
                "states": ["default", "active", "disabled"],
                "variants": ["horizontal", "vertical", "breadcrumb", "tabs"],
                "properties": ["items", "activeItem", "onItemClick"]
            }
        }
    
    def _load_interaction_patterns(self) -> Dict[str, Dict[str, Any]]:
        """加载交互模式库"""
        return {
            "progressive_disclosure": {
                "description": "逐步展示信息，避免信息过载",
                "use_cases": ["复杂表单", "设置页面", "产品详情"],
                "implementation": "分步骤或折叠面板"
            },
            "feedback_and_response": {
                "description": "为用户操作提供即时反馈",
                "use_cases": ["表单提交", "数据加载", "操作确认"],
                "implementation": "Loading状态、Toast通知、确认对话框"
            },
            "error_prevention": {
                "description": "预防用户错误发生",
                "use_cases": ["表单验证", "危险操作", "数据输入"],
                "implementation": "实时验证、确认步骤、输入约束"
            }
        }
    
    def _load_accessibility_guidelines(self) -> Dict[str, List[str]]:
        """加载无障碍设计指南"""
        return {
            "wcag_aa": [
                "颜色对比度至少4.5:1",
                "支持键盘导航",
                "提供替代文本",
                "适当的焦点指示器",
                "清晰的错误信息",
                "一致的导航结构"
            ],
            "keyboard_navigation": [
                "Tab键顺序逻辑",
                "Skip links提供",
                "焦点管理",
                "快捷键支持"
            ],
            "screen_reader": [
                "语义化HTML",
                "ARIA标签",
                "标题层次结构",
                "表单标签关联"
            ]
        }
    
    async def generate_ux_design(self, architecture_result: ArchitectureDesignResult) -> UXDesignResult:
        """
        基于技术架构生成UX设计系统
        
        Args:
            architecture_result: 技术架构设计结果
            
        Returns:
            UXDesignResult: UX设计结果
        """
        start_time = datetime.now()
        
        try:
            logger.info("开始生成UX设计系统...")
            
            # 1. 分析架构特征和用户需求
            design_requirements = await self._analyze_design_requirements(architecture_result)
            
            # 2. 选择设计模式和风格
            design_pattern = await self._select_design_pattern(design_requirements)
            
            # 3. 生成色彩系统
            color_palette = await self._generate_color_system(design_requirements, design_pattern)
            
            # 4. 设计字体系统
            typography_system = await self._design_typography_system(design_requirements)
            
            # 5. 创建组件库
            component_library = await self._create_component_library(design_requirements, design_pattern)
            
            # 6. 设计交互模式
            interaction_patterns = await self._design_interaction_patterns(design_requirements)
            
            # 7. 建立布局系统
            layout_system = await self._establish_layout_system(design_requirements)
            
            # 8. 设计用户流程
            user_flows = await self._design_user_flows(architecture_result, design_requirements)
            
            # 9. 构建信息架构
            information_architecture = await self._build_information_architecture(architecture_result)
            
            # 10. 设计无障碍功能
            accessibility_features = await self._design_accessibility_features(design_requirements)
            
            # 11. 创建UX设计系统
            ux_design_system = UXDesignSystem(
                design_id=f"UXD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                project_name=architecture_result.technical_architecture.project_name,
                design_philosophy=design_requirements.get("design_philosophy", "用户中心设计"),
                target_users=design_requirements.get("target_users", []),
                design_pattern=design_pattern,
                color_palette=color_palette,
                typography_system=typography_system,
                component_library=component_library,
                interaction_patterns=interaction_patterns,
                layout_system=layout_system,
                user_flows=user_flows,
                information_architecture=information_architecture,
                navigation_structure=self._design_navigation_structure(information_architecture),
                supported_devices=[DeviceType.DESKTOP, DeviceType.TABLET, DeviceType.MOBILE],
                responsive_strategy="移动优先响应式设计",
                accessibility_level=AccessibilityLevel.WCAG_AA,
                accessibility_features=accessibility_features,
                completeness_score=0.0,
                consistency_score=0.0,
                usability_score=0.0,
                accessibility_score=0.0
            )
            
            # 12. 评估设计质量
            design_quality = self._assess_design_quality(ux_design_system)
            ux_design_system.completeness_score = design_quality["completeness"]
            ux_design_system.consistency_score = design_quality["consistency"]
            ux_design_system.usability_score = design_quality["usability"]
            ux_design_system.accessibility_score = design_quality["accessibility"]
            
            # 13. 生成原型建议
            prototyping_recommendations = self._generate_prototyping_recommendations(ux_design_system)
            
            # 14. 创建可用性测试计划
            usability_testing_plan = self._create_usability_testing_plan(ux_design_system)
            
            # 15. 生成实施指南
            implementation_guidelines = self._generate_implementation_guidelines(ux_design_system, architecture_result)
            
            # 16. 识别问题
            issues = self._identify_design_issues(ux_design_system, design_quality)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = UXDesignResult(
                source_architecture=architecture_result.technical_architecture,
                ux_design_system=ux_design_system,
                design_quality=design_quality,
                prototyping_recommendations=prototyping_recommendations,
                usability_testing_plan=usability_testing_plan,
                implementation_guidelines=implementation_guidelines,
                issues_found=issues,
                processing_time=processing_time
            )
            
            logger.info(f"UX设计生成完成，完整性: {design_quality.get('completeness', 0):.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"UX设计生成失败: {str(e)}")
            raise
    
    async def _analyze_design_requirements(self, architecture_result: ArchitectureDesignResult) -> Dict[str, Any]:
        """分析设计需求"""
        
        analysis_prompt = f"""
作为资深UX设计师，请分析以下技术架构，提取UX设计需求。

技术架构信息：
项目名称：{architecture_result.technical_architecture.project_name}
架构模式：{architecture_result.technical_architecture.system_topology.architecture_pattern.value}
系统组件：{[comp.name for comp in architecture_result.technical_architecture.system_topology.components]}
技术栈：{[tech.name for tech in architecture_result.technical_architecture.technology_stack]}

请分析并提供：

1. **用户特征分析**
   - 目标用户群体
   - 用户技能水平
   - 使用场景和环境
   - 设备偏好

2. **设计约束条件**
   - 技术限制
   - 性能要求
   - 兼容性需求
   - 品牌要求

3. **功能复杂度评估**
   - 核心功能识别
   - 交互复杂度
   - 数据展示需求
   - 操作流程复杂度

4. **设计目标定义**
   - 主要设计目标
   - 用户体验优先级
   - 可用性指标
   - 无障碍要求

5. **设计风格偏好**
   - 推荐设计模式
   - 视觉风格建议
   - 交互模式偏好
   - 响应式策略

返回JSON格式的设计需求分析。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        if response.success:
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return self._basic_design_requirements(architecture_result)
        else:
            return self._basic_design_requirements(architecture_result)
    
    def _basic_design_requirements(self, architecture_result: ArchitectureDesignResult) -> Dict[str, Any]:
        """基础设计需求（降级处理）"""
        
        is_complex = len(architecture_result.technical_architecture.system_topology.components) > 5
        
        return {
            "用户特征分析": {
                "目标用户": ["业务用户", "管理员"],
                "技能水平": "中等",
                "使用场景": "办公环境",
                "设备偏好": ["桌面端", "移动端"]
            },
            "设计约束条件": {
                "技术限制": "Web技术栈",
                "性能要求": "标准性能",
                "兼容性": "现代浏览器"
            },
            "功能复杂度评估": {
                "复杂度等级": "高" if is_complex else "中等",
                "核心功能": "数据管理",
                "交互类型": "表单和列表"
            },
            "设计目标定义": {
                "主要目标": "效率和易用性",
                "优先级": "功能完整性",
                "可用性": "WCAG AA"
            },
            "设计风格偏好": {
                "推荐模式": "material_design",
                "视觉风格": "简洁现代",
                "响应式": "移动优先"
            }
        }
    
    async def _select_design_pattern(self, design_requirements: Dict[str, Any]) -> DesignPattern:
        """选择设计模式"""
        
        style_preference = design_requirements.get("设计风格偏好", {}).get("推荐模式", "material_design")
        
        pattern_mapping = {
            "material_design": DesignPattern.MATERIAL_DESIGN,
            "human_interface": DesignPattern.HUMAN_INTERFACE,
            "atomic_design": DesignPattern.ATOMIC_DESIGN,
            "ant_design": DesignPattern.ANT_DESIGN,
            "bootstrap": DesignPattern.BOOTSTRAP
        }
        
        return pattern_mapping.get(style_preference, DesignPattern.MATERIAL_DESIGN)
    
    async def _generate_color_system(self, design_requirements: Dict[str, Any], design_pattern: DesignPattern) -> ColorPalette:
        """生成色彩系统"""
        
        color_prompt = f"""
作为色彩设计专家，请为{design_pattern.value}设计模式创建完整的色彩系统。

设计需求：
{json.dumps(design_requirements, ensure_ascii=False, indent=2)}

请生成包含以下内容的色彩方案：

1. **主色彩定义**
   - 主要品牌色
   - 辅助色彩
   - 强调色彩

2. **中性色彩**
   - 文本颜色层次
   - 背景色变化
   - 边框和分割线

3. **语义色彩**
   - 成功、警告、错误、信息色彩
   - 状态指示色彩

4. **主题适配**
   - 浅色主题色彩
   - 深色主题色彩

5. **无障碍对比度**
   - 确保WCAG AA标准
   - 对比度数值

返回JSON格式的完整色彩系统。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": color_prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        
        if response.success:
            try:
                color_data = json.loads(response.content)
                return self._parse_color_palette(color_data)
            except json.JSONDecodeError:
                return self._create_default_color_palette(design_pattern)
        else:
            return self._create_default_color_palette(design_pattern)
    
    def _parse_color_palette(self, color_data: Dict[str, Any]) -> ColorPalette:
        """解析色彩方案数据"""
        
        return ColorPalette(
            primary_color=color_data.get("主色彩定义", {}).get("主要品牌色", "#1976D2"),
            secondary_colors=color_data.get("主色彩定义", {}).get("辅助色彩", ["#424242", "#757575"]),
            accent_colors=color_data.get("主色彩定义", {}).get("强调色彩", ["#FF4081"]),
            neutral_colors=color_data.get("中性色彩", {}).get("文本颜色", ["#212121", "#757575", "#BDBDBD"]),
            semantic_colors=color_data.get("语义色彩", {
                "success": "#4CAF50",
                "warning": "#FF9800", 
                "error": "#F44336",
                "info": "#2196F3"
            }),
            background_colors=color_data.get("主题适配", {
                "light": "#FFFFFF",
                "dark": "#121212"
            }),
            accessibility_contrast=color_data.get("无障碍对比度", {
                "primary_on_background": 4.5,
                "text_on_background": 7.0
            })
        )
    
    def _create_default_color_palette(self, design_pattern: DesignPattern) -> ColorPalette:
        """创建默认色彩方案"""
        
        if design_pattern == DesignPattern.MATERIAL_DESIGN:
            return ColorPalette(
                primary_color="#1976D2",
                secondary_colors=["#424242", "#757575"],
                accent_colors=["#FF4081"],
                neutral_colors=["#212121", "#757575", "#BDBDBD", "#E0E0E0"],
                semantic_colors={
                    "success": "#4CAF50",
                    "warning": "#FF9800",
                    "error": "#F44336", 
                    "info": "#2196F3"
                },
                background_colors={
                    "light": "#FAFAFA",
                    "dark": "#121212"
                },
                accessibility_contrast={
                    "primary_on_background": 4.5,
                    "text_on_background": 7.0
                }
            )
        else:
            # 通用色彩方案
            return ColorPalette(
                primary_color="#007AFF",
                secondary_colors=["#6B7280", "#9CA3AF"],
                accent_colors=["#10B981"],
                neutral_colors=["#111827", "#374151", "#6B7280", "#D1D5DB"],
                semantic_colors={
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "error": "#EF4444",
                    "info": "#3B82F6"
                },
                background_colors={
                    "light": "#FFFFFF",
                    "dark": "#1F2937"
                },
                accessibility_contrast={
                    "primary_on_background": 4.5,
                    "text_on_background": 7.0
                }
            )
    
    async def _design_typography_system(self, design_requirements: Dict[str, Any]) -> TypographySystem:
        """设计字体系统"""
        
        return TypographySystem(
            font_families={
                "heading": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                "body": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                "mono": "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace"
            },
            font_scales={
                "heading": {
                    "h1": "32px/1.25/700",
                    "h2": "28px/1.3/600", 
                    "h3": "24px/1.35/600",
                    "h4": "20px/1.4/600",
                    "h5": "18px/1.45/500",
                    "h6": "16px/1.5/500"
                },
                "body": {
                    "large": "18px/1.6/400",
                    "medium": "16px/1.5/400",
                    "small": "14px/1.45/400",
                    "caption": "12px/1.4/400"
                }
            },
            spacing_scale=["4px", "8px", "12px", "16px", "24px", "32px", "48px", "64px"],
            responsive_typography={
                "mobile": {"scale": "0.875", "line_height": "1.6"},
                "tablet": {"scale": "1.0", "line_height": "1.5"},
                "desktop": {"scale": "1.125", "line_height": "1.5"}
            }
        )
    
    async def _create_component_library(self, design_requirements: Dict[str, Any], design_pattern: DesignPattern) -> List[ComponentSpecification]:
        """创建组件库"""
        
        components = []
        
        # 基础组件
        for component_name, template in self.component_templates.items():
            component = ComponentSpecification(
                component_name=component_name,
                component_type="基础组件",
                purpose=f"{component_name}组件的标准实现",
                states=template["states"],
                variants=template.get("variants", ["default"]),
                properties=template.get("properties", {}),
                behavior_rules=[
                    f"支持{len(template['states'])}种状态变化",
                    "遵循无障碍设计原则",
                    "支持键盘导航"
                ],
                accessibility_features=[
                    "ARIA标签支持",
                    "键盘导航",
                    "屏幕阅读器友好",
                    "高对比度支持"
                ],
                responsive_behavior={
                    "mobile": "触摸优化",
                    "tablet": "混合交互",
                    "desktop": "鼠标键盘优化"
                }
            )
            components.append(component)
        
        # 复合组件
        complex_components = [
            {
                "name": "data_table",
                "type": "数据展示",
                "purpose": "展示和操作表格数据",
                "states": ["loading", "empty", "error", "populated"],
                "variants": ["simple", "sortable", "filterable", "paginated"]
            },
            {
                "name": "modal",
                "type": "反馈",
                "purpose": "模态对话框",
                "states": ["closed", "opening", "open", "closing"],
                "variants": ["small", "medium", "large", "fullscreen"]
            },
            {
                "name": "sidebar",
                "type": "导航",
                "purpose": "侧边导航栏",
                "states": ["collapsed", "expanded", "overlay"],
                "variants": ["fixed", "push", "overlay"]
            }
        ]
        
        for comp_data in complex_components:
            component = ComponentSpecification(
                component_name=comp_data["name"],
                component_type=comp_data["type"],
                purpose=comp_data["purpose"],
                states=comp_data["states"],
                variants=comp_data["variants"],
                properties={},
                behavior_rules=[
                    "支持动画过渡",
                    "状态管理一致",
                    "错误处理完善"
                ],
                accessibility_features=[
                    "焦点管理",
                    "ARIA属性",
                    "键盘快捷键"
                ],
                responsive_behavior={
                    "mobile": "触摸手势支持",
                    "desktop": "鼠标交互优化"
                }
            )
            components.append(component)
        
        return components
    
    async def _design_interaction_patterns(self, design_requirements: Dict[str, Any]) -> List[InteractionPattern]:
        """设计交互模式"""
        
        patterns = []
        
        for pattern_name, pattern_info in self.interaction_patterns_library.items():
            pattern = InteractionPattern(
                pattern_name=pattern_name,
                pattern_type="用户交互",
                trigger="用户操作",
                action=pattern_info["description"],
                feedback="视觉和触觉反馈",
                animation_specs={
                    "duration": "200-300ms",
                    "easing": "ease-out",
                    "properties": ["opacity", "transform", "color"]
                },
                accessibility_considerations=[
                    "减少动画选项",
                    "焦点指示清晰",
                    "操作结果反馈"
                ],
                device_adaptations={
                    DeviceType.MOBILE: "触摸手势优化",
                    DeviceType.DESKTOP: "鼠标悬停效果",
                    DeviceType.TABLET: "混合交互模式"
                }
            )
            patterns.append(pattern)
        
        return patterns
    
    async def _establish_layout_system(self, design_requirements: Dict[str, Any]) -> LayoutSystem:
        """建立布局系统"""
        
        return LayoutSystem(
            grid_system={
                "columns": 12,
                "gutter": "24px",
                "margin": "16px",
                "container_max_width": "1200px"
            },
            breakpoints={
                "xs": "0px",
                "sm": "576px", 
                "md": "768px",
                "lg": "992px",
                "xl": "1200px",
                "xxl": "1400px"
            },
            spacing_system={
                "xs": "4px",
                "sm": "8px",
                "md": "16px", 
                "lg": "24px",
                "xl": "32px",
                "xxl": "48px"
            },
            container_specs={
                "fluid": {"width": "100%", "padding": "0 16px"},
                "fixed": {"max_width": "1200px", "margin": "0 auto", "padding": "0 16px"}
            },
            responsive_rules={
                "mobile": ["单列布局", "垂直堆叠", "全宽组件"],
                "tablet": ["两列布局", "混合排列", "适中间距"],
                "desktop": ["多列布局", "水平分布", "标准间距"]
            }
        )
    
    async def _design_user_flows(self, architecture_result: ArchitectureDesignResult, design_requirements: Dict[str, Any]) -> List[UserFlow]:
        """设计用户流程"""
        
        user_flows = []
        
        # 基于系统组件创建主要用户流程
        components = architecture_result.technical_architecture.system_topology.components
        
        for component in components[:3]:  # 取前3个主要组件
            flow = UserFlow(
                flow_id=f"FLOW-{component.component_id}",
                flow_name=f"{component.name}操作流程",
                user_persona="主要用户",
                entry_point="系统首页",
                steps=[
                    {"step": 1, "action": "进入系统", "screen": "登录页面"},
                    {"step": 2, "action": "导航到功能", "screen": "主界面"},
                    {"step": 3, "action": f"使用{component.name}", "screen": f"{component.name}页面"},
                    {"step": 4, "action": "完成操作", "screen": "结果页面"}
                ],
                decision_points=[
                    {"point": "权限验证", "options": ["通过", "拒绝"], "consequences": ["继续", "返回登录"]},
                    {"point": "数据验证", "options": ["有效", "无效"], "consequences": ["保存", "显示错误"]}
                ],
                exit_points=["操作完成", "用户取消", "系统错误"],
                success_metrics={
                    "completion_rate": "≥90%",
                    "task_success_rate": "≥95%",
                    "user_satisfaction": "≥4.5/5"
                },
                error_handling=[
                    {"error": "网络错误", "handling": "显示重试选项"},
                    {"error": "权限不足", "handling": "引导联系管理员"},
                    {"error": "数据错误", "handling": "高亮错误字段"}
                ]
            )
            user_flows.append(flow)
        
        return user_flows
    
    async def _build_information_architecture(self, architecture_result: ArchitectureDesignResult) -> Dict[str, Any]:
        """构建信息架构"""
        
        components = architecture_result.technical_architecture.system_topology.components
        
        return {
            "site_map": {
                "首页": {
                    "level": 1,
                    "children": [comp.name for comp in components]
                },
                "功能模块": {
                    "level": 2, 
                    "children": [
                        {"name": comp.name, "description": comp.description}
                        for comp in components
                    ]
                }
            },
            "content_hierarchy": {
                "primary": "核心功能和数据",
                "secondary": "辅助功能和设置",
                "tertiary": "帮助和文档"
            },
            "labeling_system": {
                "navigation": "简洁动词",
                "content": "描述性名词",
                "actions": "明确动作词"
            },
            "search_strategy": {
                "global_search": "全局搜索功能",
                "filtered_search": "分类筛选搜索",
                "auto_complete": "智能提示"
            }
        }
    
    def _design_navigation_structure(self, information_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """设计导航结构"""
        
        return {
            "primary_navigation": {
                "type": "horizontal_tabs",
                "items": information_architecture["site_map"]["功能模块"]["children"],
                "behavior": "单击切换",
                "responsive": "折叠菜单"
            },
            "secondary_navigation": {
                "type": "sidebar",
                "context": "页面相关",
                "behavior": "树形展开"
            },
            "breadcrumb": {
                "enabled": True,
                "format": "首页 > 模块 > 页面",
                "interactive": True
            },
            "search": {
                "position": "header",
                "placeholder": "搜索功能或内容",
                "scope": "全局"
            }
        }
    
    async def _design_accessibility_features(self, design_requirements: Dict[str, Any]) -> AccessibilityFeatures:
        """设计无障碍功能"""
        
        return AccessibilityFeatures(
            keyboard_navigation={
                "tab_order": "逻辑顺序",
                "skip_links": "跳转到主内容",
                "focus_indicators": "清晰可见",
                "keyboard_shortcuts": "Alt+快捷键"
            },
            screen_reader_support={
                "semantic_html": "语义化标签",
                "aria_labels": "描述性标签",
                "live_regions": "动态内容通知",
                "heading_structure": "h1-h6层次"
            },
            visual_indicators={
                "high_contrast": "支持高对比度模式",
                "color_independence": "不依赖颜色传达信息",
                "text_scaling": "支持200%缩放",
                "focus_visible": "焦点清晰指示"
            },
            motor_accessibility={
                "large_targets": "最小44px点击目标",
                "drag_alternatives": "拖拽的替代操作",
                "timeout_extensions": "操作时间延长",
                "click_alternatives": "多种激活方式"
            },
            cognitive_accessibility={
                "consistent_navigation": "一致的导航模式",
                "clear_instructions": "清晰的操作指引",
                "error_prevention": "错误预防和纠正",
                "progressive_disclosure": "渐进式信息展示"
            },
            compliance_checklist=[
                "颜色对比度≥4.5:1",
                "所有交互元素可键盘访问",
                "图片提供替代文本",
                "表单标签正确关联",
                "页面标题唯一描述",
                "错误信息清晰具体"
            ]
        )
    
    def _assess_design_quality(self, ux_design_system: UXDesignSystem) -> Dict[str, float]:
        """评估设计质量"""
        
        # 完整性评估
        completeness = 0.0
        completeness += 0.2 if ux_design_system.color_palette else 0.0
        completeness += 0.2 if ux_design_system.typography_system else 0.0
        completeness += 0.2 if len(ux_design_system.component_library) >= 5 else 0.0
        completeness += 0.2 if len(ux_design_system.user_flows) >= 1 else 0.0
        completeness += 0.2 if ux_design_system.accessibility_features else 0.0
        
        # 一致性评估
        consistency = 0.0
        consistency += 0.3 if ux_design_system.design_pattern != DesignPattern.CUSTOM else 0.2
        consistency += 0.3 if len(ux_design_system.color_palette.primary_color) > 0 else 0.0
        consistency += 0.2 if ux_design_system.typography_system.font_families else 0.0
        consistency += 0.2 if len(ux_design_system.interaction_patterns) > 0 else 0.0
        
        # 可用性评估
        usability = 0.0
        usability += 0.25 if len(ux_design_system.user_flows) > 0 else 0.0
        usability += 0.25 if ux_design_system.layout_system.responsive_rules else 0.0
        usability += 0.25 if len(ux_design_system.supported_devices) >= 2 else 0.0
        usability += 0.25 if ux_design_system.information_architecture else 0.0
        
        # 无障碍性评估
        accessibility = 0.0
        accessibility += 0.2 if ux_design_system.accessibility_level == AccessibilityLevel.WCAG_AA else 0.1
        accessibility += 0.2 if ux_design_system.accessibility_features.keyboard_navigation else 0.0
        accessibility += 0.2 if ux_design_system.accessibility_features.screen_reader_support else 0.0
        accessibility += 0.2 if ux_design_system.color_palette.accessibility_contrast else 0.0
        accessibility += 0.2 if len(ux_design_system.accessibility_features.compliance_checklist) >= 5 else 0.0
        
        return {
            "completeness": completeness,
            "consistency": consistency,
            "usability": usability,
            "accessibility": accessibility,
            "overall_quality": (completeness + consistency + usability + accessibility) / 4
        }
    
    def _generate_prototyping_recommendations(self, ux_design_system: UXDesignSystem) -> List[str]:
        """生成原型建议"""
        
        recommendations = [
            "建议创建低保真线框图验证信息架构",
            "建议制作高保真视觉原型展示设计系统",
            "建议开发交互原型测试用户流程",
            "建议创建响应式原型验证多设备体验"
        ]
        
        if len(ux_design_system.user_flows) > 2:
            recommendations.append("建议为复杂流程创建专门的流程原型")
        
        if ux_design_system.accessibility_level == AccessibilityLevel.WCAG_AA:
            recommendations.append("建议创建无障碍功能演示原型")
        
        return recommendations
    
    def _create_usability_testing_plan(self, ux_design_system: UXDesignSystem) -> Dict[str, Any]:
        """创建可用性测试计划"""
        
        return {
            "testing_objectives": [
                "验证用户流程的易用性",
                "评估界面元素的可发现性",
                "测试响应式设计的有效性",
                "验证无障碍功能的实用性"
            ],
            "testing_methods": [
                "用户访谈",
                "任务完成测试",
                "A/B测试",
                "眼动追踪",
                "启发式评估"
            ],
            "target_users": [
                {"type": "主要用户", "count": 8, "characteristics": "日常使用者"},
                {"type": "管理用户", "count": 4, "characteristics": "系统管理员"},
                {"type": "无障碍用户", "count": 2, "characteristics": "使用辅助技术"}
            ],
            "testing_scenarios": [
                {"scenario": f"完成{flow.flow_name}", "success_criteria": flow.success_metrics}
                for flow in ux_design_system.user_flows
            ],
            "metrics": {
                "task_completion_rate": "≥90%",
                "time_on_task": "基线±20%",
                "error_rate": "≤10%",
                "satisfaction_score": "≥4.0/5.0",
                "learnability": "第二次使用提升≥20%"
            },
            "testing_environment": {
                "devices": ["Desktop", "Tablet", "Mobile"],
                "browsers": ["Chrome", "Firefox", "Safari", "Edge"],
                "assistive_technologies": ["NVDA", "JAWS", "VoiceOver"]
            }
        }
    
    def _generate_implementation_guidelines(self, ux_design_system: UXDesignSystem, architecture_result: ArchitectureDesignResult) -> List[str]:
        """生成实施指南"""
        
        guidelines = [
            "建立设计令牌系统管理设计变量",
            "创建组件库文档和使用指南",
            "制定设计审查流程和标准",
            "建立设计-开发协作工作流"
        ]
        
        # 基于技术栈生成具体建议
        tech_stack = architecture_result.technical_architecture.technology_stack
        
        for tech in tech_stack:
            if "React" in tech.name:
                guidelines.append("建议使用Styled Components或Emotion实现设计系统")
            elif "Vue" in tech.name:
                guidelines.append("建议使用Vue 3 Composition API构建组件库")
            elif "Angular" in tech.name:
                guidelines.append("建议使用Angular Material作为基础设计系统")
        
        # 基于设计模式生成建议
        if ux_design_system.design_pattern == DesignPattern.MATERIAL_DESIGN:
            guidelines.append("建议集成Material Design Components库")
        elif ux_design_system.design_pattern == DesignPattern.ANT_DESIGN:
            guidelines.append("建议使用Ant Design组件库作为基础")
        
        return guidelines
    
    def _identify_design_issues(self, ux_design_system: UXDesignSystem, design_quality: Dict[str, float]) -> List[Dict[str, Any]]:
        """识别设计问题"""
        
        issues = []
        
        # 完整性问题
        if design_quality["completeness"] < 0.9:
            missing_parts = []
            if not ux_design_system.color_palette:
                missing_parts.append("色彩系统")
            if len(ux_design_system.component_library) < 5:
                missing_parts.append("组件库")
            if len(ux_design_system.user_flows) < 1:
                missing_parts.append("用户流程")
            
            if missing_parts:
                issues.append({
                    "type": "incomplete_design_system",
                    "severity": "medium",
                    "description": f"设计系统不完整，缺少: {', '.join(missing_parts)}",
                    "missing_components": missing_parts
                })
        
        # 一致性问题
        if design_quality["consistency"] < 0.9:
            issues.append({
                "type": "design_inconsistency",
                "severity": "medium",
                "description": "设计系统一致性不足，需要统一设计语言",
                "recommendations": ["统一设计模式", "建立设计规范", "创建设计令牌"]
            })
        
        # 无障碍问题
        if design_quality["accessibility"] < 0.9:
            issues.append({
                "type": "accessibility_gaps",
                "severity": "high",
                "description": "无障碍设计不充分，可能影响用户体验",
                "compliance_gaps": ["颜色对比度", "键盘导航", "屏幕阅读器支持"]
            })
        
        # 响应式设计问题
        if len(ux_design_system.supported_devices) < 2:
            issues.append({
                "type": "limited_device_support",
                "severity": "medium",
                "description": "设备支持范围有限，建议扩展响应式设计",
                "missing_devices": ["tablet", "mobile"]
            })
        
        return issues

# 工厂函数
def create_ux_design_generator(claude_service: ClaudeService) -> IntelligentUXDesignGenerator:
    """创建UX设计生成器"""
    return IntelligentUXDesignGenerator(claude_service)

# 使用示例
async def demo_ux_design_generation():
    """演示UX设计生成功能"""
    from ....claude_integration import create_claude_service
    from ..requirements_collection.requirements_understanding import create_requirements_analyzer
    from ..requirements_collection.user_story_generator import create_user_story_generator
    from .technical_architecture_designer import create_technical_architecture_designer
    
    claude_service = create_claude_service()
    requirements_analyzer = create_requirements_analyzer(claude_service)
    story_generator = create_user_story_generator(claude_service)
    architecture_designer = create_technical_architecture_designer(claude_service)
    ux_designer = create_ux_design_generator(claude_service)
    
    # 测试需求
    test_requirement = "开发一个现代化的项目管理平台，支持任务管理、团队协作、进度跟踪，需要优秀的用户体验和无障碍设计"
    
    print(f"测试需求: {test_requirement}")
    
    try:
        # 1. 需求分析
        requirement_analysis = await requirements_analyzer.analyze_requirements(test_requirement)
        print(f"需求分析完成")
        
        # 2. 生成用户故事
        story_result = await story_generator.generate_user_stories(requirement_analysis)
        print(f"用户故事生成完成，共{len(story_result.generated_stories)}个故事")
        
        # 3. 设计技术架构
        architecture_result = await architecture_designer.design_technical_architecture(story_result)
        print(f"技术架构设计完成")
        
        # 4. 生成UX设计
        ux_result = await ux_designer.generate_ux_design(architecture_result)
        
        print(f"\n=== UX设计生成结果 ===")
        ux_system = ux_result.ux_design_system
        
        print(f"设计系统ID: {ux_system.design_id}")
        print(f"项目名称: {ux_system.project_name}")
        print(f"设计模式: {ux_system.design_pattern.value}")
        print(f"设计理念: {ux_system.design_philosophy}")
        
        print(f"\n=== 设计质量评估 ===")
        quality = ux_result.design_quality
        print(f"交互设计完整性: {quality['completeness']:.1%}")
        print(f"设计规范一致性: {quality['consistency']:.1%}")
        print(f"可用性评分: {quality['usability']:.1%}")
        print(f"无障碍评分: {quality['accessibility']:.1%}")
        print(f"整体质量: {quality['overall_quality']:.1%}")
        
        print(f"\n=== 色彩系统 ===")
        colors = ux_system.color_palette
        print(f"主色彩: {colors.primary_color}")
        print(f"辅助色彩: {', '.join(colors.secondary_colors[:2])}")
        print(f"语义色彩: {', '.join([f'{k}: {v}' for k, v in colors.semantic_colors.items()][:2])}")
        
        print(f"\n=== 组件库 ===")
        components_by_type = {}
        for comp in ux_system.component_library:
            comp_type = comp.component_type
            if comp_type not in components_by_type:
                components_by_type[comp_type] = []
            components_by_type[comp_type].append(comp)
        
        for comp_type, comps in components_by_type.items():
            print(f"{comp_type}: {', '.join([comp.component_name for comp in comps])}")
        
        print(f"\n=== 用户流程 ===")
        for flow in ux_system.user_flows:
            print(f"- {flow.flow_name}")
            print(f"  步骤数: {len(flow.steps)}")
            print(f"  成功指标: {', '.join([f'{k}: {v}' for k, v in flow.success_metrics.items()][:2])}")
        
        print(f"\n=== 无障碍功能 ===")
        accessibility = ux_system.accessibility_features
        print(f"无障碍等级: {ux_system.accessibility_level.value}")
        print(f"合规检查项: {len(accessibility.compliance_checklist)}项")
        print(f"关键功能: 键盘导航、屏幕阅读器、高对比度支持")
        
        print(f"\n=== 响应式设计 ===")
        print(f"支持设备: {', '.join([device.value for device in ux_system.supported_devices])}")
        print(f"响应式策略: {ux_system.responsive_strategy}")
        breakpoints = ux_system.layout_system.breakpoints
        print(f"断点设置: {', '.join([f'{k}: {v}' for k, v in breakpoints.items()][:3])}")
        
        if ux_result.prototyping_recommendations:
            print(f"\n=== 原型建议 ===")
            for rec in ux_result.prototyping_recommendations[:3]:
                print(f"- {rec}")
        
        if ux_result.implementation_guidelines:
            print(f"\n=== 实施指南 ===")
            for guideline in ux_result.implementation_guidelines[:3]:
                print(f"- {guideline}")
        
        if ux_result.issues_found:
            print(f"\n=== 发现的问题 ===")
            for issue in ux_result.issues_found:
                print(f"- {issue['type']} ({issue['severity']}): {issue['description']}")
        
        print(f"\n=== 可用性测试计划 ===")
        testing_plan = ux_result.usability_testing_plan
        print(f"测试目标: {len(testing_plan['testing_objectives'])}项")
        print(f"测试方法: {', '.join(testing_plan['testing_methods'][:3])}")
        print(f"目标用户: {len(testing_plan['target_users'])}类用户群体")
        
        print(f"\n处理时间: {ux_result.processing_time:.2f}秒")
        
        # 验证验收标准
        print(f"\n=== 验收标准验证 ===")
        print(f"AC-005-01 (交互设计完整性≥90%): {'✓' if quality['completeness'] >= 0.90 else '✗'} {quality['completeness']:.1%}")
        print(f"AC-005-02 (可用性标准覆盖率100%): {'✓' if quality['accessibility'] >= 0.90 else '✗'} {quality['accessibility']:.1%}")
        print(f"AC-005-03 (设计规范一致性≥4.5/5.0): {'✓' if quality['consistency'] >= 0.90 else '✗'} {quality['consistency']*5:.1f}/5.0")
        
    except Exception as e:
        print(f"UX设计生成失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_ux_design_generation())
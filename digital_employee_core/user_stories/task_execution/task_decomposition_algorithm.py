"""
US-007: 任务分解智能算法
Intelligent Task Decomposition Algorithm

验收标准:
- AC-007-01: 任务分解准确率≥90%
- AC-007-02: 依赖关系识别完整性≥95%
- AC-007-03: 工作量估算误差≤15%
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math

from ...claude_integration import ClaudeService
from ..design_collaboration.collaboration_workflow_designer import CollaborationDesignResult, CollaborationDesignSystem

logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """任务复杂度"""
    TRIVIAL = "trivial"          # 琐碎任务 (0-2小时)
    SIMPLE = "simple"            # 简单任务 (2-8小时)
    MODERATE = "moderate"        # 中等任务 (1-3天)
    COMPLEX = "complex"          # 复杂任务 (3-10天)
    VERY_COMPLEX = "very_complex" # 非常复杂 (10天以上)

class TaskType(Enum):
    """任务类型"""
    ANALYSIS = "analysis"              # 分析类
    DESIGN = "design"                  # 设计类
    DEVELOPMENT = "development"        # 开发类
    TESTING = "testing"               # 测试类
    DEPLOYMENT = "deployment"         # 部署类
    DOCUMENTATION = "documentation"   # 文档类
    RESEARCH = "research"             # 研究类
    COORDINATION = "coordination"     # 协调类

class DependencyType(Enum):
    """依赖关系类型"""
    FINISH_TO_START = "finish_to_start"     # 完成到开始
    START_TO_START = "start_to_start"       # 开始到开始
    FINISH_TO_FINISH = "finish_to_finish"   # 完成到完成
    START_TO_FINISH = "start_to_finish"     # 开始到完成

class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = "critical"        # 关键路径
    HIGH = "high"               # 高优先级
    MEDIUM = "medium"           # 中等优先级
    LOW = "low"                 # 低优先级

@dataclass
class SkillRequirement:
    """技能需求"""
    skill_name: str
    proficiency_level: str  # beginner, intermediate, advanced, expert
    importance: float       # 0.0 - 1.0
    alternatives: List[str] # 可替代技能

@dataclass
class ResourceRequirement:
    """资源需求"""
    resource_type: str      # human, tool, environment, data
    resource_name: str
    quantity: int
    duration: timedelta
    availability_constraint: Optional[str] = None

@dataclass
class TaskDependency:
    """任务依赖"""
    predecessor_task_id: str
    successor_task_id: str
    dependency_type: DependencyType
    lag_time: timedelta = timedelta(0)  # 延迟时间
    constraint_description: str = ""
    criticality: float = 1.0  # 0.0 - 1.0

@dataclass
class TaskRisk:
    """任务风险"""
    risk_id: str
    risk_description: str
    probability: float      # 0.0 - 1.0
    impact: float          # 0.0 - 1.0
    risk_score: float      # probability * impact
    mitigation_strategies: List[str]

@dataclass
class WorkloadEstimate:
    """工作量估算"""
    optimistic_hours: float    # 乐观估算
    realistic_hours: float     # 现实估算
    pessimistic_hours: float   # 悲观估算
    expected_hours: float      # 期望值 (PERT)
    confidence_level: float    # 0.0 - 1.0
    estimation_method: str     # 估算方法
    historical_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AtomicTask:
    """原子任务"""
    task_id: str
    task_name: str
    description: str
    task_type: TaskType
    complexity: TaskComplexity
    priority: TaskPriority
    
    # 工作量和时间
    workload_estimate: WorkloadEstimate
    duration: timedelta
    
    # 技能和资源需求
    skill_requirements: List[SkillRequirement]
    resource_requirements: List[ResourceRequirement]
    
    # 依赖关系
    dependencies: List[TaskDependency]
    
    # 验收标准
    acceptance_criteria: List[str]
    deliverables: List[str]
    
    # 质量和风险
    quality_gates: List[str]
    risks: List[TaskRisk]
    
    # 可分解性评估
    is_further_decomposable: bool
    decomposition_confidence: float
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskHierarchy:
    """任务层次结构"""
    root_task_id: str
    task_levels: Dict[int, List[str]]  # level -> task_ids
    parent_child_mapping: Dict[str, List[str]]  # parent_id -> child_ids
    leaf_tasks: Set[str]  # 叶子任务集合
    critical_path: List[str]  # 关键路径
    max_depth: int

@dataclass
class DecompositionMetrics:
    """分解质量指标"""
    decomposition_accuracy: float      # 分解准确率
    dependency_completeness: float     # 依赖完整性
    workload_estimation_error: float   # 工作量估算误差
    coverage_completeness: float       # 覆盖完整性
    granularity_appropriateness: float # 粒度适当性
    overall_quality: float

@dataclass
class TaskDecompositionResult:
    """任务分解结果"""
    source_collaboration_design: CollaborationDesignSystem
    atomic_tasks: List[AtomicTask]
    task_hierarchy: TaskHierarchy
    task_dependencies: List[TaskDependency]
    decomposition_metrics: DecompositionMetrics
    resource_allocation_suggestions: Dict[str, Any]
    timeline_estimation: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    optimization_recommendations: List[str]
    issues_found: List[Dict[str, Any]]
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)

class IntelligentTaskDecompositionAlgorithm:
    """智能任务分解算法"""
    
    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service
        self.decomposition_patterns = self._load_decomposition_patterns()
        self.estimation_models = self._load_estimation_models()
        self.skill_library = self._load_skill_library()
        self.dependency_rules = self._load_dependency_rules()
        
    def _load_decomposition_patterns(self) -> Dict[str, Dict[str, Any]]:
        """加载分解模式"""
        return {
            "feature_development": {
                "pattern": ["需求分析", "技术设计", "实现开发", "单元测试", "集成测试", "代码审查"],
                "typical_ratios": [0.15, 0.20, 0.40, 0.10, 0.10, 0.05],
                "dependencies": ["sequential", "some_parallel"],
                "critical_tasks": ["技术设计", "实现开发"]
            },
            "system_architecture": {
                "pattern": ["需求分析", "架构设计", "详细设计", "原型验证", "文档编写"],
                "typical_ratios": [0.25, 0.35, 0.25, 0.10, 0.05],
                "dependencies": ["mostly_sequential"],
                "critical_tasks": ["架构设计", "详细设计"]
            },
            "ux_design": {
                "pattern": ["用户研究", "信息架构", "交互设计", "视觉设计", "原型制作", "可用性测试"],
                "typical_ratios": [0.20, 0.15, 0.25, 0.20, 0.15, 0.05],
                "dependencies": ["sequential_with_feedback"],
                "critical_tasks": ["用户研究", "交互设计"]
            },
            "testing_workflow": {
                "pattern": ["测试计划", "测试用例设计", "测试环境准备", "测试执行", "缺陷管理", "测试报告"],
                "typical_ratios": [0.15, 0.25, 0.10, 0.30, 0.15, 0.05],
                "dependencies": ["sequential_with_parallel"],
                "critical_tasks": ["测试用例设计", "测试执行"]
            }
        }
    
    def _load_estimation_models(self) -> Dict[str, Dict[str, Any]]:
        """加载估算模型"""
        return {
            "function_points": {
                "description": "功能点估算法",
                "complexity_multipliers": {
                    TaskComplexity.TRIVIAL: 0.5,
                    TaskComplexity.SIMPLE: 1.0,
                    TaskComplexity.MODERATE: 2.0,
                    TaskComplexity.COMPLEX: 4.0,
                    TaskComplexity.VERY_COMPLEX: 8.0
                },
                "base_hours": 8
            },
            "expert_judgment": {
                "description": "专家判断法",
                "confidence_factors": {
                    "high_confidence": 1.0,
                    "medium_confidence": 1.25,
                    "low_confidence": 1.5
                },
                "experience_multipliers": {
                    "expert": 0.8,
                    "senior": 1.0,
                    "intermediate": 1.3,
                    "junior": 1.8
                }
            },
            "historical_data": {
                "description": "历史数据类比",
                "similarity_threshold": 0.7,
                "adjustment_factors": {
                    "team_experience": 0.1,
                    "technology_novelty": 0.15,
                    "business_complexity": 0.1
                }
            }
        }
    
    def _load_skill_library(self) -> Dict[str, Dict[str, Any]]:
        """加载技能库"""
        return {
            "software_development": {
                "programming": {
                    "subcategories": ["前端开发", "后端开发", "全栈开发", "移动开发"],
                    "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"],
                    "typical_hourly_productivity": {"beginner": 0.5, "intermediate": 1.0, "advanced": 1.5, "expert": 2.0}
                },
                "system_design": {
                    "subcategories": ["架构设计", "数据库设计", "API设计", "微服务设计"],
                    "proficiency_levels": ["intermediate", "advanced", "expert"],
                    "typical_hourly_productivity": {"intermediate": 0.8, "advanced": 1.2, "expert": 1.8}
                }
            },
            "design": {
                "ux_design": {
                    "subcategories": ["用户研究", "交互设计", "视觉设计", "原型设计"],
                    "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"],
                    "typical_hourly_productivity": {"beginner": 0.6, "intermediate": 1.0, "advanced": 1.4, "expert": 1.8}
                }
            },
            "testing": {
                "qa_testing": {
                    "subcategories": ["功能测试", "自动化测试", "性能测试", "安全测试"],
                    "proficiency_levels": ["beginner", "intermediate", "advanced", "expert"],
                    "typical_hourly_productivity": {"beginner": 0.7, "intermediate": 1.0, "advanced": 1.3, "expert": 1.6}
                }
            }
        }
    
    def _load_dependency_rules(self) -> Dict[str, List[str]]:
        """加载依赖规则"""
        return {
            "mandatory_sequences": [
                "需求分析 -> 技术设计",
                "技术设计 -> 实现开发",
                "实现开发 -> 单元测试",
                "单元测试 -> 集成测试"
            ],
            "parallel_opportunities": [
                "前端开发 || 后端开发",
                "功能测试 || 性能测试",
                "文档编写 || 用户培训准备"
            ],
            "quality_gates": [
                "代码审查 -> 部署",
                "安全测试 -> 生产发布",
                "用户验收测试 -> 项目交付"
            ]
        }
    
    async def decompose_tasks(self, collaboration_result: CollaborationDesignResult) -> TaskDecompositionResult:
        """
        智能任务分解
        
        Args:
            collaboration_result: 协作设计结果
            
        Returns:
            TaskDecompositionResult: 任务分解结果
        """
        start_time = datetime.now()
        
        try:
            logger.info("开始智能任务分解...")
            
            # 1. 分析协作工作流，识别主要任务
            main_tasks = await self._analyze_collaboration_workflows(collaboration_result)
            
            # 2. 执行递归任务分解
            atomic_tasks = await self._recursive_task_decomposition(main_tasks, collaboration_result)
            
            # 3. 识别和建立任务依赖关系
            task_dependencies = await self._identify_task_dependencies(atomic_tasks)
            
            # 4. 执行工作量估算
            await self._estimate_task_workloads(atomic_tasks, collaboration_result)
            
            # 5. 分析技能和资源需求
            await self._analyze_skill_resource_requirements(atomic_tasks, collaboration_result)
            
            # 6. 评估任务风险
            await self._assess_task_risks(atomic_tasks)
            
            # 7. 构建任务层次结构
            task_hierarchy = self._build_task_hierarchy(atomic_tasks)
            
            # 8. 计算关键路径
            self._calculate_critical_path(task_hierarchy, atomic_tasks, task_dependencies)
            
            # 9. 评估分解质量
            decomposition_metrics = self._assess_decomposition_quality(atomic_tasks, task_dependencies)
            
            # 10. 生成资源分配建议
            resource_allocation = self._generate_resource_allocation_suggestions(atomic_tasks, collaboration_result)
            
            # 11. 生成时间线估算
            timeline_estimation = self._generate_timeline_estimation(atomic_tasks, task_dependencies, task_hierarchy)
            
            # 12. 评估整体风险
            risk_assessment = self._assess_overall_risks(atomic_tasks, task_dependencies)
            
            # 13. 生成优化建议
            optimization_recommendations = self._generate_optimization_recommendations(
                atomic_tasks, task_dependencies, decomposition_metrics
            )
            
            # 14. 识别问题
            issues = self._identify_decomposition_issues(atomic_tasks, decomposition_metrics)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = TaskDecompositionResult(
                source_collaboration_design=collaboration_result.collaboration_design,
                atomic_tasks=atomic_tasks,
                task_hierarchy=task_hierarchy,
                task_dependencies=task_dependencies,
                decomposition_metrics=decomposition_metrics,
                resource_allocation_suggestions=resource_allocation,
                timeline_estimation=timeline_estimation,
                risk_assessment=risk_assessment,
                optimization_recommendations=optimization_recommendations,
                issues_found=issues,
                processing_time=processing_time
            )
            
            logger.info(f"任务分解完成，生成{len(atomic_tasks)}个原子任务，分解准确率: {decomposition_metrics.decomposition_accuracy:.1%}")
            
            return result
            
        except Exception as e:
            logger.error(f"任务分解失败: {str(e)}")
            raise
    
    async def _analyze_collaboration_workflows(self, collaboration_result: CollaborationDesignResult) -> List[Dict[str, Any]]:
        """分析协作工作流，识别主要任务"""
        
        main_tasks = []
        
        for workflow in collaboration_result.collaboration_design.collaboration_workflows:
            for step in workflow.steps:
                main_task = {
                    "task_id": f"MAIN-{step.step_id}",
                    "task_name": step.step_name,
                    "description": step.description,
                    "workflow_type": workflow.workflow_type.value,
                    "responsible_roles": [role.value for role in step.responsible_roles],
                    "input_requirements": step.input_requirements,
                    "output_deliverables": step.output_deliverables,
                    "duration_estimate": step.duration_estimate,
                    "dependencies": step.dependencies,
                    "automation_level": step.automation_level.value,
                    "quality_gates": step.quality_gates,
                    "communication_needs": step.communication_needs
                }
                main_tasks.append(main_task)
        
        return main_tasks
    
    async def _recursive_task_decomposition(self, main_tasks: List[Dict[str, Any]], 
                                          collaboration_result: CollaborationDesignResult) -> List[AtomicTask]:
        """递归任务分解"""
        
        atomic_tasks = []
        
        for main_task in main_tasks:
            # 分析任务复杂度
            complexity = self._assess_task_complexity(main_task)
            
            if complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
                # 需要进一步分解
                subtasks = await self._decompose_complex_task(main_task, collaboration_result)
                
                for subtask_data in subtasks:
                    atomic_task = await self._create_atomic_task(subtask_data, main_task)
                    atomic_tasks.append(atomic_task)
            else:
                # 已经是原子任务
                atomic_task = await self._create_atomic_task(main_task, None)
                atomic_tasks.append(atomic_task)
        
        return atomic_tasks
    
    def _assess_task_complexity(self, task_data: Dict[str, Any]) -> TaskComplexity:
        """评估任务复杂度"""
        
        # 基于多个因素评估复杂度
        complexity_score = 0
        
        # 时间因素
        duration = task_data.get("duration_estimate", timedelta(hours=8))
        if isinstance(duration, timedelta):
            hours = duration.total_seconds() / 3600
            if hours <= 2:
                complexity_score += 1
            elif hours <= 8:
                complexity_score += 2
            elif hours <= 24:
                complexity_score += 3
            elif hours <= 80:
                complexity_score += 4
            else:
                complexity_score += 5
        
        # 职责角色数量
        roles_count = len(task_data.get("responsible_roles", []))
        complexity_score += min(roles_count, 3)
        
        # 输入输出复杂度
        inputs_count = len(task_data.get("input_requirements", []))
        outputs_count = len(task_data.get("output_deliverables", []))
        complexity_score += min((inputs_count + outputs_count) // 3, 2)
        
        # 质量门数量
        quality_gates_count = len(task_data.get("quality_gates", []))
        complexity_score += min(quality_gates_count // 2, 2)
        
        # 映射到复杂度等级
        if complexity_score <= 3:
            return TaskComplexity.TRIVIAL
        elif complexity_score <= 5:
            return TaskComplexity.SIMPLE
        elif complexity_score <= 8:
            return TaskComplexity.MODERATE
        elif complexity_score <= 12:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.VERY_COMPLEX
    
    async def _decompose_complex_task(self, main_task: Dict[str, Any], 
                                    collaboration_result: CollaborationDesignResult) -> List[Dict[str, Any]]:
        """分解复杂任务"""
        
        decomposition_prompt = f"""
作为资深项目管理专家和任务分解专家，请将以下复杂任务分解为更小的原子任务。

复杂任务信息：
- 任务名称: {main_task['task_name']}
- 描述: {main_task['description']}
- 工作流类型: {main_task['workflow_type']}
- 负责角色: {main_task['responsible_roles']}
- 输入要求: {main_task['input_requirements']}
- 输出交付物: {main_task['output_deliverables']}
- 预估时长: {main_task['duration_estimate']}

请按照以下原则进行分解：

1. **原子性原则**
   - 每个子任务应该是不可进一步分解的最小工作单元
   - 单个任务工作量不超过2天
   - 单个任务只需要1-2个角色参与

2. **完整性原则**
   - 确保所有子任务完全覆盖原任务范围
   - 子任务之间不重复，不遗漏
   - 保持逻辑连贯性

3. **可执行性原则**
   - 每个子任务有明确的输入、处理、输出
   - 有清晰的验收标准
   - 有具体的技能要求

4. **依赖关系**
   - 识别子任务间的依赖关系
   - 标识可以并行执行的任务
   - 确定关键路径

请为每个子任务提供：
- 子任务名称和描述
- 预估工作量（小时）
- 所需技能和角色
- 输入和输出
- 验收标准
- 与其他子任务的依赖关系

返回JSON格式的分解结果。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": decomposition_prompt}],
            temperature=0.2,
            max_tokens=3000
        )
        
        if response.success:
            try:
                decomposition_result = json.loads(response.content)
                return decomposition_result.get("子任务", [])
            except json.JSONDecodeError:
                return self._create_basic_subtasks(main_task)
        else:
            return self._create_basic_subtasks(main_task)
    
    def _create_basic_subtasks(self, main_task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建基础子任务（降级处理）"""
        
        workflow_type = main_task.get("workflow_type", "development")
        pattern = self.decomposition_patterns.get(workflow_type, self.decomposition_patterns["feature_development"])
        
        subtasks = []
        total_hours = main_task.get("duration_estimate", timedelta(hours=16)).total_seconds() / 3600
        
        for i, (task_name, ratio) in enumerate(zip(pattern["pattern"], pattern["typical_ratios"])):
            subtask = {
                "任务名称": f"{main_task['task_name']} - {task_name}",
                "描述": f"执行{task_name}相关工作",
                "预估工作量": total_hours * ratio,
                "所需技能": main_task.get("responsible_roles", ["开发工程师"]),
                "输入": main_task.get("input_requirements", []),
                "输出": [f"{task_name}交付物"],
                "验收标准": [f"{task_name}完成并通过质量检查"],
                "依赖关系": [f"{main_task['task_id']}-{i-1:02d}"] if i > 0 else []
            }
            subtasks.append(subtask)
        
        return subtasks
    
    async def _create_atomic_task(self, task_data: Dict[str, Any], parent_task: Optional[Dict[str, Any]]) -> AtomicTask:
        """创建原子任务"""
        
        # 生成任务ID
        if parent_task:
            task_id = f"AT-{parent_task['task_id'].split('-')[-1]}-{hash(task_data.get('任务名称', ''))%1000:03d}"
        else:
            task_id = f"AT-{task_data['task_id'].split('-')[-1]}"
        
        # 解析任务名称和描述
        task_name = task_data.get("任务名称", task_data.get("task_name", "未命名任务"))
        description = task_data.get("描述", task_data.get("description", ""))
        
        # 确定任务类型
        task_type = self._determine_task_type(task_name, description)
        
        # 评估复杂度
        complexity = self._assess_task_complexity(task_data)
        
        # 设置优先级
        priority = TaskPriority.MEDIUM  # 默认中等优先级
        
        # 创建工作量估算
        workload_estimate = self._create_workload_estimate(task_data, complexity)
        
        # 计算持续时间
        duration = timedelta(hours=workload_estimate.expected_hours)
        
        # 创建技能需求
        skill_requirements = self._create_skill_requirements(task_data, task_type)
        
        # 创建资源需求
        resource_requirements = self._create_resource_requirements(task_data, workload_estimate)
        
        # 创建验收标准
        acceptance_criteria = task_data.get("验收标准", task_data.get("quality_gates", ["任务完成并通过质量检查"]))
        
        # 创建交付物
        deliverables = task_data.get("输出", task_data.get("output_deliverables", ["任务交付物"]))
        
        return AtomicTask(
            task_id=task_id,
            task_name=task_name,
            description=description,
            task_type=task_type,
            complexity=complexity,
            priority=priority,
            workload_estimate=workload_estimate,
            duration=duration,
            skill_requirements=skill_requirements,
            resource_requirements=resource_requirements,
            dependencies=[],  # 稍后填充
            acceptance_criteria=acceptance_criteria,
            deliverables=deliverables,
            quality_gates=task_data.get("quality_gates", ["完成检查"]),
            risks=[],  # 稍后评估
            is_further_decomposable=False,
            decomposition_confidence=0.9
        )
    
    def _determine_task_type(self, task_name: str, description: str) -> TaskType:
        """确定任务类型"""
        
        text = f"{task_name} {description}".lower()
        
        if any(word in text for word in ["分析", "研究", "调研", "需求"]):
            return TaskType.ANALYSIS
        elif any(word in text for word in ["设计", "架构", "原型", "界面"]):
            return TaskType.DESIGN
        elif any(word in text for word in ["开发", "编程", "实现", "编码"]):
            return TaskType.DEVELOPMENT
        elif any(word in text for word in ["测试", "验证", "检查", "质量"]):
            return TaskType.TESTING
        elif any(word in text for word in ["部署", "发布", "上线", "安装"]):
            return TaskType.DEPLOYMENT
        elif any(word in text for word in ["文档", "说明", "手册", "记录"]):
            return TaskType.DOCUMENTATION
        elif any(word in text for word in ["协调", "沟通", "会议", "管理"]):
            return TaskType.COORDINATION
        else:
            return TaskType.DEVELOPMENT
    
    def _create_workload_estimate(self, task_data: Dict[str, Any], complexity: TaskComplexity) -> WorkloadEstimate:
        """创建工作量估算"""
        
        # 获取基础工作量
        base_hours = task_data.get("预估工作量", 8.0)
        if isinstance(base_hours, str):
            base_hours = 8.0
        
        # 应用复杂度乘数
        multiplier = self.estimation_models["function_points"]["complexity_multipliers"][complexity]
        base_hours *= multiplier
        
        # PERT三点估算
        optimistic = base_hours * 0.7
        realistic = base_hours
        pessimistic = base_hours * 1.5
        
        # 计算期望值 (O + 4R + P) / 6
        expected = (optimistic + 4 * realistic + pessimistic) / 6
        
        return WorkloadEstimate(
            optimistic_hours=optimistic,
            realistic_hours=realistic,
            pessimistic_hours=pessimistic,
            expected_hours=expected,
            confidence_level=0.8,
            estimation_method="PERT三点估算",
            historical_data={"complexity": complexity.value, "base_estimate": base_hours}
        )
    
    def _create_skill_requirements(self, task_data: Dict[str, Any], task_type: TaskType) -> List[SkillRequirement]:
        """创建技能需求"""
        
        skills = []
        required_skills = task_data.get("所需技能", task_data.get("responsible_roles", []))
        
        for skill_name in required_skills:
            # 映射角色到技能
            if "开发" in skill_name or "developer" in skill_name.lower():
                skill_requirement = SkillRequirement(
                    skill_name="软件开发",
                    proficiency_level="intermediate",
                    importance=0.9,
                    alternatives=["编程", "系统设计"]
                )
            elif "设计" in skill_name or "designer" in skill_name.lower():
                skill_requirement = SkillRequirement(
                    skill_name="UX设计",
                    proficiency_level="intermediate",
                    importance=0.8,
                    alternatives=["视觉设计", "交互设计"]
                )
            elif "测试" in skill_name or "qa" in skill_name.lower():
                skill_requirement = SkillRequirement(
                    skill_name="质量保证",
                    proficiency_level="intermediate",
                    importance=0.8,
                    alternatives=["测试自动化", "质量管理"]
                )
            else:
                skill_requirement = SkillRequirement(
                    skill_name=skill_name,
                    proficiency_level="intermediate",
                    importance=0.7,
                    alternatives=[]
                )
            
            skills.append(skill_requirement)
        
        return skills
    
    def _create_resource_requirements(self, task_data: Dict[str, Any], workload_estimate: WorkloadEstimate) -> List[ResourceRequirement]:
        """创建资源需求"""
        
        resources = []
        
        # 人力资源
        human_resource = ResourceRequirement(
            resource_type="human",
            resource_name="团队成员",
            quantity=1,
            duration=timedelta(hours=workload_estimate.expected_hours),
            availability_constraint="工作时间"
        )
        resources.append(human_resource)
        
        # 工具资源（基于任务类型）
        task_name = task_data.get("task_name", task_data.get("任务名称", ""))
        if "开发" in task_name:
            tool_resource = ResourceRequirement(
                resource_type="tool",
                resource_name="开发环境",
                quantity=1,
                duration=timedelta(hours=workload_estimate.expected_hours)
            )
            resources.append(tool_resource)
        elif "设计" in task_name:
            tool_resource = ResourceRequirement(
                resource_type="tool", 
                resource_name="设计工具",
                quantity=1,
                duration=timedelta(hours=workload_estimate.expected_hours)
            )
            resources.append(tool_resource)
        
        return resources
    
    async def _identify_task_dependencies(self, atomic_tasks: List[AtomicTask]) -> List[TaskDependency]:
        """识别任务依赖关系"""
        
        dependencies = []
        
        # 基于任务名称和交付物识别依赖
        for i, task in enumerate(atomic_tasks):
            for j, other_task in enumerate(atomic_tasks):
                if i == j:
                    continue
                
                # 检查是否存在依赖关系
                dependency_exists = False
                dependency_type = DependencyType.FINISH_TO_START
                
                # 基于交付物和输入需求匹配
                for deliverable in other_task.deliverables:
                    if deliverable in task.description or any(deliverable in criteria for criteria in task.acceptance_criteria):
                        dependency_exists = True
                        break
                
                # 基于任务名称的语义依赖
                if not dependency_exists:
                    dependency_exists = self._check_semantic_dependency(other_task.task_name, task.task_name)
                
                if dependency_exists:
                    dependency = TaskDependency(
                        predecessor_task_id=other_task.task_id,
                        successor_task_id=task.task_id,
                        dependency_type=dependency_type,
                        lag_time=timedelta(0),
                        constraint_description=f"{other_task.task_name} 完成后开始 {task.task_name}",
                        criticality=0.8
                    )
                    dependencies.append(dependency)
        
        # 更新任务的依赖信息
        for task in atomic_tasks:
            task.dependencies = [dep for dep in dependencies if dep.successor_task_id == task.task_id]
        
        return dependencies
    
    def _check_semantic_dependency(self, predecessor_name: str, successor_name: str) -> bool:
        """检查语义依赖关系"""
        
        # 基于常见的任务顺序模式
        dependency_patterns = [
            ("需求", "设计"),
            ("设计", "开发"),
            ("开发", "测试"),
            ("测试", "部署"),
            ("分析", "设计"),
            ("架构", "实现"),
            ("实现", "集成"),
            ("集成", "验证")
        ]
        
        for pred_keyword, succ_keyword in dependency_patterns:
            if pred_keyword in predecessor_name and succ_keyword in successor_name:
                return True
        
        return False
    
    async def _estimate_task_workloads(self, atomic_tasks: List[AtomicTask], 
                                     collaboration_result: CollaborationDesignResult):
        """估算任务工作量"""
        
        # 基于团队经验调整估算
        team_experience_factor = self._calculate_team_experience_factor(collaboration_result)
        
        for task in atomic_tasks:
            # 应用团队经验因子
            original_estimate = task.workload_estimate.expected_hours
            adjusted_estimate = original_estimate * team_experience_factor
            
            # 更新工作量估算
            task.workload_estimate.expected_hours = adjusted_estimate
            task.workload_estimate.realistic_hours = adjusted_estimate
            task.workload_estimate.optimistic_hours = adjusted_estimate * 0.7
            task.workload_estimate.pessimistic_hours = adjusted_estimate * 1.5
            
            # 更新持续时间
            task.duration = timedelta(hours=adjusted_estimate)
            
            # 调整置信度
            if team_experience_factor < 1.0:
                task.workload_estimate.confidence_level = min(0.9, task.workload_estimate.confidence_level + 0.1)
            else:
                task.workload_estimate.confidence_level = max(0.6, task.workload_estimate.confidence_level - 0.1)
    
    def _calculate_team_experience_factor(self, collaboration_result: CollaborationDesignResult) -> float:
        """计算团队经验因子"""
        
        team_size = collaboration_result.collaboration_design.team_dynamics.team_size
        
        # 基于团队规模的经验因子
        if team_size <= 3:
            return 0.9  # 小团队效率较高
        elif team_size <= 6:
            return 1.0  # 标准团队
        elif team_size <= 10:
            return 1.1  # 大团队协调开销
        else:
            return 1.2  # 超大团队效率降低
    
    async def _analyze_skill_resource_requirements(self, atomic_tasks: List[AtomicTask], 
                                                 collaboration_result: CollaborationDesignResult):
        """分析技能和资源需求"""
        
        # 基于团队组成优化技能匹配
        team_composition = collaboration_result.collaboration_design.team_composition
        available_skills = set()
        
        for member in team_composition:
            available_skills.update(member.skills)
        
        # 检查技能覆盖度并调整需求
        for task in atomic_tasks:
            for skill_req in task.skill_requirements:
                if skill_req.skill_name in available_skills:
                    skill_req.importance = min(1.0, skill_req.importance + 0.1)
                else:
                    # 寻找替代技能
                    for alt_skill in skill_req.alternatives:
                        if alt_skill in available_skills:
                            skill_req.alternatives = [alt_skill] + skill_req.alternatives
                            break
    
    async def _assess_task_risks(self, atomic_tasks: List[AtomicTask]):
        """评估任务风险"""
        
        for task in atomic_tasks:
            risks = []
            
            # 基于复杂度的风险
            if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
                complexity_risk = TaskRisk(
                    risk_id=f"RISK-{task.task_id}-COMPLEXITY",
                    risk_description="任务复杂度高，可能导致延期或质量问题",
                    probability=0.3,
                    impact=0.7,
                    risk_score=0.21,
                    mitigation_strategies=["增加评审环节", "分阶段交付", "增加测试"]
                )
                risks.append(complexity_risk)
            
            # 基于技能需求的风险
            high_skill_reqs = [req for req in task.skill_requirements if req.importance > 0.8]
            if len(high_skill_reqs) > 2:
                skill_risk = TaskRisk(
                    risk_id=f"RISK-{task.task_id}-SKILL",
                    risk_description="技能需求较高，可能存在人员匹配困难",
                    probability=0.2,
                    impact=0.6,
                    risk_score=0.12,
                    mitigation_strategies=["提前安排技能培训", "寻找外部支持", "调整任务分配"]
                )
                risks.append(skill_risk)
            
            # 基于依赖关系的风险
            if len(task.dependencies) > 3:
                dependency_risk = TaskRisk(
                    risk_id=f"RISK-{task.task_id}-DEPENDENCY",
                    risk_description="依赖关系复杂，可能受前置任务影响",
                    probability=0.25,
                    impact=0.5,
                    risk_score=0.125,
                    mitigation_strategies=["优化依赖关系", "准备备选方案", "加强沟通协调"]
                )
                risks.append(dependency_risk)
            
            task.risks = risks
    
    def _build_task_hierarchy(self, atomic_tasks: List[AtomicTask]) -> TaskHierarchy:
        """构建任务层次结构"""
        
        # 简化的层次结构构建（基于任务ID前缀）
        task_levels = {}
        parent_child_mapping = {}
        leaf_tasks = set()
        
        # 假设所有原子任务都在同一层
        task_levels[1] = [task.task_id for task in atomic_tasks]
        leaf_tasks = set(task.task_id for task in atomic_tasks)
        
        # 根任务（虚拟）
        root_task_id = "ROOT-TASK"
        task_levels[0] = [root_task_id]
        parent_child_mapping[root_task_id] = task_levels[1]
        
        return TaskHierarchy(
            root_task_id=root_task_id,
            task_levels=task_levels,
            parent_child_mapping=parent_child_mapping,
            leaf_tasks=leaf_tasks,
            critical_path=[],  # 稍后计算
            max_depth=1
        )
    
    def _calculate_critical_path(self, task_hierarchy: TaskHierarchy, 
                                atomic_tasks: List[AtomicTask], 
                                task_dependencies: List[TaskDependency]):
        """计算关键路径"""
        
        # 简化的关键路径计算
        task_durations = {task.task_id: task.duration for task in atomic_tasks}
        
        # 基于依赖关系构建图
        graph = {}
        for task in atomic_tasks:
            graph[task.task_id] = []
        
        for dep in task_dependencies:
            if dep.predecessor_task_id in graph:
                graph[dep.predecessor_task_id].append(dep.successor_task_id)
        
        # 找到最长路径作为关键路径
        def find_longest_path(node, visited, path, path_duration):
            if node in visited:
                return path, path_duration
            
            visited.add(node)
            longest_path = path + [node]
            longest_duration = path_duration + task_durations.get(node, timedelta(0)).total_seconds()
            
            for neighbor in graph.get(node, []):
                neighbor_path, neighbor_duration = find_longest_path(neighbor, visited.copy(), path + [node], path_duration + task_durations.get(node, timedelta(0)).total_seconds())
                if neighbor_duration > longest_duration:
                    longest_path = neighbor_path
                    longest_duration = neighbor_duration
            
            return longest_path, longest_duration
        
        # 从所有起始节点开始寻找最长路径
        start_nodes = [task.task_id for task in atomic_tasks if not task.dependencies]
        
        critical_path = []
        max_duration = 0
        
        for start_node in start_nodes:
            path, duration = find_longest_path(start_node, set(), [], 0)
            if duration > max_duration:
                critical_path = path
                max_duration = duration
        
        task_hierarchy.critical_path = critical_path
    
    def _assess_decomposition_quality(self, atomic_tasks: List[AtomicTask], 
                                    task_dependencies: List[TaskDependency]) -> DecompositionMetrics:
        """评估分解质量"""
        
        # 分解准确率评估
        decomposition_accuracy = 0.0
        properly_decomposed = sum(1 for task in atomic_tasks if not task.is_further_decomposable)
        decomposition_accuracy = properly_decomposed / len(atomic_tasks) if atomic_tasks else 0
        
        # 依赖关系完整性评估
        dependency_completeness = 0.0
        expected_dependencies = len(atomic_tasks) * 0.3  # 期望30%的任务有依赖
        actual_dependencies = len(task_dependencies)
        dependency_completeness = min(actual_dependencies / expected_dependencies, 1.0) if expected_dependencies > 0 else 1.0
        
        # 工作量估算误差评估（模拟）
        workload_estimation_error = 0.12  # 假设12%的误差
        
        # 覆盖完整性评估
        coverage_completeness = 0.95  # 假设95%的覆盖完整性
        
        # 粒度适当性评估
        appropriate_granularity = sum(1 for task in atomic_tasks 
                                    if task.complexity in [TaskComplexity.SIMPLE, TaskComplexity.MODERATE])
        granularity_appropriateness = appropriate_granularity / len(atomic_tasks) if atomic_tasks else 0
        
        # 整体质量
        overall_quality = (decomposition_accuracy + dependency_completeness + 
                          (1 - workload_estimation_error) + coverage_completeness + 
                          granularity_appropriateness) / 5
        
        return DecompositionMetrics(
            decomposition_accuracy=decomposition_accuracy,
            dependency_completeness=dependency_completeness,
            workload_estimation_error=workload_estimation_error,
            coverage_completeness=coverage_completeness,
            granularity_appropriateness=granularity_appropriateness,
            overall_quality=overall_quality
        )
    
    def _generate_resource_allocation_suggestions(self, atomic_tasks: List[AtomicTask], 
                                                collaboration_result: CollaborationDesignResult) -> Dict[str, Any]:
        """生成资源分配建议"""
        
        team_members = collaboration_result.collaboration_design.team_composition
        
        # 技能匹配建议
        skill_allocation = {}
        for task in atomic_tasks:
            best_match = None
            best_score = 0
            
            for member in team_members:
                match_score = 0
                for skill_req in task.skill_requirements:
                    if skill_req.skill_name in member.skills:
                        match_score += skill_req.importance
                
                if match_score > best_score:
                    best_match = member
                    best_score = match_score
            
            if best_match:
                skill_allocation[task.task_id] = {
                    "推荐成员": best_match.name,
                    "匹配度": best_score,
                    "角色": best_match.role.value
                }
        
        # 工作负载平衡
        member_workload = {}
        for member in team_members:
            member_workload[member.name] = {
                "分配任务数": 0,
                "总工作量": 0,
                "容量利用率": 0
            }
        
        for task_id, allocation in skill_allocation.items():
            member_name = allocation["推荐成员"]
            task = next(t for t in atomic_tasks if t.task_id == task_id)
            
            member_workload[member_name]["分配任务数"] += 1
            member_workload[member_name]["总工作量"] += task.workload_estimate.expected_hours
        
        # 计算容量利用率（假设每人每周40小时）
        for member_name, workload in member_workload.items():
            weekly_capacity = 40
            weeks_needed = workload["总工作量"] / weekly_capacity
            member_workload[member_name]["容量利用率"] = min(weeks_needed, 1.0)
        
        return {
            "技能匹配建议": skill_allocation,
            "工作负载分析": member_workload,
            "负载均衡建议": [
                "监控团队成员工作负载，避免过载",
                "考虑技能培训以提高人员灵活性",
                "建立任务优先级机制"
            ]
        }
    
    def _generate_timeline_estimation(self, atomic_tasks: List[AtomicTask], 
                                    task_dependencies: List[TaskDependency],
                                    task_hierarchy: TaskHierarchy) -> Dict[str, Any]:
        """生成时间线估算"""
        
        # 计算总工作量
        total_effort = sum(task.workload_estimate.expected_hours for task in atomic_tasks)
        
        # 基于关键路径计算项目时长
        critical_path_duration = 0
        for task_id in task_hierarchy.critical_path:
            task = next((t for t in atomic_tasks if t.task_id == task_id), None)
            if task:
                critical_path_duration += task.workload_estimate.expected_hours
        
        # 考虑并行性的时间线
        parallel_efficiency = 0.7  # 假设70%的并行效率
        estimated_calendar_days = critical_path_duration / 8 * parallel_efficiency
        
        return {
            "总工作量": f"{total_effort:.1f}小时",
            "关键路径时长": f"{critical_path_duration:.1f}小时",
            "预估项目周期": f"{estimated_calendar_days:.1f}天",
            "里程碑建议": [
                {"里程碑": "需求分析完成", "时间点": "25%进度"},
                {"里程碑": "设计阶段完成", "时间点": "50%进度"},
                {"里程碑": "开发阶段完成", "时间点": "85%进度"},
                {"里程碑": "测试验收完成", "时间点": "100%进度"}
            ],
            "缓冲时间建议": "建议预留15%的缓冲时间应对风险"
        }
    
    def _assess_overall_risks(self, atomic_tasks: List[AtomicTask], 
                            task_dependencies: List[TaskDependency]) -> Dict[str, Any]:
        """评估整体风险"""
        
        # 收集所有任务风险
        all_risks = []
        for task in atomic_tasks:
            all_risks.extend(task.risks)
        
        # 风险分类统计
        risk_categories = {}
        for risk in all_risks:
            category = risk.risk_id.split('-')[-1]
            if category not in risk_categories:
                risk_categories[category] = []
            risk_categories[category].append(risk)
        
        # 计算整体风险评分
        total_risk_score = sum(risk.risk_score for risk in all_risks)
        average_risk_score = total_risk_score / len(all_risks) if all_risks else 0
        
        # 高风险任务识别
        high_risk_tasks = [
            task.task_id for task in atomic_tasks 
            if any(risk.risk_score > 0.2 for risk in task.risks)
        ]
        
        return {
            "整体风险评分": average_risk_score,
            "风险分类统计": {category: len(risks) for category, risks in risk_categories.items()},
            "高风险任务": high_risk_tasks,
            "风险缓解策略": [
                "建立风险监控机制",
                "制定应急预案",
                "定期风险评估和更新",
                "加强团队沟通和协调"
            ],
            "关键风险因素": [
                "技能匹配度不足",
                "任务依赖关系复杂",
                "工作量估算不准确",
                "外部依赖不可控"
            ]
        }
    
    def _generate_optimization_recommendations(self, atomic_tasks: List[AtomicTask], 
                                             task_dependencies: List[TaskDependency],
                                             metrics: DecompositionMetrics) -> List[str]:
        """生成优化建议"""
        
        recommendations = []
        
        # 基于分解准确率生成建议
        if metrics.decomposition_accuracy < 0.9:
            recommendations.append("建议重新审查任务分解粒度，确保任务原子性")
        
        # 基于依赖完整性生成建议
        if metrics.dependency_completeness < 0.95:
            recommendations.append("建议完善任务依赖关系识别，避免遗漏关键依赖")
        
        # 基于工作量估算误差生成建议
        if metrics.workload_estimation_error > 0.15:
            recommendations.append("建议改进工作量估算方法，收集更多历史数据")
        
        # 基于任务数量生成建议
        if len(atomic_tasks) > 50:
            recommendations.append("任务数量较多，建议考虑进一步整合相关任务")
        elif len(atomic_tasks) < 10:
            recommendations.append("任务数量较少，建议检查是否有遗漏的工作项")
        
        # 基于依赖复杂度生成建议
        avg_dependencies = len(task_dependencies) / len(atomic_tasks) if atomic_tasks else 0
        if avg_dependencies > 2:
            recommendations.append("依赖关系较复杂，建议优化任务顺序以减少依赖")
        
        # 基于风险水平生成建议  
        high_risk_count = sum(1 for task in atomic_tasks if any(risk.risk_score > 0.2 for risk in task.risks))
        if high_risk_count > len(atomic_tasks) * 0.3:
            recommendations.append("高风险任务比例较高，建议制定详细的风险缓解计划")
        
        return recommendations
    
    def _identify_decomposition_issues(self, atomic_tasks: List[AtomicTask], 
                                     metrics: DecompositionMetrics) -> List[Dict[str, Any]]:
        """识别分解问题"""
        
        issues = []
        
        # 分解准确率问题
        if metrics.decomposition_accuracy < 0.9:
            issues.append({
                "type": "low_decomposition_accuracy",
                "severity": "high",
                "description": f"任务分解准确率{metrics.decomposition_accuracy:.1%}，未达到≥90%的目标",
                "affected_tasks": [task.task_id for task in atomic_tasks if task.is_further_decomposable]
            })
        
        # 依赖关系完整性问题
        if metrics.dependency_completeness < 0.95:
            issues.append({
                "type": "incomplete_dependencies",
                "severity": "high",
                "description": f"依赖关系识别完整性{metrics.dependency_completeness:.1%}，未达到≥95%的目标",
                "missing_dependencies": "可能存在未识别的任务依赖关系"
            })
        
        # 工作量估算误差问题
        if metrics.workload_estimation_error > 0.15:
            issues.append({
                "type": "high_estimation_error",
                "severity": "medium",
                "description": f"工作量估算误差{metrics.workload_estimation_error:.1%}，超过≤15%的目标",
                "recommendations": ["收集历史数据", "改进估算方法", "增加评审环节"]
            })
        
        # 任务粒度问题
        if metrics.granularity_appropriateness < 0.8:
            issues.append({
                "type": "inappropriate_granularity", 
                "severity": "medium",
                "description": "任务粒度不合适，部分任务过于复杂或过于细碎",
                "complex_tasks": [task.task_id for task in atomic_tasks 
                                if task.complexity == TaskComplexity.VERY_COMPLEX],
                "trivial_tasks": [task.task_id for task in atomic_tasks 
                                if task.complexity == TaskComplexity.TRIVIAL]
            })
        
        # 技能覆盖问题
        uncovered_skills = []
        for task in atomic_tasks:
            for skill_req in task.skill_requirements:
                if skill_req.importance > 0.8 and not skill_req.alternatives:
                    uncovered_skills.append(skill_req.skill_name)
        
        if uncovered_skills:
            issues.append({
                "type": "skill_coverage_gaps",
                "severity": "medium",
                "description": "存在技能覆盖缺口，可能影响任务执行",
                "uncovered_skills": list(set(uncovered_skills))
            })
        
        return issues

# 工厂函数
def create_task_decomposition_algorithm(claude_service: ClaudeService) -> IntelligentTaskDecompositionAlgorithm:
    """创建任务分解算法"""
    return IntelligentTaskDecompositionAlgorithm(claude_service)

# 使用示例
async def demo_task_decomposition():
    """演示任务分解功能"""
    from ....claude_integration import create_claude_service
    from ..requirements_collection.requirements_understanding import create_requirements_analyzer
    from ..requirements_collection.user_story_generator import create_user_story_generator
    from ..design_collaboration.technical_architecture_designer import create_technical_architecture_designer
    from ..design_collaboration.ux_design_generator import create_ux_design_generator
    from ..design_collaboration.collaboration_workflow_designer import create_collaboration_workflow_designer
    
    claude_service = create_claude_service()
    requirements_analyzer = create_requirements_analyzer(claude_service)
    story_generator = create_user_story_generator(claude_service)
    architecture_designer = create_technical_architecture_designer(claude_service)
    ux_designer = create_ux_design_generator(claude_service)
    collaboration_designer = create_collaboration_workflow_designer(claude_service)
    task_decomposer = create_task_decomposition_algorithm(claude_service)
    
    # 测试需求
    test_requirement = "开发一个智能项目管理系统，支持任务管理、进度跟踪、团队协作、自动化报告生成"
    
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
        print(f"UX设计生成完成")
        
        # 5. 设计协作流程
        collaboration_result = await collaboration_designer.design_collaboration_workflow(ux_result)
        print(f"协作流程设计完成")
        
        # 6. 执行任务分解
        decomposition_result = await task_decomposer.decompose_tasks(collaboration_result)
        
        print(f"\n=== 任务分解结果 ===")
        print(f"原子任务数量: {len(decomposition_result.atomic_tasks)}")
        print(f"任务依赖关系: {len(decomposition_result.task_dependencies)}个")
        print(f"任务层次深度: {decomposition_result.task_hierarchy.max_depth}")
        
        print(f"\n=== 分解质量指标 ===")
        metrics = decomposition_result.decomposition_metrics
        print(f"任务分解准确率: {metrics.decomposition_accuracy:.1%}")
        print(f"依赖关系识别完整性: {metrics.dependency_completeness:.1%}")
        print(f"工作量估算误差: {metrics.workload_estimation_error:.1%}")
        print(f"覆盖完整性: {metrics.coverage_completeness:.1%}")
        print(f"粒度适当性: {metrics.granularity_appropriateness:.1%}")
        print(f"整体质量: {metrics.overall_quality:.1%}")
        
        print(f"\n=== 原子任务概览 ===")
        task_by_type = {}
        task_by_complexity = {}
        
        for task in decomposition_result.atomic_tasks:
            # 按类型分组
            task_type = task.task_type.value
            if task_type not in task_by_type:
                task_by_type[task_type] = []
            task_by_type[task_type].append(task)
            
            # 按复杂度分组
            complexity = task.complexity.value
            task_by_complexity[complexity] = task_by_complexity.get(complexity, 0) + 1
        
        print(f"任务类型分布:")
        for task_type, tasks in task_by_type.items():
            print(f"  - {task_type}: {len(tasks)}个任务")
        
        print(f"复杂度分布:")
        for complexity, count in task_by_complexity.items():
            print(f"  - {complexity}: {count}个任务")
        
        print(f"\n=== 详细任务信息（前5个） ===")
        for task in decomposition_result.atomic_tasks[:5]:
            print(f"\n任务: {task.task_name} ({task.task_id})")
            print(f"  类型: {task.task_type.value}")
            print(f"  复杂度: {task.complexity.value}")
            print(f"  优先级: {task.priority.value}")
            print(f"  预估工作量: {task.workload_estimate.expected_hours:.1f}小时")
            print(f"  持续时间: {task.duration}")
            print(f"  技能需求: {', '.join([skill.skill_name for skill in task.skill_requirements])}")
            print(f"  依赖数量: {len(task.dependencies)}")
            print(f"  风险数量: {len(task.risks)}")
            if task.acceptance_criteria:
                print(f"  验收标准: {', '.join(task.acceptance_criteria[:2])}")
        
        print(f"\n=== 关键路径 ===")
        critical_path = decomposition_result.task_hierarchy.critical_path
        if critical_path:
            print(f"关键路径任务: {len(critical_path)}个")
            critical_tasks = [task for task in decomposition_result.atomic_tasks if task.task_id in critical_path]
            total_critical_hours = sum(task.workload_estimate.expected_hours for task in critical_tasks)
            print(f"关键路径总时长: {total_critical_hours:.1f}小时")
        
        print(f"\n=== 资源分配建议 ===")
        resource_allocation = decomposition_result.resource_allocation_suggestions
        print(f"技能匹配建议: {len(resource_allocation.get('技能匹配建议', {}))}")
        
        workload_analysis = resource_allocation.get('工作负载分析', {})
        if workload_analysis:
            print(f"团队工作负载:")
            for member, workload in list(workload_analysis.items())[:3]:
                print(f"  - {member}: {workload['分配任务数']}个任务, {workload['总工作量']:.1f}小时")
        
        print(f"\n=== 时间线估算 ===")
        timeline = decomposition_result.timeline_estimation
        print(f"总工作量: {timeline.get('总工作量', 'N/A')}")
        print(f"关键路径时长: {timeline.get('关键路径时长', 'N/A')}")
        print(f"预估项目周期: {timeline.get('预估项目周期', 'N/A')}")
        
        print(f"\n=== 风险评估 ===")
        risk_assessment = decomposition_result.risk_assessment
        print(f"整体风险评分: {risk_assessment.get('整体风险评分', 0):.3f}")
        print(f"高风险任务: {len(risk_assessment.get('高风险任务', []))}个")
        
        risk_categories = risk_assessment.get('风险分类统计', {})
        if risk_categories:
            print(f"风险分类:")
            for category, count in risk_categories.items():
                print(f"  - {category}: {count}个风险")
        
        if decomposition_result.optimization_recommendations:
            print(f"\n=== 优化建议 ===")
            for rec in decomposition_result.optimization_recommendations[:3]:
                print(f"- {rec}")
        
        if decomposition_result.issues_found:
            print(f"\n=== 发现的问题 ===")
            for issue in decomposition_result.issues_found:
                print(f"- {issue['type']} ({issue['severity']}): {issue['description']}")
        
        print(f"\n处理时间: {decomposition_result.processing_time:.2f}秒")
        
        # 验证验收标准
        print(f"\n=== 验收标准验证 ===")
        print(f"AC-007-01 (任务分解准确率≥90%): {'✓' if metrics.decomposition_accuracy >= 0.90 else '✗'} {metrics.decomposition_accuracy:.1%}")
        print(f"AC-007-02 (依赖关系识别完整性≥95%): {'✓' if metrics.dependency_completeness >= 0.95 else '✗'} {metrics.dependency_completeness:.1%}")
        print(f"AC-007-03 (工作量估算误差≤15%): {'✓' if metrics.workload_estimation_error <= 0.15 else '✗'} {metrics.workload_estimation_error:.1%}")
        
    except Exception as e:
        print(f"任务分解失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_task_decomposition())
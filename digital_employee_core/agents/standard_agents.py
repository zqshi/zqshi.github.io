"""
7个标准化专业Agent完整实现
7 Standardized Professional Agents Implementation

严格按照enterprise_digital_employee_engine_complete_solution.md文档要求实现：
1. 需求分析师Agent (Requirements Analyst Agent)
2. 产品经理Agent (Product Manager Agent) 
3. 架构师Agent (Architect Agent)
4. UX设计师Agent (UX Designer Agent)
5. 项目经理Agent (Project Manager Agent)
6. 编程Agent (Coding Agent)
7. 质量保证Agent (Quality Assurance Agent)
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

from ..claude_integration import ClaudeService
from ..engines.parallel_execution import AgentExecutor, TaskExecution
from .coding.coding_agent import CodingAgent

logger = logging.getLogger(__name__)

class AgentCapabilityLevel(Enum):
    """Agent能力等级"""
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior" 
    EXPERT = "expert"

class AgentWorkMode(Enum):
    """Agent工作模式"""
    INDIVIDUAL = "individual"  # 独立工作
    COLLABORATIVE = "collaborative"  # 协作工作
    MENTORING = "mentoring"  # 指导模式

@dataclass
class AgentProfile:
    """Agent档案"""
    agent_name: str
    agent_type: str
    capabilities: List[str]
    specializations: List[str]
    capability_level: AgentCapabilityLevel
    work_modes: List[AgentWorkMode]
    max_concurrent_tasks: int
    preferred_task_types: List[str]
    collaboration_preferences: Dict[str, float]  # 与其他Agent的协作偏好
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class StandardAgentExecutor(AgentExecutor, ABC):
    """标准Agent执行器基类"""
    
    def __init__(self, agent_type, claude_service: ClaudeService, agent_profile: AgentProfile):
        super().__init__(agent_type, claude_service)
        self.agent_profile = agent_profile
        self.context_memory: Dict[str, Any] = {}
        self.collaboration_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行专业化任务 - 子类必须实现"""
        pass
    
    async def _execute_task_logic(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行任务逻辑 - 统一框架"""
        try:
            # 1. 任务预处理
            preprocessed_context = await self._preprocess_task(task_execution)
            
            # 2. 执行专业化任务
            specialized_result = await self._execute_specialized_task(task_execution)
            
            # 3. 结果后处理
            final_result = await self._postprocess_result(specialized_result, task_execution)
            
            # 4. 更新性能指标
            self._update_performance_metrics(task_execution, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"{self.agent_type.value} 任务执行失败: {str(e)}")
            raise
    
    async def _preprocess_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """任务预处理"""
        # 分析任务复杂度和所需能力
        task_analysis = {
            "complexity_level": self._assess_task_complexity(task_execution.task),
            "required_capabilities": self._identify_required_capabilities(task_execution.task),
            "estimated_effort": self._estimate_effort(task_execution.task),
            "context_dependencies": self._identify_context_dependencies(task_execution.task)
        }
        
        # 更新上下文记忆
        self.context_memory[task_execution.task_id] = task_analysis
        
        return task_analysis
    
    async def _postprocess_result(self, result: Dict[str, Any], task_execution: TaskExecution) -> Dict[str, Any]:
        """结果后处理"""
        # 添加Agent身份和质量信息
        enhanced_result = {
            "agent_type": self.agent_type.value,
            "agent_profile": {
                "name": self.agent_profile.agent_name,
                "capability_level": self.agent_profile.capability_level.value,
                "specializations": self.agent_profile.specializations
            },
            "task_execution_info": {
                "task_id": task_execution.task_id,
                "task_name": task_execution.task.name,
                "execution_time": (datetime.now() - task_execution.started_at).total_seconds() if task_execution.started_at else 0,
                "quality_score": self._calculate_output_quality(result)
            },
            "primary_result": result,
            "metadata": {
                "confidence_level": self._assess_result_confidence(result),
                "completeness_score": self._assess_result_completeness(result, task_execution.task),
                "recommendations": self._generate_recommendations(result, task_execution.task)
            }
        }
        
        return enhanced_result
    
    def _assess_task_complexity(self, task) -> str:
        """评估任务复杂度"""
        # 基于任务描述长度、关键词等评估
        description_length = len(task.description)
        deliverables_count = len(task.deliverables)
        
        if description_length > 500 or deliverables_count > 5:
            return "high"
        elif description_length > 200 or deliverables_count > 2:
            return "medium"
        else:
            return "low"
    
    def _identify_required_capabilities(self, task) -> List[str]:
        """识别所需能力"""
        # 从任务描述和类型中提取所需能力
        required = []
        task_text = f"{task.name} {task.description}".lower()
        
        for capability in self.agent_profile.capabilities:
            if any(keyword in task_text for keyword in capability.lower().split()):
                required.append(capability)
        
        return required or ["general"]
    
    def _estimate_effort(self, task) -> str:
        """估算工作量"""
        return f"{task.estimated_duration}分钟"
    
    def _identify_context_dependencies(self, task) -> List[str]:
        """识别上下文依赖"""
        return task.dependencies
    
    def _calculate_output_quality(self, result: Dict[str, Any]) -> float:
        """计算输出质量"""
        # 简化的质量评估
        quality_factors = []
        
        # 内容完整性
        if isinstance(result, dict) and len(result) > 0:
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.4)
        
        # 结构规范性
        expected_keys = ["analysis", "recommendations", "deliverables"]
        structure_score = sum(1 for key in expected_keys if key in str(result)) / len(expected_keys)
        quality_factors.append(structure_score)
        
        return sum(quality_factors) / len(quality_factors) if quality_factors else 0.5
    
    def _assess_result_confidence(self, result: Dict[str, Any]) -> float:
        """评估结果置信度"""
        # 基于内容丰富度和结构完整性
        content_richness = min(len(str(result)) / 1000, 1.0)  # 标准化到0-1
        return 0.7 + content_richness * 0.3
    
    def _assess_result_completeness(self, result: Dict[str, Any], task) -> float:
        """评估结果完整性"""
        # 检查是否满足可交付成果要求
        if not task.deliverables:
            return 1.0
        
        result_str = str(result).lower()
        covered_deliverables = sum(
            1 for deliverable in task.deliverables 
            if any(word in result_str for word in deliverable.lower().split())
        )
        
        return covered_deliverables / len(task.deliverables)
    
    def _generate_recommendations(self, result: Dict[str, Any], task) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于Agent专业性生成建议
        if self.agent_profile.capability_level == AgentCapabilityLevel.EXPERT:
            recommendations.append("建议进行深度优化分析")
        
        if task.priority.value in ["critical", "high"]:
            recommendations.append("建议安排质量审核")
        
        return recommendations
    
    def _update_performance_metrics(self, task_execution: TaskExecution, result: Dict[str, Any]):
        """更新性能指标"""
        quality_score = self._calculate_output_quality(result.get("primary_result", {}))
        
        # 更新Agent性能指标
        if "average_quality" not in self.agent_profile.performance_metrics:
            self.agent_profile.performance_metrics["average_quality"] = quality_score
        else:
            current_avg = self.agent_profile.performance_metrics["average_quality"]
            task_count = self.agent_profile.performance_metrics.get("completed_tasks", 0) + 1
            new_avg = (current_avg * (task_count - 1) + quality_score) / task_count
            self.agent_profile.performance_metrics["average_quality"] = new_avg
        
        self.agent_profile.performance_metrics["completed_tasks"] = \
            self.agent_profile.performance_metrics.get("completed_tasks", 0) + 1

class RequirementsAnalystExecutor(StandardAgentExecutor):
    """需求分析师Agent执行器"""
    
    def __init__(self, claude_service: ClaudeService):
        profile = AgentProfile(
            agent_name="需求分析师Agent",
            agent_type="requirements_analyst",
            capabilities=[
                "需求收集", "需求分析", "需求建模", "EARS规范转换", 
                "用户故事编写", "验收标准制定", "需求追踪", "业务流程分析"
            ],
            specializations=[
                "自然语言处理", "业务分析", "用户需求建模", 
                "需求规范化", "需求验证"
            ],
            capability_level=AgentCapabilityLevel.EXPERT,
            work_modes=[AgentWorkMode.INDIVIDUAL, AgentWorkMode.COLLABORATIVE],
            max_concurrent_tasks=3,
            preferred_task_types=["需求分析", "用户故事", "验收标准", "需求建模"],
            collaboration_preferences={
                "product_manager": 0.9,
                "ux_designer": 0.7,
                "quality_assurance": 0.8
            }
        )
        super().__init__("requirements_analyst", claude_service, profile)
    
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行需求分析专业任务"""
        task = task_execution.task
        
        analysis_prompt = f"""
你是一位资深的需求分析师，拥有10年以上的业务分析经验，专精于需求收集、分析和建模。

请分析以下任务需求：

任务信息：
- 任务名称: {task.name}
- 任务描述: {task.description}
- 可交付成果: {task.deliverables}
- 验收标准: {task.acceptance_criteria}

请提供专业的需求分析，包括：

1. **需求理解与分析**
   - 核心需求识别
   - 功能性需求分解
   - 非功能性需求识别
   - 隐含需求挖掘

2. **EARS规范转换**
   - 将需求转换为EARS格式
   - 消除歧义表述
   - 确保需求可测试性

3. **用户故事编写**
   - 遵循INVEST原则
   - 明确用户角色和价值
   - 定义清晰的边界

4. **业务价值分析**
   - 业务价值评估
   - 优先级建议
   - 风险识别

5. **质量保证建议**
   - 需求完整性检查
   - 一致性验证建议
   - 追踪策略

返回JSON格式的详细分析结果。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.2,
            max_tokens=3000
        )
        
        if response.success:
            try:
                analysis_result = json.loads(response.content)
                return {
                    "analysis_type": "requirements_analysis",
                    "analysis": analysis_result,
                    "deliverables": {
                        "requirements_specification": analysis_result.get("需求理解与分析", {}),
                        "ears_requirements": analysis_result.get("EARS规范转换", {}),
                        "user_stories": analysis_result.get("用户故事编写", {}),
                        "business_value": analysis_result.get("业务价值分析", {}),
                        "quality_recommendations": analysis_result.get("质量保证建议", {})
                    },
                    "recommendations": [
                        "建议与产品经理协作验证业务价值",
                        "建议与UX设计师确认用户体验需求",
                        "建议建立需求变更控制流程"
                    ]
                }
            except json.JSONDecodeError:
                return {"analysis": response.content, "format": "text"}
        else:
            raise Exception(f"需求分析失败: {response.error}")

class ProductManagerExecutor(StandardAgentExecutor):
    """产品经理Agent执行器"""
    
    def __init__(self, claude_service: ClaudeService):
        profile = AgentProfile(
            agent_name="产品经理Agent",
            agent_type="product_manager", 
            capabilities=[
                "产品策略", "市场分析", "用户研究", "产品规划",
                "功能定义", "优先级排序", "竞品分析", "商业模式设计"
            ],
            specializations=[
                "产品战略", "用户体验设计", "商业价值评估",
                "市场定位", "产品路线图"
            ],
            capability_level=AgentCapabilityLevel.EXPERT,
            work_modes=[AgentWorkMode.COLLABORATIVE, AgentWorkMode.MENTORING],
            max_concurrent_tasks=2,
            preferred_task_types=["产品设计", "功能规划", "用户研究", "商业分析"],
            collaboration_preferences={
                "requirements_analyst": 0.9,
                "ux_designer": 0.8,
                "project_manager": 0.7
            }
        )
        super().__init__("product_manager", claude_service, profile)
    
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行产品管理专业任务"""
        task = task_execution.task
        
        product_prompt = f"""
你是一位资深的产品经理，拥有10年以上的产品管理经验，专精于产品策略、用户体验和商业价值创造。

请分析以下产品任务：

任务信息：
- 任务名称: {task.name}
- 任务描述: {task.description}
- 可交付成果: {task.deliverables}
- 验收标准: {task.acceptance_criteria}

请提供专业的产品管理分析，包括：

1. **产品策略分析**
   - 产品定位和目标用户
   - 核心价值主张
   - 市场机会分析
   - 竞争优势识别

2. **功能设计与优化**
   - 核心功能定义
   - 用户旅程设计
   - 功能优先级排序
   - MVP范围确定

3. **用户体验设计**
   - 用户需求分析
   - 交互流程设计
   - 用户反馈机制
   - 可用性优化建议

4. **商业价值评估**
   - ROI预期分析
   - 成本效益评估
   - 收入模式设计
   - 成功指标定义

5. **产品路线图**
   - 短期目标(1-3个月)
   - 中期规划(3-12个月) 
   - 长期愿景(1-3年)
   - 里程碑设定

返回JSON格式的详细产品管理方案。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": product_prompt}],
            temperature=0.3,
            max_tokens=3000
        )
        
        if response.success:
            try:
                product_result = json.loads(response.content)
                return {
                    "analysis_type": "product_management",
                    "product_strategy": product_result,
                    "deliverables": {
                        "product_specification": product_result.get("产品策略分析", {}),
                        "feature_design": product_result.get("功能设计与优化", {}),
                        "ux_requirements": product_result.get("用户体验设计", {}),
                        "business_case": product_result.get("商业价值评估", {}),  
                        "product_roadmap": product_result.get("产品路线图", {})
                    },
                    "recommendations": [
                        "建议进行用户访谈验证假设",
                        "建议建立数据驱动的决策机制",
                        "建议定期评估产品市场适应性"
                    ]
                }
            except json.JSONDecodeError:
                return {"analysis": response.content, "format": "text"}
        else:
            raise Exception(f"产品管理分析失败: {response.error}")

class ArchitectExecutor(StandardAgentExecutor):
    """架构师Agent执行器"""
    
    def __init__(self, claude_service: ClaudeService):
        profile = AgentProfile(
            agent_name="架构师Agent",
            agent_type="architect",
            capabilities=[
                "系统架构设计", "技术选型", "性能优化", "可扩展性设计",
                "安全架构", "微服务设计", "数据架构", "集成架构"
            ],
            specializations=[
                "分布式系统", "云原生架构", "高并发设计",
                "数据架构", "安全设计"
            ],
            capability_level=AgentCapabilityLevel.EXPERT,
            work_modes=[AgentWorkMode.INDIVIDUAL, AgentWorkMode.MENTORING],
            max_concurrent_tasks=2,
            preferred_task_types=["架构设计", "技术方案", "性能优化", "系统集成"],
            collaboration_preferences={
                "coding_agent": 0.9,
                "quality_assurance": 0.8,
                "project_manager": 0.6
            }
        )
        super().__init__("architect", claude_service, profile)
    
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行架构设计专业任务"""
        task = task_execution.task
        
        architecture_prompt = f"""
你是一位资深的系统架构师，拥有15年以上的大型系统设计经验，专精于分布式系统、微服务架构和高并发系统设计。

请分析以下架构任务：

任务信息：
- 任务名称: {task.name}
- 任务描述: {task.description}
- 可交付成果: {task.deliverables}
- 验收标准: {task.acceptance_criteria}

请提供专业的系统架构设计，包括：

1. **系统架构设计**
   - 整体架构模式选择
   - 系统分层设计
   - 组件依赖关系
   - 数据流设计

2. **技术栈选型**
   - 编程语言建议
   - 框架和库选择
   - 数据库选型
   - 中间件推荐

3. **非功能性设计**
   - 性能设计(吞吐量、延迟)
   - 可扩展性设计
   - 可用性设计
   - 安全性设计

4. **部署架构**
   - 部署拓扑
   - 容器化方案
   - 负载均衡策略
   - 监控方案

5. **架构决策记录**
   - 关键架构决策
   - 决策理由和权衡
   - 潜在风险识别
   - 演进路径规划

返回JSON格式的详细架构设计方案。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": architecture_prompt}],
            temperature=0.2,
            max_tokens=3500
        )
        
        if response.success:
            try:
                arch_result = json.loads(response.content)
                return {
                    "analysis_type": "architecture_design",
                    "architecture_design": arch_result,
                    "deliverables": {
                        "system_architecture": arch_result.get("系统架构设计", {}),
                        "technology_stack": arch_result.get("技术栈选型", {}),
                        "nonfunctional_design": arch_result.get("非功能性设计", {}),
                        "deployment_architecture": arch_result.get("部署架构", {}),
                        "architecture_decisions": arch_result.get("架构决策记录", {})
                    },
                    "recommendations": [
                        "建议进行架构评审和技术债务评估",
                        "建议建立架构治理和演进机制",
                        "建议制定详细的实施计划"
                    ]
                }
            except json.JSONDecodeError:
                return {"analysis": response.content, "format": "text"}
        else:
            raise Exception(f"架构设计失败: {response.error}")

class UXDesignerExecutor(StandardAgentExecutor):
    """UX设计师Agent执行器"""
    
    def __init__(self, claude_service: ClaudeService):
        profile = AgentProfile(
            agent_name="UX设计师Agent",
            agent_type="ux_designer",
            capabilities=[
                "用户体验设计", "交互设计", "界面设计", "用户研究",
                "原型设计", "可用性测试", "信息架构", "视觉设计"
            ],
            specializations=[
                "用户体验研究", "交互原型设计", "可访问性设计",
                "移动端设计", "设计系统"
            ],
            capability_level=AgentCapabilityLevel.SENIOR,
            work_modes=[AgentWorkMode.COLLABORATIVE, AgentWorkMode.INDIVIDUAL],
            max_concurrent_tasks=3,
            preferred_task_types=["UX设计", "交互设计", "用户研究", "原型设计"],
            collaboration_preferences={
                "product_manager": 0.9,
                "requirements_analyst": 0.7,
                "coding_agent": 0.6
            }
        )
        super().__init__("ux_designer", claude_service, profile)
    
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行UX设计专业任务"""
        task = task_execution.task
        
        ux_prompt = f"""
你是一位资深的UX设计师，拥有8年以上的用户体验设计经验，专精于用户研究、交互设计和可用性优化。

请分析以下UX设计任务：

任务信息：
- 任务名称: {task.name}
- 任务描述: {task.description}
- 可交付成果: {task.deliverables}
- 验收标准: {task.acceptance_criteria}

请提供专业的UX设计方案，包括：

1. **用户研究与分析**
   - 目标用户画像
   - 用户需求分析
   - 使用场景分析
   - 痛点识别

2. **信息架构设计**
   - 信息分类和组织
   - 导航结构设计
   - 内容层级规划
   - 信息标签体系

3. **交互设计方案**
   - 用户流程设计
   - 交互模式选择
   - 操作反馈设计
   - 异常处理设计

4. **界面设计规范**
   - 布局设计原则
   - 视觉层级规划
   - 色彩和字体规范
   - 组件设计标准

5. **可用性优化**
   - 可访问性设计(WCAG 2.1)
   - 多设备适配
   - 性能优化建议
   - 用户测试计划

返回JSON格式的详细UX设计方案。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": ux_prompt}],
            temperature=0.3,
            max_tokens=3000
        )
        
        if response.success:
            try:
                ux_result = json.loads(response.content)
                return {
                    "analysis_type": "ux_design",
                    "ux_design": ux_result,
                    "deliverables": {
                        "user_research": ux_result.get("用户研究与分析", {}),
                        "information_architecture": ux_result.get("信息架构设计", {}),
                        "interaction_design": ux_result.get("交互设计方案", {}),
                        "ui_specifications": ux_result.get("界面设计规范", {}),
                        "usability_guidelines": ux_result.get("可用性优化", {})
                    },
                    "recommendations": [
                        "建议进行用户测试验证设计方案",
                        "建议建立设计系统提高一致性",
                        "建议定期进行可用性评估"
                    ]
                }
            except json.JSONDecodeError:
                return {"analysis": response.content, "format": "text"}
        else:
            raise Exception(f"UX设计失败: {response.error}")

class ProjectManagerExecutor(StandardAgentExecutor):
    """项目经理Agent执行器"""
    
    def __init__(self, claude_service: ClaudeService):
        profile = AgentProfile(
            agent_name="项目经理Agent",
            agent_type="project_manager",
            capabilities=[
                "项目规划", "进度管理", "资源协调", "风险管理",
                "团队协作", "质量管理", "沟通协调", "变更管理"
            ],
            specializations=[
                "敏捷项目管理", "项目治理", "团队管理",
                "干系人管理", "项目交付"
            ],
            capability_level=AgentCapabilityLevel.SENIOR,
            work_modes=[AgentWorkMode.COLLABORATIVE, AgentWorkMode.MENTORING],
            max_concurrent_tasks=5,
            preferred_task_types=["项目规划", "进度管理", "资源协调", "风险控制"],
            collaboration_preferences={
                "requirements_analyst": 0.8,
                "architect": 0.7,
                "quality_assurance": 0.9
            }
        )
        super().__init__("project_manager", claude_service, profile)
    
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行项目管理专业任务"""
        task = task_execution.task
        
        pm_prompt = f"""
你是一位资深的项目经理，拥有PMP认证和12年以上的项目管理经验，专精于敏捷项目管理和复杂项目交付。

请分析以下项目管理任务：

任务信息：
- 任务名称: {task.name}
- 任务描述: {task.description}
- 可交付成果: {task.deliverables}
- 验收标准: {task.acceptance_criteria}

请提供专业的项目管理方案，包括：

1. **项目规划与控制**
   - WBS工作分解结构
   - 时间进度计划
   - 关键路径分析
   - 里程碑设定

2. **资源管理**
   - 人力资源规划
   - 技能匹配分析
   - 负载均衡策略
   - 外部资源需求

3. **风险管理**
   - 风险识别和评估
   - 风险应对策略
   - 风险监控计划
   - 应急预案

4. **质量管理**
   - 质量标准定义
   - 质量保证措施
   - 质量控制检查点
   - 持续改进机制

5. **沟通协调**
   - 干系人管理
   - 沟通计划
   - 会议安排
   - 报告机制

返回JSON格式的详细项目管理方案。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": pm_prompt}],
            temperature=0.2,
            max_tokens=3000
        )
        
        if response.success:
            try:
                pm_result = json.loads(response.content)
                return {
                    "analysis_type": "project_management",
                    "project_management": pm_result,
                    "deliverables": {
                        "project_plan": pm_result.get("项目规划与控制", {}),
                        "resource_management": pm_result.get("资源管理", {}),
                        "risk_management": pm_result.get("风险管理", {}),
                        "quality_management": pm_result.get("质量管理", {}),
                        "communication_plan": pm_result.get("沟通协调", {})
                    },
                    "recommendations": [
                        "建议建立项目仪表板进行实时监控",
                        "建议定期举行项目回顾会议",
                        "建议建立项目知识库"
                    ]
                }
            except json.JSONDecodeError:
                return {"analysis": response.content, "format": "text"}
        else:
            raise Exception(f"项目管理分析失败: {response.error}")

class CodingAgentExecutor(StandardAgentExecutor):
    """编程Agent执行器 - 集成现有CodingAgent"""
    
    def __init__(self, claude_service: ClaudeService):
        profile = AgentProfile(
            agent_name="编程Agent",
            agent_type="coding_agent",
            capabilities=[
                "代码生成", "算法实现", "数据结构设计", "API开发",
                "数据库设计", "测试编写", "代码优化", "技术文档"
            ],
            specializations=[
                "全栈开发", "微服务开发", "数据库设计",
                "API设计", "自动化测试"
            ],
            capability_level=AgentCapabilityLevel.EXPERT,
            work_modes=[AgentWorkMode.INDIVIDUAL, AgentWorkMode.COLLABORATIVE],
            max_concurrent_tasks=2,
            preferred_task_types=["代码生成", "算法实现", "系统开发", "API设计"],
            collaboration_preferences={
                "architect": 0.9,
                "quality_assurance": 0.8,
                "requirements_analyst": 0.6
            }
        )
        super().__init__("coding_agent", claude_service, profile)
        # 集成现有的编程Agent
        self.coding_agent = CodingAgent(claude_service)
    
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行编程专业任务"""
        task = task_execution.task
        
        # 使用现有CodingAgent的能力
        try:
            # 调用现有编程Agent
            coding_result = await self.coding_agent.generate_code({
                "task_name": task.name,
                "description": task.description,
                "requirements": task.acceptance_criteria,
                "deliverables": task.deliverables
            })
            
            return {
                "analysis_type": "code_generation",
                "coding_result": coding_result,
                "deliverables": {
                    "source_code": coding_result.get("code", ""),
                    "unit_tests": coding_result.get("tests", ""),
                    "documentation": coding_result.get("documentation", ""),
                    "api_specification": coding_result.get("api_spec", {}),
                    "deployment_guide": coding_result.get("deployment", "")
                },
                "recommendations": [
                    "建议进行代码审查",
                    "建议完善单元测试覆盖率",
                    "建议进行性能测试"
                ]
            }
            
        except Exception as e:
            # 降级到基本代码生成
            logger.warning(f"CodingAgent调用失败，使用基本代码生成: {str(e)}")
            
            basic_prompt = f"""
你是一位资深的软件工程师，拥有10年以上的编程经验，精通多种编程语言和开发框架。

请为以下任务生成代码：

任务信息：
- 任务名称: {task.name}
- 任务描述: {task.description}
- 验收标准: {task.acceptance_criteria}

请提供：
1. 完整的代码实现
2. 单元测试代码
3. API文档
4. 部署说明

返回JSON格式的代码方案。
"""
            
            response = await self.claude.chat_completion(
                messages=[{"role": "user", "content": basic_prompt}],
                temperature=0.1,
                max_tokens=4000
            )
            
            if response.success:
                try:
                    code_result = json.loads(response.content)
                    return {
                        "analysis_type": "code_generation",
                        "coding_result": code_result,
                        "deliverables": {
                            "source_code": code_result.get("代码实现", ""),
                            "unit_tests": code_result.get("单元测试", ""),
                            "documentation": code_result.get("API文档", ""),
                            "deployment_guide": code_result.get("部署说明", "")
                        }
                    }
                except json.JSONDecodeError:
                    return {"coding_result": response.content, "format": "text"}
            else:
                raise Exception(f"代码生成失败: {response.error}")

class QualityAssuranceExecutor(StandardAgentExecutor):
    """质量保证Agent执行器"""
    
    def __init__(self, claude_service: ClaudeService):
        profile = AgentProfile(
            agent_name="质量保证Agent",
            agent_type="quality_assurance",
            capabilities=[
                "测试策略设计", "测试用例编写", "缺陷管理", "质量评估",
                "自动化测试", "性能测试", "安全测试", "质量度量"
            ],
            specializations=[
                "测试自动化", "性能测试", "安全测试",
                "质量管理", "测试策略"
            ],
            capability_level=AgentCapabilityLevel.SENIOR,
            work_modes=[AgentWorkMode.INDIVIDUAL, AgentWorkMode.COLLABORATIVE],
            max_concurrent_tasks=4,
            preferred_task_types=["质量评估", "测试设计", "缺陷分析", "质量保证"],
            collaboration_preferences={
                "coding_agent": 0.9,
                "requirements_analyst": 0.8,
                "project_manager": 0.7
            }
        )
        super().__init__("quality_assurance", claude_service, profile)
    
    async def _execute_specialized_task(self, task_execution: TaskExecution) -> Dict[str, Any]:
        """执行质量保证专业任务"""
        task = task_execution.task
        
        qa_prompt = f"""
你是一位资深的质量保证工程师，拥有10年以上的软件测试和质量管理经验，精通各种测试方法和质量保证体系。

请分析以下质量保证任务：

任务信息：
- 任务名称: {task.name}
- 任务描述: {task.description}
- 可交付成果: {task.deliverables}
- 验收标准: {task.acceptance_criteria}

请提供专业的质量保证方案，包括：

1. **测试策略设计**
   - 测试目标和范围
   - 测试方法选择
   - 测试环境规划
   - 测试数据准备

2. **测试用例设计**
   - 功能测试用例
   - 边界值测试
   - 异常处理测试
   - 性能测试场景

3. **质量评估框架**
   - 质量度量指标
   - 验收标准检查
   - 缺陷严重性分级
   - 质量门禁设置

4. **自动化测试**
   - 自动化测试策略
   - 测试工具选择
   - 持续集成集成
   - 测试报告机制

5. **质量改进建议**
   - 质量风险识别
   - 改进措施建议
   - 最佳实践推荐
   - 团队能力提升

返回JSON格式的详细质量保证方案。
"""
        
        response = await self.claude.chat_completion(
            messages=[{"role": "user", "content": qa_prompt}],
            temperature=0.2,
            max_tokens=3000
        )
        
        if response.success:
            try:
                qa_result = json.loads(response.content)
                return {
                    "analysis_type": "quality_assurance",
                    "qa_analysis": qa_result,
                    "deliverables": {
                        "test_strategy": qa_result.get("测试策略设计", {}),
                        "test_cases": qa_result.get("测试用例设计", {}),
                        "quality_framework": qa_result.get("质量评估框架", {}),
                        "automation_plan": qa_result.get("自动化测试", {}),
                        "improvement_plan": qa_result.get("质量改进建议", {})
                    },
                    "recommendations": [
                        "建议建立持续测试流水线",
                        "建议实施质量度量和监控",
                        "建议定期进行质量回顾"
                    ]
                }
            except json.JSONDecodeError:
                return {"analysis": response.content, "format": "text"}
        else:
            raise Exception(f"质量保证分析失败: {response.error}")

# Agent注册表
STANDARD_AGENTS = {
    "requirements_analyst": RequirementsAnalystExecutor,
    "product_manager": ProductManagerExecutor,
    "architect": ArchitectExecutor,
    "ux_designer": UXDesignerExecutor,
    "project_manager": ProjectManagerExecutor,
    "coding_agent": CodingAgentExecutor,
    "quality_assurance": QualityAssuranceExecutor
}

def create_standard_agent(agent_type: str, claude_service: ClaudeService) -> StandardAgentExecutor:
    """创建标准Agent"""
    agent_class = STANDARD_AGENTS.get(agent_type)
    if not agent_class:
        raise ValueError(f"未知的Agent类型: {agent_type}")
    
    return agent_class(claude_service)

def get_available_agent_types() -> List[str]:
    """获取可用的Agent类型"""
    return list(STANDARD_AGENTS.keys())

def get_agent_capabilities(agent_type: str) -> Dict[str, Any]:
    """获取Agent能力信息"""
    if agent_type not in STANDARD_AGENTS:
        return {}
    
    # 临时创建Agent以获取能力信息
    class MockClaudeService:
        pass
    
    try:
        agent = STANDARD_AGENTS[agent_type](MockClaudeService())
        return {
            "agent_name": agent.agent_profile.agent_name,
            "capabilities": agent.agent_profile.capabilities,
            "specializations": agent.agent_profile.specializations,
            "capability_level": agent.agent_profile.capability_level.value,
            "max_concurrent_tasks": agent.agent_profile.max_concurrent_tasks,
            "preferred_task_types": agent.agent_profile.preferred_task_types,
            "collaboration_preferences": agent.agent_profile.collaboration_preferences
        }
    except Exception:
        return {"error": "无法获取Agent能力信息"}

# 使用示例
async def demo_standard_agents():
    """演示标准Agent"""
    from ..claude_integration import create_claude_service
    from ..engines.task_orchestrator import Task, TaskType, TaskPriority
    
    claude_service = create_claude_service()
    
    # 创建测试任务
    test_task = Task(
        task_id="test_001",
        name="用户管理系统需求分析",
        description="分析用户管理系统的需求，包括用户注册、登录、权限管理等功能",
        task_type=TaskType.REQUIREMENT_ANALYSIS,
        priority=TaskPriority.HIGH,
        estimated_duration=120,
        deliverables=["需求规格说明书", "用户故事", "验收标准"],
        acceptance_criteria=["需求完整性≥90%", "用户故事符合INVEST原则", "验收标准可测试"]
    )
    
    # 测试各个Agent
    agent_types = ["requirements_analyst", "product_manager", "architect"]
    
    for agent_type in agent_types:
        print(f"\n=== 测试 {agent_type} ===")
        
        try:
            agent = create_standard_agent(agent_type, claude_service)
            
            # 显示Agent能力
            print(f"Agent: {agent.agent_profile.agent_name}")
            print(f"能力等级: {agent.agent_profile.capability_level.value}")
            print(f"专业领域: {', '.join(agent.agent_profile.specializations)}")
            
            # 执行任务（模拟）
            task_execution = TaskExecution(
                task_id=test_task.task_id,
                task=test_task,
                agent_type=agent.agent_type
            )
            task_execution.started_at = datetime.now()
            
            # result = await agent.execute_task(task_execution)
            # print(f"执行结果类型: {result.get('analysis_type', 'unknown')}")
            print("Agent创建成功")
            
        except Exception as e:
            print(f"Agent测试失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(demo_standard_agents())
"""
AI增强的统一数字员工Agent
基于现有UnifiedAgent，集成真正的AI能力
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, List
from ..core.agent_base import BaseAgent, TaskRequest, TaskResponse, TaskType
from ..core.ai_service import generate_ai_response, AIResponse

logger = logging.getLogger(__name__)


class AIEnhancedUnifiedEmployee(BaseAgent):
    """
    AI增强的统一数字员工
    
    核心改进：
    1. 用AI替代硬编码逻辑
    2. 保持现有接口兼容性
    3. 增加智能上下文处理
    4. 支持结果缓存优化
    """
    
    def __init__(self):
        super().__init__("AIEnhancedUnifiedEmployee")
        self.supported_tasks = {
            TaskType.REQUIREMENT_ANALYSIS,
            TaskType.SOLUTION_DESIGN,
            TaskType.CODE_GENERATION,
            TaskType.PROJECT_PLANNING,
            TaskType.GENERAL_INQUIRY
        }
        # 简单的结果缓存
        self.result_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_max_size = 100
    
    def can_handle(self, task_type: TaskType) -> bool:
        """可以处理所有类型的任务"""
        return task_type in self.supported_tasks
    
    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """处理任务的核心方法"""
        start_time = time.time()
        
        try:
            # 检查缓存
            cache_key = f"{request.task_type.value}:{hash(request.user_input)}"
            if cache_key in self.result_cache:
                logger.info(f"使用缓存结果: {request.task_id}")
                cached_result = self.result_cache[cache_key]
                processing_time = time.time() - start_time
                
                return TaskResponse(
                    task_id=request.task_id,
                    success=True,
                    result=cached_result,
                    confidence_score=cached_result.get('confidence_score', 0.8),
                    processing_time=processing_time
                )
            
            # 根据任务类型分发处理
            if request.task_type == TaskType.REQUIREMENT_ANALYSIS:
                result = await self._analyze_requirement_ai(request.user_input)
            elif request.task_type == TaskType.SOLUTION_DESIGN:
                result = await self._design_solution_ai(request.user_input, request.context)
            elif request.task_type == TaskType.CODE_GENERATION:
                result = await self._generate_code_ai(request.user_input, request.context)
            elif request.task_type == TaskType.PROJECT_PLANNING:
                result = await self._plan_project_ai(request.user_input, request.context)
            else:
                result = await self._handle_general_inquiry_ai(request.user_input)
            
            processing_time = time.time() - start_time
            
            # 缓存结果
            self._cache_result(cache_key, result)
            
            # 更新统计信息
            self.update_statistics(True)
            
            return TaskResponse(
                task_id=request.task_id,
                success=True,
                result=result,
                confidence_score=result.get('confidence_score', 0.8),
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.update_statistics(False)
            
            logger.error(f"任务处理失败: {request.task_id}, 错误: {str(e)}")
            
            return TaskResponse(
                task_id=request.task_id,
                success=False,
                result={},
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _analyze_requirement_ai(self, user_input: str) -> Dict[str, Any]:
        """AI驱动的需求分析"""
        
        system_prompt = """
        你是一个专业的软件需求分析师。请分析用户输入的需求，提供结构化的分析结果。

        请按照以下JSON格式返回分析结果：
        {
            "functional_requirements": ["功能需求1", "功能需求2", ...],
            "non_functional_requirements": ["非功能需求1", "非功能需求2", ...],
            "clarification_questions": ["澄清问题1", "澄清问题2", ...],
            "ears_format": ["EARS格式需求1", "EARS格式需求2", ...],
            "stakeholders": ["相关方1", "相关方2", ...],
            "business_value": "业务价值描述",
            "risk_assessment": ["风险1", "风险2", ...],
            "confidence_score": 0.85
        }

        注意：
        1. 功能需求应该具体明确，避免模糊表述
        2. 非功能需求包括性能、安全、可用性等
        3. EARS格式：The system shall [requirement]
        4. 澄清问题要针对需求中的模糊点
        5. 置信度应该基于需求的明确程度
        """
        
        try:
            ai_response = await generate_ai_response(
                system_prompt=system_prompt,
                user_input=f"请分析以下需求：\n\n{user_input}",
                temperature=0.3,  # 需求分析需要相对严谨
                max_tokens=2000
            )
            
            if ai_response.error:
                # AI服务失败，使用简化逻辑
                return self._fallback_requirement_analysis(user_input)
            
            # 尝试解析JSON响应
            try:
                result = json.loads(ai_response.content)
                result['ai_enhanced'] = True
                result['model_used'] = ai_response.model
                result['tokens_used'] = ai_response.usage_tokens
                return result
            except json.JSONDecodeError:
                # JSON解析失败，提取关键信息
                return self._parse_requirement_text(ai_response.content, ai_response)
                
        except Exception as e:
            logger.error(f"AI需求分析失败: {str(e)}")
            return self._fallback_requirement_analysis(user_input)
    
    async def _design_solution_ai(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI驱动的方案设计"""
        
        context_info = ""
        if context and context.get("requirements"):
            context_info = f"\\n\\n已知需求信息：\\n{json.dumps(context['requirements'], indent=2, ensure_ascii=False)}"
        
        system_prompt = f"""
        你是一个资深的技术架构师。基于用户的需求描述，设计合适的技术方案。

        请按照以下JSON格式返回方案设计：
        {{
            "tech_stack": {{
                "backend": "后端技术选择及理由",
                "frontend": "前端技术选择及理由", 
                "database": "数据库选择及理由",
                "cache": "缓存方案",
                "deployment": "部署方案"
            }},
            "architecture_components": ["组件1", "组件2", ...],
            "system_architecture": "整体架构描述",
            "data_flow": "数据流设计",
            "api_design": "API设计要点",
            "security_considerations": ["安全考虑1", "安全考虑2", ...],
            "scalability_strategy": "扩展策略",
            "deployment_plan": {{
                "development": "开发环境部署",
                "staging": "测试环境部署",
                "production": "生产环境部署"
            }},
            "estimated_timeline": "预估开发周期",
            "team_requirements": "团队配置建议",
            "risks_and_mitigations": ["风险及缓解策略1", "风险及缓解策略2", ...],
            "confidence_score": 0.82
        }}

        考虑因素：
        1. 技术栈的成熟度和社区支持
        2. 团队技术能力匹配
        3. 项目规模和复杂度
        4. 性能和扩展性要求
        5. 开发和维护成本
        """
        
        try:
            ai_response = await generate_ai_response(
                system_prompt=system_prompt,
                user_input=f"请为以下需求设计技术方案：\\n\\n{user_input}{context_info}",
                temperature=0.4,
                max_tokens=2500
            )
            
            if ai_response.error:
                return self._fallback_solution_design(user_input, context)
            
            try:
                result = json.loads(ai_response.content)
                result['ai_enhanced'] = True
                result['model_used'] = ai_response.model
                result['tokens_used'] = ai_response.usage_tokens
                return result
            except json.JSONDecodeError:
                return self._parse_solution_text(ai_response.content, ai_response)
                
        except Exception as e:
            logger.error(f"AI方案设计失败: {str(e)}")
            return self._fallback_solution_design(user_input, context)
    
    async def _generate_code_ai(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI驱动的代码生成"""
        
        context_info = ""
        if context:
            if context.get("tech_stack"):
                context_info += f"\\n\\n技术栈：\\n{json.dumps(context['tech_stack'], indent=2, ensure_ascii=False)}"
            if context.get("requirements"):
                context_info += f"\\n\\n需求信息：\\n{json.dumps(context['requirements'], indent=2, ensure_ascii=False)}"
        
        system_prompt = f"""
        你是一个资深的软件开发工程师。基于用户需求和上下文信息，生成高质量的代码。

        请按照以下JSON格式返回代码生成结果：
        {{
            "code_examples": {{
                "main_code": "主要代码实现",
                "models": "数据模型代码（如果需要）",
                "api": "API接口代码（如果需要）",
                "tests": "测试代码示例"
            }},
            "file_structure": ["文件/目录结构数组"],
            "dependencies": ["依赖包列表"],
            "configuration": "配置文件示例",
            "database_schema": "数据库表结构（如果需要）",
            "deployment_config": "部署配置示例",
            "next_steps": ["后续开发步骤1", "后续开发步骤2", ...],
            "best_practices": ["最佳实践建议1", "最佳实践建议2", ...],
            "potential_issues": ["潜在问题1", "潜在问题2", ...],
            "confidence_score": 0.78
        }}

        代码要求：
        1. 代码要完整可运行
        2. 包含必要的错误处理
        3. 添加适当的注释
        4. 遵循代码规范
        5. 考虑安全性和性能
        """
        
        try:
            ai_response = await generate_ai_response(
                system_prompt=system_prompt,
                user_input=f"请为以下需求生成代码：\\n\\n{user_input}{context_info}",
                temperature=0.2,  # 代码生成需要更精确
                max_tokens=3000
            )
            
            if ai_response.error:
                return self._fallback_code_generation(user_input, context)
            
            try:
                result = json.loads(ai_response.content)
                result['ai_enhanced'] = True
                result['model_used'] = ai_response.model
                result['tokens_used'] = ai_response.usage_tokens
                return result
            except json.JSONDecodeError:
                return self._parse_code_text(ai_response.content, ai_response)
                
        except Exception as e:
            logger.error(f"AI代码生成失败: {str(e)}")
            return self._fallback_code_generation(user_input, context)
    
    async def _plan_project_ai(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI驱动的项目规划"""
        
        context_info = ""
        if context:
            for key, value in context.items():
                if value:
                    context_info += f"\\n\\n{key}：\\n{json.dumps(value, indent=2, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)}"
        
        system_prompt = f"""
        你是一个经验丰富的项目经理。基于用户需求和技术方案，制定详细的项目实施计划。

        请按照以下JSON格式返回项目规划：
        {{
            "project_phases": [
                {{
                    "name": "阶段名称",
                    "duration": "持续时间",
                    "tasks": ["任务1", "任务2", ...],
                    "deliverables": ["交付物1", "交付物2", ...],
                    "dependencies": ["依赖项1", "依赖项2", ...]
                }}
            ],
            "total_timeline": "总体时间线",
            "critical_path": ["关键路径任务1", "关键路径任务2", ...],
            "team_structure": {{
                "roles": ["角色1", "角色2", ...],
                "team_size": "团队规模",
                "skill_requirements": ["技能要求1", "技能要求2", ...]
            }},
            "resource_requirements": {{
                "human_resources": "人力资源需求",
                "technical_resources": "技术资源需求",
                "budget_estimate": "预算估算"
            }},
            "risks": [
                {{
                    "risk": "风险描述",
                    "impact": "影响级别",
                    "probability": "发生概率",
                    "mitigation": "缓解策略"
                }}
            ],
            "quality_assurance": ["质量保证措施1", "质量保证措施2", ...],
            "success_metrics": ["成功指标1", "成功指标2", ...],
            "communication_plan": "沟通计划",
            "change_management": "变更管理策略",
            "confidence_score": 0.80
        }}

        规划原则：
        1. 阶段划分要合理，便于管理和控制
        2. 时间估算要考虑技术复杂度和团队经验
        3. 风险识别要全面，缓解策略要可行
        4. 质量保证要贯穿整个开发过程
        5. 成功指标要可量化、可验证
        """
        
        try:
            ai_response = await generate_ai_response(
                system_prompt=system_prompt,
                user_input=f"请为以下项目制定实施计划：\\n\\n{user_input}{context_info}",
                temperature=0.3,
                max_tokens=3000
            )
            
            if ai_response.error:
                return self._fallback_project_planning(user_input, context)
            
            try:
                result = json.loads(ai_response.content)
                result['ai_enhanced'] = True
                result['model_used'] = ai_response.model
                result['tokens_used'] = ai_response.usage_tokens
                return result
            except json.JSONDecodeError:
                return self._parse_planning_text(ai_response.content, ai_response)
                
        except Exception as e:
            logger.error(f"AI项目规划失败: {str(e)}")
            return self._fallback_project_planning(user_input, context)
    
    async def _handle_general_inquiry_ai(self, user_input: str) -> Dict[str, Any]:
        """AI驱动的通用询问处理"""
        
        system_prompt = """
        你是一个专业的数字员工助手。用户向你咨询各种问题，请提供有用、准确的回答。

        如果用户的问题涉及：
        - 软件开发相关：提供技术建议和最佳实践
        - 项目管理相关：提供管理方法和工具建议  
        - 业务分析相关：提供分析思路和框架
        - 其他技术问题：基于你的知识提供帮助

        请以友好、专业的方式回答，并在适当时候引导用户使用更专业的功能（需求分析、方案设计等）。

        返回JSON格式：
        {
            "response": "详细回答",
            "suggestions": ["建议1", "建议2", ...],
            "related_services": ["相关服务1", "相关服务2", ...],
            "confidence_score": 0.75
        }
        """
        
        try:
            ai_response = await generate_ai_response(
                system_prompt=system_prompt,
                user_input=user_input,
                temperature=0.6,
                max_tokens=1500
            )
            
            if ai_response.error:
                return self._fallback_general_inquiry(user_input)
            
            try:
                result = json.loads(ai_response.content)
                result['ai_enhanced'] = True
                result['model_used'] = ai_response.model
                result['tokens_used'] = ai_response.usage_tokens
                return result
            except json.JSONDecodeError:
                return {
                    "response": ai_response.content,
                    "suggestions": ["如需更专业的帮助，请使用需求分析或方案设计功能"],
                    "related_services": ["requirement_analysis", "solution_design"],
                    "confidence_score": ai_response.confidence_score,
                    "ai_enhanced": True,
                    "model_used": ai_response.model,
                    "tokens_used": ai_response.usage_tokens
                }
                
        except Exception as e:
            logger.error(f"AI通用询问处理失败: {str(e)}")
            return self._fallback_general_inquiry(user_input)
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """缓存结果"""
        if len(self.result_cache) >= self.cache_max_size:
            # 移除最旧的缓存项（简单LRU）
            oldest_key = next(iter(self.result_cache))
            del self.result_cache[oldest_key]
        
        self.result_cache[cache_key] = result
    
    # 降级方法（当AI服务不可用时）
    def _fallback_requirement_analysis(self, user_input: str) -> Dict[str, Any]:
        """需求分析降级方法"""
        return {
            "functional_requirements": ["基于输入提取的功能需求"],
            "non_functional_requirements": ["基于输入提取的非功能需求"],
            "clarification_questions": ["需要进一步澄清的问题"],
            "ears_format": ["The system shall..."],
            "confidence_score": 0.5,
            "fallback_used": True,
            "note": "AI服务不可用，使用降级处理"
        }
    
    def _fallback_solution_design(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """方案设计降级方法"""
        return {
            "tech_stack": {
                "backend": "Python + FastAPI",
                "frontend": "React + TypeScript",
                "database": "PostgreSQL",
                "cache": "Redis"
            },
            "architecture_components": ["API Gateway", "Business Logic", "Data Access"],
            "confidence_score": 0.5,
            "fallback_used": True,
            "note": "AI服务不可用，使用降级处理"
        }
    
    def _fallback_code_generation(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """代码生成降级方法"""
        return {
            "code_examples": {
                "main_code": "# 基础代码框架\\nclass Example:\\n    pass"
            },
            "file_structure": ["src/", "tests/", "docs/"],
            "confidence_score": 0.3,
            "fallback_used": True,
            "note": "AI服务不可用，使用降级处理"
        }
    
    def _fallback_project_planning(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """项目规划降级方法"""
        return {
            "project_phases": [
                {"name": "需求分析", "duration": "1周", "tasks": ["需求收集", "需求分析"]},
                {"name": "设计开发", "duration": "4周", "tasks": ["设计", "开发", "测试"]},
                {"name": "部署上线", "duration": "1周", "tasks": ["部署", "上线"]}
            ],
            "confidence_score": 0.4,
            "fallback_used": True,
            "note": "AI服务不可用，使用降级处理"
        }
    
    def _fallback_general_inquiry(self, user_input: str) -> Dict[str, Any]:
        """通用询问降级方法"""
        return {
            "response": f"我理解您的询问：{user_input}",
            "suggestions": ["请使用专业功能获得更好的帮助"],
            "confidence_score": 0.3,
            "fallback_used": True,
            "note": "AI服务不可用，使用降级处理"
        }
    
    # 文本解析方法（当JSON解析失败时）
    def _parse_requirement_text(self, content: str, ai_response: AIResponse) -> Dict[str, Any]:
        """解析需求分析文本响应"""
        # 这里可以实现简单的文本解析逻辑
        return {
            "raw_response": content,
            "confidence_score": ai_response.confidence_score,
            "ai_enhanced": True,
            "model_used": ai_response.model,
            "tokens_used": ai_response.usage_tokens,
            "parsing_note": "AI返回了文本格式，已保存原始响应"
        }
    
    def _parse_solution_text(self, content: str, ai_response: AIResponse) -> Dict[str, Any]:
        """解析方案设计文本响应"""
        return {
            "raw_response": content,
            "confidence_score": ai_response.confidence_score,
            "ai_enhanced": True,
            "model_used": ai_response.model,
            "tokens_used": ai_response.usage_tokens,
            "parsing_note": "AI返回了文本格式，已保存原始响应"
        }
    
    def _parse_code_text(self, content: str, ai_response: AIResponse) -> Dict[str, Any]:
        """解析代码生成文本响应"""
        return {
            "code_content": content,
            "confidence_score": ai_response.confidence_score,
            "ai_enhanced": True,
            "model_used": ai_response.model,
            "tokens_used": ai_response.usage_tokens,
            "parsing_note": "AI返回了文本格式，已保存代码内容"
        }
    
    def _parse_planning_text(self, content: str, ai_response: AIResponse) -> Dict[str, Any]:
        """解析项目规划文本响应"""
        return {
            "planning_content": content,
            "confidence_score": ai_response.confidence_score,
            "ai_enhanced": True,
            "model_used": ai_response.model,
            "tokens_used": ai_response.usage_tokens,
            "parsing_note": "AI返回了文本格式，已保存规划内容"
        }
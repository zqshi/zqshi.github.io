"""
统一数字员工Agent
一个Agent处理所有任务，基于实际需求决定是否需要分离
"""

import asyncio
import time
import re
from typing import Dict, Any, List
from ..core.agent_base import BaseAgent, TaskRequest, TaskResponse, TaskType


class UnifiedDigitalEmployee(BaseAgent):
    """
    统一数字员工
    
    这是一个务实的设计：
    1. 先让一个Agent处理所有任务
    2. 基于使用数据决定是否需要分离
    3. 避免过度设计
    """
    
    def __init__(self):
        super().__init__("UnifiedDigitalEmployee")
        self.supported_tasks = {
            TaskType.REQUIREMENT_ANALYSIS,
            TaskType.SOLUTION_DESIGN,
            TaskType.CODE_GENERATION,
            TaskType.PROJECT_PLANNING,
            TaskType.GENERAL_INQUIRY
        }
    
    def can_handle(self, task_type: TaskType) -> bool:
        """可以处理所有类型的任务"""
        return task_type in self.supported_tasks
    
    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """处理任务的核心方法"""
        start_time = time.time()
        
        try:
            # 根据任务类型分发处理
            if request.task_type == TaskType.REQUIREMENT_ANALYSIS:
                result = await self._analyze_requirement(request.user_input)
            elif request.task_type == TaskType.SOLUTION_DESIGN:
                result = await self._design_solution(request.user_input, request.context)
            elif request.task_type == TaskType.CODE_GENERATION:
                result = await self._generate_code(request.user_input, request.context)
            elif request.task_type == TaskType.PROJECT_PLANNING:
                result = await self._plan_project(request.user_input, request.context)
            else:
                result = await self._handle_general_inquiry(request.user_input)
            
            processing_time = time.time() - start_time
            
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
            
            return TaskResponse(
                task_id=request.task_id,
                success=False,
                result={},
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _analyze_requirement(self, user_input: str) -> Dict[str, Any]:
        """需求分析处理逻辑"""
        # 模拟AI处理时间
        await asyncio.sleep(0.1)
        
        # 简单的需求分析逻辑
        functional_requirements = []
        non_functional_requirements = []
        
        # 提取功能性需求
        if "登录" in user_input or "认证" in user_input:
            functional_requirements.append("用户身份认证功能")
        if "数据库" in user_input or "存储" in user_input:
            functional_requirements.append("数据存储功能")
        if "API" in user_input or "接口" in user_input:
            functional_requirements.append("API接口功能")
        
        # 提取非功能性需求
        performance_match = re.search(r'(\d+)(?:个|万)(?:用户|并发)', user_input)
        if performance_match:
            non_functional_requirements.append(f"支持{performance_match.group(1)}并发用户")
        
        # 生成澄清问题
        clarification_questions = [
            "具体的用户角色有哪些？",
            "期望的响应时间是多少？",
            "有哪些安全要求？",
            "需要支持哪些设备和浏览器？"
        ]
        
        # 转换为EARS格式
        ears_format = self._convert_to_ears(functional_requirements + non_functional_requirements)
        
        return {
            "functional_requirements": functional_requirements,
            "non_functional_requirements": non_functional_requirements,
            "clarification_questions": clarification_questions,
            "ears_format": ears_format,
            "confidence_score": 0.85
        }
    
    async def _design_solution(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """方案设计处理逻辑"""
        await asyncio.sleep(0.2)
        
        # 简单的方案设计逻辑
        tech_stack = {
            "backend": "Python + FastAPI",
            "frontend": "React + TypeScript",
            "database": "PostgreSQL",
            "cache": "Redis",
            "deployment": "Docker + Kubernetes"
        }
        
        architecture_components = [
            "API Gateway (Nginx)",
            "Business Logic Layer (FastAPI)",
            "Data Access Layer (SQLAlchemy)",
            "Caching Layer (Redis)",
            "Database (PostgreSQL)",
            "Monitoring (Prometheus + Grafana)"
        ]
        
        deployment_plan = {
            "development": "Docker Compose本地部署",
            "staging": "Kubernetes集群部署",
            "production": "高可用Kubernetes部署"
        }
        
        return {
            "tech_stack": tech_stack,
            "architecture_components": architecture_components,
            "deployment_plan": deployment_plan,
            "estimated_timeline": "4-6周开发周期",
            "confidence_score": 0.82
        }
    
    async def _generate_code(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """代码生成处理逻辑"""
        await asyncio.sleep(0.3)
        
        # 简单的代码生成逻辑
        if "API" in user_input or "接口" in user_input:
            code_example = '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserRequest(BaseModel):
    name: str
    email: str

@app.post("/api/users")
async def create_user(user: UserRequest):
    """创建用户接口"""
    # 这里添加业务逻辑
    return {"message": "用户创建成功", "user": user}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    """获取用户信息接口"""
    # 这里添加查询逻辑
    return {"user_id": user_id, "name": "示例用户"}
'''
        else:
            code_example = '''
# 示例Python类
class ExampleClass:
    def __init__(self, name: str):
        self.name = name
    
    def process(self):
        """处理逻辑"""
        return f"处理完成: {self.name}"
'''
        
        return {
            "code_example": code_example,
            "file_structure": [
                "src/",
                "├── main.py",
                "├── models/",
                "├── api/",
                "├── services/",
                "└── tests/"
            ],
            "next_steps": [
                "完善业务逻辑",
                "添加错误处理",
                "编写单元测试",
                "添加API文档"
            ],
            "confidence_score": 0.78
        }
    
    async def _plan_project(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """项目规划处理逻辑"""
        await asyncio.sleep(0.15)
        
        # 简单的项目规划逻辑
        phases = [
            {
                "name": "需求分析阶段",
                "duration": "1周",
                "tasks": ["需求收集", "需求分析", "验收标准制定"]
            },
            {
                "name": "设计阶段",
                "duration": "1-2周",
                "tasks": ["架构设计", "API设计", "数据库设计", "UI/UX设计"]
            },
            {
                "name": "开发阶段",
                "duration": "3-4周",
                "tasks": ["后端开发", "前端开发", "集成测试", "代码审查"]
            },
            {
                "name": "测试部署阶段",
                "duration": "1周",
                "tasks": ["系统测试", "性能测试", "部署上线", "监控配置"]
            }
        ]
        
        risks = [
            {"risk": "需求变更频繁", "impact": "中", "mitigation": "建立变更控制流程"},
            {"risk": "技术难点", "impact": "高", "mitigation": "提前技术预研"},
            {"risk": "资源不足", "impact": "中", "mitigation": "合理安排开发计划"}
        ]
        
        return {
            "project_phases": phases,
            "total_timeline": "6-8周",
            "team_size": "3-5人",
            "risks": risks,
            "success_metrics": ["功能完整性", "性能指标", "用户满意度"],
            "confidence_score": 0.80
        }
    
    async def _handle_general_inquiry(self, user_input: str) -> Dict[str, Any]:
        """通用询问处理逻辑"""
        await asyncio.sleep(0.05)
        
        return {
            "response": f"我理解您的询问：{user_input}",
            "suggestion": "如果您有具体的需求分析、方案设计、代码生成或项目规划需求，我可以为您提供更专业的帮助。",
            "confidence_score": 0.75
        }
    
    def _convert_to_ears(self, requirements: List[str]) -> List[str]:
        """转换为EARS格式的需求"""
        ears_list = []
        for req in requirements:
            ears_format = f"The system shall {req.lower()}"
            ears_list.append(ears_format)
        return ears_list
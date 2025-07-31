"""
数字员工API接口
务实的REST API设计
"""

import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from ..core.agent_base import TaskRequest, TaskType
from ..agents.unified_agent import UnifiedDigitalEmployee

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="数字员工API",
    description="一个务实的、可执行的智能协作系统",
    version="0.1.0"
)

# 全局Agent实例
digital_employee = UnifiedDigitalEmployee()

# 任务存储（生产环境应使用数据库）
task_storage: Dict[str, Dict[str, Any]] = {}


class TaskSubmissionRequest(BaseModel):
    """任务提交请求"""
    task_type: str
    user_input: str
    context: Optional[Dict[str, Any]] = None
    priority: Optional[int] = 5


class TaskSubmissionResponse(BaseModel):
    """任务提交响应"""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """主页"""
    return """
    <html>
        <head>
            <title>数字员工系统</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .api-link { color: #007bff; text-decoration: none; }
                .api-link:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>数字员工系统 - MVP版本</h1>
                <p>欢迎使用数字员工智能协作系统！</p>
                
                <h2>系统特点</h2>
                <ul>
                    <li>统一智能Agent处理所有任务</li>
                    <li>支持需求分析、方案设计、代码生成、项目规划</li>
                    <li>基于实际使用数据优化系统</li>
                    <li>务实、可执行的设计理念</li>
                </ul>
                
                <h2>API文档</h2>
                <p><a href="/docs" class="api-link">Swagger UI 文档</a></p>
                <p><a href="/redoc" class="api-link">ReDoc 文档</a></p>
                
                <h2>系统状态</h2>
                <p><a href="/system/status" class="api-link">查看系统状态</a></p>
            </div>
        </body>
    </html>
    """


@app.post("/tasks/submit", response_model=TaskSubmissionResponse)
async def submit_task(request: TaskSubmissionRequest, background_tasks: BackgroundTasks):
    """提交任务"""
    try:
        # 验证任务类型
        task_type_mapping = {
            "requirement_analysis": TaskType.REQUIREMENT_ANALYSIS,
            "solution_design": TaskType.SOLUTION_DESIGN,
            "code_generation": TaskType.CODE_GENERATION,
            "project_planning": TaskType.PROJECT_PLANNING,
            "general_inquiry": TaskType.GENERAL_INQUIRY
        }
        
        if request.task_type not in task_type_mapping:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的任务类型: {request.task_type}"
            )
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务请求
        task_request = TaskRequest(
            task_id=task_id,
            task_type=task_type_mapping[request.task_type],
            user_input=request.user_input,
            context=request.context or {},
            priority=request.priority
        )
        
        # 初始化任务状态
        task_storage[task_id] = {
            "status": "processing",
            "created_at": datetime.now(),
            "task_request": task_request
        }
        
        # 后台处理任务
        background_tasks.add_task(process_task_background, task_request)
        
        logger.info(f"任务提交成功: {task_id}, 类型: {request.task_type}")
        
        return TaskSubmissionResponse(
            task_id=task_id,
            status="submitted",
            message="任务已提交，正在处理中"
        )
        
    except Exception as e:
        logger.error(f"任务提交失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")


@app.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task_info = task_storage[task_id]
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task_info["status"],
        result=task_info.get("result"),
        error_message=task_info.get("error_message"),
        processing_time=task_info.get("processing_time"),
        confidence_score=task_info.get("confidence_score")
    )


@app.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    return {
        "system_name": "数字员工系统",
        "version": "0.1.0",
        "status": "running",
        "agent_status": digital_employee.get_status(),
        "total_tasks": len(task_storage),
        "completed_tasks": sum(1 for task in task_storage.values() if task["status"] == "completed"),
        "failed_tasks": sum(1 for task in task_storage.values() if task["status"] == "failed"),
        "uptime": "运行中"
    }


@app.get("/tasks")
async def list_tasks():
    """获取任务列表"""
    tasks = []
    for task_id, task_info in task_storage.items():
        tasks.append({
            "task_id": task_id,
            "status": task_info["status"],
            "created_at": task_info["created_at"],
            "task_type": task_info["task_request"].task_type.value if "task_request" in task_info else "unknown"
        })
    return {"tasks": tasks}


async def process_task_background(task_request: TaskRequest):
    """后台处理任务"""
    try:
        logger.info(f"开始处理任务: {task_request.task_id}")
        
        # 处理任务
        response = await digital_employee.process_task(task_request)
        
        # 更新任务状态
        task_storage[task_request.task_id].update({
            "status": "completed" if response.success else "failed",
            "result": response.result if response.success else None,
            "error_message": response.error_message,
            "processing_time": response.processing_time,
            "confidence_score": response.confidence_score,
            "completed_at": datetime.now()
        })
        
        logger.info(f"任务处理完成: {task_request.task_id}, 成功: {response.success}")
        
    except Exception as e:
        logger.error(f"任务处理异常: {task_request.task_id}, 错误: {str(e)}")
        task_storage[task_request.task_id].update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": datetime.now()
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
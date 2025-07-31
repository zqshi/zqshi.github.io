"""
AI增强版API接口
基于现有API，集成AI能力和配置管理
"""

import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 添加项目根目录到路径
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import config, setup_logging, validate_config
from digital_employee.core.agent_base import TaskRequest, TaskType
from digital_employee.core.ai_service import initialize_ai_services
from digital_employee.agents.unified_agent_ai import AIEnhancedUnifiedEmployee

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动数字员工系统...")
    
    try:
        # 验证配置
        validate_config()
        
        # 初始化AI服务
        ai_config = config.get_ai_config()
        initialize_ai_services(ai_config)
        
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger.info("系统初始化完成")
        
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭系统...")


# 创建FastAPI应用
app = FastAPI(
    title=config.get("app.name", "数字员工系统"),
    description="AI增强的智能协作系统",
    version=config.get("app.version", "0.2.0"),
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("security.cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局AI增强Agent实例
digital_employee = AIEnhancedUnifiedEmployee()

# 任务存储（生产环境应使用数据库）
task_storage: Dict[str, Dict[str, Any]] = {}

# 系统统计
system_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "start_time": datetime.now()
}


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


def update_system_stats(success: bool):
    """更新系统统计"""
    system_stats["total_requests"] += 1
    if success:
        system_stats["successful_requests"] += 1
    else:
        system_stats["failed_requests"] += 1


@app.get("/", response_class=HTMLResponse)
async def root():
    """主页"""
    uptime = datetime.now() - system_stats["start_time"]
    return f"""
    <html>
        <head>
            <title>{config.get("app.name")}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ color: #2c3e50; margin-bottom: 30px; }}
                .stats {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-item {{ background: white; padding: 15px; border-radius: 5px; text-align: center; }}
                .stat-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
                .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
                .api-link {{ color: #3498db; text-decoration: none; padding: 10px 15px; background: #ecf0f1; border-radius: 5px; display: inline-block; margin: 5px; }}
                .api-link:hover {{ background: #d5dbdb; }}
                .feature {{ margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; }}
                .ai-badge {{ background: #e74c3c; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{config.get("app.name")} <span class="ai-badge">AI增强版</span></h1>
                    <p>基于大语言模型的智能协作系统，为您提供专业的需求分析、方案设计、代码生成和项目规划服务。</p>
                </div>
                
                <div class="stats">
                    <h3>系统状态</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">{system_stats["total_requests"]}</div>
                            <div class="stat-label">总请求数</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{system_stats["successful_requests"]}</div>
                            <div class="stat-label">成功请求</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{len(task_storage)}</div>
                            <div class="stat-label">任务总数</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{uptime.days}天{uptime.seconds//3600}时</div>
                            <div class="stat-label">运行时间</div>
                        </div>
                    </div>
                </div>
                
                <h2>AI增强功能</h2>
                <div class="feature">
                    <h4>🔍 智能需求分析</h4>
                    <p>基于大语言模型的需求理解和结构化分析，自动提取功能和非功能需求，生成澄清问题。</p>
                </div>
                <div class="feature">
                    <h4>🏗️ 智能方案设计</h4>
                    <p>根据需求自动推荐合适的技术栈和架构方案，考虑扩展性、性能和团队能力。</p>
                </div>
                <div class="feature">
                    <h4>💻 智能代码生成</h4>
                    <p>生成高质量、可运行的代码示例，包含错误处理、注释和最佳实践。</p>
                </div>
                <div class="feature">
                    <h4>📋 智能项目规划</h4>
                    <p>制定详细的项目实施计划，包含时间线、风险评估和资源配置建议。</p>
                </div>
                
                <h2>API文档</h2>
                <div>
                    <a href="/docs" class="api-link">📖 Swagger UI 文档</a>
                    <a href="/redoc" class="api-link">📋 ReDoc 文档</a>
                    <a href="/system/status" class="api-link">📊 系统状态</a>
                    <a href="/system/ai-stats" class="api-link">🤖 AI统计</a>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; color: #7f8c8d; text-align: center;">
                    <p>Version {config.get("app.version")} | Powered by FastAPI + AI</p>
                </div>
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
                detail=f"不支持的任务类型: {request.task_type}. 支持的类型: {list(task_type_mapping.keys())}"
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
            "task_request": task_request,
            "task_type_str": request.task_type
        }
        
        # 后台处理任务
        background_tasks.add_task(process_task_background, task_request)
        
        logger.info(f"任务提交成功: {task_id}, 类型: {request.task_type}")
        
        return TaskSubmissionResponse(
            task_id=task_id,
            status="submitted",
            message="任务已提交，正在处理中"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"任务提交失败: {str(e)}")
        update_system_stats(False)
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


@app.get("/tasks")
async def list_tasks(limit: int = 20, offset: int = 0):
    """获取任务列表"""
    tasks = []
    task_items = list(task_storage.items())[offset:offset + limit]
    
    for task_id, task_info in task_items:
        tasks.append({
            "task_id": task_id,
            "status": task_info["status"],
            "task_type": task_info.get("task_type_str", "unknown"),
            "created_at": task_info["created_at"],
            "processing_time": task_info.get("processing_time"),
            "confidence_score": task_info.get("confidence_score")
        })
    
    return {
        "tasks": tasks,
        "total": len(task_storage),
        "limit": limit,
        "offset": offset
    }


@app.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    uptime = datetime.now() - system_stats["start_time"]
    
    return {
        "system_name": config.get("app.name"),
        "version": config.get("app.version"),
        "status": "running",
        "uptime_seconds": int(uptime.total_seconds()),
        "ai_enhanced": True,
        "agent_status": digital_employee.get_status(),
        "task_statistics": {
            "total_tasks": len(task_storage),
            "completed_tasks": sum(1 for task in task_storage.values() if task["status"] == "completed"),
            "failed_tasks": sum(1 for task in task_storage.values() if task["status"] == "failed"),
            "processing_tasks": sum(1 for task in task_storage.values() if task["status"] == "processing")
        },
        "system_statistics": system_stats,
        "configuration": {
            "debug_mode": config.is_debug(),
            "cache_enabled": config.get("cache.enabled"),
            "monitoring_enabled": config.get("monitoring.enabled")
        }
    }


@app.get("/system/ai-stats")
async def get_ai_stats():
    """获取AI服务统计"""
    from digital_employee.core.ai_service import ai_manager
    
    return {
        "ai_services": ai_manager.get_statistics(),
        "cache_stats": {
            "cache_size": len(digital_employee.result_cache),
            "cache_max_size": digital_employee.cache_max_size
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": config.get("app.version")
    }


async def process_task_background(task_request: TaskRequest):
    """后台处理任务"""
    try:
        logger.info(f"开始处理任务: {task_request.task_id}, 类型: {task_request.task_type.value}")
        
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
        
        # 更新系统统计
        update_system_stats(response.success)
        
        logger.info(f"任务处理完成: {task_request.task_id}, 成功: {response.success}, 耗时: {response.processing_time:.2f}s")
        
    except Exception as e:
        logger.error(f"任务处理异常: {task_request.task_id}, 错误: {str(e)}")
        task_storage[task_request.task_id].update({
            "status": "failed",
            "error_message": str(e),
            "completed_at": datetime.now()
        })
        update_system_stats(False)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=config.get("app.host", "0.0.0.0"),
        port=config.get("app.port", 8000),
        log_level=config.get("logging.level", "info").lower(),
        access_log=True
    )
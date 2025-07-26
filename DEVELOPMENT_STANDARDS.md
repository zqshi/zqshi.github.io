# 数字员工系统开发规范
## Digital Employee System Development Standards v2.0

### 📋 文档信息
- **文档版本**: v2.0.0
- **更新日期**: 2024-07-24
- **适用范围**: 数字员工系统全部开发工作
- **维护团队**: 数字员工系统技术团队

---

## 🎯 规范概述

本文档定义了数字员工系统的完整开发规范，确保代码质量、系统稳定性和团队协作效率。所有开发人员必须严格遵守这些规范。

---

## 💻 技术开发规范

### 1. 代码结构规范

#### 1.1 项目结构标准
```
digital_employee_system/
├── digital_employee_core/           # 核心模块
│   ├── __init__.py                 # 模块入口
│   ├── intent_recognition.py       # 意图识别引擎
│   ├── task_planner.py            # 任务规划器
│   ├── agent_scheduler.py         # Agent调度器
│   ├── enterprise_agents.py       # 企业Agent实现
│   ├── digital_employee_system.py # 系统控制器
│   └── tests/                     # 单元测试
├── memory_engine/                  # 记忆引擎模块
├── integration_tests/              # 集成测试
├── docs/                          # 文档
├── config/                        # 配置文件
├── scripts/                       # 部署脚本
└── requirements.txt               # 依赖文件
```

#### 1.2 文件命名规范
- **Python文件**: 使用蛇形命名法 `snake_case.py`
- **类名**: 使用帕斯卡命名法 `PascalCase`
- **函数名**: 使用蛇形命名法 `snake_case`
- **常量**: 使用大写蛇形命名法 `CONSTANT_NAME`
- **私有属性/方法**: 使用单下划线前缀 `_private_method`

### 2. 编码规范

#### 2.1 Python编码标准
```python
"""
模块文档字符串
描述模块的功能和用途
"""

from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentRequest:
    """Agent请求数据类
    
    Args:
        user_input: 用户输入内容
        context: 上下文信息
        priority: 优先级 (1-10)
    """
    user_input: str
    context: Dict[str, Any]
    priority: int = 5
    
    def __post_init__(self):
        """数据验证"""
        if not self.user_input.strip():
            raise ValueError("用户输入不能为空")
        if not 1 <= self.priority <= 10:
            raise ValueError("优先级必须在1-10之间")

class BaseAgent(ABC):
    """Agent基类
    
    定义所有Agent的通用接口和行为
    """
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self._initialized = False
        logger.info(f"初始化Agent: {agent_id}")
    
    @abstractmethod
    async def execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """执行任务的抽象方法
        
        Args:
            request: Agent请求对象
            
        Returns:
            任务执行结果
            
        Raises:
            AgentExecutionError: 任务执行失败时抛出
        """
        pass
    
    async def _validate_request(self, request: AgentRequest) -> bool:
        """请求验证
        
        Args:
            request: 待验证的请求
            
        Returns:
            验证是否通过
        """
        try:
            # 验证逻辑
            return True
        except Exception as e:
            logger.error(f"请求验证失败: {str(e)}")
            return False
```

#### 2.2 代码质量要求
- **类型注解**: 所有函数必须有完整的类型注解
- **文档字符串**: 所有类和公共方法必须有docstring
- **异常处理**: 必须有适当的异常处理和日志记录
- **单元测试**: 核心功能必须有单元测试覆盖
- **代码复杂度**: 函数复杂度不超过10，类复杂度不超过20

#### 2.3 异步编程规范
```python
import asyncio
from typing import Coroutine, Any

class AsyncAgentManager:
    """异步Agent管理器"""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._semaphore = asyncio.Semaphore(10)  # 并发控制
    
    async def execute_parallel_tasks(
        self, 
        tasks: List[Coroutine[Any, Any, Any]]
    ) -> List[Any]:
        """并行执行任务
        
        Args:
            tasks: 协程任务列表
            
        Returns:
            任务执行结果列表
        """
        async with self._semaphore:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return self._process_results(results)
            except Exception as e:
                logger.error(f"并行任务执行失败: {str(e)}")
                raise
    
    def _process_results(self, results: List[Any]) -> List[Any]:
        """处理并行执行结果"""
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"任务执行异常: {str(result)}")
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
        return processed_results
```

### 3. 测试规范

#### 3.1 单元测试标准
```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

class TestBaseAgent:
    """Agent基类测试"""
    
    @pytest.fixture
    def mock_agent(self):
        """测试Agent fixture"""
        class TestAgent(BaseAgent):
            async def execute_task(self, request):
                return {"status": "success", "result": "test"}
        
        return TestAgent("test_agent", ["test_capability"])
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self, mock_agent):
        """测试任务执行成功场景"""
        request = AgentRequest(
            user_input="test input",
            context={"test": "context"}
        )
        
        result = await mock_agent.execute_task(request)
        
        assert result["status"] == "success"
        assert result["result"] == "test"
    
    @pytest.mark.asyncio
    async def test_execute_task_with_invalid_input(self, mock_agent):
        """测试无效输入场景"""
        with pytest.raises(ValueError, match="用户输入不能为空"):
            AgentRequest(user_input="", context={})
    
    @patch('logging.Logger.error')
    def test_error_logging(self, mock_logger, mock_agent):
        """测试错误日志记录"""
        # 测试逻辑
        mock_logger.assert_called_once()
```

#### 3.2 集成测试标准
```python
import pytest
from digital_employee_core import quick_setup_system

class TestSystemIntegration:
    """系统集成测试"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """测试完整工作流程"""
        # 设置系统
        system = await quick_setup_system()
        
        # 测试用户请求处理
        response = await system.process_user_request(
            "分析用户数据并生成报告"
        )
        
        # 验证响应
        assert response.status in ["success", "partial"]
        assert response.processing_time > 0
        assert len(response.agent_contributions) > 0
        assert 0 <= response.confidence_score <= 1
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """测试错误处理机制"""
        system = await quick_setup_system()
        
        # 测试异常输入
        response = await system.process_user_request("")
        
        assert response.status == "failed"
        assert "error" in response.result
```

#### 3.3 性能测试标准
```python
import time
import asyncio
import pytest

class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求性能"""
        system = await quick_setup_system()
        
        # 创建50个并发请求
        tasks = []
        for i in range(50):
            task = system.process_user_request(f"测试请求 {i}")
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 性能断言
        assert end_time - start_time < 30  # 30秒内完成
        success_count = len([r for r in results if r.status == "success"])
        assert success_count / len(results) >= 0.9  # 90%成功率
```

---

## 🔌 API接口规范

### 1. RESTful API设计标准

#### 1.1 URL设计规范
```
基础URL: https://api.digitalemployee.com/v2/

资源命名规范:
GET    /agents                    # 获取所有Agent
GET    /agents/{agent_id}         # 获取特定Agent
POST   /agents                    # 创建Agent
PUT    /agents/{agent_id}         # 更新Agent
DELETE /agents/{agent_id}         # 删除Agent

GET    /tasks                     # 获取任务列表
POST   /tasks                     # 创建新任务
GET    /tasks/{task_id}           # 获取任务详情
PUT    /tasks/{task_id}/status    # 更新任务状态

POST   /requests/process          # 处理用户请求
GET    /requests/{request_id}     # 获取请求状态
GET    /system/health             # 系统健康检查
GET    /system/metrics           # 系统指标
```

#### 1.2 HTTP状态码规范
```
成功响应:
200 OK              - 请求成功
201 Created         - 资源创建成功
202 Accepted        - 请求已接受，异步处理中
204 No Content      - 请求成功但无返回内容

客户端错误:
400 Bad Request     - 请求参数错误
401 Unauthorized    - 未认证
403 Forbidden       - 无权限
404 Not Found       - 资源不存在
409 Conflict        - 资源冲突
422 Unprocessable   - 请求格式正确但语义错误
429 Too Many Requests - 请求频率超限

服务器错误:
500 Internal Server Error - 服务器内部错误
502 Bad Gateway          - 网关错误
503 Service Unavailable  - 服务不可用
504 Gateway Timeout      - 网关超时
```

#### 1.3 请求/响应格式标准

**标准请求格式:**
```json
{
  "data": {
    "user_input": "分析销售数据",
    "context": {
      "department": "sales",
      "priority": "high"
    },
    "options": {
      "timeout": 30,
      "require_explanation": true
    }
  },
  "metadata": {
    "request_id": "req_123456",
    "user_id": "user_001",
    "timestamp": "2024-07-24T10:30:00Z"
  }
}
```

**标准响应格式:**
```json
{
  "success": true,
  "data": {
    "status": "success",
    "result": "分析结果内容",
    "agent_contributions": [
      {
        "agent_id": "finance_analyst_001",
        "role": "财务分析师",
        "contribution": "财务数据分析",
        "confidence": 0.95
      }
    ],
    "processing_time": 2.5,
    "confidence_score": 0.92
  },
  "metadata": {
    "request_id": "req_123456",
    "response_id": "resp_789012",
    "timestamp": "2024-07-24T10:30:02Z",
    "api_version": "v2.0"
  },
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "has_more": true
  }
}
```

**错误响应格式:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "用户输入不能为空",
    "details": {
      "field": "user_input",
      "reason": "required_field_missing"
    },
    "suggestion": "请提供有效的用户输入内容"
  },
  "metadata": {
    "request_id": "req_123456",
    "timestamp": "2024-07-24T10:30:00Z",
    "api_version": "v2.0"
  }
}
```

### 2. API接口实现标准

#### 2.1 FastAPI实现示例
```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

app = FastAPI(
    title="数字员工系统API",
    description="企业级Multi-Agent系统API接口",
    version="2.0.0"
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProcessRequest(BaseModel):
    """处理请求模型"""
    user_input: str = Field(..., min_length=1, description="用户输入")
    context: Optional[Dict[str, Any]] = Field(default={}, description="上下文")
    options: Optional[Dict[str, Any]] = Field(default={}, description="选项")
    
    @validator('user_input')
    def validate_user_input(cls, v):
        if not v.strip():
            raise ValueError('用户输入不能为空')
        return v.strip()

class ProcessResponse(BaseModel):
    """处理响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]

@app.post("/v2/requests/process", response_model=ProcessResponse)
async def process_request(
    request: ProcessRequest,
    user_id: Optional[str] = None
):
    """处理用户请求"""
    request_id = str(uuid.uuid4())
    
    try:
        # 获取数字员工系统实例
        system = await get_digital_employee_system()
        
        # 处理请求
        response = await system.process_user_request(
            user_input=request.user_input,
            context=request.context,
            user_id=user_id
        )
        
        return ProcessResponse(
            success=True,
            data={
                "status": response.status,
                "result": response.result,
                "agent_contributions": response.agent_contributions,
                "processing_time": response.processing_time,
                "confidence_score": response.confidence_score
            },
            metadata={
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "v2.0"
            }
        )
        
    except Exception as e:
        logger.error(f"请求处理失败: {str(e)}")
        return ProcessResponse(
            success=False,
            error={
                "code": "PROCESSING_ERROR",
                "message": str(e),
                "suggestion": "请检查输入参数或稍后重试"
            },
            metadata={
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "api_version": "v2.0"
            }
        )

@app.get("/v2/system/health")
async def health_check():
    """健康检查"""
    try:
        system = await get_digital_employee_system()
        status = system.get_system_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system_info": {
                "registered_agents": status["registered_agents"],
                "success_rate": status["success_rate"],
                "uptime": status["uptime_seconds"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"系统不健康: {str(e)}"
        )
```

#### 2.2 认证和授权
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌"
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌验证失败"
        )

@app.post("/v2/requests/process")
async def process_request(
    request: ProcessRequest,
    user_id: str = Depends(verify_token)
):
    """需要认证的接口"""
    # 接口实现
    pass
```

#### 2.3 API文档和测试
```python
# API文档自动生成
@app.get("/v2/agents", tags=["agents"], summary="获取Agent列表")
async def get_agents(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    department: Optional[str] = Query(None, description="部门筛选")
):
    """
    获取系统中所有Agent的列表
    
    - **limit**: 返回结果数量限制 (1-100)
    - **offset**: 分页偏移量
    - **department**: 按部门筛选Agent
    
    返回Agent列表，包含每个Agent的基本信息和能力描述
    """
    pass

# API测试用例
class TestAPI:
    """API测试"""
    
    @pytest.mark.asyncio
    async def test_process_request_success(self, client):
        """测试请求处理成功场景"""
        response = await client.post("/v2/requests/process", json={
            "user_input": "分析销售数据",
            "context": {"department": "sales"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "processing_time" in data["data"]
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查"""
        response = await client.get("/v2/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
```

---

## 🗄️ 数据库设计规范

### 1. 数据库架构标准

#### 1.1 数据库选型规范
```yaml
主数据库:
  类型: PostgreSQL 14+
  用途: 业务数据存储
  特性: ACID事务, JSON支持, 全文搜索

缓存数据库:
  类型: Redis 6+
  用途: 缓存, 会话存储, 消息队列
  特性: 高性能, 数据结构丰富

时序数据库:
  类型: InfluxDB 2.0+
  用途: 监控指标, 性能数据
  特性: 时间序列优化, 高写入性能

搜索引擎:
  类型: Elasticsearch 8+
  用途: 全文搜索, 日志分析
  特性: 分布式搜索, 实时分析
```

#### 1.2 数据库连接配置
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# 数据库配置
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME", "digital_employee"),
    "username": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600
}

# 数据库引擎
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DATABASE_CONFIG["pool_size"],
    max_overflow=DATABASE_CONFIG["max_overflow"],
    pool_timeout=DATABASE_CONFIG["pool_timeout"],
    pool_recycle=DATABASE_CONFIG["pool_recycle"],
    echo=False  # 生产环境设置为False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DatabaseManager:
    """数据库管理器"""
    
    @staticmethod
    def get_db():
        """获取数据库会话"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @staticmethod
    async def execute_with_retry(query, max_retries=3):
        """带重试的查询执行"""
        for attempt in range(max_retries):
            try:
                db = SessionLocal()
                result = db.execute(query)
                db.commit()
                return result
            except Exception as e:
                db.rollback()
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # 指数退避
            finally:
                db.close()
```

### 2. 数据模型设计标准

#### 2.1 基础模型类
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
import uuid

class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    
    def to_dict(self):
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
```

#### 2.2 索引设计规范
```python
from sqlalchemy import Index

class AgentModel(BaseModel):
    """Agent模型"""
    __tablename__ = "agents"
    
    agent_id = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)
    department = Column(String(50), nullable=False, index=True)
    status = Column(String(20), default="active", index=True)
    capabilities = Column(JSON, nullable=False)
    config = Column(JSON, nullable=True)
    
    # 复合索引
    __table_args__ = (
        Index('idx_agent_role_dept', 'role', 'department'),
        Index('idx_agent_status_created', 'status', 'created_at'),
        Index('idx_agent_dept_status', 'department', 'status', 'is_deleted'),
    )

class TaskModel(BaseModel):
    """任务模型"""
    __tablename__ = "tasks"
    
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    user_input = Column(Text, nullable=False)
    context = Column(JSON, nullable=True)
    priority = Column(Integer, default=5, index=True)
    status = Column(String(20), default="pending", index=True)
    assigned_agent_id = Column(String(100), nullable=True, index=True)
    result = Column(JSON, nullable=True)
    processing_time = Column(Integer, nullable=True)  # 毫秒
    
    # 分区表索引 (按创建时间)
    __table_args__ = (
        Index('idx_task_status_priority', 'status', 'priority'),
        Index('idx_task_agent_status', 'assigned_agent_id', 'status'),
        Index('idx_task_created_status', 'created_at', 'status'),
    )
```

---

## 📊 数据库表设计规范

### 1. 表设计标准

#### 1.1 命名规范
```sql
-- 表命名规范
表名: 复数形式，下划线分隔
  ✓ agents, tasks, user_requests
  ✗ agent, Task, UserRequest

-- 字段命名规范
字段名: 下划线分隔，描述性强
  ✓ created_at, agent_id, processing_time
  ✗ createdAt, aid, time

-- 索引命名规范
索引名: idx_表名_字段名
  ✓ idx_agents_role, idx_tasks_status_priority
  ✗ agent_role_index, task_idx

-- 约束命名规范
主键: pk_表名
外键: fk_表名_引用表名_字段名
唯一: uk_表名_字段名
检查: ck_表名_字段名
```

#### 1.2 核心业务表设计

**1. Agent管理表**
```sql
-- Agent注册表
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    capabilities JSONB NOT NULL DEFAULT '[]',
    config JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1
);

-- 索引
CREATE INDEX idx_agents_role ON agents(role) WHERE is_deleted = FALSE;
CREATE INDEX idx_agents_department ON agents(department) WHERE is_deleted = FALSE;
CREATE INDEX idx_agents_status ON agents(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_agents_role_dept ON agents(role, department) WHERE is_deleted = FALSE;
CREATE INDEX idx_agents_capabilities ON agents USING GIN (capabilities);

-- 注释
COMMENT ON TABLE agents IS 'Agent注册和管理表';
COMMENT ON COLUMN agents.agent_id IS 'Agent唯一标识符';
COMMENT ON COLUMN agents.role IS 'Agent角色类型';
COMMENT ON COLUMN agents.capabilities IS 'Agent能力列表，JSON格式';
COMMENT ON COLUMN agents.performance_metrics IS '性能指标，JSON格式';
```

**2. 任务管理表**
```sql
-- 任务主表
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    user_input TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    complexity_level INTEGER CHECK (complexity_level BETWEEN 1 AND 10),
    urgency_level VARCHAR(20) CHECK (urgency_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'processing', 'completed', 'failed', 'cancelled')),
    assigned_agent_id VARCHAR(100),
    result JSONB,
    error_info JSONB,
    processing_time INTEGER, -- 毫秒
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    is_deleted BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1
);

-- 分区表 (按月分区)
CREATE TABLE tasks_y2024m07 PARTITION OF tasks
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');
CREATE TABLE tasks_y2024m08 PARTITION OF tasks
    FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');

-- 索引
CREATE INDEX idx_tasks_status ON tasks(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_tasks_priority ON tasks(priority) WHERE is_deleted = FALSE;
CREATE INDEX idx_tasks_agent_id ON tasks(assigned_agent_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority) WHERE is_deleted = FALSE;
CREATE INDEX idx_tasks_created_at ON tasks(created_at) WHERE is_deleted = FALSE;
CREATE INDEX idx_tasks_context ON tasks USING GIN (context);

-- 外键约束
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_agents 
    FOREIGN KEY (assigned_agent_id) REFERENCES agents(agent_id);
```

**3. 用户请求表**
```sql
-- 用户请求表
CREATE TABLE user_requests (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    session_id VARCHAR(100),
    original_input TEXT NOT NULL,
    processed_input TEXT,
    intent_analysis JSONB,
    processing_strategy VARCHAR(50),
    task_ids JSONB DEFAULT '[]', -- 关联的任务ID列表
    final_result JSONB,
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    processing_time INTEGER, -- 毫秒
    status VARCHAR(20) DEFAULT 'received' CHECK (status IN ('received', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1
);

-- 索引
CREATE INDEX idx_user_requests_user_id ON user_requests(user_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_user_requests_session_id ON user_requests(session_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_user_requests_status ON user_requests(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_user_requests_created_at ON user_requests(created_at) WHERE is_deleted = FALSE;
CREATE INDEX idx_user_requests_intent ON user_requests USING GIN (intent_analysis);
```

**4. Agent协作表**
```sql
-- Agent协作记录表
CREATE TABLE agent_collaborations (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    collaboration_id VARCHAR(100) UNIQUE NOT NULL,
    task_id VARCHAR(100) NOT NULL,
    primary_agent_id VARCHAR(100) NOT NULL,
    participating_agents JSONB NOT NULL DEFAULT '[]',
    collaboration_type VARCHAR(50) NOT NULL,
    workflow_design JSONB,
    coordination_rules JSONB,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'initiated' CHECK (status IN ('initiated', 'coordinating', 'executing', 'integrating', 'completed', 'failed')),
    results JSONB,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1
);

-- 外键约束
ALTER TABLE agent_collaborations ADD CONSTRAINT fk_collaborations_tasks
    FOREIGN KEY (task_id) REFERENCES tasks(task_id);
ALTER TABLE agent_collaborations ADD CONSTRAINT fk_collaborations_primary_agent
    FOREIGN KEY (primary_agent_id) REFERENCES agents(agent_id);

-- 索引
CREATE INDEX idx_collaborations_task_id ON agent_collaborations(task_id);
CREATE INDEX idx_collaborations_primary_agent ON agent_collaborations(primary_agent_id);
CREATE INDEX idx_collaborations_status ON agent_collaborations(status) WHERE is_deleted = FALSE;
```

### 2. 数据分区和归档策略

#### 2.1 时间分区策略
```sql
-- 按月分区的任务表
CREATE TABLE tasks (
    -- 字段定义
) PARTITION BY RANGE (created_at);

-- 创建分区函数
CREATE OR REPLACE FUNCTION create_monthly_partitions()
RETURNS void AS $$
DECLARE
    start_date date;
    end_date date;
    partition_name text;
BEGIN
    start_date := date_trunc('month', CURRENT_DATE);
    
    FOR i IN 0..11 LOOP
        end_date := start_date + interval '1 month';
        partition_name := 'tasks_' || to_char(start_date, 'YYYY_MM');
        
        EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF tasks 
                       FOR VALUES FROM (%L) TO (%L)',
                       partition_name, start_date, end_date);
        
        start_date := end_date;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 定期执行分区创建
SELECT create_monthly_partitions();
```

#### 2.2 数据归档策略
```sql
-- 创建归档表
CREATE TABLE tasks_archive (LIKE tasks INCLUDING ALL);

-- 归档函数
CREATE OR REPLACE FUNCTION archive_old_tasks()
RETURNS void AS $$
BEGIN
    -- 归档6个月前的已完成任务
    INSERT INTO tasks_archive 
    SELECT * FROM tasks 
    WHERE status IN ('completed', 'failed', 'cancelled')
      AND created_at < CURRENT_DATE - INTERVAL '6 months';
    
    -- 删除已归档的数据
    DELETE FROM tasks 
    WHERE status IN ('completed', 'failed', 'cancelled')
      AND created_at < CURRENT_DATE - INTERVAL '6 months';
      
    -- 更新统计信息
    ANALYZE tasks;
    ANALYZE tasks_archive;
END;
$$ LANGUAGE plpgsql;

-- 定期执行归档 (通过cron job)
-- 0 2 1 * * /usr/bin/psql -c "SELECT archive_old_tasks();"
```

---

## 📝 字段设计规范

### 1. 字段类型标准

#### 1.1 基础字段类型映射
```sql
-- 字符串类型
短文本 (< 255字符):     VARCHAR(255)
中等文本 (< 65535字符): TEXT
长文本 (> 65535字符):   LONGTEXT
固定长度字符串:         CHAR(n)

-- 数值类型
整数:                  INTEGER, BIGINT
小整数:                SMALLINT
金额:                  DECIMAL(15,2)
百分比:                DECIMAL(5,2)  -- 0.00-999.99
浮点数:                REAL, DOUBLE PRECISION

-- 时间类型
日期时间:              TIMESTAMP WITH TIME ZONE
日期:                  DATE
时间:                  TIME
持续时间:              INTERVAL

-- 布尔类型
是否标志:              BOOLEAN

-- JSON类型
结构化数据:            JSONB (PostgreSQL推荐)
配置信息:              JSONB
数组数据:              JSONB

-- 二进制类型
文件内容:              BYTEA
大文件:                存储文件路径，文件存储在对象存储
```

#### 1.2 常用字段设计模板

**身份标识字段:**
```sql
-- 主键ID
id SERIAL PRIMARY KEY

-- UUID (全局唯一)
uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()

-- 业务ID (人类可读)
agent_id VARCHAR(100) UNIQUE NOT NULL
task_id VARCHAR(100) UNIQUE NOT NULL
request_id VARCHAR(100) UNIQUE NOT NULL

-- 用户标识
user_id VARCHAR(100) NOT NULL
session_id VARCHAR(100)
```

**时间字段:**
```sql
-- 审计时间字段 (所有表必备)
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

-- 业务时间字段
start_time TIMESTAMP WITH TIME ZONE
end_time TIMESTAMP WITH TIME ZONE
scheduled_time TIMESTAMP WITH TIME ZONE
expire_time TIMESTAMP WITH TIME ZONE

-- 时间间隔字段
processing_time INTEGER  -- 毫秒
timeout_duration INTEGER -- 秒
retry_interval INTEGER   -- 秒
```

**状态字段:**
```sql
-- 通用状态字段
status VARCHAR(20) DEFAULT 'active' 
  CHECK (status IN ('active', 'inactive', 'pending', 'processing', 'completed', 'failed'))

-- 布尔状态字段
is_active BOOLEAN DEFAULT TRUE
is_deleted BOOLEAN DEFAULT FALSE
is_public BOOLEAN DEFAULT FALSE
is_verified BOOLEAN DEFAULT FALSE

-- 优先级字段
priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10)
urgency_level VARCHAR(20) CHECK (urgency_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'))
```

**配置和数据字段:**
```sql
-- JSON配置字段
config JSONB DEFAULT '{}'
metadata JSONB DEFAULT '{}'
options JSONB DEFAULT '{}'
context JSONB DEFAULT '{}'

-- 数组字段 (使用JSONB存储)
capabilities JSONB DEFAULT '[]'
tags JSONB DEFAULT '[]'
attachments JSONB DEFAULT '[]'

-- 计数字段
retry_count INTEGER DEFAULT 0
view_count INTEGER DEFAULT 0
success_count INTEGER DEFAULT 0
failure_count INTEGER DEFAULT 0
```

**性能和监控字段:**
```sql
-- 性能指标
response_time INTEGER    -- 毫秒
throughput INTEGER       -- 每秒处理数
cpu_usage DECIMAL(5,2)   -- CPU使用率百分比
memory_usage BIGINT      -- 内存使用字节数

-- 质量指标
confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1)
accuracy_rate DECIMAL(5,2)    -- 准确率百分比
error_rate DECIMAL(5,2)       -- 错误率百分比

-- 统计字段
total_requests INTEGER DEFAULT 0
successful_requests INTEGER DEFAULT 0
failed_requests INTEGER DEFAULT 0
average_processing_time INTEGER DEFAULT 0
```

### 2. 字段约束和验证

#### 2.1 约束规范
```sql
-- 非空约束 (关键业务字段)
agent_id VARCHAR(100) NOT NULL
user_input TEXT NOT NULL
status VARCHAR(20) NOT NULL

-- 唯一约束
email VARCHAR(255) UNIQUE NOT NULL
phone VARCHAR(20) UNIQUE
agent_id VARCHAR(100) UNIQUE NOT NULL

-- 检查约束
priority INTEGER CHECK (priority BETWEEN 1 AND 10)
confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1)
status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'pending'))

-- 外键约束
assigned_agent_id VARCHAR(100) REFERENCES agents(agent_id)
user_id VARCHAR(100) REFERENCES users(user_id)

-- 复合唯一约束
CONSTRAINT uk_agent_role_dept UNIQUE (agent_id, department)
```

#### 2.2 默认值规范
```sql
-- 时间默认值
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP

-- 状态默认值
status VARCHAR(20) DEFAULT 'active'
is_deleted BOOLEAN DEFAULT FALSE
is_active BOOLEAN DEFAULT TRUE

-- 数值默认值
priority INTEGER DEFAULT 5
retry_count INTEGER DEFAULT 0
version INTEGER DEFAULT 1

-- JSON默认值
config JSONB DEFAULT '{}'
capabilities JSONB DEFAULT '[]'
metadata JSONB DEFAULT '{}'

-- UUID默认值
uuid VARCHAR(36) DEFAULT gen_random_uuid()
```

### 3. 字段命名和注释规范

#### 3.1 命名规范示例
```sql
-- 好的字段命名 ✓
user_id              -- 用户ID
created_at           -- 创建时间
is_active           -- 是否激活
processing_time     -- 处理时间
confidence_score    -- 置信度分数
agent_capabilities  -- Agent能力

-- 不好的字段命名 ✗
uid                 -- 不明确
time                -- 哪个时间？
flag                -- 什么标志？
data                -- 什么数据？
temp                -- 临时什么？
```

#### 3.2 注释规范
```sql
-- 表注释
COMMENT ON TABLE agents IS 'Agent注册和管理表，存储所有数字员工Agent的基本信息';

-- 字段注释
COMMENT ON COLUMN agents.agent_id IS 'Agent唯一标识符，格式：角色_部门_序号';
COMMENT ON COLUMN agents.capabilities IS 'Agent能力列表，JSON数组格式，包含技能和专长';
COMMENT ON COLUMN agents.performance_metrics IS '性能指标，JSON对象，包含响应时间、成功率等';
COMMENT ON COLUMN agents.config IS 'Agent配置信息，JSON对象，包含个性化设置';

-- 索引注释  
COMMENT ON INDEX idx_agents_role IS '按Agent角色查询的索引，用于角色筛选';
COMMENT ON INDEX idx_agents_status_created IS '按状态和创建时间的复合索引，用于活跃Agent查询';
```

---

## 🔍 数据库维护和监控

### 1. 性能监控
```sql
-- 慢查询监控
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE mean_time > 100  -- 平均执行时间超过100ms
ORDER BY mean_time DESC;

-- 索引使用情况
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0;  -- 未使用的索引

-- 表大小监控
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 2. 备份和恢复策略
```bash
#!/bin/bash
# 数据库备份脚本

DB_NAME="digital_employee"
BACKUP_DIR="/backup/database"
DATE=$(date +%Y%m%d_%H%M%S)

# 全量备份
pg_dump -h localhost -U postgres -d $DB_NAME -f $BACKUP_DIR/full_backup_$DATE.sql

# 增量备份 (WAL)
pg_basebackup -h localhost -U postgres -D $BACKUP_DIR/base_backup_$DATE -Ft -z -P

# 清理30天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

---

这套开发规范涵盖了数字员工系统的完整技术栈，确保了代码质量、系统稳定性和团队协作效率。请根据项目具体需求进行调整和补充。
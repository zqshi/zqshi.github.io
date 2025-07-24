# 数字员工智能系统 (Digital Employee Intelligent System)

基于Multi Agent技术架构和分层动态记忆引擎的企业数字化转型解决方案，通过"数字员工"作为企业内主要工作对象，实现智能化的组织协作模式。

## 🌟 核心特性

### 🧠 分层动态记忆引擎
- **五层记忆体系**: 工作记忆、情景记忆、语义记忆、程序性记忆、情感记忆
- **动态记忆重构**: 关联检索、记忆衰减、记忆融合机制
- **感知-记忆闭环**: 智能输入处理 → 记忆匹配 → 推理引擎 → 响应输出
- **跨层记忆检索**: 基于图神经网络的关联分析和记忆融合

### 🤖 智能Agent系统
- **多角色Agent支持**: 人力、法务、财务、产品、运营、架构师、研发、设计、运维等9个核心岗位
- **智能Prompt管理**: 企业级Prompt库、版本控制、约束管理
- **智能任务调度**: 基于能力匹配和负载均衡的任务自动分配
- **分层处理机制**: 现有工具检索 → 单Agent处理 → 多Agent协同 → 人工介入

### 🔧 企业级特性
- **企业级安全**: RBAC权限控制、数据加密、隐私保护、审计追踪
- **高可用架构**: 容器化部署、自动伸缩、故障恢复、监控告警
- **模块化设计**: 记忆引擎与数字员工核心分离，支持独立部署和扩展
- **版本管理**: 全链路版本控制和日志记录

## 📁 项目结构

### 模块化架构

```
digital-employee-system/
├── memory_engine_module/          # 🧠 记忆引擎模块
│   ├── __init__.py               # 模块入口和API导出
│   ├── memory_engine.py          # 核心记忆层实现 (五层记忆体系)
│   ├── memory_reconstruction.py  # 动态记忆重构机制
│   ├── memory_perception_loop.py # 感知-记忆闭环系统
│   ├── memory_system_demo.py     # 演示和测试代码
│   ├── MEMORY_ENGINE_README.md   # 记忆引擎详细文档
│   └── README.md                 # 模块说明文档
│
├── digital_employee_core/         # 🤖 数字员工核心模块
│   ├── __init__.py               # 模块入口和API导出
│   ├── prompt_manager.py         # 智能Prompt管理系统
│   ├── agent_implementations.py  # Agent实现框架
│   ├── test_framework.py         # 测试验证框架
│   ├── quick_test.py            # 快速测试工具
│   ├── simple_test.py           # 简单测试示例
│   ├── prompts/                 # Prompt模板库
│   │   ├── system_prompts.json  # 系统级提示词
│   │   ├── agent_prompts.json   # Agent专用提示词
│   │   ├── task_prompts.json    # 任务型提示词
│   │   ├── constraint_prompts.json # 约束条件提示词
│   │   └── version.json         # 版本信息
│   └── README.md                # 模块说明文档
│
├── integrated_system_test.py     # 🧪 集成测试工具
├── digital_employee_system.md   # 系统设计文档
├── technical_implementation.md  # 技术实现方案
├── requirements.txt             # Python依赖 (包含记忆引擎依赖)
├── Dockerfile                   # Docker镜像构建
├── docker-compose.yml          # Docker Compose配置
├── k8s-deployment.yaml          # Kubernetes部署配置
├── deploy.sh                    # 部署脚本
├── README.md                    # 项目说明文档 (本文档)
├── LOCAL_GIT_STRATEGY.md        # 本地Git版本管理策略
├── .gitignore                   # Git忽略规则
├── .gitattributes              # Git文件属性配置
└── .claude/                     # Claude工具配置目录
```

### 模块职责划分

| 模块 | 核心职责 | 主要组件 |
|-----|---------|---------|
| **记忆引擎模块** | Agent认知能力基石 | 五层记忆体系、动态重构机制、感知闭环 |
| **数字员工核心** | 业务逻辑实现 | Prompt管理、Agent框架、测试工具 |
| **集成测试** | 跨模块验证 | 模块集成测试、性能验证、隔离性测试 |

## 🚀 快速开始

### 环境要求

- Python 3.7+ (推荐 3.11+)
- numpy, networkx (记忆引擎依赖)
- Docker & Docker Compose (可选，用于容器化部署)
- Kubernetes (可选，用于生产部署)
- Redis (可选，用于分布式缓存)
- PostgreSQL (可选，用于持久化存储)

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd digital-employee-system

# 安装核心依赖
pip install numpy networkx

# 安装完整依赖 (可选)
pip install -r requirements.txt

# 设置环境变量 (如需要)
cp .env.example .env
# 编辑.env文件，设置必要的配置
```

### 2. 模块化快速体验

#### 🧠 记忆引擎模块体验
```python
# 导入记忆引擎模块
from memory_engine_module import create_memory_system, InputType

# 创建记忆系统
memory_system = create_memory_system()

# 处理查询输入
result = memory_system.process(
    "我需要帮助生成销售报告",
    InputType.QUERY,
    {"source": "user", "urgency": "high"}
)

print(f"响应: {result.response}")
print(f"置信度: {result.confidence}")
print(f"激活记忆数: {len(result.activated_memories)}")

# 运行完整演示
from memory_engine_module.memory_system_demo import MemorySystemDemo
demo = MemorySystemDemo()
demo.run_complete_demo()
```

#### 🤖 数字员工核心模块体验
```python
# 导入数字员工核心模块
from digital_employee_core import (
    get_module_info,
    check_dependencies,
    create_digital_employee_system
)

# 检查模块状态
module_info = get_module_info()
print(f"模块: {module_info['name']} v{module_info['version']}")

# 检查依赖
dependencies = check_dependencies()
for dep, info in dependencies.items():
    status = "✓" if info["available"] else "❌"
    print(f"{status} {dep}: {info.get('version', info.get('error'))}")

# 创建完整系统 (如果组件可用)
if module_info['components_available']:
    system = create_digital_employee_system()
    print(f"系统创建成功，可用Agent: {len(system['available_agents'])}")
```

#### 🧪 集成测试体验
```bash
# 运行完整的集成测试
python integrated_system_test.py

# 选择测试选项:
# ✓ 记忆引擎模块测试
# ✓ 数字员工核心模块测试  
# ✓ 跨模块集成测试
# ✓ 模块隔离性测试
```

### 2. 开发环境部署

```bash
# 使用Docker Compose启动开发环境
./deploy.sh docker-dev

# 或者手动启动
docker-compose up -d
```

### 3. 生产环境部署

```bash
# Docker Compose生产部署
./deploy.sh docker-prod

# Kubernetes生产部署
./deploy.sh k8s-prod
```

### 4. 验证部署

```bash
# 检查服务状态
curl http://localhost:8080/api/v1/health

# 查看所有Agent状态
curl http://localhost:8080/api/v1/agents/hr_001/status
```

## 🔧 配置说明

### 环境变量配置

```bash
# .env文件示例
OPENAI_API_KEY=your-openai-api-key
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/digital_employees
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Agent配置

每个Agent都有独立的配置文件，支持以下设置：
- 角色权限和约束
- 工具集成配置  
- 性能参数调优
- 安全策略设置

## 📊 监控和运维

### 访问监控面板

- **Grafana监控**: http://localhost:3000 (admin/admin123)
- **Prometheus指标**: http://localhost:9090
- **Kibana日志**: http://localhost:5601

### 关键监控指标

- Agent响应时间和成功率
- 系统资源使用情况
- 任务队列长度和处理速度
- 数据库连接池状态
- API请求统计

## 🔐 安全配置

### 权限管理

系统采用RBAC权限模型：
- 角色定义和权限分配
- 资源访问控制
- 操作审计日志
- 多租户数据隔离

### 数据保护

- 字段级数据加密
- 敏感信息脱敏
- GDPR合规支持
- 备份和恢复策略

## 🧪 测试

```bash
# 运行所有测试
./deploy.sh test

# 手动测试
pytest tests/ -v --cov=./

# 性能测试
locust -f tests/load_test.py --host=http://localhost:8080
```

## 📚 API文档

### 核心API端点

#### 任务提交
```http
POST /api/v1/tasks
Content-Type: application/json

{
  "task_type": "employee_analysis",
  "priority": "high",
  "data": {
    "employee_id": "E001",
    "analysis_type": "performance"
  }
}
```

#### Agent状态查询
```http
GET /api/v1/agents/{agent_id}/status
```

#### 健康检查
```http
GET /api/v1/health
```

### 响应格式

```json
{
  "task_id": "task_123456789",
  "status": "success",
  "result": {
    "employee_id": "E001",
    "performance_score": 8.5,
    "recommendations": ["提供技能培训", "参与跨部门项目"]
  },
  "agent_id": "hr_001",
  "processing_time": 2.35
}
```

## 🛠️ 开发指南

### 添加新的Agent

1. 继承`BaseAgent`类
2. 实现必要的抽象方法
3. 定义Agent能力和约束
4. 注册到调度器

```python
class CustomAgent(BaseAgent):
    def __init__(self, agent_id: str):
        capabilities = [
            AgentCapability("custom_skill", "自定义能力", 8, ["tool1"])
        ]
        super().__init__(agent_id, AgentRole.CUSTOM, capabilities)
    
    def _load_constraints(self):
        return [
            AgentConstraint("custom_rule", "自定义规则", lambda task: True)
        ]
    
    async def _execute_task(self, task: Task):
        # 实现具体的任务处理逻辑
        return {"result": "处理完成"}
```

### 扩展工具集成

```python
def _initialize_tools(self):
    return [
        Tool(
            name="Custom Tool",
            description="自定义工具描述",
            func=self._custom_tool_function
        )
    ]
```

## 🔄 部署模式

### 单机部署
- 适用于开发和小规模测试
- 使用Docker Compose
- 资源需求较低

### 集群部署
- 适用于生产环境
- 使用Kubernetes
- 支持自动伸缩和故障恢复

### 混合云部署
- 核心服务本地部署
- 计算密集型任务云端处理
- 数据安全和性能兼顾

## 🐛 故障排除

### 常见问题

1. **Agent启动失败**
   - 检查环境变量配置
   - 验证数据库连接
   - 查看日志文件

2. **任务处理超时**
   - 调整任务超时设置
   - 检查系统资源使用
   - 分析任务复杂度

3. **性能问题**
   - 监控CPU和内存使用
   - 优化数据库查询
   - 调整并发配置

### 日志分析

```bash
# 查看应用日志
docker-compose logs -f digital-employee-api

# 查看特定Agent日志
grep "hr_001" logs/application.log

# 分析错误日志
grep "ERROR" logs/application.log | tail -20
```

## 🤝 贡献指南

1. Fork项目到个人仓库
2. 创建特性分支 (`git checkout -b feature/new-agent`)
3. 提交更改 (`git commit -am 'Add new agent'`)
4. 推送分支 (`git push origin feature/new-agent`)
5. 创建Pull Request

### 代码规范

- 遵循PEP 8代码风格
- 添加完整的类型注解
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🆘 支持和反馈

- 📧 邮箱: support@digital-employees.com
- 💬 社区: [GitHub Discussions](https://github.com/your-org/digital-employee-system/discussions)
- 🐛 问题报告: [GitHub Issues](https://github.com/your-org/digital-employee-system/issues)
- 📖 文档: [Wiki](https://github.com/your-org/digital-employee-system/wiki)

## 🗺️ 路线图

### v1.0 (当前)
- ✅ 核心Agent实现
- ✅ 任务调度系统
- ✅ 基础监控和日志
- ✅ Docker部署支持

### v1.1 (规划中)
- 🔄 更多行业Agent
- 🔄 机器学习优化
- 🔄 移动端支持
- 🔄 第三方系统集成

### v2.0 (未来)
- 📋 自然语言交互
- 📋 知识图谱支持
- 📋 联邦学习能力
- 📋 边缘计算部署

---

**让数字员工为您的企业赋能！** 🚀
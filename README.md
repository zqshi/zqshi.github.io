# 数字员工系统 - MVP版本

**一个务实的、可执行的智能协作系统**

## 🎯 核心理念

- **简单优先**: 一个统一Agent处理所有任务，避免过度设计
- **务实可行**: 基于实际代码而非理论架构
- **数据驱动**: 根据使用数据决定是否需要功能分离
- **渐进增强**: 从MVP开始，逐步优化

## 🚀 快速开始

### 环境要求
- Python 3.9+
- 虚拟环境（推荐）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd "Digital employees"
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   
   # Windows
   venv\\Scripts\\activate
   
   # macOS/Linux  
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动服务**
   ```bash
   python run_server.py
   ```

5. **访问系统**
   - 主页: http://localhost:8000
   - API文档: http://localhost:8000/docs
   - 系统状态: http://localhost:8000/system/status

## 📋 功能特性

### 统一数字员工Agent
一个智能Agent处理以下所有任务类型：

- **需求分析** (`requirement_analysis`)
  - 自然语言需求解析
  - 功能性/非功能性需求提取
  - EARS格式转换
  - 澄清问题生成

- **方案设计** (`solution_design`)
  - 技术栈选择
  - 架构设计
  - 组件规划
  - 部署方案

- **代码生成** (`code_generation`)
  - 基础代码框架
  - API接口代码
  - 项目结构建议
  - 最佳实践示例

- **项目规划** (`project_planning`)
  - 开发阶段规划
  - 风险识别
  - 时间估算
  - 资源建议

- **通用询问** (`general_inquiry`)
  - 技术咨询
  - 最佳实践建议
  - 问题解答

## 🔧 API使用示例

### 提交任务
```bash
curl -X POST "http://localhost:8000/tasks/submit" \\
  -H "Content-Type: application/json" \\
  -d '{
    "task_type": "requirement_analysis",
    "user_input": "我需要一个支持1000并发用户的电商系统",
    "priority": 8
  }'
```

### 查询任务状态
```bash
curl "http://localhost:8000/tasks/{task_id}/status"
```

### 查看系统状态
```bash
curl "http://localhost:8000/system/status"
```

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_unified_agent.py

# 生成覆盖率报告
pytest --cov=digital_employee tests/
```

## 📊 系统监控

### 性能指标
- 响应时间: 目标 < 2秒
- 并发处理: 支持多任务并行
- 准确率: 目标 > 80%
- 系统可用性: 目标 > 99%

### 监控端点
- `/system/status` - 系统状态
- `/tasks` - 任务列表
- `/tasks/{task_id}/status` - 具体任务状态

## 🏗️ 项目结构

```
Digital employees/
├── digital_employee/           # 核心代码包
│   ├── core/                  # 基础框架
│   │   ├── agent_base.py      # Agent基类
│   │   └── __init__.py
│   ├── agents/                # Agent实现
│   │   ├── unified_agent.py   # 统一数字员工
│   │   └── __init__.py
│   ├── api/                   # API接口
│   │   ├── main.py           # FastAPI主应用
│   │   └── __init__.py
│   └── __init__.py
├── tests/                     # 测试代码
│   ├── test_unified_agent.py  # Agent测试
│   └── __init__.py
├── requirements.txt           # 依赖包
├── run_server.py             # 启动脚本
└── README.md                 # 本文档
```

## 🔄 开发工作流

### 本地开发
1. 启动开发服务器: `python run_server.py`
2. 修改代码（自动重载）
3. 运行测试: `pytest`
4. 检查API文档: http://localhost:8000/docs

### 添加新功能
1. 在统一Agent中添加处理逻辑
2. 编写相应测试用例
3. 更新API文档
4. 验证端到端功能

## 📈 未来扩展计划

### 何时考虑Agent分离？
基于实际使用数据，当出现以下情况时考虑分离：
- 单一Agent处理时间 > 30秒
- 特定领域错误率 > 20%
- 用户满意度 < 70%
- 并发处理成为瓶颈

### 可能的分离方向
1. **专业领域Agent**: 基于技术栈分离（Python、JavaScript等）
2. **功能类型Agent**: 基于任务类型分离（分析、设计、编码）
3. **复杂度Agent**: 基于任务复杂度分离（简单、中等、复杂）

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交Pull Request

## 📝 许可证

[MIT License](LICENSE)

## 🆘 技术支持

- **问题反馈**: 通过GitHub Issues
- **功能建议**: 通过GitHub Discussions
- **紧急问题**: 联系项目维护者

---

**记住**: 这是一个务实的MVP系统。我们优先考虑可用性和实际价值，而不是理论完美性。让数据和用户反馈指导我们的发展方向！
# 数字员工系统 - Prompt管理系统

## 版本信息
- **当前版本**: 1.0.0
- **创建日期**: 2025-07-23
- **维护者**: Claude Code

## 系统概述

本系统实现了企业级的Prompt版本管理，将原本分散在代码中的Agent角色定义、约束条件和任务模板统一管理，支持版本控制和迭代更新。

## 目录结构

```
prompts/
├── version.json                # 版本控制文件
├── system_prompts.json         # 系统级Prompt模板
├── agent_prompts.json          # Agent角色定义
├── constraint_prompts.json     # 约束条件模板
└── task_prompts.json          # 任务执行模板

prompt_manager.py              # Prompt管理器
agent_implementations.py       # 更新后的Agent实现(v2.0.0)
```

## 核心功能

### 1. 版本控制
- 统一的版本号管理
- 变更记录追踪
- 向后兼容性保证

### 2. 分层管理
- **系统层**: 基础Agent行为模板
- **角色层**: 各职能Agent的个性化设定
- **约束层**: 安全、业务、技术约束规则
- **任务层**: 具体任务执行指导

### 3. 动态渲染
- 模板变量替换
- 运行时Prompt组装
- 上下文相关的指令生成

## 使用方法

### 基础使用

```python
from prompt_manager import PromptManager

# 初始化管理器
pm = PromptManager()

# 创建Agent专用Prompt
hr_prompt = pm.create_agent_prompt("hr_001", "hr_agent")

# 创建任务专用Prompt  
task_data = {"employee_id": "EMP001", "analysis_type": "performance"}
task_prompt = pm.create_task_prompt("hr_agent", "employee_analysis", task_data)
```

### 版本管理

```python
# 检查当前版本
version_info = pm.get_version_info()
print(f"当前版本: {version_info['version']}")

# 更新版本
pm.update_version("1.1.0", ["新增设计师Agent角色", "优化约束条件模板"], "开发者姓名")
```

### 系统验证

```python
# 验证所有Prompt文件
validation = pm.validate_prompts()

# 列出可用的Prompt类型
available = pm.list_available_prompts()
```

## Agent角色配置

### 当前支持的Agent类型

1. **hr_agent** - 人力资源专员
2. **legal_agent** - 法务顾问  
3. **finance_agent** - 财务分析师
4. **product_agent** - 产品经理
5. **operations_agent** - 运营专员
6. **architect_agent** - 技术架构师
7. **developer_agent** - 软件工程师
8. **designer_agent** - UI/UX设计师
9. **devops_agent** - 运维工程师

### Agent配置示例

```json
{
  "hr_agent": {
    "version": "1.0.0",
    "role_name": "人力资源专员",
    "personality": "专业、细致、关注员工体验...",
    "system_prompt": "你是一名专业的数字化人力资源专员...",
    "capabilities": ["招聘筛选", "绩效分析", "政策咨询"],
    "tools": ["简历解析工具", "人才数据库", "绩效系统"]
  }
}
```

## 约束系统

### 约束类别

1. **安全约束**
   - 隐私保护
   - 数据访问控制

2. **业务约束**
   - 财务审批流程
   - 法律合规要求
   - 人力资源伦理

3. **技术约束**
   - 生产环境安全
   - 代码质量标准

4. **升级规则**
   - 人工介入条件

### 约束配置示例

```json
{
  "privacy_protection": {
    "template": "## 隐私保护约束\n你必须严格遵循以下隐私保护规定...",
    "applicable_agents": ["hr_agent", "finance_agent"],
    "last_updated": "2025-07-23"
  }
}
```

## 任务模板

### 支持的任务类型

- **HR任务**: 员工分析、简历筛选、政策查询
- **财务任务**: 财务报告、预算分析、费用审计
- **技术任务**: 代码审查、系统监控
- **通用任务**: 任务规划、质量验证

### 任务模板示例

```json
{
  "employee_analysis": {
    "template": "## 员工数据分析任务\n分析维度...",
    "variables": ["employee_id", "analysis_type"],
    "last_updated": "2025-07-23"
  }
}
```

## 集成方式

### 原有系统升级

原有的`agent_implementations.py`已升级至v2.0.0，主要变更：

1. **BaseAgent类增强**
   ```python
   def __init__(self, agent_id: str, role: AgentRole, capabilities: List[AgentCapability]):
       # 新增Prompt管理器
       self.prompt_manager = PromptManager()
       self.system_prompt = self._generate_system_prompt()
   ```

2. **任务处理增强**
   ```python
   async def process_task(self, task: Task) -> Dict[str, Any]:
       # 生成任务专用prompt
       task_prompt = self._generate_task_prompt(task)
       result = await self._execute_task(task, task_prompt)
   ```

3. **执行方法签名更新**
   ```python
   async def _execute_task(self, task: Task, task_prompt: str = None) -> Any:
       # 支持自定义任务prompt
   ```

## 版本迭代指南

### 版本号规则
- **主版本号**: 重大架构变更或不兼容更新
- **次版本号**: 新增功能或重要优化
- **修订号**: Bug修复或小幅改进

### 迭代流程

1. **修改Prompt文件**
   ```bash
   # 编辑对应的JSON文件
   vim prompts/agent_prompts.json
   ```

2. **更新版本信息**
   ```python
   pm.update_version("1.1.0", ["变更说明"], "作者")
   ```

3. **验证系统完整性**
   ```python
   validation = pm.validate_prompts()
   ```

4. **测试Agent行为**
   ```python
   python prompt_manager.py
   ```

## 最佳实践

### 1. Prompt设计原则
- **清晰明确**: 避免歧义表达
- **结构化**: 使用标准格式和层次
- **上下文相关**: 根据任务类型定制
- **安全优先**: 内置约束和验证

### 2. 版本管理
- **语义化版本**: 遵循标准版本规则
- **变更记录**: 详细记录每次修改
- **向后兼容**: 保持API稳定性
- **测试验证**: 充分测试新版本

### 3. 性能优化
- **缓存机制**: 避免重复文件读取
- **延迟加载**: 按需加载Prompt模板
- **压缩存储**: 优化JSON文件大小

## 故障排除

### 常见问题

1. **文件不存在错误**
   ```
   FileNotFoundError: Prompt file not found
   ```
   解决：检查prompts目录是否完整

2. **JSON格式错误**
   ```
   json.JSONDecodeError: Invalid JSON format
   ```
   解决：验证JSON文件语法

3. **模板变量缺失**
   ```
   KeyError: Missing template variable
   ```
   解决：检查模板变量定义

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 运行验证
pm = PromptManager()
validation = pm.validate_prompts()
```

## 扩展开发

### 添加新Agent类型

1. **更新agent_prompts.json**
   ```json
   {
     "new_agent": {
       "version": "1.0.0",
       "role_name": "新角色名称",
       "system_prompt": "角色描述...",
       "capabilities": ["能力列表"],
       "tools": ["工具列表"]
     }
   }
   ```

2. **更新constraint_prompts.json**
   ```json
   {
     "new_constraint": {
       "template": "约束模板...",
       "applicable_agents": ["new_agent"]
     }
   }
   ```

3. **更新task_prompts.json**
   ```json
   {
     "new_tasks": {
       "task_type": {
         "template": "任务模板...",
         "variables": ["变量列表"]
       }
     }
   }
   ```

4. **更新版本信息**
   ```python
   pm.update_version("1.1.0", ["添加新Agent类型"], "开发者")
   ```

## 总结

本Prompt管理系统实现了：

✅ **统一管理**: 所有Prompt模板集中管理  
✅ **版本控制**: 完整的版本追踪和迭代支持  
✅ **灵活配置**: 支持动态模板渲染和变量替换  
✅ **安全约束**: 内置多层安全和业务约束  
✅ **向后兼容**: 与现有系统无缝集成  
✅ **可扩展性**: 支持新Agent类型和任务模板  

这套系统为数字员工的智能化和规范化提供了坚实的基础，使得Prompt的维护和迭代变得更加高效和可控。
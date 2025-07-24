# 数字员工核心模块 (Digital Employee Core Module)

## 模块概述

数字员工核心模块是数字员工系统的主要业务逻辑实现，包含智能Prompt管理系统、多类型Agent实现框架以及测试验证工具。

## 核心特性

### 🎯 智能Prompt管理系统
- **企业级Prompt库**: 分层级、分场景的Prompt模板管理
- **版本控制**: 支持Prompt模板的版本管理和回滚
- **约束管理**: 安全性、合规性约束的统一管理
- **性能监控**: Prompt使用效果的实时监控和优化

### 🤖 多类型Agent实现
- **客户服务Agent**: 智能客服，处理咨询和投诉
- **数据分析Agent**: 自动化数据分析和报告生成
- **内容创作Agent**: 文档、文案、代码生成
- **项目管理Agent**: 任务分配、进度跟踪、风险评估
- **技术支持Agent**: 技术问题诊断和解决方案

### 🔧 测试验证框架
- **单元测试**: 组件级功能验证
- **集成测试**: 跨模块协作测试
- **性能测试**: 响应时间和并发能力测试
- **业务测试**: 真实场景模拟测试

## 快速开始

### 基础使用

```python
from digital_employee_core import (
    create_digital_employee_system,
    get_module_info,
    check_dependencies
)

# 检查模块状态
module_info = get_module_info()
print(f"模块: {module_info['name']} v{module_info['version']}")
print(f"组件可用: {module_info['components_available']}")

# 检查依赖
dependencies = check_dependencies()
for dep, info in dependencies.items():
    status = "✓" if info["available"] else "❌"
    print(f"{status} {dep}: {info.get('version', info.get('error'))}")

# 创建数字员工系统（如果组件可用）
if module_info['components_available']:
    system = create_digital_employee_system()
    print(f"系统创建成功，可用Agent: {len(system['available_agents'])}")
```

### Prompt管理使用

```python
from digital_employee_core import (
    create_prompt_manager,
    PromptTemplate,
    PromptConstraint
)

# 创建Prompt管理器
prompt_manager = create_prompt_manager()

# 创建Prompt模板
template = PromptTemplate(
    template_id="customer_service_greeting",
    name="客服问候模板",
    content="您好！我是{agent_name}，很高兴为您服务。请问有什么可以帮助您的吗？",
    category="customer_service",
    variables=["agent_name"],
    description="客服系统标准问候语模板"
)

# 添加约束
constraint = PromptConstraint(
    constraint_id="polite_language",
    name="礼貌用语约束",
    type="content_filter",
    rule="必须使用礼貌用语，避免不当表达",
    severity="high"
)

# 注册到管理器
prompt_manager.add_template(template)
prompt_manager.add_constraint(constraint)

# 使用模板
rendered_prompt = prompt_manager.render_template(
    "customer_service_greeting",
    {"agent_name": "小助手"}
)
print(f"渲染结果: {rendered_prompt}")
```

### Agent使用示例

```python
from digital_employee_core import (
    create_agent,
    CustomerServiceAgent,
    DataAnalysisAgent
)

# 创建客服Agent
customer_agent = create_agent(
    agent_type="CustomerServiceAgent",
    config={
        "name": "智能客服小助手",
        "department": "客户服务部",
        "specialties": ["产品咨询", "订单处理", "投诉处理"]
    }
)

# 处理客户咨询
response = customer_agent.handle_inquiry(
    customer_message="我想了解你们的产品功能",
    customer_context={
        "customer_id": "C001",
        "history": [],
        "priority": "normal"
    }
)

print(f"客服响应: {response}")

# 创建数据分析Agent
data_agent = create_agent(
    agent_type="DataAnalysisAgent",
    config={
        "name": "数据分析专家",
        "analysis_types": ["销售分析", "用户行为分析", "趋势预测"]
    }
)

# 执行数据分析任务
analysis_result = data_agent.analyze_data(
    data_source="sales_data.csv",
    analysis_type="monthly_report",
    parameters={
        "start_date": "2024-01-01",
        "end_date": "2024-07-31"
    }
)

print(f"分析结果: {analysis_result}")
```

## 模块结构

```
digital_employee_core/
├── __init__.py                 # 模块入口和API导出
├── prompt_manager.py           # Prompt管理系统
├── agent_implementations.py    # Agent实现框架
├── test_framework.py           # 测试验证框架
├── quick_test.py              # 快速测试工具
├── simple_test.py             # 简单测试示例
├── prompts/                   # Prompt模板库
│   ├── system_prompts.json    # 系统级提示词
│   ├── agent_prompts.json     # Agent专用提示词
│   ├── task_prompts.json      # 任务型提示词
│   ├── constraint_prompts.json # 约束条件提示词
│   └── version.json           # 版本信息
└── README.md                  # 本文档
```

## API 参考

### Prompt管理系统

#### PromptManager 主管理器
```python
class PromptManager:
    def add_template(self, template: PromptTemplate) -> bool
    def get_template(self, template_id: str) -> Optional[PromptTemplate]
    def render_template(self, template_id: str, variables: Dict[str, Any]) -> str
    def add_constraint(self, constraint: PromptConstraint) -> bool
    def validate_content(self, content: str) -> ValidationResult
    def get_usage_statistics(self) -> Dict[str, Any]
```

#### PromptTemplate 模板类
```python
@dataclass
class PromptTemplate:
    template_id: str              # 模板唯一ID
    name: str                    # 模板名称
    content: str                 # 模板内容
    category: str                # 分类
    variables: List[str]         # 变量列表
    constraints: List[str] = []  # 约束ID列表
    metadata: Dict[str, Any] = None
    created_at: float = 0.0
    updated_at: float = 0.0
    version: str = "1.0.0"
    active: bool = True
```

### Agent实现框架

#### DigitalEmployeeAgent 基类
```python
class DigitalEmployeeAgent:
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any])
    def process_input(self, input_data: Any, context: Dict[str, Any]) -> AgentResponse
    def get_capabilities(self) -> List[str]
    def get_status(self) -> Dict[str, Any]
    def update_config(self, new_config: Dict[str, Any]) -> bool
```

#### 专业Agent类型

**CustomerServiceAgent 客服Agent**
```python
class CustomerServiceAgent(DigitalEmployeeAgent):
    def handle_inquiry(self, customer_message: str, customer_context: Dict) -> str
    def process_complaint(self, complaint_data: Dict) -> Dict[str, Any]
    def escalate_issue(self, issue_data: Dict) -> bool
```

**DataAnalysisAgent 数据分析Agent**
```python
class DataAnalysisAgent(DigitalEmployeeAgent):
    def analyze_data(self, data_source: str, analysis_type: str, parameters: Dict) -> Dict
    def generate_report(self, analysis_results: Dict, report_format: str) -> str
    def create_visualization(self, data: Dict, chart_type: str) -> str
```

**ContentCreationAgent 内容创作Agent**
```python
class ContentCreationAgent(DigitalEmployeeAgent):
    def create_document(self, doc_type: str, requirements: Dict) -> str
    def generate_code(self, language: str, specifications: Dict) -> str
    def write_marketing_copy(self, product_info: Dict, target_audience: str) -> str
```

### 配置选项

```python
DEFAULT_AGENT_CONFIG = {
    "max_conversation_history": 50,
    "response_timeout": 30,
    "enable_memory_integration": True,
    "log_level": "INFO",
    "enable_prompt_caching": True,
    "max_prompt_cache_size": 100
}
```

## 测试框架

### 运行测试套件

```python
from digital_employee_core.test_framework import DigitalEmployeeTestFramework

# 创建测试框架
test_framework = DigitalEmployeeTestFramework()

# 运行完整测试套件
test_framework.run_comprehensive_test_suite()

# 运行特定测试
test_framework.test_prompt_management()
test_framework.test_agent_implementations()
test_framework.test_integration_scenarios()
```

### 自定义测试

```python
from digital_employee_core.test_framework import TestCase, TestResult

class CustomTest(TestCase):
    def test_custom_functionality(self):
        # 自定义测试逻辑
        result = self.target_function()
        self.assert_equals(result, expected_value)
        return TestResult.PASS

# 注册并运行
test_framework.add_test_case(CustomTest())
test_framework.run_tests()
```

## 性能优化

### Prompt缓存优化

```python
# 启用Prompt缓存
config = {
    "enable_prompt_caching": True,
    "max_prompt_cache_size": 200,
    "cache_ttl": 3600  # 1小时过期
}

prompt_manager = create_prompt_manager(config)
```

### Agent并发处理

```python
import asyncio
from digital_employee_core import create_agent

async def handle_multiple_requests():
    agent = create_agent("CustomerServiceAgent")
    
    # 并发处理多个请求
    tasks = [
        agent.handle_inquiry_async(msg1, ctx1),
        agent.handle_inquiry_async(msg2, ctx2),
        agent.handle_inquiry_async(msg3, ctx3)
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

## 集成示例

### 与记忆引擎集成

```python
from memory_engine_module import create_memory_system, InputType
from digital_employee_core import create_agent

# 创建记忆系统和Agent
memory_system = create_memory_system()
customer_agent = create_agent("CustomerServiceAgent")

# 集成工作流
def integrated_customer_service(customer_message, customer_context):
    # 1. 使用记忆系统处理输入
    memory_result = memory_system.process(
        customer_message,
        InputType.QUERY,
        {"source": "customer", "agent_type": "customer_service"}
    )
    
    # 2. Agent基于记忆结果生成响应
    enhanced_context = {
        **customer_context,
        "memory_insights": memory_result.response,
        "confidence": memory_result.confidence,
        "activated_memories": memory_result.activated_memories
    }
    
    # 3. 生成最终响应
    agent_response = customer_agent.handle_inquiry(
        customer_message, 
        enhanced_context
    )
    
    # 4. 将交互结果存入记忆
    interaction_event = {
        "description": f"客服处理: {customer_message[:50]}...",
        "participants": ["customer", "customer_service_agent"],
        "actions": ["receive_inquiry", "analyze_context", "provide_response"],
        "results": [agent_response[:50] + "..."]
    }
    
    memory_system.process(
        interaction_event,
        InputType.EVENT,
        {"source": "service_interaction"}
    )
    
    return agent_response

# 使用集成系统
response = integrated_customer_service(
    "我的订单什么时候能到？",
    {"customer_id": "C123", "order_id": "O456"}
)
```

## 故障排除

### 常见问题

1. **组件导入失败**
   ```python
   # 检查组件可用性
   from digital_employee_core import get_module_info
   
   info = get_module_info()
   if not info['components_available']:
       print(f"导入错误: {info.get('import_error', '未知错误')}")
   ```

2. **Prompt渲染失败**
   ```python
   # 检查模板变量
   template = prompt_manager.get_template("template_id")
   print(f"必需变量: {template.variables}")
   
   # 提供所有必需变量
   result = prompt_manager.render_template(
       "template_id",
       {var: "default_value" for var in template.variables}
   )
   ```

3. **Agent响应超时**
   ```python
   # 调整超时配置
   config = DEFAULT_AGENT_CONFIG.copy()
   config["response_timeout"] = 60  # 增加到60秒
   
   agent = create_agent("AgentType", config)
   ```

### 调试模式

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('digital_employee_core')
logger.setLevel(logging.DEBUG)

# 启用测试模式
from digital_employee_core import DEFAULT_AGENT_CONFIG
config = DEFAULT_AGENT_CONFIG.copy()
config["debug_mode"] = True
config["log_level"] = "DEBUG"
```

## 扩展开发

### 自定义Agent类型

```python
from digital_employee_core import DigitalEmployeeAgent, AgentResponse

class CustomAgent(DigitalEmployeeAgent):
    def __init__(self, agent_id: str, name: str, config: Dict[str, Any]):
        super().__init__(agent_id, name, config)
        self.custom_capabilities = config.get("custom_capabilities", [])
    
    def process_input(self, input_data: Any, context: Dict[str, Any]) -> AgentResponse:
        # 自定义处理逻辑
        response_text = f"Custom processing: {input_data}"
        
        return AgentResponse(
            content=response_text,
            confidence=0.8,
            metadata={"custom_field": "custom_value"}
        )
    
    def get_capabilities(self) -> List[str]:
        base_capabilities = super().get_capabilities()
        return base_capabilities + self.custom_capabilities

# 注册自定义Agent
from digital_employee_core.agent_implementations import register_agent_type
register_agent_type("CustomAgent", CustomAgent)
```

### 自定义Prompt约束

```python
from digital_employee_core import PromptConstraint, ValidationResult

def custom_constraint_validator(content: str, constraint: PromptConstraint) -> ValidationResult:
    # 自定义验证逻辑
    if "forbidden_word" in content:
        return ValidationResult(
            is_valid=False,
            error_message="包含禁用词汇",
            suggestions=["请使用更合适的表达"]
        )
    return ValidationResult(is_valid=True)

# 注册自定义约束
from digital_employee_core.prompt_manager import register_constraint_validator
register_constraint_validator("custom_filter", custom_constraint_validator)
```

## 版本信息

- **当前版本**: 1.0.0
- **Python要求**: >= 3.7
- **可选依赖**: requests (HTTP支持)

## 许可证

本模块是数字员工系统的一部分，遵循项目整体许可证。

---

更多详细信息请参考各组件的具体文档和源代码注释。
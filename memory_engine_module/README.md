# 记忆引擎模块 (Memory Engine Module)

## 模块概述

记忆引擎模块是数字员工Agent认知能力的核心基石，实现了模拟人类记忆认知过程的分层动态记忆系统。

## 核心特性

### 🧠 五层记忆体系
- **工作记忆**: 短期注意力焦点，处理当前对话上下文
- **情景记忆**: 具体事件序列，记录时间-地点-动作-结果
- **语义记忆**: 抽象概念知识，构建规则关系网络
- **程序性记忆**: 技能操作流程，存储API调用模式
- **情感记忆**: 决策情感反馈，基于用户满意度加权

### 🔄 动态记忆重构
- **关联检索**: 基于图神经网络的跨层记忆关联分析
- **记忆衰减**: 多种衰减算法（指数、幂律、艾宾浩斯遗忘曲线）
- **记忆融合**: 简化Transformer架构的跨记忆融合器

### 🔍 感知-记忆闭环
- **输入处理**: 多类型输入解析和特征提取
- **记忆匹配**: 智能记忆检索和相关性评分
- **推理引擎**: 基于激活记忆的多策略推理
- **响应生成**: 融合多记忆源的综合响应

## 快速开始

### 安装依赖

```bash
pip install numpy networkx
```

### 基础使用

```python
from memory_engine_module import create_memory_system, InputType

# 创建记忆系统
memory_system = create_memory_system()

# 处理文本查询
result = memory_system.process(
    "我需要帮助生成报告",
    InputType.QUERY,
    {"source": "user", "urgency": "high"}
)

print(f"响应: {result.response}")
print(f"置信度: {result.confidence}")
print(f"激活记忆数: {len(result.activated_memories)}")
```

### 高级使用

```python
from memory_engine_module import (
    WorkingMemoryNode, EpisodicMemoryNode, SemanticMemoryNode,
    MemoryGraph, AssociationDetector, MemoryFusionEngine
)

# 创建自定义记忆节点
working_memory = WorkingMemoryNode(
    id="work_001",
    content="用户当前对话内容",
    timestamp=time.time(),
    attention_score=0.9
)

# 创建情景记忆
episode_memory = EpisodicMemoryNode(
    id="episode_001", 
    content="成功处理客户投诉",
    timestamp=time.time(),
    location="客服系统",
    participants=["客户", "客服agent"],
    actions=["接收投诉", "分析问题", "提供解决方案"],
    results=["问题解决", "客户满意"]
)

# 使用记忆图谱分析关联
memory_graph = MemoryGraph()
memory_graph.add_memory_node(working_memory)
memory_graph.add_memory_node(episode_memory)

# 检测记忆关联
detector = AssociationDetector()
associations = detector.detect_associations(working_memory, episode_memory)

for assoc in associations:
    print(f"发现{assoc.association_type}关联，强度: {assoc.strength:.2f}")
```

## 模块结构

```
memory_engine_module/
├── __init__.py                 # 模块入口和API导出
├── memory_engine.py            # 核心记忆层实现
├── memory_reconstruction.py    # 动态重构机制
├── memory_perception_loop.py   # 感知-记忆闭环
├── memory_system_demo.py       # 演示和测试代码
└── README.md                   # 本文档
```

## API 参考

### 核心类

#### MemoryNode 记忆节点基类
```python
@dataclass
class MemoryNode:
    id: str                    # 唯一标识
    content: Any              # 记忆内容
    timestamp: float          # 创建时间戳
    access_count: int = 0     # 访问次数
    last_access: float = 0.0  # 最后访问时间
    weight: float = 1.0       # 记忆权重
    connections: List[str]    # 关联记忆ID列表
    metadata: Dict[str, Any]  # 元数据
```

#### MemoryPerceptionLoop 主控制器
```python
class MemoryPerceptionLoop:
    def process(self, raw_input: Any, input_type: InputType, 
               context: Dict[str, Any] = None) -> ReasoningResult
    def get_memory_status(self) -> Dict[str, Any]
    def get_processing_stats(self) -> Dict[str, Any]
```

### 输入类型

```python
class InputType(Enum):
    TEXT = "text"        # 文本输入
    EVENT = "event"      # 事件输入  
    KNOWLEDGE = "knowledge"  # 知识输入
    SKILL = "skill"      # 技能输入
    EMOTION = "emotion"  # 情感输入
    QUERY = "query"      # 查询输入
```

### 配置选项

```python
DEFAULT_MEMORY_CONFIG = {
    "working_memory_capacity": 20,
    "episodic_memory_capacity": 1000,
    "semantic_memory_capacity": 5000,
    "procedural_memory_capacity": 500,
    "emotional_memory_capacity": 1000,
    "memory_decay_rate": 0.1,
    "association_threshold": 0.6,
    "fusion_confidence_threshold": 0.5
}
```

## 演示和测试

### 运行完整演示

```python
from memory_engine_module.memory_system_demo import MemorySystemDemo

demo = MemorySystemDemo()
demo.run_complete_demo()
```

### 运行单元测试

```python
from memory_engine_module.memory_system_demo import run_unit_tests

run_unit_tests()
```

### 交互式体验

```python
from memory_engine_module.memory_system_demo import interactive_demo

interactive_demo()
```

## 性能指标

- **处理延迟**: < 100ms
- **记忆容量**: 总计7,520个记忆节点
- **关联检测**: 支持4种关联类型
- **衰减算法**: 3种可选算法
- **并发支持**: 支持多线程访问

## 扩展开发

### 自定义记忆类型

```python
@dataclass
class CustomMemoryNode(MemoryNode):
    custom_field: str = ""
    
    def custom_method(self):
        # 自定义逻辑
        pass
```

### 自定义记忆层

```python
class CustomMemoryLayer(MemoryLayer):
    def store(self, memory: MemoryNode) -> bool:
        # 自定义存储逻辑
        pass
    
    def retrieve(self, query: Any, top_k: int = 5) -> List[MemoryNode]:
        # 自定义检索逻辑
        pass
```

### 自定义衰减算法

```python
def custom_decay_function(initial_weight: float, time_passed: float) -> float:
    # 自定义衰减逻辑
    return modified_weight

# 注册到系统
MemoryDecayAlgorithm.custom_decay = custom_decay_function
```

## 故障排除

### 常见问题

1. **导入错误**: 确保安装了必要的依赖包
   ```bash
   pip install numpy networkx
   ```

2. **内存使用过高**: 调整记忆层容量限制
   ```python
   config = DEFAULT_MEMORY_CONFIG.copy()
   config["semantic_memory_capacity"] = 1000  # 降低容量
   ```

3. **响应速度慢**: 启用记忆衰减和清理
   ```python
   # 定期执行记忆衰减
   for layer in memory_system.memory_layers.values():
       layer.decay_memories()
   ```

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 启用详细日志
logger = logging.getLogger('memory_engine_module')
logger.setLevel(logging.DEBUG)
```

## 版本信息

- **当前版本**: 1.0.0
- **Python要求**: >= 3.7
- **依赖包**: numpy, networkx, python-louvain (可选)

## 许可证

本模块是数字员工系统的一部分，遵循项目整体许可证。

---

更多详细文档请参考: [MEMORY_ENGINE_README.md](./MEMORY_ENGINE_README.md)
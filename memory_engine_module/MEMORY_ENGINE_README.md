# 数字员工Agent分层动态记忆引擎

## 概述

本项目实现了一个模拟人类记忆认知过程的分层动态记忆引擎，作为数字员工Agent认知能力的核心基石。系统设计基于认知科学中的记忆分层理论，包含工作记忆、情景记忆、语义记忆、程序性记忆和情感记忆五个层级，具备动态重构、关联检索和记忆融合能力。

## 核心特性

### 🧠 五层记忆体系

| 记忆层级 | 存储内容 | 认知类比 | 容量限制 |
|---------|---------|---------|---------|
| **工作记忆** | 对话上下文、临时数据 | 短期注意力焦点 | 20 |
| **情景记忆** | 具体事件序列 | 经历回忆与故事重构 | 1000 |
| **语义记忆** | 抽象概念、规则关系 | 知识网络与逻辑推理 | 5000 |
| **程序性记忆** | 技能操作流程 | 肌肉记忆与熟练度 | 500 |
| **情感记忆** | 决策情感反馈 | 情感经验影响决策 | 1000 |

### 🔄 动态记忆重构机制

- **关联检索**: 基于图神经网络的跨层记忆关联分析
- **记忆衰减**: 多种衰减算法（指数、幂律、艾宾浩斯遗忘曲线）
- **记忆融合**: Transformer架构的跨记忆融合器

### 🔍 记忆-感知闭环

```
信息输入 → 工作记忆缓冲 → 记忆匹配引擎 → 激活记忆/创建新记忆 → 推理引擎 → 响应输出
     ↑                                                                    ↓
     ←←←←←←←←←←←←←← 记忆更新与关联建立 ←←←←←←←←←←←←←←←←←←
```

## 项目结构

```
记忆引擎/
├── memory_engine.py              # 核心记忆层实现
├── memory_reconstruction.py      # 动态重构机制
├── memory_perception_loop.py     # 感知-记忆闭环
├── memory_system_demo.py         # 演示与测试代码
├── MEMORY_ENGINE_README.md       # 本文档
└── requirements.txt              # 依赖列表（已更新）
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 可选：安装图社区检测库（用于记忆聚类）
pip install python-louvain
```

### 2. 基础使用

```python
from memory_perception_loop import create_memory_perception_system, InputType

# 创建记忆系统
memory_system = create_memory_perception_system()

# 处理用户查询
result = memory_system.process(
    "我需要生成一份销售报告",
    InputType.QUERY,
    {"source": "user", "urgency": "high"}
)

print(f"响应: {result.response}")
print(f"置信度: {result.confidence}")
print(f"激活记忆数: {len(result.activated_memories)}")
```

### 3. 运行演示

```bash
python memory_system_demo.py
```

选择运行模式：
- **1. 完整演示**: 展示所有功能模块
- **2. 单元测试**: 验证核心组件功能
- **3. 交互式演示**: 实时交互体验

## 核心组件详解

### 记忆节点类型

```python
# 工作记忆 - 短期缓存
WorkingMemoryNode(
    content="用户询问报告生成",
    attention_score=0.9,
    context_window=10
)

# 情景记忆 - 事件序列
EpisodicMemoryNode(
    content="成功生成Q3销售报告",
    location="工作系统",
    participants=["用户", "系统"],
    actions=["数据收集", "分析", "生成"],
    results=["完整报告", "用户满意"]
)

# 语义记忆 - 知识概念
SemanticMemoryNode(
    content="报告生成流程包含三个步骤",
    concepts=["数据收集", "分析", "可视化"],
    rules=["先收集再分析", "分析后可视化"]
)

# 程序性记忆 - 技能流程
ProceduralMemoryNode(
    skill_type="报告生成",
    steps=[
        {"step": 1, "action": "确定需求"},
        {"step": 2, "action": "收集数据"},
        {"step": 3, "action": "分析处理"}
    ],
    success_rate=0.85
)

# 情感记忆 - 情感反馈
EmotionalMemoryNode(
    emotion_type="satisfaction",
    valence=0.8,      # 情感效价 (-1到1)
    arousal=0.6,      # 唤醒度 (0到1)
    user_satisfaction=0.9,
    decision_context="成功完成任务"
)
```

### 记忆关联类型

- **语义关联**: 基于内容相似度的概念关联
- **时间关联**: 基于时间邻近性的序列关联  
- **因果关联**: 检测原因-结果关系链
- **情感关联**: 基于情感状态的体验关联

### 记忆衰减算法

```python
# 指数衰减
weight = initial * exp(-decay_rate * time_passed)

# 幂律衰减（更符合人类遗忘曲线）
weight = initial / (1 + time_passed) ** alpha

# 艾宾浩斯遗忘曲线
weight = initial * exp(-sensitivity * time_passed / strength)
```

## 高级功能

### 跨层记忆检索

```python
# 一次查询检索所有记忆层
retrieval_result = cross_layer_retriever.cross_layer_retrieve(
    query="报告生成流程",
    max_results=10
)

# 结果包含：
# - primary_results: 主要检索结果
# - layer_breakdown: 各层详细结果
# - fused_response: 融合后的响应
# - associated_memories: 关联记忆
```

### 记忆融合引擎

基于简化的Transformer注意力机制，将多个相关记忆融合生成综合响应：

```python
fusion_result = fusion_engine.fuse_memories(memories, query_embedding)

# 返回：
# - fused_content: 融合内容
# - confidence: 融合置信度
# - sources: 来源记忆信息
# - attention_weights: 注意力权重分布
```

### 记忆图谱与聚类

- 构建记忆节点间的关联图谱
- 支持社区发现算法进行记忆聚类
- 提供关联路径分析和记忆网络可视化

## 性能特性

### 容量管理
- **工作记忆**: 20个节点（FIFO淘汰）
- **情景记忆**: 1000个节点（权重淘汰）
- **语义记忆**: 5000个节点（访问频率淘汰）
- **程序性记忆**: 500个节点（成功率淘汰）
- **情感记忆**: 1000个节点（时间+权重淘汰）

### 实时处理能力
- 平均处理延迟: < 100ms
- 支持并发记忆访问
- 动态权重更新与衰减

### 可扩展性
- 模块化设计，支持自定义记忆类型
- 可插拔的衰减算法和融合策略
- 支持持久化存储（SQLite/PostgreSQL）

## 应用场景

### 1. 智能客服Agent
- 记住用户历史问题和偏好
- 学习最佳回答模式
- 情感化交互体验

### 2. 个人助理Agent  
- 长期记忆用户习惯和需求
- 学习工作流程和技能
- 提供个性化建议

### 3. 知识工作Agent
- 积累领域专业知识
- 学习最佳实践流程
- 基于经验优化决策

### 4. 教育培训Agent
- 记忆学习者的知识状态
- 个性化教学策略调整
- 学习效果反馈机制

## 技术架构

### 设计原则
1. **分层抽象**: 清晰的记忆层级划分
2. **动态适应**: 基于使用模式的自适应调整
3. **关联学习**: 自动发现和强化记忆关联
4. **情感驱动**: 情感记忆影响决策权重
5. **可解释性**: 提供推理路径和置信度

### 核心算法
- **记忆匹配**: 基于向量相似度和语义匹配
- **关联检测**: 多维度关联关系识别
- **注意力机制**: 简化Transformer架构
- **图神经网络**: 记忆关联图的学习与推理

## 开发指南

### 自定义记忆类型

```python
@dataclass
class CustomMemoryNode(MemoryNode):
    custom_field: str = ""
    custom_data: Dict[str, Any] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.custom_data is None:
            self.custom_data = {}
```

### 自定义记忆层

```python
class CustomMemoryLayer(MemoryLayer):
    def store(self, memory: MemoryNode) -> bool:
        # 实现自定义存储逻辑
        pass
    
    def retrieve(self, query: Any, top_k: int = 5) -> List[MemoryNode]:
        # 实现自定义检索逻辑
        pass
```

### 自定义衰减算法

```python
def custom_decay(initial_weight: float, time_passed: float, **kwargs) -> float:
    # 实现自定义衰减逻辑
    return modified_weight
```

## 测试与验证

### 单元测试
```bash
python memory_system_demo.py
# 选择 "2. 单元测试"
```

### 功能测试
- 记忆存储与检索准确性
- 关联关系检测精度
- 记忆衰减算法有效性
- 跨层融合质量评估

### 性能测试
- 大规模记忆存储性能
- 并发访问处理能力
- 记忆检索响应时间
- 内存使用效率

## 监控与调试

### 系统状态监控
```python
# 获取记忆层状态
memory_status = memory_system.get_memory_status()

# 获取处理统计
processing_stats = memory_system.get_processing_stats()
```

### 日志配置
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 未来发展方向

### 短期计划
- [ ] 持久化存储支持
- [ ] 记忆压缩与归档机制
- [ ] 更精确的情感分析模型
- [ ] Web API接口封装

### 中期计划  
- [ ] 分布式记忆存储
- [ ] 强化学习优化记忆策略
- [ ] 多模态记忆支持（图像、音频）
- [ ] 记忆网络可视化工具

### 长期愿景
- [ ] 神经网络记忆编码
- [ ] 量子计算记忆加速
- [ ] 脑科学启发的记忆机制
- [ ] 集体智能记忆网络

## 参考文献

1. [MemoryOS - GitHub](https://github.com/BAI-LAB/MemoryOS)
2. [认知架构中的记忆系统 - 知乎](https://zhuanlan.zhihu.com/p/18312278393)
3. [AI Agent的记忆系统设计 - CSDN](https://blog.csdn.net/sinat_28461591/article/details/148390608)
4. [大模型长期记忆机制 - 知乎](https://zhuanlan.zhihu.com/p/1928787696622473952)

## 贡献指南

欢迎提交Issue和Pull Request来改进记忆引擎！

### 贡献类型
- 🐛 Bug报告和修复
- ✨ 新功能建议和实现
- 📝 文档改进和示例
- ⚡ 性能优化
- 🧪 测试用例增加

### 开发流程
1. Fork项目并创建功能分支
2. 编写代码并添加测试
3. 确保所有测试通过
4. 提交Pull Request

---

**版本**: 1.0.0  
**更新时间**: 2024-07-24  
**作者**: Digital Employee System Team
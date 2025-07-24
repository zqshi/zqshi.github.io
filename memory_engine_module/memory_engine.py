"""
数字员工Agent分层动态记忆引擎

模拟人类记忆的分层性、组织/关联性、动态重构特性
包含五个记忆层级：工作记忆、情景记忆、语义记忆、程序性记忆、情感记忆
"""

import json
import time
import math
import hashlib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import sqlite3
import pickle
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryNode:
    """记忆节点基类"""
    id: str
    content: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    weight: float = 1.0
    connections: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
        if self.metadata is None:
            self.metadata = {}
        if self.last_access == 0.0:
            self.last_access = self.timestamp

@dataclass
class WorkingMemoryNode(MemoryNode):
    """工作记忆节点 - 短期注意力焦点"""
    context_window: int = 10  # 上下文窗口大小
    attention_score: float = 1.0
    
@dataclass  
class EpisodicMemoryNode(MemoryNode):
    """情景记忆节点 - 具象化事件序列"""
    location: str = ""
    participants: List[str] = None
    actions: List[str] = None
    results: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.participants is None:
            self.participants = []
        if self.actions is None:
            self.actions = []
        if self.results is None:
            self.results = []

@dataclass
class SemanticMemoryNode(MemoryNode):
    """语义记忆节点 - 抽象知识"""
    concepts: List[str] = None
    rules: List[str] = None
    relationships: Dict[str, List[str]] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.concepts is None:
            self.concepts = []
        if self.rules is None:
            self.rules = []
        if self.relationships is None:
            self.relationships = {}

@dataclass
class ProceduralMemoryNode(MemoryNode):
    """程序性记忆节点 - 技能操作流程"""
    skill_type: str = ""
    steps: List[Dict[str, Any]] = None
    success_rate: float = 0.0
    usage_frequency: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        if self.steps is None:
            self.steps = []

@dataclass
class EmotionalMemoryNode(MemoryNode):
    """情感记忆节点 - 历史决策的情感反馈"""
    emotion_type: str = ""
    valence: float = 0.0  # 情感效价 (-1到1)
    arousal: float = 0.0  # 情感唤醒度 (0到1)
    user_satisfaction: float = 0.0  # 用户满意度
    decision_context: str = ""

class MemoryDecayAlgorithm:
    """记忆衰减算法"""
    
    @staticmethod
    def exponential_decay(initial_weight: float, time_passed: float, decay_rate: float = 0.1) -> float:
        """指数衰减"""
        return initial_weight * math.exp(-decay_rate * time_passed)
    
    @staticmethod
    def power_law_decay(initial_weight: float, time_passed: float, alpha: float = 0.5) -> float:
        """幂律衰减 - 更符合人类遗忘曲线"""
        return initial_weight / (1 + time_passed) ** alpha
    
    @staticmethod
    def ebbinghaus_forgetting_curve(initial_weight: float, time_passed: float, 
                                   strength: float = 1.0, sensitivity: float = 1.0) -> float:
        """艾宾浩斯遗忘曲线"""
        return initial_weight * math.exp(-sensitivity * time_passed / strength)

class MemoryLayer(ABC):
    """记忆层抽象基类"""
    
    def __init__(self, name: str, capacity: int = 1000):
        self.name = name
        self.capacity = capacity
        self.memories: Dict[str, MemoryNode] = {}
        self.access_history = deque(maxlen=1000)
        
    @abstractmethod
    def store(self, memory: MemoryNode) -> bool:
        """存储记忆"""
        pass
    
    @abstractmethod
    def retrieve(self, query: Any, top_k: int = 5) -> List[MemoryNode]:
        """检索记忆"""
        pass
    
    def update_access(self, memory_id: str):
        """更新访问记录"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            memory.access_count += 1
            memory.last_access = time.time()
            self.access_history.append((memory_id, time.time()))
    
    def decay_memories(self):
        """记忆衰减处理"""
        current_time = time.time()
        for memory_id, memory in self.memories.items():
            time_passed = (current_time - memory.last_access) / 3600  # 小时为单位
            memory.weight = MemoryDecayAlgorithm.power_law_decay(
                memory.weight, time_passed
            )
    
    def get_size(self) -> int:
        """获取当前记忆数量"""
        return len(self.memories)
    
    def is_full(self) -> bool:
        """检查是否已满"""
        return len(self.memories) >= self.capacity

class WorkingMemory(MemoryLayer):
    """工作记忆 - 短期缓存"""
    
    def __init__(self, capacity: int = 20):
        super().__init__("WorkingMemory", capacity)
        self.attention_buffer = deque(maxlen=capacity)
    
    def store(self, memory: WorkingMemoryNode) -> bool:
        if self.is_full():
            # 移除最旧的记忆
            oldest_id = min(self.memories.keys(), 
                           key=lambda x: self.memories[x].last_access)
            del self.memories[oldest_id]
        
        self.memories[memory.id] = memory
        self.attention_buffer.append(memory.id)
        logger.info(f"存储工作记忆: {memory.id}")
        return True
    
    def retrieve(self, query: str, top_k: int = 5) -> List[WorkingMemoryNode]:
        # 简单的关键词匹配检索
        results = []
        for memory in self.memories.values():
            if isinstance(memory.content, str) and query.lower() in memory.content.lower():
                results.append(memory)
                self.update_access(memory.id)
        
        # 按注意力分数和时间排序
        results.sort(key=lambda x: (x.attention_score, x.timestamp), reverse=True)
        return results[:top_k]

class EpisodicMemory(MemoryLayer):
    """情景记忆 - 事件序列"""
    
    def __init__(self, capacity: int = 1000):
        super().__init__("EpisodicMemory", capacity)
        self.event_timeline = []
    
    def store(self, memory: EpisodicMemoryNode) -> bool:
        if self.is_full():
            # 移除权重最低的记忆
            lowest_weight_id = min(self.memories.keys(),
                                 key=lambda x: self.memories[x].weight)
            del self.memories[lowest_weight_id]
        
        self.memories[memory.id] = memory
        self.event_timeline.append((memory.timestamp, memory.id))
        self.event_timeline.sort()  # 保持时间顺序
        logger.info(f"存储情景记忆: {memory.id}")
        return True
    
    def retrieve(self, query: str, top_k: int = 5) -> List[EpisodicMemoryNode]:
        results = []
        for memory in self.memories.values():
            # 检索匹配的事件
            if (query.lower() in memory.content.lower() or 
                any(query.lower() in action.lower() for action in memory.actions)):
                results.append(memory)
                self.update_access(memory.id)
        
        # 按权重和时间排序
        results.sort(key=lambda x: (x.weight, x.timestamp), reverse=True)
        return results[:top_k]
    
    def get_events_by_timerange(self, start_time: float, end_time: float) -> List[EpisodicMemoryNode]:
        """根据时间范围获取事件"""
        events = []
        for timestamp, memory_id in self.event_timeline:
            if start_time <= timestamp <= end_time:
                events.append(self.memories[memory_id])
        return events

class SemanticMemory(MemoryLayer):
    """语义记忆 - 概念知识"""
    
    def __init__(self, capacity: int = 5000):
        super().__init__("SemanticMemory", capacity)
        self.concept_graph = defaultdict(set)  # 概念关系图
        
    def store(self, memory: SemanticMemoryNode) -> bool:
        if self.is_full():
            # 移除访问频率最低的记忆
            lowest_access_id = min(self.memories.keys(),
                                 key=lambda x: self.memories[x].access_count)
            del self.memories[lowest_access_id]
        
        self.memories[memory.id] = memory
        
        # 构建概念关系图
        for concept in memory.concepts:
            self.concept_graph[concept].add(memory.id)
            
        logger.info(f"存储语义记忆: {memory.id}")
        return True
    
    def retrieve(self, query: str, top_k: int = 5) -> List[SemanticMemoryNode]:
        results = []
        
        # 概念匹配
        for memory in self.memories.values():
            score = 0
            if query.lower() in memory.content.lower():
                score += 2
            if any(query.lower() in concept.lower() for concept in memory.concepts):
                score += 3
            if any(query.lower() in rule.lower() for rule in memory.rules):
                score += 1
                
            if score > 0:
                memory.metadata['relevance_score'] = score
                results.append(memory)
                self.update_access(memory.id)
        
        # 按相关性分数排序
        results.sort(key=lambda x: x.metadata.get('relevance_score', 0), reverse=True)
        return results[:top_k]

class ProceduralMemory(MemoryLayer):
    """程序性记忆 - 技能流程"""
    
    def __init__(self, capacity: int = 500):
        super().__init__("ProceduralMemory", capacity)
        self.skill_index = defaultdict(list)
        
    def store(self, memory: ProceduralMemoryNode) -> bool:
        if self.is_full():
            # 移除成功率最低的记忆
            lowest_success_id = min(self.memories.keys(),
                                  key=lambda x: self.memories[x].success_rate)
            del self.memories[lowest_success_id]
        
        self.memories[memory.id] = memory
        self.skill_index[memory.skill_type].append(memory.id)
        logger.info(f"存储程序性记忆: {memory.id}")
        return True
    
    def retrieve(self, query: str, top_k: int = 5) -> List[ProceduralMemoryNode]:
        results = []
        
        # 技能类型匹配
        if query in self.skill_index:
            for memory_id in self.skill_index[query]:
                results.append(self.memories[memory_id])
                self.update_access(memory_id)
        
        # 内容匹配
        for memory in self.memories.values():
            if query.lower() in memory.content.lower():
                if memory not in results:
                    results.append(memory)
                    self.update_access(memory.id)
        
        # 按成功率和使用频率排序
        results.sort(key=lambda x: (x.success_rate, x.usage_frequency), reverse=True)
        return results[:top_k]

class EmotionalMemory(MemoryLayer):
    """情感记忆 - 情感反馈"""
    
    def __init__(self, capacity: int = 1000):
        super().__init__("EmotionalMemory", capacity)
        self.emotion_clusters = defaultdict(list)
        
    def store(self, memory: EmotionalMemoryNode) -> bool:
        if self.is_full():
            # 移除最旧且权重最低的记忆
            oldest_low_weight_id = min(self.memories.keys(),
                                     key=lambda x: (self.memories[x].weight, 
                                                   self.memories[x].timestamp))
            del self.memories[oldest_low_weight_id]
        
        self.memories[memory.id] = memory
        self.emotion_clusters[memory.emotion_type].append(memory.id)
        logger.info(f"存储情感记忆: {memory.id}")
        return True
    
    def retrieve(self, query: str, top_k: int = 5) -> List[EmotionalMemoryNode]:
        results = []
        
        # 情感类型匹配
        if query in self.emotion_clusters:
            for memory_id in self.emotion_clusters[query]:
                results.append(self.memories[memory_id])
                self.update_access(memory_id)
        
        # 决策上下文匹配
        for memory in self.memories.values():
            if query.lower() in memory.decision_context.lower():
                if memory not in results:
                    results.append(memory)
                    self.update_access(memory.id)
        
        # 按用户满意度和情感强度排序
        results.sort(key=lambda x: (x.user_satisfaction, abs(x.valence) + x.arousal), 
                    reverse=True)
        return results[:top_k]
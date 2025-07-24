"""
记忆-感知闭环系统

实现信息输入 -> 工作记忆缓冲 -> 记忆匹配引擎 -> 激活记忆/创建新记忆 -> 推理引擎
模拟人类认知的感知-记忆-推理闭环过程
"""

import time
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from collections import deque

from memory_engine import (
    MemoryNode, WorkingMemoryNode, EpisodicMemoryNode, 
    SemanticMemoryNode, ProceduralMemoryNode, EmotionalMemoryNode,
    WorkingMemory, EpisodicMemory, SemanticMemory, 
    ProceduralMemory, EmotionalMemory
)
from memory_reconstruction import (
    MemoryGraph, AssociationDetector, MemoryFusionEngine, 
    CrossLayerRetriever, create_memory_reconstruction_system
)

logger = logging.getLogger(__name__)

class InputType(Enum):
    """输入信息类型"""
    TEXT = "text"
    EVENT = "event"
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    EMOTION = "emotion"
    QUERY = "query"

@dataclass
class PerceptionInput:
    """感知输入数据结构"""
    id: str
    content: Any
    input_type: InputType
    timestamp: float
    context: Dict[str, Any] = None
    source: str = ""
    priority: float = 1.0
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class MemoryMatchResult:
    """记忆匹配结果"""
    matched_memories: List[MemoryNode]
    match_confidence: float
    match_type: str  # exact, partial, semantic, none
    suggested_actions: List[str]

@dataclass 
class ReasoningResult:
    """推理结果"""
    response: str
    confidence: float
    reasoning_path: List[str]
    activated_memories: List[str]
    new_memories_created: List[str]
    emotional_context: Dict[str, Any]

class PerceptionProcessor:
    """感知处理器 - 处理输入信息"""
    
    def __init__(self):
        self.input_filters = {
            InputType.TEXT: self._process_text_input,
            InputType.EVENT: self._process_event_input,
            InputType.KNOWLEDGE: self._process_knowledge_input,
            InputType.SKILL: self._process_skill_input,
            InputType.EMOTION: self._process_emotion_input,
            InputType.QUERY: self._process_query_input
        }
    
    def process_input(self, raw_input: Any, input_type: InputType, 
                     context: Dict[str, Any] = None) -> PerceptionInput:
        """处理原始输入"""
        perception_input = PerceptionInput(
            id=str(uuid.uuid4()),
            content=raw_input,
            input_type=input_type,
            timestamp=time.time(),
            context=context or {},
            source=context.get('source', 'unknown') if context else 'unknown'
        )
        
        # 使用特定处理器处理
        if input_type in self.input_filters:
            perception_input = self.input_filters[input_type](perception_input)
        
        logger.info(f"处理感知输入: {input_type.value} - {perception_input.id}")
        return perception_input
    
    def _process_text_input(self, input_data: PerceptionInput) -> PerceptionInput:
        """处理文本输入"""
        content = str(input_data.content)
        
        # 分析文本特征
        word_count = len(content.split())
        has_question = '?' in content or '？' in content
        has_emotion = any(word in content.lower() for word in 
                         ['happy', 'sad', 'angry', 'excited', '高兴', '难过', '生气', '兴奋'])
        
        input_data.context.update({
            'word_count': word_count,
            'has_question': has_question,
            'has_emotion': has_emotion,
            'length_category': 'short' if word_count < 10 else 'medium' if word_count < 50 else 'long'
        })
        
        return input_data
    
    def _process_event_input(self, input_data: PerceptionInput) -> PerceptionInput:
        """处理事件输入"""
        if isinstance(input_data.content, dict):
            event_data = input_data.content
        else:
            event_data = {'description': str(input_data.content)}
        
        input_data.context.update({
            'event_type': event_data.get('type', 'general'),
            'participants': event_data.get('participants', []),
            'location': event_data.get('location', ''),
            'outcome': event_data.get('outcome', '')
        })
        
        return input_data
    
    def _process_knowledge_input(self, input_data: PerceptionInput) -> PerceptionInput:
        """处理知识输入"""
        input_data.context.update({
            'knowledge_domain': input_data.content.get('domain', 'general'),
            'certainty': input_data.content.get('certainty', 0.8),
            'source_reliability': input_data.context.get('source_reliability', 0.7)
        })
        
        return input_data
    
    def _process_skill_input(self, input_data: PerceptionInput) -> PerceptionInput:
        """处理技能输入"""
        input_data.context.update({
            'skill_category': input_data.content.get('category', 'general'),
            'complexity': input_data.content.get('complexity', 'medium'),
            'prerequisites': input_data.content.get('prerequisites', [])
        })
        
        return input_data
    
    def _process_emotion_input(self, input_data: PerceptionInput) -> PerceptionInput:
        """处理情感输入"""
        input_data.context.update({
            'emotion_category': input_data.content.get('emotion', 'neutral'),
            'intensity': input_data.content.get('intensity', 0.5),
            'trigger': input_data.content.get('trigger', '')
        })
        
        return input_data
    
    def _process_query_input(self, input_data: PerceptionInput) -> PerceptionInput:
        """处理查询输入"""
        query = str(input_data.content)
        
        # 分析查询类型
        query_type = 'general'
        if any(word in query.lower() for word in ['how', 'what', 'when', 'where', 'why']):
            query_type = 'question'
        elif any(word in query.lower() for word in ['help', 'assist', 'support']):
            query_type = 'assistance'
        elif any(word in query.lower() for word in ['do', 'perform', 'execute']):
            query_type = 'action'
        
        input_data.context.update({
            'query_type': query_type,
            'urgency': input_data.context.get('urgency', 'normal')
        })
        
        return input_data

class MemoryMatchEngine:
    """记忆匹配引擎"""
    
    def __init__(self, cross_layer_retriever: CrossLayerRetriever):
        self.retriever = cross_layer_retriever
        self.match_threshold = 0.6
        
    def match_memories(self, perception_input: PerceptionInput) -> MemoryMatchResult:
        """匹配相关记忆"""
        query = self._extract_query_from_input(perception_input)
        
        # 跨层检索
        retrieval_result = self.retriever.cross_layer_retrieve(query, max_results=10)
        
        matched_memories = []
        total_confidence = 0.0
        
        for result in retrieval_result['primary_results']:
            if result['weight'] > self.match_threshold:
                # 重建记忆对象（简化版）
                memory_node = self._rebuild_memory_from_result(result)
                if memory_node:
                    matched_memories.append(memory_node)
                    total_confidence += result['weight']
        
        # 确定匹配类型
        match_type = self._determine_match_type(matched_memories, total_confidence)
        
        # 生成建议动作
        suggested_actions = self._generate_suggested_actions(
            perception_input, matched_memories, match_type
        )
        
        avg_confidence = total_confidence / len(matched_memories) if matched_memories else 0.0
        
        return MemoryMatchResult(
            matched_memories=matched_memories,
            match_confidence=min(avg_confidence, 1.0),
            match_type=match_type,
            suggested_actions=suggested_actions
        )
    
    def _extract_query_from_input(self, perception_input: PerceptionInput) -> str:
        """从输入中提取查询字符串"""
        if isinstance(perception_input.content, str):
            return perception_input.content
        elif isinstance(perception_input.content, dict):
            return perception_input.content.get('query', 
                   perception_input.content.get('description', 
                   str(perception_input.content)))
        else:
            return str(perception_input.content)
    
    def _rebuild_memory_from_result(self, result: Dict[str, Any]) -> Optional[MemoryNode]:
        """从检索结果重建记忆对象"""
        memory_type = result.get('type', 'MemoryNode')
        
        # 基础记忆节点信息
        base_args = {
            'id': result['id'],
            'content': result['content'],
            'timestamp': time.time(),  # 简化处理
            'weight': result['weight']
        }
        
        # 根据类型创建相应的记忆节点
        if memory_type == 'WorkingMemoryNode':
            return WorkingMemoryNode(**base_args)
        elif memory_type == 'EpisodicMemoryNode':
            return EpisodicMemoryNode(**base_args)
        elif memory_type == 'SemanticMemoryNode':
            return SemanticMemoryNode(**base_args)
        elif memory_type == 'ProceduralMemoryNode':
            return ProceduralMemoryNode(**base_args)
        elif memory_type == 'EmotionalMemoryNode':
            return EmotionalMemoryNode(**base_args)
        else:
            return MemoryNode(**base_args)
    
    def _determine_match_type(self, memories: List[MemoryNode], confidence: float) -> str:
        """确定匹配类型"""
        if not memories:
            return "none"
        elif confidence > 0.9:
            return "exact"
        elif confidence > 0.7:
            return "partial"
        else:
            return "semantic"
    
    def _generate_suggested_actions(self, perception_input: PerceptionInput, 
                                  memories: List[MemoryNode], match_type: str) -> List[str]:
        """生成建议动作"""
        actions = []
        
        if match_type == "none":
            actions.append("create_new_memory")
            actions.append("search_broader_context")
        elif match_type == "exact":
            actions.append("activate_existing_memory")
            actions.append("update_access_count")
        else:
            actions.append("activate_partial_memory")
            actions.append("enhance_with_new_info")
        
        # 根据输入类型添加特定动作
        if perception_input.input_type == InputType.QUERY:
            actions.append("generate_response")
        elif perception_input.input_type == InputType.EVENT:
            actions.append("store_as_episode")
            actions.append("detect_patterns")
        elif perception_input.input_type == InputType.KNOWLEDGE:
            actions.append("integrate_knowledge")
            actions.append("update_semantic_network")
        
        return actions

class ReasoningEngine:
    """推理引擎 - 基于激活的记忆进行推理"""
    
    def __init__(self, fusion_engine: MemoryFusionEngine):
        self.fusion_engine = fusion_engine
        self.reasoning_strategies = {
            'direct_recall': self._direct_recall_reasoning,
            'analogical': self._analogical_reasoning,
            'causal': self._causal_reasoning,
            'creative': self._creative_reasoning
        }
    
    def reason(self, perception_input: PerceptionInput, 
              match_result: MemoryMatchResult) -> ReasoningResult:
        """执行推理过程"""
        reasoning_path = []
        activated_memories = [m.id for m in match_result.matched_memories]
        
        # 选择推理策略
        strategy = self._select_reasoning_strategy(perception_input, match_result)
        reasoning_path.append(f"选择推理策略: {strategy}")
        
        # 执行推理
        if strategy in self.reasoning_strategies:
            response, confidence = self.reasoning_strategies[strategy](
                perception_input, match_result.matched_memories
            )
        else:
            response, confidence = self._default_reasoning(
                perception_input, match_result.matched_memories
            )
        
        reasoning_path.append(f"生成响应，置信度: {confidence}")
        
        # 分析情感上下文
        emotional_context = self._analyze_emotional_context(
            perception_input, match_result.matched_memories
        )
        
        # 创建新记忆（如果需要）
        new_memories_created = self._create_new_memories(
            perception_input, match_result, response
        )
        
        return ReasoningResult(
            response=response,
            confidence=confidence,
            reasoning_path=reasoning_path,
            activated_memories=activated_memories,
            new_memories_created=new_memories_created,
            emotional_context=emotional_context
        )
    
    def _select_reasoning_strategy(self, perception_input: PerceptionInput, 
                                 match_result: MemoryMatchResult) -> str:
        """选择推理策略"""
        if match_result.match_type == "exact":
            return "direct_recall"
        elif match_result.match_type == "none":
            return "creative"
        elif any(isinstance(m, EpisodicMemoryNode) for m in match_result.matched_memories):
            return "analogical"
        else:
            return "causal"
    
    def _direct_recall_reasoning(self, perception_input: PerceptionInput, 
                               memories: List[MemoryNode]) -> Tuple[str, float]:
        """直接回忆推理"""
        if not memories:
            return "无法找到相关记忆", 0.0
        
        # 使用权重最高的记忆
        best_memory = max(memories, key=lambda m: m.weight)
        
        response = f"基于记忆 {best_memory.id}: {best_memory.content}"
        confidence = best_memory.weight
        
        return response, confidence
    
    def _analogical_reasoning(self, perception_input: PerceptionInput, 
                            memories: List[MemoryNode]) -> Tuple[str, float]:
        """类比推理"""
        if not memories:
            return "无法进行类比推理", 0.0
        
        # 找到最相似的情景记忆
        episodic_memories = [m for m in memories if isinstance(m, EpisodicMemoryNode)]
        
        if episodic_memories:
            similar_episode = max(episodic_memories, key=lambda m: m.weight)
            response = f"根据类似情况 {similar_episode.id}，建议: {similar_episode.content}"
            confidence = similar_episode.weight * 0.8  # 类比推理置信度打折
        else:
            response = "无法找到类似的情景进行类比"
            confidence = 0.3
        
        return response, confidence
    
    def _causal_reasoning(self, perception_input: PerceptionInput, 
                        memories: List[MemoryNode]) -> Tuple[str, float]:
        """因果推理"""
        # 简化的因果推理逻辑
        response = "基于因果关系分析: "
        confidence = 0.0
        
        for memory in memories[:3]:  # 只考虑前3个记忆
            response += f" {memory.content};"
            confidence += memory.weight
        
        confidence = min(confidence / len(memories), 1.0) if memories else 0.0
        
        return response, confidence
    
    def _creative_reasoning(self, perception_input: PerceptionInput, 
                          memories: List[MemoryNode]) -> Tuple[str, float]:
        """创造性推理"""
        response = f"基于创造性思维处理: {perception_input.content}"
        confidence = 0.5  # 创造性推理具有中等置信度
        
        return response, confidence
    
    def _default_reasoning(self, perception_input: PerceptionInput, 
                         memories: List[MemoryNode]) -> Tuple[str, float]:
        """默认推理"""
        if memories:
            # 融合多个记忆
            query_embedding = self._generate_simple_embedding(str(perception_input.content))
            fusion_result = self.fusion_engine.fuse_memories(memories, query_embedding)
            
            return fusion_result['fused_content'], fusion_result['confidence']
        else:
            return f"处理输入: {perception_input.content}", 0.4
    
    def _analyze_emotional_context(self, perception_input: PerceptionInput, 
                                 memories: List[MemoryNode]) -> Dict[str, Any]:
        """分析情感上下文"""
        emotional_memories = [m for m in memories if isinstance(m, EmotionalMemoryNode)]
        
        if not emotional_memories:
            return {
                'dominant_emotion': 'neutral',
                'average_valence': 0.0,
                'average_arousal': 0.0,
                'confidence': 0.0
            }
        
        avg_valence = sum(m.valence for m in emotional_memories) / len(emotional_memories)
        avg_arousal = sum(m.arousal for m in emotional_memories) / len(emotional_memories)
        
        # 确定主导情感
        if avg_valence > 0.3:
            dominant_emotion = 'positive'
        elif avg_valence < -0.3:
            dominant_emotion = 'negative'
        else:
            dominant_emotion = 'neutral'
        
        return {
            'dominant_emotion': dominant_emotion,
            'average_valence': avg_valence,
            'average_arousal': avg_arousal,
            'confidence': sum(m.weight for m in emotional_memories) / len(emotional_memories)
        }
    
    def _create_new_memories(self, perception_input: PerceptionInput, 
                           match_result: MemoryMatchResult, response: str) -> List[str]:
        """创建新记忆"""
        new_memory_ids = []
        
        # 如果没有匹配的记忆，创建新记忆
        if match_result.match_type == "none" or not match_result.matched_memories:
            memory_id = str(uuid.uuid4())
            new_memory_ids.append(memory_id)
            
            logger.info(f"创建新记忆: {memory_id} for input {perception_input.id}")
        
        return new_memory_ids
    
    def _generate_simple_embedding(self, text: str, dim: int = 128):
        """生成简单嵌入"""
        import numpy as np
        hash_value = hash(text)
        np.random.seed(abs(hash_value) % (2**32))
        embedding = np.random.normal(0, 1, dim)
        return embedding / np.linalg.norm(embedding)

class MemoryPerceptionLoop:
    """记忆-感知闭环系统主控制器"""
    
    def __init__(self):
        # 初始化记忆层
        self.memory_layers = {
            'working': WorkingMemory(capacity=20),
            'episodic': EpisodicMemory(capacity=1000),
            'semantic': SemanticMemory(capacity=5000),
            'procedural': ProceduralMemory(capacity=500),
            'emotional': EmotionalMemory(capacity=1000)
        }
        
        # 初始化各组件
        self.perception_processor = PerceptionProcessor()
        self.cross_layer_retriever = create_memory_reconstruction_system(self.memory_layers)
        self.memory_match_engine = MemoryMatchEngine(self.cross_layer_retriever)
        self.reasoning_engine = ReasoningEngine(self.cross_layer_retriever.fusion_engine)
        
        # 处理历史
        self.processing_history = deque(maxlen=1000)
        
        logger.info("记忆-感知闭环系统初始化完成")
    
    def process(self, raw_input: Any, input_type: InputType, 
               context: Dict[str, Any] = None) -> ReasoningResult:
        """处理输入的主流程"""
        start_time = time.time()
        
        # 1. 感知输入处理
        perception_input = self.perception_processor.process_input(
            raw_input, input_type, context
        )
        
        # 2. 记忆匹配
        match_result = self.memory_match_engine.match_memories(perception_input)
        
        # 3. 推理处理
        reasoning_result = self.reasoning_engine.reason(perception_input, match_result)
        
        # 4. 更新记忆关联
        if match_result.matched_memories:
            # 假设创建了一个新的工作记忆节点
            working_memory = WorkingMemoryNode(
                id=perception_input.id,
                content=perception_input.content,
                timestamp=perception_input.timestamp,
                attention_score=1.0
            )
            
            self.cross_layer_retriever.update_associations(working_memory)
        
        # 5. 记录处理历史
        processing_time = time.time() - start_time
        
        self.processing_history.append({
            'input_id': perception_input.id,
            'input_type': input_type.value,
            'match_confidence': match_result.match_confidence,
            'response_confidence': reasoning_result.confidence,
            'processing_time': processing_time,
            'timestamp': start_time
        })
        
        logger.info(f"处理完成 - 输入ID: {perception_input.id}, "
                   f"置信度: {reasoning_result.confidence:.2f}, "
                   f"耗时: {processing_time:.3f}s")
        
        return reasoning_result
    
    def get_memory_status(self) -> Dict[str, Any]:
        """获取记忆系统状态"""
        status = {}
        
        for layer_name, layer in self.memory_layers.items():
            status[layer_name] = {
                'size': layer.get_size(),
                'capacity': layer.capacity,
                'utilization': layer.get_size() / layer.capacity,
                'recent_access': len([h for h in layer.access_history 
                                    if time.time() - h[1] < 3600])  # 最近1小时访问
            }
        
        return status
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        if not self.processing_history:
            return {}
        
        recent_history = [h for h in self.processing_history 
                         if time.time() - h['timestamp'] < 3600]  # 最近1小时
        
        if not recent_history:
            return {}
        
        avg_processing_time = sum(h['processing_time'] for h in recent_history) / len(recent_history)
        avg_confidence = sum(h['response_confidence'] for h in recent_history) / len(recent_history)
        
        input_type_dist = {}
        for h in recent_history:
            input_type_dist[h['input_type']] = input_type_dist.get(h['input_type'], 0) + 1
        
        return {
            'total_processed': len(recent_history),
            'average_processing_time': avg_processing_time,
            'average_confidence': avg_confidence,
            'input_type_distribution': input_type_dist
        }

def create_memory_perception_system() -> MemoryPerceptionLoop:
    """创建记忆-感知闭环系统"""
    system = MemoryPerceptionLoop()
    logger.info("记忆-感知闭环系统创建完成")
    return system
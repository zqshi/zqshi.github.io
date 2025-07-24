"""
动态记忆重构机制

实现关联检索、记忆衰减、记忆融合等核心功能
基于图神经网络思想的跨记忆层检索与融合
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
import json
import time
import logging
from dataclasses import dataclass
from .memory_engine import (
    MemoryNode, WorkingMemoryNode, EpisodicMemoryNode, 
    SemanticMemoryNode, ProceduralMemoryNode, EmotionalMemoryNode,
    MemoryLayer
)

logger = logging.getLogger(__name__)

@dataclass
class MemoryAssociation:
    """记忆关联关系"""
    source_id: str
    target_id: str
    association_type: str  # semantic, temporal, causal, emotional
    strength: float
    created_at: float
    last_activated: float = 0.0
    activation_count: int = 0

class MemoryGraph:
    """记忆图谱 - 管理记忆节点间的关联关系"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.associations: Dict[str, MemoryAssociation] = {}
        self.node_embeddings: Dict[str, np.ndarray] = {}
        
    def add_memory_node(self, memory: MemoryNode, embedding: Optional[np.ndarray] = None):
        """添加记忆节点"""
        self.graph.add_node(memory.id, 
                           memory_type=type(memory).__name__,
                           timestamp=memory.timestamp,
                           weight=memory.weight)
        
        if embedding is not None:
            self.node_embeddings[memory.id] = embedding
        else:
            # 生成简单的嵌入表示
            self.node_embeddings[memory.id] = self._generate_embedding(memory)
    
    def add_association(self, association: MemoryAssociation):
        """添加记忆关联"""
        edge_id = f"{association.source_id}->{association.target_id}"
        self.associations[edge_id] = association
        
        self.graph.add_edge(association.source_id, association.target_id,
                           association_type=association.association_type,
                           strength=association.strength,
                           edge_id=edge_id)
    
    def get_associated_memories(self, memory_id: str, max_depth: int = 3) -> List[Tuple[str, float]]:
        """获取关联记忆"""
        if memory_id not in self.graph:
            return []
        
        associated = []
        visited = set()
        
        def dfs(node_id: str, depth: int, cumulative_strength: float):
            if depth > max_depth or node_id in visited:
                return
            
            visited.add(node_id)
            
            # 获取邻接节点
            for neighbor in self.graph.neighbors(node_id):
                edge_data = self.graph[node_id][neighbor]
                strength = edge_data['strength'] * cumulative_strength
                
                if neighbor != memory_id:
                    associated.append((neighbor, strength))
                    dfs(neighbor, depth + 1, strength * 0.8)  # 衰减系数
        
        dfs(memory_id, 0, 1.0)
        
        # 按关联强度排序
        associated.sort(key=lambda x: x[1], reverse=True)
        return associated
    
    def find_memory_clusters(self, min_cluster_size: int = 3) -> List[Set[str]]:
        """发现记忆聚类"""
        # 使用社区发现算法
        undirected_graph = self.graph.to_undirected()
        try:
            import community  # python-louvain
            partition = community.best_partition(undirected_graph)
            
            clusters = defaultdict(set)
            for node, cluster_id in partition.items():
                clusters[cluster_id].add(node)
            
            return [cluster for cluster in clusters.values() 
                   if len(cluster) >= min_cluster_size]
        except ImportError:
            logger.warning("python-louvain未安装，使用简单的连通分量算法")
            return [set(component) for component in 
                   nx.connected_components(undirected_graph)
                   if len(component) >= min_cluster_size]
    
    def _generate_embedding(self, memory: MemoryNode, dim: int = 128) -> np.ndarray:
        """生成记忆节点的嵌入表示"""
        # 简单的内容哈希嵌入
        content_str = str(memory.content)
        hash_value = hash(content_str)
        
        # 生成伪随机嵌入
        np.random.seed(abs(hash_value) % (2**32))
        embedding = np.random.normal(0, 1, dim)
        
        # 添加记忆类型特征
        type_features = {
            'WorkingMemoryNode': [1, 0, 0, 0, 0],
            'EpisodicMemoryNode': [0, 1, 0, 0, 0], 
            'SemanticMemoryNode': [0, 0, 1, 0, 0],
            'ProceduralMemoryNode': [0, 0, 0, 1, 0],
            'EmotionalMemoryNode': [0, 0, 0, 0, 1]
        }
        
        type_name = type(memory).__name__
        if type_name in type_features:
            type_vec = np.array(type_features[type_name])
            embedding[:5] = type_vec
        
        return embedding / np.linalg.norm(embedding)

class AssociationDetector:
    """关联关系检测器"""
    
    def __init__(self):
        self.semantic_threshold = 0.7
        self.temporal_threshold = 3600  # 1小时
        self.causal_keywords = ['因为', '所以', '导致', '引起', '造成', 'because', 'cause', 'result']
        
    def detect_associations(self, memory1: MemoryNode, memory2: MemoryNode) -> List[MemoryAssociation]:
        """检测两个记忆节点间的关联关系"""
        associations = []
        current_time = time.time()
        
        # 语义关联
        semantic_strength = self._calculate_semantic_similarity(memory1, memory2)
        if semantic_strength > self.semantic_threshold:
            association = MemoryAssociation(
                source_id=memory1.id,
                target_id=memory2.id,
                association_type="semantic",
                strength=semantic_strength,
                created_at=current_time
            )
            associations.append(association)
        
        # 时间关联
        time_diff = abs(memory1.timestamp - memory2.timestamp)
        if time_diff < self.temporal_threshold:
            temporal_strength = 1.0 - (time_diff / self.temporal_threshold)
            association = MemoryAssociation(
                source_id=memory1.id,
                target_id=memory2.id,
                association_type="temporal",
                strength=temporal_strength,
                created_at=current_time
            )
            associations.append(association)
        
        # 因果关联
        causal_strength = self._detect_causal_relationship(memory1, memory2)
        if causal_strength > 0.5:
            association = MemoryAssociation(
                source_id=memory1.id,
                target_id=memory2.id,
                association_type="causal",
                strength=causal_strength,
                created_at=current_time
            )
            associations.append(association)
        
        # 情感关联
        if isinstance(memory1, EmotionalMemoryNode) or isinstance(memory2, EmotionalMemoryNode):
            emotional_strength = self._calculate_emotional_similarity(memory1, memory2)
            if emotional_strength > 0.6:
                association = MemoryAssociation(
                    source_id=memory1.id,
                    target_id=memory2.id,
                    association_type="emotional",
                    strength=emotional_strength,
                    created_at=current_time
                )
                associations.append(association)
        
        return associations
    
    def _calculate_semantic_similarity(self, memory1: MemoryNode, memory2: MemoryNode) -> float:
        """计算语义相似度"""
        content1 = str(memory1.content).lower()
        content2 = str(memory2.content).lower()
        
        # 简单的词汇重叠度计算
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        # 考虑记忆类型的语义关联
        if type(memory1) == type(memory2):
            jaccard_similarity *= 1.2  # 同类型记忆加权
        
        return min(jaccard_similarity, 1.0)
    
    def _detect_causal_relationship(self, memory1: MemoryNode, memory2: MemoryNode) -> float:
        """检测因果关系"""
        content1 = str(memory1.content).lower()
        content2 = str(memory2.content).lower()
        
        causal_score = 0.0
        
        # 检查因果关键词
        for keyword in self.causal_keywords:
            if keyword in content1 or keyword in content2:
                causal_score += 0.3
        
        # 检查时间顺序（原因通常在结果之前）
        if memory1.timestamp < memory2.timestamp:
            causal_score += 0.4
        
        # 检查情景记忆中的动作-结果关系
        if isinstance(memory1, EpisodicMemoryNode) and isinstance(memory2, EpisodicMemoryNode):
            if memory1.results and memory2.actions:
                if any(result in memory2.content for result in memory1.results):
                    causal_score += 0.5
        
        return min(causal_score, 1.0)
    
    def _calculate_emotional_similarity(self, memory1: MemoryNode, memory2: MemoryNode) -> float:
        """计算情感相似度"""
        if isinstance(memory1, EmotionalMemoryNode) and isinstance(memory2, EmotionalMemoryNode):
            # 计算情感向量相似度
            valence_diff = abs(memory1.valence - memory2.valence)
            arousal_diff = abs(memory1.arousal - memory2.arousal)
            
            emotional_distance = np.sqrt(valence_diff**2 + arousal_diff**2)
            similarity = 1.0 - (emotional_distance / 2.828)  # 最大距离为sqrt(8)
            
            return max(similarity, 0.0)
        
        return 0.0

class MemoryFusionEngine:
    """记忆融合引擎 - 基于Transformer架构的跨记忆融合"""
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.attention_weights = None
        
    def fuse_memories(self, memories: List[MemoryNode], query_embedding: np.ndarray) -> Dict[str, Any]:
        """融合多个记忆生成综合响应"""
        if not memories:
            return {"fused_content": "", "confidence": 0.0, "sources": []}
        
        # 生成记忆嵌入
        memory_embeddings = []
        memory_contents = []
        
        for memory in memories:
            embedding = self._get_memory_embedding(memory)
            memory_embeddings.append(embedding)
            memory_contents.append({
                "id": memory.id,
                "content": memory.content,
                "type": type(memory).__name__,
                "weight": memory.weight
            })
        
        memory_embeddings = np.array(memory_embeddings)
        
        # 计算注意力权重
        attention_weights = self._compute_attention(query_embedding, memory_embeddings)
        
        # 融合记忆内容
        fused_result = self._weighted_fusion(memory_contents, attention_weights)
        
        return {
            "fused_content": fused_result["content"],
            "confidence": fused_result["confidence"], 
            "sources": fused_result["sources"],
            "attention_weights": attention_weights.tolist()
        }
    
    def _get_memory_embedding(self, memory: MemoryNode) -> np.ndarray:
        """获取记忆的嵌入表示"""
        # 简化的嵌入生成
        content_str = str(memory.content)
        hash_value = hash(content_str)
        
        np.random.seed(abs(hash_value) % (2**32))
        embedding = np.random.normal(0, 1, self.embedding_dim)
        
        return embedding / np.linalg.norm(embedding)
    
    def _compute_attention(self, query: np.ndarray, keys: np.ndarray) -> np.ndarray:
        """计算注意力权重"""
        # 简化的注意力机制：余弦相似度
        similarities = np.dot(keys, query) / (np.linalg.norm(keys, axis=1) * np.linalg.norm(query))
        
        # Softmax归一化
        exp_similarities = np.exp(similarities - np.max(similarities))
        attention_weights = exp_similarities / np.sum(exp_similarities)
        
        return attention_weights
    
    def _weighted_fusion(self, memory_contents: List[Dict[str, Any]], 
                        attention_weights: np.ndarray) -> Dict[str, Any]:
        """加权融合记忆内容"""
        # 按权重排序记忆
        weighted_memories = list(zip(memory_contents, attention_weights))
        weighted_memories.sort(key=lambda x: x[1], reverse=True)
        
        # 生成融合内容
        fused_parts = []
        total_confidence = 0.0
        sources = []
        
        for memory_content, weight in weighted_memories:
            if weight > 0.1:  # 只考虑权重较高的记忆
                fused_parts.append({
                    "content": memory_content["content"],
                    "weight": float(weight),
                    "source_id": memory_content["id"]
                })
                
                total_confidence += weight * memory_content["weight"]
                sources.append({
                    "id": memory_content["id"],
                    "type": memory_content["type"],
                    "weight": float(weight)
                })
        
        # 组合内容
        if len(fused_parts) == 1:
            fused_content = fused_parts[0]["content"]
        else:
            fused_content = self._combine_content_parts(fused_parts)
        
        return {
            "content": fused_content,
            "confidence": min(total_confidence, 1.0),
            "sources": sources
        }
    
    def _combine_content_parts(self, parts: List[Dict[str, Any]]) -> str:
        """组合内容片段"""
        if not parts:
            return ""
        
        # 简单的内容组合策略
        combined = []
        for part in parts:
            content = str(part["content"]).strip()
            if content and content not in combined:
                combined.append(content)
        
        return " | ".join(combined)

class CrossLayerRetriever:
    """跨记忆层检索器"""
    
    def __init__(self, memory_layers: Dict[str, MemoryLayer]):
        self.memory_layers = memory_layers
        self.memory_graph = MemoryGraph()
        self.association_detector = AssociationDetector()
        self.fusion_engine = MemoryFusionEngine()
        
    def cross_layer_retrieve(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """跨层检索记忆"""
        all_memories = []
        layer_results = {}
        
        # 从各层检索
        for layer_name, layer in self.memory_layers.items():
            memories = layer.retrieve(query, top_k=5)
            layer_results[layer_name] = [
                {"id": m.id, "content": m.content, "weight": m.weight} 
                for m in memories
            ]
            all_memories.extend(memories)
        
        # 去重
        unique_memories = []
        seen_ids = set()
        for memory in all_memories:
            if memory.id not in seen_ids:
                unique_memories.append(memory)
                seen_ids.add(memory.id)
        
        # 按相关性排序
        unique_memories.sort(key=lambda x: x.weight, reverse=True)
        top_memories = unique_memories[:max_results]
        
        # 生成查询嵌入
        query_embedding = self._generate_query_embedding(query)
        
        # 融合记忆
        fusion_result = self.fusion_engine.fuse_memories(top_memories, query_embedding)
        
        # 获取关联记忆
        associated_memories = []
        for memory in top_memories[:3]:  # 只对前3个记忆查找关联
            associated = self.memory_graph.get_associated_memories(memory.id, max_depth=2)
            associated_memories.extend(associated[:2])  # 每个记忆最多2个关联
        
        return {
            "query": query,
            "primary_results": [
                {
                    "id": m.id,
                    "content": m.content,
                    "type": type(m).__name__,
                    "weight": m.weight,
                    "layer": self._get_memory_layer(m)
                }
                for m in top_memories
            ],
            "layer_breakdown": layer_results,
            "fused_response": fusion_result,
            "associated_memories": associated_memories,
            "total_results": len(unique_memories)
        }
    
    def _generate_query_embedding(self, query: str, dim: int = 128) -> np.ndarray:
        """生成查询嵌入"""
        hash_value = hash(query)
        np.random.seed(abs(hash_value) % (2**32))
        embedding = np.random.normal(0, 1, dim)
        return embedding / np.linalg.norm(embedding)
    
    def _get_memory_layer(self, memory: MemoryNode) -> str:
        """获取记忆所属层级"""
        type_to_layer = {
            'WorkingMemoryNode': 'WorkingMemory',
            'EpisodicMemoryNode': 'EpisodicMemory',
            'SemanticMemoryNode': 'SemanticMemory', 
            'ProceduralMemoryNode': 'ProceduralMemory',
            'EmotionalMemoryNode': 'EmotionalMemory'
        }
        return type_to_layer.get(type(memory).__name__, 'Unknown')
    
    def update_associations(self, new_memory: MemoryNode):
        """更新记忆关联关系"""
        # 添加新记忆到图谱
        self.memory_graph.add_memory_node(new_memory)
        
        # 检测与现有记忆的关联
        for layer in self.memory_layers.values():
            for existing_memory in layer.memories.values():
                if existing_memory.id != new_memory.id:
                    associations = self.association_detector.detect_associations(
                        new_memory, existing_memory
                    )
                    
                    for association in associations:
                        self.memory_graph.add_association(association)
                        logger.info(f"发现关联: {association.association_type} "
                                  f"({association.source_id} -> {association.target_id})")

def create_memory_reconstruction_system(memory_layers: Dict[str, MemoryLayer]) -> CrossLayerRetriever:
    """创建记忆重构系统"""
    retriever = CrossLayerRetriever(memory_layers)
    
    logger.info("记忆重构系统初始化完成")
    logger.info(f"已加载 {len(memory_layers)} 个记忆层")
    
    return retriever
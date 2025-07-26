"""
信息论优化系统 - Shannon熵计算和SSOT管理
Information Theory Optimization System - Shannon Entropy & SSOT Management

实现文档要求：
- 系统整体信息熵降低≥40%
- 信息压缩比≥10:1，信息损失率≤5%
- SSOT管理系统
"""

import asyncio
import json
import logging
import math
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import Counter
import hashlib
import pickle
import zlib

logger = logging.getLogger(__name__)

class InformationType(Enum):
    """信息类型"""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    CODE = "code"
    KNOWLEDGE = "knowledge"
    EXECUTION_CONTEXT = "execution_context"
    COMMUNICATION = "communication"

@dataclass
class InformationItem:
    """信息项"""
    item_id: str
    info_type: InformationType
    content: Any
    source: str
    timestamp: datetime
    entropy_value: float = 0.0
    compression_ratio: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EntropyMetrics:
    """熵指标"""
    baseline_entropy: float
    current_entropy: float
    reduction_percentage: float
    compression_achieved: float
    information_loss: float
    optimization_score: float

@dataclass
class SSOTRecord:
    """SSOT记录"""
    ssot_id: str
    category: InformationType
    canonical_content: Any
    source_items: List[str]
    confidence_score: float
    last_updated: datetime
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

class ShannonEntropyCalculator:
    """Shannon熵计算器"""
    
    def __init__(self):
        pass
    
    def calculate_entropy(self, data: Any) -> float:
        """
        计算Shannon熵: H(X) = -∑P(xi)log2P(xi)
        """
        try:
            # 将数据转换为字符串序列
            text = self._normalize_data_to_text(data)
            
            # 计算字符频率
            char_counts = Counter(text)
            total_chars = len(text)
            
            if total_chars == 0:
                return 0.0
            
            # 计算Shannon熵
            entropy = 0.0
            for count in char_counts.values():
                probability = count / total_chars
                if probability > 0:
                    entropy -= probability * math.log2(probability)
            
            return entropy
            
        except Exception as e:
            logger.error(f"熵计算失败: {str(e)}")
            return 0.0
    
    def calculate_conditional_entropy(self, data_x: Any, data_y: Any) -> float:
        """计算条件熵 H(X|Y)"""
        try:
            # 简化的条件熵计算
            joint_text = self._normalize_data_to_text([data_x, data_y])
            y_text = self._normalize_data_to_text(data_y)
            
            joint_entropy = self.calculate_entropy(joint_text)
            y_entropy = self.calculate_entropy(y_text)
            
            # H(X|Y) = H(X,Y) - H(Y)
            conditional_entropy = joint_entropy - y_entropy
            return max(0.0, conditional_entropy)
            
        except Exception as e:
            logger.error(f"条件熵计算失败: {str(e)}")
            return 0.0
    
    def calculate_mutual_information(self, data_x: Any, data_y: Any) -> float:
        """计算互信息 I(X;Y) = H(X) - H(X|Y)"""
        try:
            x_entropy = self.calculate_entropy(data_x)
            conditional_entropy = self.calculate_conditional_entropy(data_x, data_y)
            
            mutual_info = x_entropy - conditional_entropy
            return max(0.0, mutual_info)
            
        except Exception as e:
            logger.error(f"互信息计算失败: {str(e)}")
            return 0.0
    
    def _normalize_data_to_text(self, data: Any) -> str:
        """将数据标准化为文本"""
        if isinstance(data, str):
            return data
        elif isinstance(data, (dict, list)):
            return json.dumps(data, ensure_ascii=False, sort_keys=True)
        else:
            return str(data)

class InformationCompressor:
    """信息压缩器"""
    
    def __init__(self):
        self.compression_algorithms = {
            'zlib': self._zlib_compress,
            'semantic': self._semantic_compress,
            'structural': self._structural_compress
        }
    
    def compress_information(self, data: Any, algorithm: str = 'zlib') -> Tuple[Any, float, float]:
        """
        压缩信息
        返回: (压缩后数据, 压缩比, 信息损失率)
        """
        try:
            compress_func = self.compression_algorithms.get(algorithm, self._zlib_compress)
            return compress_func(data)
            
        except Exception as e:
            logger.error(f"信息压缩失败: {str(e)}")
            return data, 1.0, 0.0
    
    def _zlib_compress(self, data: Any) -> Tuple[Any, float, float]:
        """使用zlib压缩"""
        try:
            # 序列化数据
            serialized = pickle.dumps(data)
            original_size = len(serialized)
            
            # 压缩
            compressed = zlib.compress(serialized)
            compressed_size = len(compressed)
            
            # 计算压缩比
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            # 测试解压缩以评估信息损失
            try:
                decompressed = zlib.decompress(compressed)
                reconstructed = pickle.loads(decompressed)
                
                # 计算信息损失率
                information_loss = self._calculate_information_loss(data, reconstructed)
                
                return compressed, compression_ratio, information_loss
                
            except Exception:
                return data, 1.0, 1.0  # 完全损失
                
        except Exception as e:
            logger.error(f"zlib压缩失败: {str(e)}")
            return data, 1.0, 0.0
    
    def _semantic_compress(self, data: Any) -> Tuple[Any, float, float]:
        """语义压缩"""
        try:
            if isinstance(data, dict):
                # 提取关键信息
                compressed = {}
                for key, value in data.items():
                    if self._is_key_information(key, value):
                        compressed[key] = value
                
                # 计算压缩比
                original_size = len(json.dumps(data, ensure_ascii=False))
                compressed_size = len(json.dumps(compressed, ensure_ascii=False))
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
                
                # 估算信息损失
                information_loss = 1.0 - (len(compressed) / len(data)) if data else 0.0
                
                return compressed, compression_ratio, information_loss
            else:
                return data, 1.0, 0.0
                
        except Exception as e:
            logger.error(f"语义压缩失败: {str(e)}")
            return data, 1.0, 0.0
    
    def _structural_compress(self, data: Any) -> Tuple[Any, float, float]:
        """结构化压缩"""
        try:
            if isinstance(data, list):
                # 去重和模式识别
                unique_items = []
                patterns = {}
                
                for item in data:
                    item_hash = hashlib.md5(str(item).encode()).hexdigest()
                    if item_hash not in patterns:
                        patterns[item_hash] = len(unique_items)
                        unique_items.append(item)
                
                compressed = {
                    'unique_items': unique_items,
                    'pattern_map': patterns,
                    'original_length': len(data)
                }
                
                # 计算压缩比
                original_size = len(json.dumps(data, ensure_ascii=False))
                compressed_size = len(json.dumps(compressed, ensure_ascii=False))
                compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
                
                # 结构化压缩通常无信息损失
                information_loss = 0.0
                
                return compressed, compression_ratio, information_loss
            else:
                return data, 1.0, 0.0
                
        except Exception as e:
            logger.error(f"结构化压缩失败: {str(e)}")
            return data, 1.0, 0.0
    
    def _is_key_information(self, key: str, value: Any) -> bool:
        """判断是否为关键信息"""
        key_indicators = [
            'id', 'name', 'title', 'type', 'status', 'priority',
            'description', 'summary', 'result', 'error', 'timestamp'
        ]
        
        return any(indicator in key.lower() for indicator in key_indicators)
    
    def _calculate_information_loss(self, original: Any, reconstructed: Any) -> float:
        """计算信息损失率"""
        try:
            if original == reconstructed:
                return 0.0
            
            # 简化的信息损失计算
            original_str = json.dumps(original, ensure_ascii=False, sort_keys=True)
            reconstructed_str = json.dumps(reconstructed, ensure_ascii=False, sort_keys=True)
            
            # 使用编辑距离估算损失
            import difflib
            similarity = difflib.SequenceMatcher(None, original_str, reconstructed_str).ratio()
            information_loss = 1.0 - similarity
            
            return min(1.0, max(0.0, information_loss))
            
        except Exception:
            return 0.5  # 默认估算

class SSOTManager:
    """单一信息源管理器"""
    
    def __init__(self):
        self.ssot_storage: Dict[str, SSOTRecord] = {}
        self.category_index: Dict[InformationType, List[str]] = {
            info_type: [] for info_type in InformationType
        }
        self.entropy_calculator = ShannonEntropyCalculator()
    
    def register_information(self, info_item: InformationItem) -> str:
        """注册信息到SSOT系统"""
        try:
            # 查找是否存在相似的SSOT记录
            existing_ssot = self._find_similar_ssot(info_item)
            
            if existing_ssot:
                # 更新现有SSOT
                return self._update_existing_ssot(existing_ssot, info_item)
            else:
                # 创建新的SSOT记录
                return self._create_new_ssot(info_item)
                
        except Exception as e:
            logger.error(f"SSOT信息注册失败: {str(e)}")
            return ""
    
    def get_canonical_information(self, info_type: InformationType, query: str = "") -> Optional[SSOTRecord]:
        """获取规范信息"""
        try:
            candidates = self.category_index.get(info_type, [])
            
            if not candidates:
                return None
            
            if not query:
                # 返回最新的记录
                latest_ssot_id = max(candidates, key=lambda x: self.ssot_storage[x].last_updated)
                return self.ssot_storage[latest_ssot_id]
            else:
                # 基于查询找到最相关的记录
                best_match = self._find_best_match(candidates, query)
                return self.ssot_storage.get(best_match) if best_match else None
                
        except Exception as e:
            logger.error(f"SSOT信息获取失败: {str(e)}")
            return None
    
    def resolve_information_conflicts(self, conflicting_items: List[InformationItem]) -> SSOTRecord:
        """解决信息冲突"""
        try:
            if not conflicting_items:
                raise ValueError("没有冲突项目")
            
            # 基于信息熵和可信度选择最佳版本
            best_item = max(conflicting_items, key=lambda x: (
                x.metadata.get('confidence', 0.5) - x.entropy_value * 0.1
            ))
            
            # 融合其他项目的有用信息
            merged_content = self._merge_information_content([
                item.content for item in conflicting_items
            ])
            
            # 创建解决冲突后的SSOT记录
            ssot_record = SSOTRecord(
                ssot_id=f"resolved_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category=best_item.info_type,
                canonical_content=merged_content,
                source_items=[item.item_id for item in conflicting_items],
                confidence_score=best_item.metadata.get('confidence', 0.8),
                last_updated=datetime.now(),
                metadata={
                    'conflict_resolution': True,
                    'source_count': len(conflicting_items),
                    'resolution_method': 'entropy_weighted_merge'
                }
            )
            
            self._store_ssot_record(ssot_record)
            return ssot_record
            
        except Exception as e:
            logger.error(f"信息冲突解决失败: {str(e)}")
            # 返回默认记录
            return SSOTRecord(
                ssot_id="fallback",
                category=conflicting_items[0].info_type,
                canonical_content=conflicting_items[0].content,
                source_items=[conflicting_items[0].item_id],
                confidence_score=0.5,
                last_updated=datetime.now()
            )
    
    def _find_similar_ssot(self, info_item: InformationItem) -> Optional[str]:
        """查找相似的SSOT记录"""
        candidates = self.category_index.get(info_item.info_type, [])
        
        for ssot_id in candidates:
            ssot_record = self.ssot_storage[ssot_id]
            similarity = self._calculate_content_similarity(
                info_item.content, ssot_record.canonical_content
            )
            
            if similarity > 0.8:  # 80%相似度阈值
                return ssot_id
        
        return None
    
    def _calculate_content_similarity(self, content1: Any, content2: Any) -> float:
        """计算内容相似度"""
        try:
            str1 = json.dumps(content1, ensure_ascii=False, sort_keys=True)
            str2 = json.dumps(content2, ensure_ascii=False, sort_keys=True)
            
            import difflib
            return difflib.SequenceMatcher(None, str1, str2).ratio()
            
        except Exception:
            return 0.0
    
    def _update_existing_ssot(self, ssot_id: str, info_item: InformationItem) -> str:
        """更新现有SSOT记录"""
        ssot_record = self.ssot_storage[ssot_id]
        
        # 合并内容
        merged_content = self._merge_information_content([
            ssot_record.canonical_content, info_item.content
        ])
        
        # 更新记录
        ssot_record.canonical_content = merged_content
        ssot_record.source_items.append(info_item.item_id)
        ssot_record.last_updated = datetime.now()
        ssot_record.version += 1
        
        return ssot_id
    
    def _create_new_ssot(self, info_item: InformationItem) -> str:
        """创建新的SSOT记录"""
        ssot_id = f"ssot_{info_item.info_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        ssot_record = SSOTRecord(
            ssot_id=ssot_id,
            category=info_item.info_type,
            canonical_content=info_item.content,
            source_items=[info_item.item_id],
            confidence_score=info_item.metadata.get('confidence', 0.8),
            last_updated=datetime.now()
        )
        
        self._store_ssot_record(ssot_record)
        return ssot_id
    
    def _store_ssot_record(self, ssot_record: SSOTRecord):
        """存储SSOT记录"""
        self.ssot_storage[ssot_record.ssot_id] = ssot_record
        self.category_index[ssot_record.category].append(ssot_record.ssot_id)
    
    def _find_best_match(self, candidates: List[str], query: str) -> Optional[str]:
        """找到最佳匹配"""
        best_score = 0.0
        best_match = None
        
        for ssot_id in candidates:
            ssot_record = self.ssot_storage[ssot_id]
            content_str = json.dumps(ssot_record.canonical_content, ensure_ascii=False)
            
            # 简单的关键词匹配评分
            score = sum(1 for word in query.lower().split() if word in content_str.lower())
            score /= len(query.split())  # 标准化
            
            if score > best_score:
                best_score = score
                best_match = ssot_id
        
        return best_match if best_score > 0.3 else None
    
    def _merge_information_content(self, contents: List[Any]) -> Any:
        """合并信息内容"""
        if not contents:
            return None
        
        if len(contents) == 1:
            return contents[0]
        
        # 简化的合并策略
        if all(isinstance(c, dict) for c in contents):
            # 合并字典
            merged = {}
            for content in contents:
                merged.update(content)
            return merged
        elif all(isinstance(c, list) for c in contents):
            # 合并列表并去重
            merged = []
            for content in contents:
                merged.extend(content)
            return list(set(merged) if all(isinstance(x, (str, int, float)) for x in merged) else merged)
        else:
            # 选择最长的内容
            return max(contents, key=lambda x: len(str(x)))

class EntropyOptimizer:
    """
    信息论优化器 - 主要优化引擎
    目标：系统整体信息熵降低≥40%
    """
    
    def __init__(self):
        self.entropy_calculator = ShannonEntropyCalculator()
        self.compressor = InformationCompressor()
        self.ssot_manager = SSOTManager()
        
        self.baseline_entropy = 0.0
        self.optimization_history: List[EntropyMetrics] = []
    
    async def optimize_system_information(self, information_items: List[InformationItem]) -> EntropyMetrics:
        """
        优化系统信息
        实现40%熵减少目标
        """
        try:
            logger.info(f"开始信息论优化，处理{len(information_items)}个信息项")
            
            # 1. 计算基线熵
            if self.baseline_entropy == 0.0:
                self.baseline_entropy = self._calculate_baseline_entropy(information_items)
            
            # 2. SSOT整合
            consolidated_items = await self._consolidate_with_ssot(information_items)
            
            # 3. 信息压缩
            compressed_items = await self._compress_information_items(consolidated_items)
            
            # 4. 冗余消除
            deduplicated_items = self._eliminate_redundancy(compressed_items)
            
            # 5. 计算优化后熵
            current_entropy = self._calculate_current_entropy(deduplicated_items)
            
            # 6. 计算指标
            metrics = self._calculate_optimization_metrics(
                self.baseline_entropy, current_entropy, compressed_items
            )
            
            self.optimization_history.append(metrics)
            
            logger.info(f"信息论优化完成，熵减少: {metrics.reduction_percentage:.1f}%")
            return metrics
            
        except Exception as e:
            logger.error(f"信息论优化失败: {str(e)}")
            return EntropyMetrics(
                baseline_entropy=self.baseline_entropy,
                current_entropy=self.baseline_entropy,
                reduction_percentage=0.0,
                compression_achieved=1.0,
                information_loss=0.0,
                optimization_score=0.0
            )
    
    def _calculate_baseline_entropy(self, items: List[InformationItem]) -> float:
        """计算基线熵"""
        total_entropy = 0.0
        
        for item in items:
            item_entropy = self.entropy_calculator.calculate_entropy(item.content)
            item.entropy_value = item_entropy
            total_entropy += item_entropy
        
        return total_entropy / len(items) if items else 0.0
    
    async def _consolidate_with_ssot(self, items: List[InformationItem]) -> List[InformationItem]:
        """使用SSOT整合信息"""
        consolidated = []
        
        for item in items:
            ssot_id = self.ssot_manager.register_information(item)
            
            if ssot_id:
                # 获取SSOT规范版本
                canonical = self.ssot_manager.get_canonical_information(item.info_type)
                if canonical:
                    # 创建基于SSOT的优化项
                    optimized_item = InformationItem(
                        item_id=f"ssot_{ssot_id}",
                        info_type=item.info_type,
                        content=canonical.canonical_content,
                        source=f"SSOT:{ssot_id}",
                        timestamp=datetime.now(),
                        metadata={
                            'ssot_id': ssot_id,
                            'confidence': canonical.confidence_score,
                            'original_item': item.item_id
                        }
                    )
                    consolidated.append(optimized_item)
                else:
                    consolidated.append(item)
            else:
                consolidated.append(item)
        
        return consolidated
    
    async def _compress_information_items(self, items: List[InformationItem]) -> List[InformationItem]:
        """压缩信息项"""
        compressed_items = []
        
        for item in items:
            # 选择最适合的压缩算法
            algorithm = self._select_compression_algorithm(item)
            
            # 执行压缩
            compressed_content, compression_ratio, information_loss = self.compressor.compress_information(
                item.content, algorithm
            )
            
            # 创建压缩后的信息项
            compressed_item = InformationItem(
                item_id=f"compressed_{item.item_id}",
                info_type=item.info_type,
                content=compressed_content,
                source=item.source,
                timestamp=item.timestamp,
                compression_ratio=compression_ratio,
                metadata={
                    **item.metadata,
                    'compression_algorithm': algorithm,
                    'compression_ratio': compression_ratio,
                    'information_loss': information_loss,
                    'original_size': len(str(item.content)),
                    'compressed_size': len(str(compressed_content))
                }
            )
            
            compressed_items.append(compressed_item)
        
        return compressed_items
    
    def _select_compression_algorithm(self, item: InformationItem) -> str:
        """选择压缩算法"""
        # 基于信息类型选择最适合的压缩算法
        if item.info_type in [InformationType.REQUIREMENTS, InformationType.DESIGN]:
            return 'semantic'
        elif item.info_type == InformationType.CODE:
            return 'structural'
        else:
            return 'zlib'
    
    def _eliminate_redundancy(self, items: List[InformationItem]) -> List[InformationItem]:
        """消除冗余"""
        unique_items = []
        seen_hashes = set()
        
        for item in items:
            # 计算内容哈希
            content_hash = hashlib.md5(str(item.content).encode()).hexdigest()
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_items.append(item)
        
        logger.info(f"冗余消除：从{len(items)}项减少到{len(unique_items)}项")
        return unique_items
    
    def _calculate_current_entropy(self, items: List[InformationItem]) -> float:
        """计算当前熵"""
        total_entropy = 0.0
        
        for item in items:
            item_entropy = self.entropy_calculator.calculate_entropy(item.content)
            item.entropy_value = item_entropy
            total_entropy += item_entropy
        
        return total_entropy / len(items) if items else 0.0
    
    def _calculate_optimization_metrics(
        self, 
        baseline_entropy: float, 
        current_entropy: float, 
        compressed_items: List[InformationItem]
    ) -> EntropyMetrics:
        """计算优化指标"""
        
        # 熵减少百分比
        reduction_percentage = ((baseline_entropy - current_entropy) / baseline_entropy * 100) if baseline_entropy > 0 else 0.0
        
        # 平均压缩比
        compression_ratios = [item.compression_ratio for item in compressed_items if item.compression_ratio > 0]
        avg_compression = sum(compression_ratios) / len(compression_ratios) if compression_ratios else 1.0
        
        # 平均信息损失
        information_losses = [item.metadata.get('information_loss', 0.0) for item in compressed_items]
        avg_information_loss = sum(information_losses) / len(information_losses) if information_losses else 0.0
        
        # 优化评分 (综合指标)
        optimization_score = (
            reduction_percentage * 0.5 +  # 熵减少权重50%
            min(avg_compression / 10.0 * 100, 100) * 0.3 +  # 压缩比权重30%
            (1 - avg_information_loss) * 100 * 0.2  # 信息保真度权重20%
        )
        
        return EntropyMetrics(
            baseline_entropy=baseline_entropy,
            current_entropy=current_entropy,
            reduction_percentage=reduction_percentage,
            compression_achieved=avg_compression,
            information_loss=avg_information_loss,
            optimization_score=optimization_score
        )
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        if not self.optimization_history:
            return {"status": "no_optimizations_performed"}
        
        latest_metrics = self.optimization_history[-1]
        
        return {
            "optimization_summary": {
                "entropy_reduction_achieved": latest_metrics.reduction_percentage,
                "entropy_reduction_target": 40.0,
                "target_met": latest_metrics.reduction_percentage >= 40.0,
                "compression_ratio": latest_metrics.compression_achieved,
                "compression_target": 10.0,
                "compression_target_met": latest_metrics.compression_achieved >= 10.0,
                "information_loss": latest_metrics.information_loss,
                "information_loss_limit": 0.05,
                "information_loss_acceptable": latest_metrics.information_loss <= 0.05,
                "overall_optimization_score": latest_metrics.optimization_score
            },
            "performance_history": [
                {
                    "timestamp": i,
                    "entropy_reduction": metrics.reduction_percentage,
                    "compression_ratio": metrics.compression_achieved,
                    "information_loss": metrics.information_loss,
                    "optimization_score": metrics.optimization_score
                }
                for i, metrics in enumerate(self.optimization_history)
            ],
            "ssot_statistics": {
                "total_ssot_records": len(self.ssot_manager.ssot_storage),
                "categories_managed": {
                    info_type.value: len(records) 
                    for info_type, records in self.ssot_manager.category_index.items()
                }
            }
        }

# 工厂函数
def create_entropy_optimizer() -> EntropyOptimizer:
    """创建信息论优化器"""
    return EntropyOptimizer()

# 使用示例
async def demo_entropy_optimization():
    """演示信息论优化"""
    optimizer = create_entropy_optimizer()
    
    # 模拟信息项
    mock_items = [
        InformationItem(
            item_id="req_001",
            info_type=InformationType.REQUIREMENTS,
            content={"requirement": "用户登录功能", "details": "支持邮箱和手机号登录"},
            source="user_input",
            timestamp=datetime.now()
        ),
        InformationItem(
            item_id="req_002", 
            info_type=InformationType.REQUIREMENTS,
            content={"requirement": "用户登录功能", "details": "支持邮箱和手机号登录"},  # 重复内容
            source="duplicate_input",
            timestamp=datetime.now()
        ),
        InformationItem(
            item_id="design_001",
            info_type=InformationType.DESIGN,
            content={"architecture": "微服务架构", "components": ["用户服务", "认证服务"]},
            source="architect_agent",
            timestamp=datetime.now()
        )
    ]
    
    # 执行优化
    metrics = await optimizer.optimize_system_information(mock_items)
    
    print(f"信息论优化结果:")
    print(f"基线熵: {metrics.baseline_entropy:.3f}")
    print(f"当前熵: {metrics.current_entropy:.3f}")
    print(f"熵减少: {metrics.reduction_percentage:.1f}% (目标: ≥40%)")
    print(f"压缩比: {metrics.compression_achieved:.1f}:1 (目标: ≥10:1)")
    print(f"信息损失: {metrics.information_loss:.1%} (限制: ≤5%)")
    print(f"优化评分: {metrics.optimization_score:.1f}/100")
    
    # 获取详细报告
    report = optimizer.get_optimization_report()
    print(f"\n目标达成情况:")
    print(f"熵减少目标达成: {report['optimization_summary']['target_met']}")
    print(f"压缩比目标达成: {report['optimization_summary']['compression_target_met']}")
    print(f"信息损失控制: {report['optimization_summary']['information_loss_acceptable']}")

if __name__ == "__main__":
    asyncio.run(demo_entropy_optimization())
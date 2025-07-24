"""
数字员工Agent分层动态记忆引擎演示

展示记忆系统的核心功能：
1. 分层记忆存储与检索
2. 动态记忆重构与关联
3. 记忆-感知闭环处理
4. 跨层记忆融合
"""

import time
import json
import logging
from typing import Dict, List, Any
from memory_engine import *
from memory_reconstruction import *
from memory_perception_loop import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MemorySystemDemo:
    """记忆系统演示类"""
    
    def __init__(self):
        self.memory_system = create_memory_perception_system()
        self.demo_data = self._prepare_demo_data()
        
    def _prepare_demo_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """准备演示数据"""
        return {
            'conversations': [
                {"content": "用户询问如何生成报告", "type": "query"},
                {"content": "用户对上次的报告很满意", "type": "feedback"},
                {"content": "需要生成销售数据分析报告", "type": "task"}
            ],
            'events': [
                {
                    "description": "成功生成了Q3季度销售报告",
                    "participants": ["用户", "系统"],
                    "actions": ["数据收集", "分析处理", "报告生成"],
                    "results": ["生成完整报告", "用户满意"],
                    "location": "工作系统"
                },
                {
                    "description": "处理客户投诉关于数据错误",
                    "participants": ["客户", "客服", "系统"],
                    "actions": ["接收投诉", "核查数据", "修正错误"],
                    "results": ["问题解决", "客户满意"],
                    "location": "客服系统"
                }
            ],
            'knowledge': [
                {
                    "content": "报告生成需要包含数据收集、分析、可视化三个步骤",
                    "domain": "报告生成",
                    "concepts": ["数据收集", "数据分析", "可视化"],
                    "rules": ["先收集再分析", "分析后可视化"],
                    "certainty": 0.9
                },
                {
                    "content": "客户满意度评估基于响应时间、准确性、友好度",
                    "domain": "客户服务",
                    "concepts": ["满意度", "响应时间", "准确性", "友好度"],
                    "rules": ["快速响应提升满意度", "准确性是基础"],
                    "certainty": 0.8
                }
            ],
            'skills': [
                {
                    "skill_type": "报告生成",
                    "description": "自动生成各类数据报告的技能流程",
                    "steps": [
                        {"step": 1, "action": "确定报告类型和需求"},
                        {"step": 2, "action": "收集相关数据源"},
                        {"step": 3, "action": "进行数据清洗和处理"},
                        {"step": 4, "action": "执行数据分析"},
                        {"step": 5, "action": "生成图表和可视化"},
                        {"step": 6, "action": "编写报告内容"},
                        {"step": 7, "action": "格式化和输出报告"}
                    ],
                    "success_rate": 0.85,
                    "complexity": "medium"
                },
                {
                    "skill_type": "客户服务",
                    "description": "处理客户咨询和投诉的标准流程",
                    "steps": [
                        {"step": 1, "action": "接收并记录客户问题"},
                        {"step": 2, "action": "分析问题类型和优先级"},
                        {"step": 3, "action": "查找相关解决方案"},
                        {"step": 4, "action": "提供解决方案或转接"},
                        {"step": 5, "action": "跟进问题解决情况"},
                        {"step": 6, "action": "收集客户反馈"}
                    ],
                    "success_rate": 0.78,
                    "complexity": "high"
                }
            ],
            'emotions': [
                {
                    "emotion": "satisfaction",
                    "valence": 0.8,
                    "arousal": 0.6,
                    "user_satisfaction": 0.9,
                    "decision_context": "成功完成报告生成任务",
                    "trigger": "用户表扬"
                },
                {
                    "emotion": "concern",
                    "valence": -0.3,
                    "arousal": 0.7,
                    "user_satisfaction": 0.4,
                    "decision_context": "客户投诉数据错误",
                    "trigger": "质量问题"
                }
            ]
        }
    
    def run_complete_demo(self):
        """运行完整演示"""
        print("="*60)
        print("数字员工Agent分层动态记忆引擎演示")
        print("="*60)
        
        # 1. 演示记忆存储
        print("\n1. 演示分层记忆存储...")
        self.demo_memory_storage()
        
        # 2. 演示记忆检索
        print("\n2. 演示记忆检索...")
        self.demo_memory_retrieval()
        
        # 3. 演示动态关联
        print("\n3. 演示动态记忆关联...")
        self.demo_memory_associations()
        
        # 4. 演示感知-记忆闭环
        print("\n4. 演示感知-记忆闭环处理...")
        self.demo_perception_loop()
        
        # 5. 演示记忆融合
        print("\n5. 演示跨层记忆融合...")
        self.demo_memory_fusion()
        
        # 6. 展示系统状态
        print("\n6. 系统状态总览...")
        self.show_system_status()
        
        print("\n" + "="*60)
        print("演示完成！")
        print("="*60)
    
    def demo_memory_storage(self):
        """演示记忆存储功能"""
        print("正在向各记忆层存储数据...")
        
        # 存储工作记忆
        for i, conv in enumerate(self.demo_data['conversations']):
            memory = WorkingMemoryNode(
                id=f"work_mem_{i}",
                content=conv['content'],
                timestamp=time.time() - i * 100,
                attention_score=0.9 - i * 0.1
            )
            self.memory_system.memory_layers['working'].store(memory)
            print(f"  ✓ 工作记忆: {conv['content'][:30]}...")
        
        # 存储情景记忆
        for i, event in enumerate(self.demo_data['events']):
            memory = EpisodicMemoryNode(
                id=f"episode_mem_{i}",
                content=event['description'],
                timestamp=time.time() - i * 3600,
                location=event['location'],
                participants=event['participants'],
                actions=event['actions'],
                results=event['results']
            )
            self.memory_system.memory_layers['episodic'].store(memory)
            print(f"  ✓ 情景记忆: {event['description'][:30]}...")
        
        # 存储语义记忆
        for i, knowledge in enumerate(self.demo_data['knowledge']):
            memory = SemanticMemoryNode(
                id=f"semantic_mem_{i}",
                content=knowledge['content'],
                timestamp=time.time() - i * 1800,
                concepts=knowledge['concepts'],
                rules=knowledge['rules'],
                weight=knowledge['certainty']
            )
            self.memory_system.memory_layers['semantic'].store(memory)
            print(f"  ✓ 语义记忆: {knowledge['content'][:30]}...")
        
        # 存储程序性记忆
        for i, skill in enumerate(self.demo_data['skills']):
            memory = ProceduralMemoryNode(
                id=f"procedural_mem_{i}",
                content=skill['description'],
                timestamp=time.time() - i * 7200,
                skill_type=skill['skill_type'],
                steps=skill['steps'],
                success_rate=skill['success_rate']
            )
            self.memory_system.memory_layers['procedural'].store(memory)
            print(f"  ✓ 程序性记忆: {skill['skill_type']}")
        
        # 存储情感记忆
        for i, emotion in enumerate(self.demo_data['emotions']):
            memory = EmotionalMemoryNode(
                id=f"emotional_mem_{i}",  
                content=emotion['decision_context'],
                timestamp=time.time() - i * 1200,
                emotion_type=emotion['emotion'],
                valence=emotion['valence'],
                arousal=emotion['arousal'],
                user_satisfaction=emotion['user_satisfaction'],
                decision_context=emotion['decision_context']
            )
            self.memory_system.memory_layers['emotional'].store(memory)
            print(f"  ✓ 情感记忆: {emotion['emotion']} ({emotion['decision_context'][:20]}...)")
    
    def demo_memory_retrieval(self):
        """演示记忆检索功能"""
        print("演示各层记忆检索...")
        
        test_queries = [
            ("报告", "semantic"),
            ("客户", "episodic"), 
            ("生成", "procedural"),
            ("满意", "emotional"),
            ("用户", "working")
        ]
        
        for query, preferred_layer in test_queries:
            print(f"\n查询: '{query}' (优先从{preferred_layer}层检索)")
            
            if preferred_layer in self.memory_system.memory_layers:
                layer = self.memory_system.memory_layers[preferred_layer]
                results = layer.retrieve(query, top_k=2)
                
                for result in results:
                    print(f"  → [{type(result).__name__}] {str(result.content)[:50]}...")
                    print(f"     权重: {result.weight:.2f}, 访问次数: {result.access_count}")
    
    def demo_memory_associations(self):
        """演示记忆关联功能"""
        print("演示动态记忆关联检测...")
        
        # 获取一些示例记忆
        semantic_memories = list(self.memory_system.memory_layers['semantic'].memories.values())
        episodic_memories = list(self.memory_system.memory_layers['episodic'].memories.values())
        
        if len(semantic_memories) >= 2:
            print(f"\n检测语义记忆间的关联:")
            detector = AssociationDetector()
            
            associations = detector.detect_associations(
                semantic_memories[0], semantic_memories[1]
            )
            
            for assoc in associations:
                print(f"  → {assoc.association_type}关联 (强度: {assoc.strength:.2f})")
                print(f"     {assoc.source_id} -> {assoc.target_id}")
        
        if semantic_memories and episodic_memories:
            print(f"\n检测跨层记忆关联:")
            associations = detector.detect_associations(
                semantic_memories[0], episodic_memories[0]
            )
            
            for assoc in associations:
                print(f"  → {assoc.association_type}关联 (强度: {assoc.strength:.2f})")
                print(f"     语义记忆 -> 情景记忆")
    
    def demo_perception_loop(self):
        """演示感知-记忆闭环处理"""
        print("演示感知-记忆闭环处理...")
        
        test_inputs = [
            {
                "input": "我需要生成一份销售报告",
                "type": InputType.QUERY,
                "context": {"urgency": "high", "source": "user"}
            },
            {
                "input": {
                    "description": "用户反馈报告质量很好",
                    "participants": ["用户", "系统"],
                    "outcome": "positive_feedback"
                },
                "type": InputType.EVENT,
                "context": {"source": "feedback_system"}
            },
            {
                "input": {
                    "emotion": "satisfaction",
                    "intensity": 0.8,
                    "trigger": "successful_task_completion"
                },
                "type": InputType.EMOTION,
                "context": {"source": "emotional_analyzer"}
            }
        ]
        
        for i, test_case in enumerate(test_inputs):
            print(f"\n处理输入 {i+1}: {test_case['type'].value}")
            print(f"内容: {str(test_case['input'])[:60]}...")
            
            # 处理输入
            result = self.memory_system.process(
                test_case['input'],
                test_case['type'],
                test_case['context']
            )
            
            print(f"响应: {result.response[:80]}...")
            print(f"置信度: {result.confidence:.2f}")
            print(f"激活记忆数: {len(result.activated_memories)}")
            print(f"推理路径: {' -> '.join(result.reasoning_path)}")
            
            if result.emotional_context['dominant_emotion'] != 'neutral':
                print(f"情感上下文: {result.emotional_context['dominant_emotion']} "
                     f"(效价: {result.emotional_context['average_valence']:.2f})")
    
    def demo_memory_fusion(self):
        """演示记忆融合功能"""
        print("演示跨层记忆融合...")
        
        # 跨层检索
        fusion_query = "报告生成流程"
        print(f"\n融合查询: '{fusion_query}'")
        
        retrieval_result = self.memory_system.cross_layer_retriever.cross_layer_retrieve(
            fusion_query, max_results=5
        )
        
        print("检索到的记忆:")
        for result in retrieval_result['primary_results']:
            print(f"  → [{result['layer']}] {str(result['content'])[:40]}... "
                 f"(权重: {result['weight']:.2f})")
        
        print(f"\n融合响应:")
        fusion_response = retrieval_result['fused_response']
        print(f"内容: {fusion_response['fused_content'][:100]}...")
        print(f"置信度: {fusion_response['confidence']:.2f}")
        print(f"来源数量: {len(fusion_response['sources'])}")
        
        if retrieval_result['associated_memories']:
            print(f"\n关联记忆:")
            for mem_id, strength in retrieval_result['associated_memories'][:3]:
                print(f"  → {mem_id} (关联强度: {strength:.2f})")
    
    def show_system_status(self):
        """显示系统状态"""
        print("系统当前状态:")
        
        # 记忆层状态
        memory_status = self.memory_system.get_memory_status()
        print(f"\n记忆层利用率:")
        for layer_name, status in memory_status.items():
            utilization = status['utilization'] * 100
            print(f"  {layer_name:12}: {status['size']:3}/{status['capacity']:4} "
                 f"({utilization:5.1f}%) - 近期访问: {status['recent_access']}")
        
        # 处理统计
        processing_stats = self.memory_system.get_processing_stats()
        if processing_stats:
            print(f"\n处理统计 (最近1小时):")
            print(f"  总处理数: {processing_stats['total_processed']}")
            print(f"  平均耗时: {processing_stats['average_processing_time']:.3f}s")
            print(f"  平均置信度: {processing_stats['average_confidence']:.2f}")
            
            print(f"  输入类型分布:")
            for input_type, count in processing_stats['input_type_distribution'].items():
                percentage = (count / processing_stats['total_processed']) * 100
                print(f"    {input_type}: {count} ({percentage:.1f}%)")

def run_unit_tests():
    """运行单元测试"""
    print("运行记忆引擎单元测试...")
    
    # 测试记忆衰减算法
    print("\n测试记忆衰减算法:")
    initial_weight = 1.0
    time_passed = 24.0  # 24小时
    
    exp_decay = MemoryDecayAlgorithm.exponential_decay(initial_weight, time_passed)
    power_decay = MemoryDecayAlgorithm.power_law_decay(initial_weight, time_passed)
    ebbinghaus_decay = MemoryDecayAlgorithm.ebbinghaus_forgetting_curve(initial_weight, time_passed)
    
    print(f"  指数衰减: {initial_weight:.2f} -> {exp_decay:.2f}")
    print(f"  幂律衰减: {initial_weight:.2f} -> {power_decay:.2f}")
    print(f"  艾宾浩斯曲线: {initial_weight:.2f} -> {ebbinghaus_decay:.2f}")
    
    # 测试记忆层基本功能
    print("\n测试记忆层基本功能:")
    
    # 工作记忆测试
    working_mem = WorkingMemory(capacity=3)
    for i in range(5):  # 超过容量测试
        memory = WorkingMemoryNode(
            id=f"test_{i}",
            content=f"测试内容 {i}",
            timestamp=time.time() + i
        )
        working_mem.store(memory)
    
    print(f"  工作记忆存储测试: 容量={working_mem.capacity}, 实际={working_mem.get_size()}")
    
    # 检索测试
    results = working_mem.retrieve("测试", top_k=2)
    print(f"  工作记忆检索测试: 找到 {len(results)} 条结果")
    
    # 测试记忆图谱
    print("\n测试记忆图谱:")
    memory_graph = MemoryGraph()
    
    # 添加测试节点
    test_memory1 = SemanticMemoryNode(
        id="test_semantic_1",
        content="测试语义记忆1",
        timestamp=time.time(),
        concepts=["测试", "记忆"]
    )
    
    test_memory2 = SemanticMemoryNode(
        id="test_semantic_2", 
        content="测试语义记忆2",
        timestamp=time.time(),
        concepts=["测试", "系统"]
    )
    
    memory_graph.add_memory_node(test_memory1)
    memory_graph.add_memory_node(test_memory2)
    
    print(f"  记忆图谱节点数: {memory_graph.graph.number_of_nodes()}")
    
    # 测试关联检测
    detector = AssociationDetector()
    associations = detector.detect_associations(test_memory1, test_memory2)
    print(f"  检测到 {len(associations)} 个关联关系")
    
    for assoc in associations:
        print(f"    {assoc.association_type}: {assoc.strength:.2f}")
    
    print("✓ 所有单元测试通过")

def interactive_demo():
    """交互式演示"""
    print("启动交互式记忆系统演示...")
    print("你可以输入不同类型的信息，系统将展示记忆处理过程")
    print("输入 'quit' 退出，'status' 查看系统状态，'help' 查看帮助")
    
    memory_system = create_memory_perception_system()
    
    # 预加载一些示例数据
    demo = MemorySystemDemo()
    demo.memory_system = memory_system
    demo.demo_memory_storage()
    
    print("\n系统已准备就绪，预加载了示例记忆数据")
    
    while True:
        try:
            user_input = input("\n请输入 > ").strip()
            
            if user_input.lower() == 'quit':
                print("退出交互式演示")
                break
            elif user_input.lower() == 'status':
                demo.show_system_status()
                continue
            elif user_input.lower() == 'help':
                print("可用命令:")
                print("  - 直接输入文本进行查询处理")
                print("  - 'status' - 显示系统状态")
                print("  - 'quit' - 退出程序")
                print("  - 'help' - 显示此帮助信息")
                continue
            elif not user_input:
                continue
            
            # 处理用户输入
            print(f"\n处理输入: {user_input}")
            
            result = memory_system.process(
                user_input,
                InputType.QUERY,
                {"source": "interactive_user", "timestamp": time.time()}
            )
            
            print(f"\n系统响应:")
            print(f"  内容: {result.response}")
            print(f"  置信度: {result.confidence:.2f}")
            print(f"  激活记忆: {len(result.activated_memories)} 个")
            
            if result.reasoning_path:
                print(f"  推理路径: {' → '.join(result.reasoning_path)}")
            
            if result.emotional_context['dominant_emotion'] != 'neutral':
                emotion = result.emotional_context
                print(f"  情感分析: {emotion['dominant_emotion']} "
                     f"(效价: {emotion['average_valence']:.2f}, "
                     f"唤醒: {emotion['average_arousal']:.2f})")
            
        except KeyboardInterrupt:
            print("\n收到中断信号，退出程序")
            break
        except Exception as e:
            print(f"处理错误: {e}")
            logger.error(f"交互式演示错误: {e}", exc_info=True)

if __name__ == "__main__":
    print("数字员工Agent分层动态记忆引擎")
    print("选择运行模式:")
    print("1. 完整演示")
    print("2. 单元测试")
    print("3. 交互式演示")
    
    try:
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            demo = MemorySystemDemo()
            demo.run_complete_demo()
        elif choice == "2":
            run_unit_tests()
        elif choice == "3":
            interactive_demo()
        else:
            print("无效选择，运行完整演示...")
            demo = MemorySystemDemo()
            demo.run_complete_demo()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行错误: {e}")
        logger.error(f"主程序错误: {e}", exc_info=True)
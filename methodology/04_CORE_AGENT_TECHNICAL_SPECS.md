# 核心Agent技术规范
*面向开发团队的详细技术实现规范*

## Agent基础架构规范

### BaseAgent抽象类定义
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

@dataclass
class AgentCapability:
    """Agent能力定义"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    processing_time_sla: int  # 秒
    accuracy_target: float    # 0.0-1.0

@dataclass
class AgentMetrics:
    """Agent性能指标"""
    total_requests: int = 0
    successful_requests: int = 0
    average_processing_time: float = 0.0
    accuracy_score: float = 0.0
    error_rate: float = 0.0
    last_updated: datetime = datetime.now()

class BaseAgent(ABC):
    """Agent基类，定义通用接口和行为"""
    
    def __init__(self, agent_id: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.metrics = AgentMetrics()
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.status = "initialized"
        self._message_handlers = {}
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理业务请求的核心方法"""
        pass
    
    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据的有效性"""
        pass
    
    @abstractmethod
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """验证输出数据的有效性"""
        pass
    
    async def handle_message(self, message: 'AgentMessage') -> Optional['AgentMessage']:
        """处理来自其他Agent的消息"""
        try:
            start_time = datetime.now()
            
            # 输入验证
            if not await self.validate_input(message.content):
                raise ValueError("Invalid input data")
            
            # 业务处理
            result = await self.process_request(message.content)
            
            # 输出验证
            if not await self.validate_output(result):
                raise ValueError("Invalid output data")
            
            # 更新指标
            processing_time = (datetime.now() - start_time).total_seconds()
            await self.update_metrics(processing_time, success=True)
            
            # 构造响应消息
            response = AgentMessage(
                message_id=f"{self.agent_id}_{datetime.now().timestamp()}",
                sender_agent=self.agent_id,
                receiver_agent=message.sender_agent,
                message_type="RESPONSE",
                content=result,
                timestamp=datetime.now()
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            await self.update_metrics(0, success=False)
            raise
    
    async def update_metrics(self, processing_time: float, success: bool):
        """更新Agent性能指标"""
        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_requests += 1
        
        # 更新平均处理时间
        total_time = self.metrics.average_processing_time * (self.metrics.total_requests - 1)
        self.metrics.average_processing_time = (total_time + processing_time) / self.metrics.total_requests
        
        # 更新错误率
        self.metrics.error_rate = 1 - (self.metrics.successful_requests / self.metrics.total_requests)
        
        self.metrics.last_updated = datetime.now()
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取Agent健康状态"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.successful_requests / max(self.metrics.total_requests, 1),
                "average_processing_time": self.metrics.average_processing_time,
                "error_rate": self.metrics.error_rate
            },
            "capabilities": [cap.name for cap in self.capabilities],
            "last_updated": self.metrics.last_updated.isoformat()
        }
```

## 需求理解Agent技术规范

### 核心算法实现
```python
import re
from typing import List, Dict, Tuple
import nltk
from transformers import pipeline, AutoTokenizer, AutoModel
import spacy

class RequirementAnalysisAgent(BaseAgent):
    """需求理解Agent实现"""
    
    def __init__(self):
        capabilities = [
            AgentCapability(
                name="requirement_analysis",
                description="自然语言需求分析和结构化",
                input_types=["natural_language"],
                output_types=["structured_requirement"],
                processing_time_sla=30,
                accuracy_target=0.85
            )
        ]
        super().__init__("requirement_agent", capabilities)
        
        # 初始化NLP组件
        self.nlp = spacy.load("zh_core_web_sm")
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-chinanews-chinese")
        self.tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-bert-wwm-ext")
        
        # 需求模板库
        self.requirement_templates = {
            "functional": [
                "系统应当在{}时{}",
                "用户可以通过{}来{}",
                "当{}发生时，系统会{}"
            ],
            "performance": [
                "系统响应时间不应超过{}",
                "系统应支持{}并发用户",
                "系统可用性应达到{}"
            ],
            "security": [
                "系统应当验证{}",
                "敏感数据应当{}",
                "访问权限应当基于{}"
            ]
        }
        
        # 关键词词典
        self.keywords = {
            "performance": ["性能", "响应时间", "并发", "吞吐量", "可用性"],
            "security": ["安全", "权限", "认证", "加密", "防护"],
            "functional": ["功能", "操作", "处理", "管理", "查询"],
            "usability": ["界面", "体验", "易用性", "友好", "直观"]
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理需求分析请求"""
        user_input = request.get("user_input", "")
        context = request.get("context", {})
        
        # 1. 预处理输入文本
        cleaned_text = await self.preprocess_text(user_input)
        
        # 2. 实体识别和关键信息提取
        entities = await self.extract_entities(cleaned_text)
        
        # 3. 需求分类
        requirement_type = await self.classify_requirement_type(cleaned_text)
        
        # 4. 结构化需求
        structured_req = await self.structure_requirement(cleaned_text, entities, requirement_type)
        
        # 5. 生成澄清问题
        clarification_questions = await self.generate_clarification_questions(structured_req)
        
        # 6. 转换为EARS格式
        ears_format = await self.convert_to_ears(structured_req)
        
        # 7. 置信度计算
        confidence_score = await self.calculate_confidence(structured_req, entities)
        
        return {
            "structured_requirement": structured_req,
            "requirement_type": requirement_type,
            "entities": entities,
            "clarification_questions": clarification_questions,
            "ears_format": ears_format,
            "confidence_score": confidence_score,
            "processing_metadata": {
                "original_text": user_input,
                "cleaned_text": cleaned_text,
                "processing_time": datetime.now().isoformat()
            }
        }
    
    async def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 标准化标点符号
        text = re.sub(r'[，。！？；：]', lambda m: {'，': ',', '。': '.', '！': '!', '？': '?', '；': ';', '：': ':'}[m.group()], text)
        
        # 去除特殊字符但保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s,.!?;:]', '', text)
        
        return text
    
    async def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """实体识别"""
        doc = self.nlp(text)
        
        entities = {
            "persons": [],
            "organizations": [],
            "systems": [],
            "functions": [],
            "metrics": [],
            "constraints": []
        }
        
        # 使用spaCy进行基础实体识别
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
        
        # 自定义规则识别系统和功能实体
        system_patterns = [r'(\w+系统)', r'(\w+平台)', r'(\w+服务)']
        for pattern in system_patterns:
            matches = re.findall(pattern, text)
            entities["systems"].extend(matches)
        
        function_patterns = [r'(\w+功能)', r'(\w+模块)', r'(\w+管理)']
        for pattern in function_patterns:
            matches = re.findall(pattern, text)
            entities["functions"].extend(matches)
        
        # 性能指标识别
        metric_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:秒|毫秒|分钟)',  # 时间
            r'(\d+)\s*(?:用户|人|并发)',           # 用户数
            r'(\d+(?:\.\d+)?)\s*(?:%|百分比)'      # 百分比
        ]
        for pattern in metric_patterns:
            matches = re.findall(pattern, text)
            entities["metrics"].extend(matches)
        
        return entities
    
    async def classify_requirement_type(self, text: str) -> str:
        """需求类型分类"""
        type_scores = {}
        
        for req_type, keywords in self.keywords.items():
            score = 0
            for keyword in keywords:
                score += text.count(keyword)
            type_scores[req_type] = score
        
        # 返回得分最高的类型
        return max(type_scores, key=type_scores.get) if max(type_scores.values()) > 0 else "functional"
    
    async def structure_requirement(self, text: str, entities: Dict, req_type: str) -> Dict[str, Any]:
        """结构化需求"""
        structured = {
            "id": f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": req_type,
            "title": await self.extract_title(text),
            "description": text,
            "actors": entities.get("persons", []),
            "systems": entities.get("systems", []),
            "functions": entities.get("functions", []),
            "constraints": await self.extract_constraints(text, entities),
            "priorities": await self.extract_priorities(text),
            "acceptance_criteria": []
        }
        
        return structured
    
    async def extract_title(self, text: str) -> str:
        """提取需求标题"""
        # 简单实现：取前20个字符作为标题
        title = text[:20].strip()
        if len(text) > 20:
            title += "..."
        return title
    
    async def extract_constraints(self, text: str, entities: Dict) -> List[str]:
        """提取约束条件"""
        constraints = []
        
        # 时间约束
        time_patterns = [
            r'在(\d+(?:\.\d+)?(?:秒|分钟|小时|天))内',
            r'不超过(\d+(?:\.\d+)?(?:秒|分钟|小时|天))'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                constraints.append(f"时间约束: {match}")
        
        # 性能约束
        if entities.get("metrics"):
            for metric in entities["metrics"]:
                constraints.append(f"性能约束: {metric}")
        
        return constraints
    
    async def extract_priorities(self, text: str) -> str:
        """提取优先级"""
        high_priority_keywords = ["紧急", "重要", "关键", "必须", "立即"]
        medium_priority_keywords = ["需要", "应该", "希望"]
        low_priority_keywords = ["可以", "建议", "最好"]
        
        for keyword in high_priority_keywords:
            if keyword in text:
                return "高"
        
        for keyword in medium_priority_keywords:
            if keyword in text:
                return "中"
        
        for keyword in low_priority_keywords:
            if keyword in text:
                return "低"
        
        return "中"  # 默认中等优先级
    
    async def generate_clarification_questions(self, structured_req: Dict) -> List[str]:
        """生成澄清问题"""
        questions = []
        
        # 根据需求类型生成特定问题
        if structured_req["type"] == "performance":
            questions.extend([
                "具体的性能指标是什么？（如响应时间、并发用户数）",
                "在什么场景下需要达到这些性能指标？",
                "如果性能不达标，可接受的降级方案是什么？"
            ])
        
        elif structured_req["type"] == "functional":
            questions.extend([
                "这个功能的具体操作流程是什么？",
                "需要支持哪些用户角色？",
                "异常情况下应该如何处理？"
            ])
        
        elif structured_req["type"] == "security":
            questions.extend([
                "需要保护哪些敏感数据？",
                "用户权限如何划分？",
                "安全审计需要记录哪些信息？"
            ])
        
        # 通用问题
        if not structured_req.get("constraints"):
            questions.append("这个需求有什么特殊的约束条件吗？")
        
        if not structured_req.get("actors"):
            questions.append("主要的使用者是谁？")
        
        return questions[:5]  # 最多返回5个问题
    
    async def convert_to_ears(self, structured_req: Dict) -> str:
        """转换为EARS格式"""
        req_type = structured_req["type"]
        description = structured_req["description"]
        
        if req_type == "functional":
            # 功能性需求：The system shall...
            return f"The system shall {description.lower()} when requested by authorized users."
        
        elif req_type == "performance":
            # 性能需求：The system shall... within...
            constraints = structured_req.get("constraints", [])
            time_constraint = next((c for c in constraints if "时间约束" in c), "2秒")
            return f"The system shall {description.lower()} within {time_constraint}."
        
        elif req_type == "security":
            # 安全需求：The system shall... to ensure...
            return f"The system shall {description.lower()} to ensure data security and user privacy."
        
        else:
            # 默认格式
            return f"The system shall {description.lower()}."
    
    async def calculate_confidence(self, structured_req: Dict, entities: Dict) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度
        
        # 根据实体数量调整
        entity_count = sum(len(v) for v in entities.values())
        confidence += min(entity_count * 0.05, 0.3)
        
        # 根据描述长度调整
        desc_length = len(structured_req["description"])
        if desc_length > 20:
            confidence += 0.1
        if desc_length > 50:
            confidence += 0.1
        
        # 根据约束条件调整
        if structured_req.get("constraints"):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ["user_input"]
        return all(field in input_data and input_data[field] for field in required_fields)
    
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """验证输出数据"""
        required_fields = ["structured_requirement", "confidence_score"]
        return all(field in output_data for field in required_fields)
```

## Agent通信中间件

### 消息路由器实现
```python
import asyncio
from typing import Dict, List, Callable, Optional
from enum import Enum
import json
import redis.asyncio as redis

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10

class MessageRouter:
    """Agent消息路由器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.agents: Dict[str, BaseAgent] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
    
    async def register_agent(self, agent: BaseAgent):
        """注册Agent"""
        self.agents[agent.agent_id] = agent
        self.message_handlers[agent.agent_id] = agent.handle_message
        await self.redis_client.sadd("active_agents", agent.agent_id)
    
    async def unregister_agent(self, agent_id: str):
        """注销Agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.message_handlers[agent_id]
            await self.redis_client.srem("active_agents", agent_id)
    
    async def send_message(self, message: 'AgentMessage') -> bool:
        """发送消息"""
        try:
            # 验证目标Agent是否存在
            if not await self.redis_client.sismember("active_agents", message.receiver_agent):
                raise ValueError(f"Agent {message.receiver_agent} not registered")
            
            # 序列化消息
            message_data = {
                "message_id": message.message_id,
                "sender_agent": message.sender_agent,
                "receiver_agent": message.receiver_agent,
                "message_type": message.message_type,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "priority": getattr(message, 'priority', MessagePriority.NORMAL.value)
            }
            
            # 根据优先级选择队列
            queue_name = f"agent_queue:{message.receiver_agent}"
            if message_data["priority"] >= MessagePriority.HIGH.value:
                queue_name += ":high"
            
            # 推送到Redis队列
            await self.redis_client.lpush(queue_name, json.dumps(message_data))
            
            # 记录消息路由日志
            await self.log_message(message_data, "sent")
            
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    async def start_workers(self, worker_count: int = 5):
        """启动消息处理工作者"""
        self.running = True
        
        for i in range(worker_count):
            task = asyncio.create_task(self.message_worker(f"worker_{i}"))
            self.worker_tasks.append(task)
    
    async def stop_workers(self):
        """停止消息处理工作者"""
        self.running = False
        
        for task in self.worker_tasks:
            task.cancel()
        
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
    
    async def message_worker(self, worker_id: str):
        """消息处理工作者"""
        while self.running:
            try:
                # 获取所有活跃的Agent队列
                active_agents = await self.redis_client.smembers("active_agents")
                
                if not active_agents:
                    await asyncio.sleep(1)
                    continue
                
                # 构建队列名称列表（高优先级队列优先）
                queues = []
                for agent_id in active_agents:
                    agent_id = agent_id.decode()
                    queues.append(f"agent_queue:{agent_id}:high")
                    queues.append(f"agent_queue:{agent_id}")
                
                # 阻塞式获取消息
                result = await self.redis_client.brpop(queues, timeout=5)
                
                if result:
                    queue_name, message_data = result
                    queue_name = queue_name.decode()
                    message_data = json.loads(message_data)
                    
                    # 提取目标Agent ID
                    agent_id = message_data["receiver_agent"]
                    
                    # 处理消息
                    await self.process_message(agent_id, message_data, worker_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)
    
    async def process_message(self, agent_id: str, message_data: Dict, worker_id: str):
        """处理单个消息"""
        try:
            # 重构AgentMessage对象
            message = AgentMessage(
                message_id=message_data["message_id"],
                sender_agent=message_data["sender_agent"],
                receiver_agent=message_data["receiver_agent"],
                message_type=message_data["message_type"],
                content=message_data["content"],
                timestamp=datetime.fromisoformat(message_data["timestamp"])
            )
            
            # 调用Agent处理器
            if agent_id in self.message_handlers:
                response = await self.message_handlers[agent_id](message)
                
                # 如果有响应消息，则路由回发送者
                if response:
                    await self.send_message(response)
                
                # 记录处理日志
                await self.log_message(message_data, "processed", worker_id)
            
        except Exception as e:
            print(f"Error processing message {message_data.get('message_id')}: {e}")
            await self.log_message(message_data, "failed", worker_id, str(e))
    
    async def log_message(self, message_data: Dict, status: str, worker_id: str = None, error: str = None):
        """记录消息日志"""
        log_entry = {
            "message_id": message_data["message_id"],
            "sender": message_data["sender_agent"],
            "receiver": message_data["receiver_agent"],
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "worker_id": worker_id,
            "error": error
        }
        
        await self.redis_client.lpush("message_logs", json.dumps(log_entry))
        
        # 保持日志队列长度
        await self.redis_client.ltrim("message_logs", 0, 9999)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        active_agents = await self.redis_client.smembers("active_agents")
        agent_statuses = {}
        
        for agent_id in active_agents:
            agent_id = agent_id.decode()
            if agent_id in self.agents:
                status = await self.agents[agent_id].get_health_status()
                agent_statuses[agent_id] = status
        
        # 队列状态
        queue_statuses = {}
        for agent_id in active_agents:
            agent_id = agent_id.decode()
            high_queue = f"agent_queue:{agent_id}:high"
            normal_queue = f"agent_queue:{agent_id}"
            
            high_count = await self.redis_client.llen(high_queue)
            normal_count = await self.redis_client.llen(normal_queue)
            
            queue_statuses[agent_id] = {
                "high_priority_messages": high_count,
                "normal_priority_messages": normal_count,
                "total_pending": high_count + normal_count
            }
        
        return {
            "system_status": "running" if self.running else "stopped",
            "active_agents": len(active_agents),
            "worker_count": len(self.worker_tasks),
            "agent_statuses": agent_statuses,
            "queue_statuses": queue_statuses,
            "timestamp": datetime.now().isoformat()
        }
```

## 监控和告警系统

### 性能监控实现
```python
import time
from typing import Dict, List
from dataclasses import dataclass, asdict
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import asyncio

@dataclass
class AlertRule:
    """告警规则定义"""
    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq"
    threshold: float
    duration: int   # 持续时间（秒）
    severity: str   # "low", "medium", "high", "critical"
    message: str

class AgentMonitor:
    """Agent监控系统"""
    
    def __init__(self):
        # Prometheus指标
        self.request_counter = Counter(
            'agent_requests_total',
            'Total number of requests processed by agents',
            ['agent_id', 'status']
        )
        
        self.processing_time = Histogram(
            'agent_processing_seconds',
            'Time spent processing requests',
            ['agent_id']
        )
        
        self.active_agents = Gauge(
            'active_agents_count',
            'Number of active agents'
        )
        
        self.queue_size = Gauge(
            'agent_queue_size',
            'Number of messages in agent queues',
            ['agent_id', 'priority']
        )
        
        # 告警规则
        self.alert_rules = [
            AlertRule(
                name="high_error_rate",
                metric_name="error_rate",
                condition="gt",
                threshold=0.1,
                duration=300,
                severity="high",
                message="Agent error rate exceeds 10%"
            ),
            AlertRule(
                name="slow_processing",
                metric_name="avg_processing_time",
                condition="gt",
                threshold=30.0,
                duration=600,
                severity="medium",
                message="Agent processing time is too slow"
            ),
            AlertRule(
                name="queue_backlog",
                metric_name="queue_size",
                condition="gt",
                threshold=100,
                duration=180,
                severity="high",
                message="Agent queue has too many pending messages"
            )
        ]
        
        self.alert_states = {}
        self.alert_callbacks: List[Callable] = []
    
    async def start_monitoring(self, port: int = 8000):
        """启动监控服务"""
        # 启动Prometheus指标服务器
        start_http_server(port)
        
        # 启动告警检查任务
        asyncio.create_task(self.alert_checker())
    
    async def record_request(self, agent_id: str, processing_time: float, success: bool):
        """记录请求指标"""
        status = "success" if success else "error"
        self.request_counter.labels(agent_id=agent_id, status=status).inc()
        self.processing_time.labels(agent_id=agent_id).observe(processing_time)
    
    async def update_queue_metrics(self, agent_id: str, high_priority_count: int, normal_count: int):
        """更新队列指标"""
        self.queue_size.labels(agent_id=agent_id, priority="high").set(high_priority_count)
        self.queue_size.labels(agent_id=agent_id, priority="normal").set(normal_count)
    
    async def update_agent_count(self, count: int):
        """更新活跃Agent数量"""
        self.active_agents.set(count)
    
    async def alert_checker(self):
        """告警检查器"""
        while True:
            try:
                for rule in self.alert_rules:
                    await self.check_alert_rule(rule)
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                print(f"Alert checker error: {e}")
                await asyncio.sleep(60)
    
    async def check_alert_rule(self, rule: AlertRule):
        """检查单个告警规则"""
        # 这里需要实现具体的指标获取逻辑
        # 由于Prometheus客户端库的限制，这里简化实现
        current_time = time.time()
        
        # 获取指标值（简化实现）
        metric_value = await self.get_metric_value(rule.metric_name)
        
        # 检查条件
        triggered = False
        if rule.condition == "gt" and metric_value > rule.threshold:
            triggered = True
        elif rule.condition == "lt" and metric_value < rule.threshold:
            triggered = True
        elif rule.condition == "eq" and metric_value == rule.threshold:
            triggered = True
        
        # 处理告警状态
        if triggered:
            if rule.name not in self.alert_states:
                self.alert_states[rule.name] = current_time
            elif current_time - self.alert_states[rule.name] >= rule.duration:
                # 触发告警
                await self.trigger_alert(rule, metric_value)
        else:
            # 清除告警状态
            if rule.name in self.alert_states:
                del self.alert_states[rule.name]
    
    async def get_metric_value(self, metric_name: str) -> float:
        """获取指标值（简化实现）"""
        # 实际实现中需要从Prometheus或其他监控系统获取指标值
        return 0.0
    
    async def trigger_alert(self, rule: AlertRule, current_value: float):
        """触发告警"""
        alert_data = {
            "rule_name": rule.name,
            "severity": rule.severity,
            "message": rule.message,
            "current_value": current_value,
            "threshold": rule.threshold,
            "timestamp": datetime.now().isoformat()
        }
        
        # 调用所有注册的告警回调
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def register_alert_callback(self, callback: Callable):
        """注册告警回调函数"""
        self.alert_callbacks.append(callback)

# 告警回调函数示例
async def slack_alert_callback(alert_data: Dict):
    """Slack告警回调"""
    # 实现发送Slack消息的逻辑
    print(f"Slack Alert: {alert_data['message']}")

async def email_alert_callback(alert_data: Dict):
    """邮件告警回调"""
    # 实现发送邮件的逻辑
    print(f"Email Alert: {alert_data['message']}")
```

## 部署和运维规范

### Docker容器化配置
```dockerfile
# Dockerfile.agent
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 下载spaCy中文模型
RUN python -m spacy download zh_core_web_sm

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# 启动命令
CMD ["python", "-m", "agents.main"]
```

### Kubernetes部署配置
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-employee-agents
  labels:
    app: digital-employee
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digital-employee-agent
  template:
    metadata:
      labels:
        app: digital-employee-agent
    spec:
      containers:
      - name: agent
        image: digital-employee/agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: connection-string
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: agent-service
spec:
  selector:
    app: digital-employee-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

## 安全和合规规范

### 数据安全实现
```python
import hashlib
import hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class SecurityManager:
    """安全管理器"""
    
    def __init__(self, master_key: str):
        self.master_key = master_key.encode()
        self.fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """创建加密器"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'stable_salt',  # 实际使用中应该使用随机盐
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)
    
    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    def hash_sensitive_data(self, data: str) -> str:
        """对敏感数据进行哈希"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_signature(self, data: str, signature: str) -> bool:
        """验证数字签名"""
        expected_signature = hmac.new(
            self.master_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    
    def create_signature(self, data: str) -> str:
        """创建数字签名"""
        return hmac.new(
            self.master_key,
            data.encode(),
            hashlib.sha256
        ).hexdigest()

# 权限管理
class RoleBasedAccessControl:
    """基于角色的访问控制"""
    
    def __init__(self):
        self.roles = {
            "admin": {
                "permissions": ["*"],
                "description": "系统管理员"
            },
            "project_manager": {
                "permissions": [
                    "project.read", "project.write",
                    "agent.read", "agent.execute"
                ],
                "description": "项目经理"
            },
            "developer": {
                "permissions": [
                    "agent.read", "agent.execute",
                    "code.read", "code.write"
                ],
                "description": "开发人员"
            },
            "business_user": {
                "permissions": [
                    "requirement.read", "requirement.write",
                    "agent.read"
                ],
                "description": "业务用户"
            }
        }
        
        self.user_roles = {}
    
    def assign_role(self, user_id: str, role: str):
        """分配角色"""
        if role in self.roles:
            self.user_roles[user_id] = role
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """检查权限"""
        if user_id not in self.user_roles:
            return False
        
        role = self.user_roles[user_id]
        role_permissions = self.roles.get(role, {}).get("permissions", [])
        
        # 管理员有所有权限
        if "*" in role_permissions:
            return True
        
        return permission in role_permissions
```

---

**实施建议**：技术规范要保持简洁实用，避免过度设计。重点关注代码质量、性能监控和安全合规，确保系统的稳定性和可维护性。所有Agent都应该有完善的错误处理和日志记录机制。
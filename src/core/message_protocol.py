"""
Message Protocol for Agent Communication

Defines the standard message format and communication protocols
between agents in the Digital Employees system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid
import json


class MessageType(Enum):
    """Types of messages that can be sent between agents"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    STATUS_UPDATE = "status_update"
    ERROR_NOTIFICATION = "error_notification"
    HEARTBEAT = "heartbeat"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Message:
    """
    Standard message format for agent communication
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: MessageType = MessageType.TASK_REQUEST
    priority: MessagePriority = MessagePriority.MEDIUM
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    requires_response: bool = False
    correlation_id: Optional[str] = None  # For linking request/response pairs
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        data = {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "requires_response": self.requires_response,
            "correlation_id": self.correlation_id
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls(
            id=data["id"],
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            message_type=MessageType(data["message_type"]),
            priority=MessagePriority(data["priority"]),
            content=data["content"],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            requires_response=data["requires_response"],
            correlation_id=data["correlation_id"]
        )
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def create_response(self, sender_id: str, content: Dict[str, Any]) -> 'Message':
        """Create a response message to this message"""
        return Message(
            sender_id=sender_id,
            receiver_id=self.sender_id,
            message_type=MessageType.TASK_RESPONSE if self.message_type == MessageType.TASK_REQUEST
                         else MessageType.COLLABORATION_RESPONSE,
            priority=self.priority,
            content=content,
            correlation_id=self.id,
            requires_response=False
        )


@dataclass
class TaskRequestMessage:
    """Specialized message for task requests"""
    task_description: str
    task_data: Dict[str, Any]
    required_capabilities: List[str]
    deadline: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None
    
    def to_message(self, sender_id: str, receiver_id: str = "") -> Message:
        """Convert to standard Message format"""
        return Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_description": self.task_description,
                "task_data": self.task_data,
                "required_capabilities": self.required_capabilities,
                "deadline": self.deadline.isoformat() if self.deadline else None,
                "context": self.context or {}
            },
            requires_response=True
        )


@dataclass 
class TaskResponseMessage:
    """Specialized message for task responses"""
    success: bool
    result_data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    
    def to_message(self, sender_id: str, receiver_id: str, correlation_id: str) -> Message:
        """Convert to standard Message format"""
        return Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.TASK_RESPONSE,
            content={
                "success": self.success,
                "result_data": self.result_data,
                "error_message": self.error_message,
                "execution_time": self.execution_time
            },
            correlation_id=correlation_id,
            requires_response=False
        )


class MessageValidator:
    """Validates message format and content"""
    
    @staticmethod
    def validate_message(message: Message) -> bool:
        """
        Validate message format and required fields
        
        Args:
            message: Message to validate
            
        Returns:
            bool: True if message is valid
        """
        if not message.id or not message.sender_id:
            return False
        
        if message.is_expired():
            return False
            
        # Validate message type specific requirements
        if message.message_type in [MessageType.TASK_REQUEST, MessageType.COLLABORATION_REQUEST]:
            if not message.requires_response:
                return False
                
        return True
    
    @staticmethod
    def validate_task_request(message: Message) -> bool:
        """Validate task request message content"""
        if message.message_type != MessageType.TASK_REQUEST:
            return False
            
        required_fields = ["task_description", "task_data", "required_capabilities"]
        return all(field in message.content for field in required_fields)
    
    @staticmethod
    def validate_task_response(message: Message) -> bool:
        """Validate task response message content"""
        if message.message_type != MessageType.TASK_RESPONSE:
            return False
            
        required_fields = ["success", "result_data"]
        return all(field in message.content for field in required_fields)


class MessageRouter:
    """Routes messages between agents"""
    
    def __init__(self):
        self.message_handlers: Dict[str, callable] = {}
        self.message_queue: List[Message] = []
        
    def register_handler(self, agent_id: str, handler: callable):
        """Register message handler for an agent"""
        self.message_handlers[agent_id] = handler
        
    def unregister_handler(self, agent_id: str):
        """Unregister message handler for an agent"""
        self.message_handlers.pop(agent_id, None)
    
    async def send_message(self, message: Message) -> bool:
        """
        Send message to target agent
        
        Args:
            message: Message to send
            
        Returns:
            bool: True if message was sent successfully
        """
        if not MessageValidator.validate_message(message):
            return False
            
        if message.receiver_id in self.message_handlers:
            handler = self.message_handlers[message.receiver_id]
            try:
                await handler(message)
                return True
            except Exception as e:
                # Log error and optionally send error notification
                print(f"Error delivering message {message.id}: {e}")
                return False
        else:
            # Queue message for later delivery
            self.message_queue.append(message)
            return True
    
    async def broadcast_message(self, message: Message, exclude_sender: bool = True) -> int:
        """
        Broadcast message to all registered agents
        
        Args:
            message: Message to broadcast
            exclude_sender: Whether to exclude sender from broadcast
            
        Returns:
            int: Number of agents message was sent to
        """
        sent_count = 0
        for agent_id, handler in self.message_handlers.items():
            if exclude_sender and agent_id == message.sender_id:
                continue
                
            try:
                message.receiver_id = agent_id
                await handler(message)
                sent_count += 1
            except Exception as e:
                print(f"Error broadcasting to {agent_id}: {e}")
                
        return sent_count
    
    def get_queued_messages(self, agent_id: str) -> List[Message]:
        """Get queued messages for an agent"""
        messages = [msg for msg in self.message_queue if msg.receiver_id == agent_id]
        # Remove returned messages from queue
        self.message_queue = [msg for msg in self.message_queue if msg.receiver_id != agent_id]
        return messages
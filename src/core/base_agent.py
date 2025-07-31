"""
Base Agent Class - Foundation for all Digital Employees

This is the abstract base class that defines the core interface and behavior
for all agents in the Digital Employees system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import logging
import asyncio
from datetime import datetime


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """Represents a task to be executed by an agent"""
    id: str
    description: str
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = None
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TaskResult:
    """Result of task execution"""
    task_id: str
    success: bool
    output_data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """
    Abstract base class for all Digital Employees agents.
    
    Each agent must implement the core execute method and can override
    lifecycle methods for custom behavior.
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.current_task: Optional[Task] = None
        self.task_history: List[TaskResult] = []
        
    @abstractmethod
    async def execute(self, task: Task) -> TaskResult:
        """
        Execute a task and return the result.
        
        Args:
            task: Task to be executed
            
        Returns:
            TaskResult: Result of the task execution
        """
        pass
    
    @abstractmethod
    def can_handle(self, task: Task) -> bool:
        """
        Check if this agent can handle the given task.
        
        Args:
            task: Task to check
            
        Returns:
            bool: True if agent can handle the task
        """
        pass
    
    async def initialize(self) -> None:
        """Initialize the agent. Override for custom initialization."""
        self.logger.info(f"Initializing agent {self.agent_id}")
        self.status = AgentStatus.IDLE
    
    async def shutdown(self) -> None:
        """Shutdown the agent. Override for custom cleanup."""
        self.logger.info(f"Shutting down agent {self.agent_id}")
        self.status = AgentStatus.OFFLINE
    
    async def health_check(self) -> bool:
        """
        Perform health check on the agent.
        
        Returns:
            bool: True if agent is healthy
        """
        return self.status != AgentStatus.ERROR
    
    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return self.capabilities.copy()
    
    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status
    
    def get_task_history(self) -> List[TaskResult]:
        """Get history of completed tasks."""
        return self.task_history.copy()
    
    async def _execute_with_lifecycle(self, task: Task) -> TaskResult:
        """
        Execute task with full lifecycle management.
        Internal method that handles status updates and error handling.
        """
        start_time = datetime.now()
        self.current_task = task
        self.status = AgentStatus.BUSY
        
        try:
            self.logger.info(f"Starting task {task.id}: {task.description}")
            result = await self.execute(task)
            result.execution_time = (datetime.now() - start_time).total_seconds()
            
            self.task_history.append(result)
            self.logger.info(f"Completed task {task.id} successfully")
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {str(e)}")
            result = TaskResult(
                task_id=task.id,
                success=False,
                output_data={},
                error_message=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            self.status = AgentStatus.ERROR
            self.task_history.append(result)
            
        finally:
            self.current_task = None
            if self.status != AgentStatus.ERROR:
                self.status = AgentStatus.IDLE
                
        return result
    
    def __str__(self) -> str:
        return f"Agent({self.agent_id}, {self.agent_type}, {self.status.value})"
    
    def __repr__(self) -> str:
        return (f"BaseAgent(id='{self.agent_id}', "
                f"type='{self.agent_type}', "
                f"status='{self.status.value}', "
                f"capabilities={self.capabilities})")
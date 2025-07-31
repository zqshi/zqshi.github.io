"""
Agent Registry System

Manages registration, discovery, and lifecycle of agents in the
Digital Employees system.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from .base_agent import BaseAgent, AgentStatus, Task, TaskResult
from .message_protocol import Message, MessageType, MessageRouter


@dataclass
class AgentInfo:
    """Information about a registered agent"""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    status: AgentStatus
    registered_at: datetime
    last_heartbeat: datetime
    max_concurrent_tasks: int = 1
    current_task_count: int = 0
    total_tasks_completed: int = 0
    average_execution_time: float = 0.0
    error_count: int = 0
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return (self.status == AgentStatus.IDLE and 
                self.current_task_count < self.max_concurrent_tasks)
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy based on heartbeat"""
        heartbeat_timeout = timedelta(minutes=5)
        return datetime.now() - self.last_heartbeat < heartbeat_timeout
    
    def update_performance_metrics(self, execution_time: float, success: bool):
        """Update agent performance metrics"""
        if success:
            self.total_tasks_completed += 1
            # Update rolling average
            if self.average_execution_time == 0:
                self.average_execution_time = execution_time
            else:
                self.average_execution_time = (
                    (self.average_execution_time * (self.total_tasks_completed - 1) + execution_time) /
                    self.total_tasks_completed
                )
        else:
            self.error_count += 1


class AgentRegistry:
    """
    Central registry for managing all agents in the system
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_info: Dict[str, AgentInfo] = {}
        self.capabilities_index: Dict[str, Set[str]] = {}  # capability -> agent_ids
        self.type_index: Dict[str, Set[str]] = {}  # agent_type -> agent_ids
        self.message_router = MessageRouter()
        self.logger = logging.getLogger("agent_registry")
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._running = False
        
    async def start(self):
        """Start the agent registry"""
        self._running = True
        self.logger.info("Agent Registry started")
        # Start background tasks
        asyncio.create_task(self._health_check_loop())
        
    async def stop(self):
        """Stop the agent registry"""
        self._running = False
        self.logger.info("Agent Registry stopped")
        self._executor.shutdown(wait=True)
    
    async def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent with the registry
        
        Args:
            agent: Agent instance to register
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Initialize agent if not already done
            await agent.initialize()
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                capabilities=agent.capabilities,
                status=agent.status,
                registered_at=datetime.now(),
                last_heartbeat=datetime.now()
            )
            
            # Store agent and info
            self.agents[agent.agent_id] = agent
            self.agent_info[agent.agent_id] = agent_info
            
            # Update indices
            self._update_indices(agent_info)
            
            # Register message handler
            self.message_router.register_handler(
                agent.agent_id, 
                self._create_message_handler(agent)
            )
            
            self.logger.info(f"Registered agent {agent.agent_id} of type {agent.agent_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the registry
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            bool: True if unregistration successful
        """
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            agent_info = self.agent_info[agent_id]
            
            # Shutdown agent
            await agent.shutdown()
            
            # Remove from indices
            self._remove_from_indices(agent_info)
            
            # Remove from storage
            del self.agents[agent_id]
            del self.agent_info[agent_id]
            
            # Unregister message handler
            self.message_router.unregister_handler(agent_id)
            
            self.logger.info(f"Unregistered agent {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """
        Find all agents that have a specific capability
        
        Args:
            capability: Capability to search for
            
        Returns:
            List[str]: List of agent IDs
        """
        return list(self.capabilities_index.get(capability, set()))
    
    def find_agents_by_type(self, agent_type: str) -> List[str]:
        """
        Find all agents of a specific type
        
        Args:
            agent_type: Agent type to search for
            
        Returns:
            List[str]: List of agent IDs
        """
        return list(self.type_index.get(agent_type, set()))
    
    def find_best_agent_for_task(self, task: Task) -> Optional[str]:
        """
        Find the best available agent for a task
        
        Args:
            task: Task to find agent for
            
        Returns:
            Optional[str]: Agent ID of best agent, or None if none available
        """
        # Get all agents that can potentially handle the task
        candidate_agents = []
        
        for agent_id, agent_info in self.agent_info.items():
            if not agent_info.is_available() or not agent_info.is_healthy():
                continue
            
            agent = self.agents[agent_id]
            if agent.can_handle(task):
                candidate_agents.append((agent_id, agent_info))
        
        if not candidate_agents:
            return None
        
        # Score agents based on performance metrics
        best_agent = None
        best_score = float('-inf')
        
        for agent_id, agent_info in candidate_agents:
            # Calculate score based on:
            # - Low average execution time (faster is better)
            # - Low error rate
            # - Low current load
            error_rate = agent_info.error_count / max(agent_info.total_tasks_completed, 1)
            load_factor = agent_info.current_task_count / agent_info.max_concurrent_tasks
            
            score = (
                1.0 / (agent_info.average_execution_time + 1.0) +  # Favor faster agents
                1.0 / (error_rate + 0.01) +  # Favor reliable agents
                1.0 / (load_factor + 0.1)  # Favor less loaded agents
            )
            
            if score > best_score:
                best_score = score
                best_agent = agent_id
        
        return best_agent
    
    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a specific agent"""
        return self.agent_info.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, AgentInfo]:
        """Get information about all registered agents"""
        return self.agent_info.copy()
    
    def get_system_stats(self) -> Dict[str, any]:
        """Get system-wide statistics"""
        total_agents = len(self.agents)
        active_agents = sum(1 for info in self.agent_info.values() 
                           if info.status not in [AgentStatus.OFFLINE, AgentStatus.ERROR])
        available_agents = sum(1 for info in self.agent_info.values() if info.is_available())
        
        total_tasks = sum(info.total_tasks_completed for info in self.agent_info.values())
        total_errors = sum(info.error_count for info in self.agent_info.values())
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "available_agents": available_agents,
            "total_tasks_completed": total_tasks,
            "total_errors": total_errors,
            "error_rate": total_errors / max(total_tasks, 1),
            "unique_capabilities": len(self.capabilities_index),
            "agent_types": len(self.type_index)
        }
    
    async def execute_task(self, task: Task, preferred_agent_id: Optional[str] = None) -> TaskResult:
        """
        Execute a task using the registry
        
        Args:
            task: Task to execute
            preferred_agent_id: Preferred agent ID (optional)
            
        Returns:
            TaskResult: Result of task execution
        """
        # Find agent to execute task
        agent_id = preferred_agent_id
        if agent_id and (agent_id not in self.agents or 
                        not self.agent_info[agent_id].is_available()):
            agent_id = None
        
        if not agent_id:
            agent_id = self.find_best_agent_for_task(task)
        
        if not agent_id:
            return TaskResult(
                task_id=task.id,
                success=False,
                output_data={},
                error_message="No available agent found for task"
            )
        
        # Execute task
        agent = self.agents[agent_id]
        agent_info = self.agent_info[agent_id]
        
        # Update task count
        agent_info.current_task_count += 1
        
        try:
            result = await agent._execute_with_lifecycle(task)
            agent_info.update_performance_metrics(result.execution_time or 0, result.success)
            return result
        finally:
            agent_info.current_task_count -= 1
    
    def _update_indices(self, agent_info: AgentInfo):
        """Update capability and type indices"""
        agent_id = agent_info.agent_id
        
        # Update capabilities index
        for capability in agent_info.capabilities:
            if capability not in self.capabilities_index:
                self.capabilities_index[capability] = set()
            self.capabilities_index[capability].add(agent_id)
        
        # Update type index
        if agent_info.agent_type not in self.type_index:
            self.type_index[agent_info.agent_type] = set()
        self.type_index[agent_info.agent_type].add(agent_id)
    
    def _remove_from_indices(self, agent_info: AgentInfo):
        """Remove agent from capability and type indices"""
        agent_id = agent_info.agent_id
        
        # Remove from capabilities index
        for capability in agent_info.capabilities:
            if capability in self.capabilities_index:
                self.capabilities_index[capability].discard(agent_id)
                if not self.capabilities_index[capability]:
                    del self.capabilities_index[capability]
        
        # Remove from type index
        if agent_info.agent_type in self.type_index:
            self.type_index[agent_info.agent_type].discard(agent_id)
            if not self.type_index[agent_info.agent_type]:
                del self.type_index[agent_info.agent_type]
    
    def _create_message_handler(self, agent: BaseAgent):
        """Create message handler for an agent"""
        async def handler(message: Message):
            # Handle different message types
            if message.message_type == MessageType.HEARTBEAT:
                # Update heartbeat timestamp
                if agent.agent_id in self.agent_info:
                    self.agent_info[agent.agent_id].last_heartbeat = datetime.now()
            
            # Additional message handling can be added here
            
        return handler
    
    async def _health_check_loop(self):
        """Background loop for health checking agents"""
        while self._running:
            try:
                unhealthy_agents = []
                for agent_id, agent_info in self.agent_info.items():
                    if not agent_info.is_healthy():
                        unhealthy_agents.append(agent_id)
                        self.logger.warning(f"Agent {agent_id} appears unhealthy")
                
                # Handle unhealthy agents (could implement auto-restart logic)
                for agent_id in unhealthy_agents:
                    self.agent_info[agent_id].status = AgentStatus.ERROR
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
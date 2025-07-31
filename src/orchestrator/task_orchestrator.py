"""
Task Orchestrator

Manages task distribution, workflow orchestration, and coordination
between multiple agents in the Digital Employees system.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import uuid

from ..core.base_agent import BaseAgent, Task, TaskResult, TaskPriority
from ..core.agent_registry import AgentRegistry
from ..core.message_protocol import Message, MessageType, TaskRequestMessage, TaskResponseMessage


class WorkflowStatus(Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single step in a workflow"""
    id: str
    name: str
    task_description: str
    required_capabilities: List[str]
    input_data: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)  # List of step IDs this depends on
    timeout_minutes: int = 30
    retry_count: int = 0
    max_retries: int = 2
    
    # Execution state
    status: WorkflowStatus = WorkflowStatus.PENDING
    assigned_agent_id: Optional[str] = None
    result: Optional[TaskResult] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class Workflow:
    """Represents a complete workflow with multiple steps"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to execute (dependencies satisfied)"""
        ready_steps = []
        for step in self.steps:
            if step.status != WorkflowStatus.PENDING:
                continue
                
            # Check if all dependencies are completed
            dependencies_met = all(
                any(s.id == dep_id and s.status == WorkflowStatus.COMPLETED 
                    for s in self.steps)
                for dep_id in step.depends_on
            )
            
            if dependencies_met:
                ready_steps.append(step)
                
        return ready_steps
    
    def is_completed(self) -> bool:
        """Check if workflow is completed"""
        return all(step.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED] 
                  for step in self.steps)
    
    def has_failed_steps(self) -> bool:
        """Check if workflow has any failed steps"""
        return any(step.status == WorkflowStatus.FAILED for step in self.steps)


class TaskOrchestrator:
    """
    Main orchestrator for managing tasks and workflows
    """
    
    def __init__(self, agent_registry: AgentRegistry):
        self.agent_registry = agent_registry
        self.workflows: Dict[str, Workflow] = {}
        self.active_tasks: Dict[str, Task] = {}
        self.logger = logging.getLogger("task_orchestrator")
        self._running = False
        
    async def start(self):
        """Start the task orchestrator"""
        self._running = True
        self.logger.info("Task Orchestrator started")
        # Start background workflow execution loop
        asyncio.create_task(self._workflow_execution_loop())
        
    async def stop(self):
        """Stop the task orchestrator"""
        self._running = False
        self.logger.info("Task Orchestrator stopped")
    
    async def execute_single_task(self, 
                                task_description: str,
                                task_data: Dict[str, Any],
                                required_capabilities: List[str] = None,
                                priority: TaskPriority = TaskPriority.MEDIUM,
                                preferred_agent_id: Optional[str] = None) -> TaskResult:
        """
        Execute a single task immediately
        
        Args:
            task_description: Description of the task
            task_data: Input data for the task
            required_capabilities: Required capabilities (optional)
            priority: Task priority
            preferred_agent_id: Preferred agent to execute task
            
        Returns:
            TaskResult: Result of task execution
        """
        task = Task(
            id=str(uuid.uuid4()),
            description=task_description,
            input_data=task_data,
            priority=priority,
            context={"required_capabilities": required_capabilities or []}
        )
        
        self.logger.info(f"Executing single task: {task_description}")
        return await self.agent_registry.execute_task(task, preferred_agent_id)
    
    async def create_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """
        Create a new workflow from definition
        
        Args:
            workflow_definition: Dictionary containing workflow definition
            
        Returns:
            str: Workflow ID
        """
        workflow_id = str(uuid.uuid4())
        
        # Parse workflow steps
        steps = []
        for step_def in workflow_definition.get("steps", []):
            step = WorkflowStep(
                id=step_def["id"],
                name=step_def["name"],
                task_description=step_def["task_description"],
                required_capabilities=step_def.get("required_capabilities", []),
                input_data=step_def.get("input_data", {}),
                depends_on=step_def.get("depends_on", []),
                timeout_minutes=step_def.get("timeout_minutes", 30),
                max_retries=step_def.get("max_retries", 2)
            )
            steps.append(step)
        
        workflow = Workflow(
            id=workflow_id,
            name=workflow_definition["name"],
            description=workflow_definition.get("description", ""),
            steps=steps
        )
        
        self.workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow {workflow_id}: {workflow.name}")
        return workflow_id
    
    async def start_workflow(self, workflow_id: str) -> bool:
        """
        Start execution of a workflow
        
        Args:
            workflow_id: ID of workflow to start
            
        Returns:
            bool: True if workflow started successfully
        """
        if workflow_id not in self.workflows:
            self.logger.error(f"Workflow {workflow_id} not found")
            return False
        
        workflow = self.workflows[workflow_id]
        if workflow.status != WorkflowStatus.PENDING:
            self.logger.error(f"Workflow {workflow_id} is not in pending state")
            return False
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        self.logger.info(f"Started workflow {workflow_id}: {workflow.name}")
        return True
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow
        
        Args:
            workflow_id: ID of workflow to cancel
            
        Returns:
            bool: True if workflow cancelled successfully
        """
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED
        
        # Cancel any running steps
        for step in workflow.steps:
            if step.status == WorkflowStatus.RUNNING:
                step.status = WorkflowStatus.CANCELLED
        
        self.logger.info(f"Cancelled workflow {workflow_id}")
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow"""
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "status": step.status.value,
                    "assigned_agent": step.assigned_agent_id,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error_message": step.error_message
                }
                for step in workflow.steps
            ],
            "results": workflow.results
        }
    
    def get_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all workflows"""
        return {wf_id: self.get_workflow_status(wf_id) 
                for wf_id in self.workflows.keys()}
    
    async def _workflow_execution_loop(self):
        """Background loop for executing workflows"""
        while self._running:
            try:
                # Process all running workflows
                for workflow_id, workflow in self.workflows.items():
                    if workflow.status == WorkflowStatus.RUNNING:
                        await self._process_workflow(workflow)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in workflow execution loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_workflow(self, workflow: Workflow):
        """Process a single workflow"""
        try:
            # Get steps ready for execution
            ready_steps = workflow.get_ready_steps()
            
            # Execute ready steps
            for step in ready_steps:
                await self._execute_workflow_step(workflow, step)
            
            # Check if workflow is completed
            if workflow.is_completed():
                workflow.status = WorkflowStatus.COMPLETED if not workflow.has_failed_steps() else WorkflowStatus.FAILED
                workflow.completed_at = datetime.now()
                
                # Collect results
                workflow.results = {
                    step.id: step.result.output_data if step.result else {}
                    for step in workflow.steps
                    if step.status == WorkflowStatus.COMPLETED
                }
                
                self.logger.info(f"Workflow {workflow.id} completed with status: {workflow.status.value}")
        
        except Exception as e:
            self.logger.error(f"Error processing workflow {workflow.id}: {e}")
            workflow.status = WorkflowStatus.FAILED
    
    async def _execute_workflow_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute a single workflow step"""
        try:
            # Prepare input data from previous steps
            input_data = step.input_data.copy()
            
            # Add results from dependent steps
            for dep_id in step.depends_on:
                dep_step = next((s for s in workflow.steps if s.id == dep_id), None)
                if dep_step and dep_step.result:
                    input_data[f"step_{dep_id}_result"] = dep_step.result.output_data
            
            # Create task
            task = Task(
                id=f"{workflow.id}_{step.id}_{uuid.uuid4()}",
                description=step.task_description,
                input_data=input_data,
                context={"required_capabilities": step.required_capabilities}
            )
            
            # Find best agent
            agent_id = self.agent_registry.find_best_agent_for_task(task)
            if not agent_id:
                step.status = WorkflowStatus.FAILED
                step.error_message = "No suitable agent found"
                return
            
            # Execute step
            step.status = WorkflowStatus.RUNNING
            step.assigned_agent_id = agent_id
            step.started_at = datetime.now()
            
            self.logger.info(f"Executing workflow step {step.id} with agent {agent_id}")
            
            result = await self.agent_registry.execute_task(task, agent_id)
            
            step.result = result
            step.completed_at = datetime.now()
            
            if result.success:
                step.status = WorkflowStatus.COMPLETED
                self.logger.info(f"Workflow step {step.id} completed successfully")
            else:
                # Handle retry logic
                if step.retry_count < step.max_retries:
                    step.retry_count += 1
                    step.status = WorkflowStatus.PENDING
                    step.assigned_agent_id = None
                    step.started_at = None
                    self.logger.warning(f"Workflow step {step.id} failed, retrying ({step.retry_count}/{step.max_retries})")
                else:
                    step.status = WorkflowStatus.FAILED
                    step.error_message = result.error_message
                    self.logger.error(f"Workflow step {step.id} failed permanently: {result.error_message}")
        
        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error_message = str(e)
            step.completed_at = datetime.now()
            self.logger.error(f"Error executing workflow step {step.id}: {e}")


# Utility functions for creating common workflow patterns
def create_linear_workflow(name: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a linear workflow where each task depends on the previous one"""
    steps = []
    for i, task in enumerate(tasks):
        step_id = f"step_{i+1}"
        step = {
            "id": step_id,
            "name": task.get("name", f"Step {i+1}"),
            "task_description": task["description"],
            "required_capabilities": task.get("capabilities", []),
            "input_data": task.get("input_data", {}),
            "depends_on": [f"step_{i}"] if i > 0 else []
        }
        steps.append(step)
    
    return {
        "name": name,
        "description": f"Linear workflow with {len(tasks)} steps",
        "steps": steps
    }


def create_parallel_workflow(name: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a parallel workflow where all tasks can run simultaneously"""
    steps = []
    for i, task in enumerate(tasks):
        step = {
            "id": f"step_{i+1}",
            "name": task.get("name", f"Step {i+1}"),
            "task_description": task["description"],
            "required_capabilities": task.get("capabilities", []),
            "input_data": task.get("input_data", {}),
            "depends_on": []  # No dependencies for parallel execution
        }
        steps.append(step)
    
    return {
        "name": name,
        "description": f"Parallel workflow with {len(tasks)} steps",
        "steps": steps
    }
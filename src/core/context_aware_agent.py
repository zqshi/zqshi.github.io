"""
Context Aware Agent Base Class

This module extends the BaseAgent with context-aware capabilities, enabling
intelligent situational decision making through the Context State Manager.
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime
import logging

from .base_agent import BaseAgent, Task, TaskResult, TaskPriority
from .context_state_manager import get_context_manager, ContextStateManager
from .project_context import ProjectContext, PriorityMatrix


@dataclass
class DecisionStrategy:
    """Represents a decision strategy with its configuration and rationale"""
    strategy_type: str                    # "fast_delivery", "high_quality", "balanced"
    approach: str                        # Specific approach description
    parameters: Dict[str, Any]           # Strategy-specific parameters
    rationale: str                       # Explanation of why this strategy was chosen
    quality_target: float = 0.7         # Target quality level 0.0-1.0
    speed_factor: float = 1.0           # Speed multiplier (1.0 = normal)
    resource_intensity: float = 0.5     # Resource usage 0.0-1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_type": self.strategy_type,
            "approach": self.approach,
            "parameters": self.parameters,
            "rationale": self.rationale,
            "quality_target": self.quality_target,
            "speed_factor": self.speed_factor,
            "resource_intensity": self.resource_intensity
        }


@dataclass
class ContextualDecision:
    """Represents a decision made by an agent with full context information"""
    decision_id: str
    agent_id: str
    task_id: str
    strategy: DecisionStrategy
    context_snapshot: Dict[str, Any]     # Snapshot of context at decision time
    estimated_time_days: float
    resource_demand: float               # 0.0-1.0
    dependencies: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "strategy": self.strategy.to_dict(),
            "context_snapshot": self.context_snapshot,
            "estimated_time_days": self.estimated_time_days,
            "resource_demand": self.resource_demand,
            "dependencies": self.dependencies,
            "risks": self.risks,
            "created_at": self.created_at.isoformat()
        }


class ContextAwareAgent(BaseAgent):
    """
    Context-aware agent base class that enables intelligent situational decision making.
    
    This class extends BaseAgent with context awareness capabilities:
    - Queries project context before making decisions
    - Selects appropriate strategies based on context
    - Records decisions with full context information
    - Provides explainable decision rationale
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str], 
                 project_id: Optional[str] = None):
        super().__init__(agent_id, agent_type, capabilities)
        
        self.project_id = project_id
        self.context_manager: ContextStateManager = get_context_manager()
        self.context_logger = logging.getLogger(f"context.{agent_id}")
        
        # Decision tracking
        self.decisions_made: List[ContextualDecision] = []
        self.current_strategy: Optional[DecisionStrategy] = None
        
        # Strategy definitions (to be overridden by subclasses)
        self.available_strategies = self._define_strategies()
        
        self.context_logger.info(f"Context-aware agent {agent_id} initialized")
    
    # ========== Core Context-Aware Execution ==========
    
    async def execute(self, task: Task) -> TaskResult:
        """
        Execute task with context-aware decision making.
        This method orchestrates the full context-aware execution flow.
        """
        try:
            # 1. Get current project context
            context = await self.get_project_context(task)
            if not context:
                return await self._execute_without_context(task)
            
            # 2. Make contextual decision
            decision = await self.make_contextual_decision(task, context)
            self.decisions_made.append(decision)
            self.current_strategy = decision.strategy
            
            # 3. Execute with selected strategy
            result = await self.execute_with_strategy(task, decision.strategy, context)
            
            # 4. Record execution results
            result.metadata = result.metadata or {}
            result.metadata.update({
                "context_aware": True,
                "strategy_used": decision.strategy.to_dict(),
                "context_snapshot": decision.context_snapshot,
                "decision_id": decision.decision_id
            })
            
            self.context_logger.info(
                f"Task {task.id} completed with strategy {decision.strategy.strategy_type}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Context-aware execution failed: {str(e)}")
            # Fallback to base implementation
            return await super().execute(task)
    
    async def get_project_context(self, task: Task) -> Optional[ProjectContext]:
        """Get project context, with fallback options"""
        # Try task context first
        if task.context and "project_id" in task.context:
            project_id = task.context["project_id"]
        # Try agent's default project
        elif self.project_id:
            project_id = self.project_id
        else:
            self.context_logger.warning("No project context available")
            return None
        
        return await self.context_manager.get_project_context(project_id)
    
    async def make_contextual_decision(self, task: Task, context: ProjectContext) -> ContextualDecision:
        """
        Make a contextual decision based on current project state.
        This is the core of situational intelligence.
        """
        # 1. Get contextual recommendations from CSM
        recommendations = await self.context_manager.get_contextual_recommendations(
            context.project_id, self.agent_id
        )
        
        # 2. Select strategy based on context
        strategy = self.select_strategy(context, task, recommendations)
        
        # 3. Estimate resource requirements
        time_estimate, resource_demand = self.estimate_resources(strategy, task, context)
        
        # 4. Identify risks and dependencies
        risks = self.identify_risks(strategy, task, context)
        dependencies = self.identify_dependencies(strategy, task, context)
        
        # 5. Create decision record
        decision = ContextualDecision(
            decision_id=f"{self.agent_id}_{task.id}_{datetime.now().timestamp()}",
            agent_id=self.agent_id,
            task_id=task.id,
            strategy=strategy,
            context_snapshot=context.to_dict(),
            estimated_time_days=time_estimate,
            resource_demand=resource_demand,
            dependencies=dependencies,
            risks=risks
        )
        
        self.context_logger.info(
            f"Decision made: {strategy.strategy_type} for task {task.id}, "
            f"estimated {time_estimate:.1f} days, {resource_demand:.1%} resources"
        )
        
        return decision
    
    @abstractmethod
    def select_strategy(self, context: ProjectContext, task: Task, 
                       recommendations: Dict[str, Any]) -> DecisionStrategy:
        """
        Select the optimal strategy based on context.
        Must be implemented by each specific agent.
        """
        pass
    
    @abstractmethod
    async def execute_with_strategy(self, task: Task, strategy: DecisionStrategy, 
                                  context: ProjectContext) -> TaskResult:
        """
        Execute the task using the selected strategy.
        Must be implemented by each specific agent.
        """
        pass
    
    # ========== Strategy Management ==========
    
    def _define_strategies(self) -> Dict[str, DecisionStrategy]:
        """
        Define available strategies for this agent.
        Override in subclasses to provide agent-specific strategies.
        """
        return {
            "balanced": DecisionStrategy(
                strategy_type="balanced",
                approach="Standard balanced approach",
                parameters={},
                rationale="Default strategy balancing speed, quality, and cost",
                quality_target=0.7,
                speed_factor=1.0,
                resource_intensity=0.5
            ),
            "fast_delivery": DecisionStrategy(
                strategy_type="fast_delivery",
                approach="Speed-optimized approach",
                parameters={"optimize_for": "speed"},
                rationale="Prioritize delivery speed over perfection",
                quality_target=0.6,
                speed_factor=1.5,
                resource_intensity=0.7
            ),
            "high_quality": DecisionStrategy(
                strategy_type="high_quality",
                approach="Quality-optimized approach",
                parameters={"optimize_for": "quality"},
                rationale="Prioritize quality and long-term maintainability",
                quality_target=0.9,
                speed_factor=0.8,
                resource_intensity=0.6
            )
        }
    
    def get_strategy_by_context(self, context: ProjectContext) -> str:
        """Get recommended strategy name based on context priorities"""
        if context.is_speed_prioritized():
            return "fast_delivery"
        elif context.is_quality_prioritized():
            return "high_quality"
        else:
            return "balanced"
    
    # ========== Resource Estimation ==========
    
    def estimate_resources(self, strategy: DecisionStrategy, task: Task, 
                          context: ProjectContext) -> tuple[float, float]:
        """
        Estimate time and resource requirements for the task with given strategy.
        Returns (time_in_days, resource_demand_ratio)
        """
        # Base estimation (override in subclasses for more accurate estimates)
        base_time = self._estimate_base_time(task)
        base_resources = 0.5
        
        # Apply strategy modifiers
        time_estimate = base_time / strategy.speed_factor
        resource_demand = base_resources * strategy.resource_intensity
        
        # Apply context modifiers
        if context.time_pressure_level() == "critical":
            time_estimate *= 0.8  # Work faster under pressure
            resource_demand *= 1.2  # But need more resources
        
        return time_estimate, min(resource_demand, 1.0)
    
    def _estimate_base_time(self, task: Task) -> float:
        """Estimate base time for task (in days). Override in subclasses."""
        # Simple estimation based on task priority
        if task.priority == TaskPriority.URGENT:
            return 0.5
        elif task.priority == TaskPriority.HIGH:
            return 1.0
        elif task.priority == TaskPriority.MEDIUM:
            return 2.0
        else:
            return 3.0
    
    # ========== Risk and Dependency Analysis ==========
    
    def identify_risks(self, strategy: DecisionStrategy, task: Task, 
                      context: ProjectContext) -> List[str]:
        """Identify potential risks for the chosen strategy"""
        risks = []
        
        # Strategy-specific risks
        if strategy.strategy_type == "fast_delivery":
            risks.extend([
                "Reduced test coverage may introduce bugs",
                "Technical debt accumulation",
                "Potential performance issues"
            ])
        elif strategy.strategy_type == "high_quality":
            risks.extend([
                "Extended timeline may miss market window",
                "Over-engineering risk",
                "Higher resource consumption"
            ])
        
        # Context-specific risks
        if context.tech_debt.is_critical:
            risks.append("High technical debt may slow development")
        
        if context.time_pressure_level() == "critical":
            risks.append("Extreme time pressure may compromise quality")
        
        return risks
    
    def identify_dependencies(self, strategy: DecisionStrategy, task: Task, 
                            context: ProjectContext) -> List[str]:
        """Identify dependencies for the chosen strategy"""
        dependencies = []
        
        # Common dependencies based on strategy
        if strategy.strategy_type == "high_quality":
            dependencies.extend([
                "qa-engineer for comprehensive testing",
                "system-architect for design review"
            ])
        
        # Context-specific dependencies
        if "security" in context.constraints.compliance_requirements:
            dependencies.append("security-engineer for compliance review")
        
        if context.constraints.technical_expertise:
            for expertise in context.constraints.technical_expertise:
                dependencies.append(f"Expert in {expertise}")
        
        return dependencies
    
    # ========== Fallback Execution ==========
    
    async def _execute_without_context(self, task: Task) -> TaskResult:
        """Fallback execution when no context is available"""
        self.context_logger.warning(f"Executing task {task.id} without context awareness")
        
        # Use balanced strategy as default
        strategy = self.available_strategies["balanced"]
        self.current_strategy = strategy
        
        # Create minimal context
        minimal_context = None  # Subclasses should handle None context gracefully
        
        return await self.execute_with_strategy(task, strategy, minimal_context)
    
    # ========== Status and Reporting ==========
    
    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get history of decisions made by this agent"""
        return [decision.to_dict() for decision in self.decisions_made]
    
    def get_current_strategy(self) -> Optional[Dict[str, Any]]:
        """Get current strategy being used"""
        return self.current_strategy.to_dict() if self.current_strategy else None
    
    def get_context_awareness_stats(self) -> Dict[str, Any]:
        """Get statistics about context-aware operations"""
        total_decisions = len(self.decisions_made)
        
        if total_decisions == 0:
            return {"total_decisions": 0, "strategy_distribution": {}}
        
        strategy_counts = {}
        for decision in self.decisions_made:
            strategy_type = decision.strategy.strategy_type
            strategy_counts[strategy_type] = strategy_counts.get(strategy_type, 0) + 1
        
        return {
            "total_decisions": total_decisions,
            "strategy_distribution": strategy_counts,
            "avg_resource_demand": sum(d.resource_demand for d in self.decisions_made) / total_decisions,
            "avg_estimated_time": sum(d.estimated_time_days for d in self.decisions_made) / total_decisions
        }
    
    def explain_current_decision(self) -> str:
        """Provide human-readable explanation of current decision"""
        if not self.current_strategy:
            return "No active strategy"
        
        return (
            f"Using {self.current_strategy.strategy_type} strategy: "
            f"{self.current_strategy.rationale}. "
            f"Target quality: {self.current_strategy.quality_target:.1%}, "
            f"Speed factor: {self.current_strategy.speed_factor:.1f}x"
        )
    
    # ========== Agent Registration ==========
    
    async def initialize(self) -> None:
        """Initialize the context-aware agent"""
        await super().initialize()
        
        # Subscribe to context updates
        self.context_manager.subscribe_to_context_updates(self._on_context_update)
        
        self.context_logger.info(f"Context-aware agent {self.agent_id} fully initialized")
    
    async def _on_context_update(self, event: Dict[str, Any]) -> None:
        """Handle context update events"""
        if event.get("project_id") == self.project_id:
            self.context_logger.info(
                f"Context updated for project {self.project_id}: {event.get('event_type')}"
            )
            
            # If currently executing a task, may need to adjust strategy
            if self.current_task and self.current_strategy:
                await self._consider_strategy_adjustment(event)
    
    async def _consider_strategy_adjustment(self, context_event: Dict[str, Any]) -> None:
        """Consider adjusting current strategy based on context changes"""
        # This is a placeholder for dynamic strategy adjustment
        # Implementation depends on specific agent requirements
        self.context_logger.debug(f"Considering strategy adjustment due to context change: {context_event}")
    
    def __repr__(self) -> str:
        return (f"ContextAwareAgent(id='{self.agent_id}', "
                f"type='{self.agent_type}', "
                f"project='{self.project_id}', "
                f"status='{self.status.value}', "
                f"current_strategy='{self.current_strategy.strategy_type if self.current_strategy else None}')")
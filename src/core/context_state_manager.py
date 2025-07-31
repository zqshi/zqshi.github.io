"""
Context State Manager - Core coordination system for intelligent agent collaboration

This module implements the Context State Manager that enables intelligent coordination
between agents through shared project context, replacing traditional hierarchical
coordination with situational awareness.
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Set
from dataclasses import asdict
import logging
from threading import Lock
from weakref import WeakSet

from .project_context import (
    ProjectContext, DecisionMatrix, PriorityMatrix, 
    TechDebtStatus, LifecyclePhase, ConflictType
)


class ContextStateManager:
    """
    Context State Manager - The core coordination system that provides 
    intelligent agent coordination through shared situational awareness.
    
    Key principles:
    - No hierarchical management, only information sharing
    - Context-driven decision making
    - Automatic conflict prevention through information synchronization
    - Event-driven updates with caching optimization
    """
    
    def __init__(self, cache_ttl_seconds: int = 60):
        self.logger = logging.getLogger("context_state_manager")
        
        # Core context storage
        self._contexts: Dict[str, ProjectContext] = {}
        self._decision_matrix = DecisionMatrix()
        
        # Caching system
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cached_contexts: Dict[str, tuple] = {}  # (context, timestamp, hash)
        
        # Event system for context updates
        self._context_subscribers: WeakSet = WeakSet()
        self._update_lock = Lock()
        
        # Metrics and monitoring
        self._query_count = 0
        self._cache_hits = 0
        self._update_count = 0
        
        self.logger.info("Context State Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize the Context State Manager"""
        self.logger.info("Initializing Context State Manager")
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_cache())
        asyncio.create_task(self._periodic_health_check())
    
    # ========== Core Context Management ==========
    
    async def register_project_context(self, context: ProjectContext) -> None:
        """Register a new project context"""
        with self._update_lock:
            self._contexts[context.project_id] = context
            self._invalidate_cache(context.project_id)
            self._update_count += 1
        
        await self._notify_context_update(context.project_id, "registered")
        self.logger.info(f"Registered context for project {context.project_id}")
    
    async def get_project_context(self, project_id: str) -> Optional[ProjectContext]:
        """
        Get project context with caching optimization.
        This is the primary interface for agents to query context.
        """
        self._query_count += 1
        
        # Check cache first
        cached_result = self._get_from_cache(project_id)
        if cached_result:
            self._cache_hits += 1
            return cached_result
        
        # Get from primary storage
        context = self._contexts.get(project_id)
        if context:
            self._add_to_cache(project_id, context)
        
        return context
    
    async def update_project_context(self, project_id: str, 
                                   updates: Dict[str, Any],
                                   updated_by: str) -> bool:
        """
        Update project context with validation and event notification.
        
        Args:
            project_id: Project identifier
            updates: Dictionary of fields to update
            updated_by: Agent or user making the update
            
        Returns:
            bool: True if update was successful
        """
        context = self._contexts.get(project_id)
        if not context:
            self.logger.error(f"Project context not found: {project_id}")
            return False
        
        try:
            with self._update_lock:
                # Apply updates
                if "priority_matrix" in updates:
                    pm = updates["priority_matrix"]
                    context.update_priority_matrix(pm["speed"], pm["quality"], pm["cost"], updated_by)
                
                if "tech_debt_level" in updates:
                    context.update_tech_debt(updates["tech_debt_level"], updated_by)
                
                # Update other fields
                for field, value in updates.items():
                    if field not in ["priority_matrix", "tech_debt_level"] and hasattr(context, field):
                        setattr(context, field, value)
                
                # Update metadata
                context.last_updated = datetime.now()
                context.updated_by = updated_by
                context.version += 1
                
                self._invalidate_cache(project_id)
                self._update_count += 1
            
            await self._notify_context_update(project_id, "updated", updates)
            self.logger.info(f"Updated context for project {project_id} by {updated_by}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update context for {project_id}: {str(e)}")
            return False
    
    # ========== Agent Decision Support ==========
    
    def get_decision_authority(self, decision_type: str) -> Dict[str, Any]:
        """
        Get RACI matrix information for a specific decision type.
        This helps agents understand their role in decision making.
        """
        try:
            responsible = self._decision_matrix.get_responsible_agent(decision_type)
            consulted = self._decision_matrix.get_consulted_agents(decision_type)
            
            return {
                "responsible": responsible,
                "consulted": consulted,
                "decision_type": decision_type
            }
        except ValueError:
            return {"error": f"Unknown decision type: {decision_type}"}
    
    async def get_contextual_recommendations(self, project_id: str, 
                                           agent_id: str) -> Dict[str, Any]:
        """
        Get contextual recommendations for an agent based on current project state.
        This is the core of situational decision making.
        """
        context = await self.get_project_context(project_id)
        if not context:
            return {"error": "Project context not found"}
        
        recommendations = {
            "project_phase": context.lifecycle_phase.value,
            "dominant_priority": context.get_dominant_priority(),
            "time_pressure": context.time_pressure_level(),
            "suggested_strategy": self._get_strategy_recommendation(context, agent_id),
            "quality_constraints": self._get_quality_constraints(context),
            "resource_constraints": self._get_resource_constraints(context),
            "tech_debt_status": context.tech_debt.to_dict()
        }
        
        return recommendations
    
    def _get_strategy_recommendation(self, context: ProjectContext, agent_id: str) -> Dict[str, str]:
        """Generate strategy recommendations based on context"""
        strategy = {"type": "balanced", "rationale": "Default balanced approach"}
        
        # Speed-prioritized strategy
        if context.is_speed_prioritized():
            if agent_id == "qa-engineer":
                strategy = {
                    "type": "essential_testing",
                    "rationale": "Focus on critical path testing, defer comprehensive coverage"
                }
            elif agent_id == "system-architect":
                strategy = {
                    "type": "evolutionary_architecture", 
                    "rationale": "Implement minimal viable architecture, plan for evolution"
                }
            elif "developer" in agent_id or "engineer" in agent_id:
                strategy = {
                    "type": "mvp_focused",
                    "rationale": "Implement core features first, optimize later"
                }
        
        # Quality-prioritized strategy
        elif context.is_quality_prioritized():
            if agent_id == "qa-engineer":
                strategy = {
                    "type": "comprehensive_testing",
                    "rationale": "Full TDD implementation with high coverage requirements"
                }
            elif agent_id == "system-architect":
                strategy = {
                    "type": "robust_architecture",
                    "rationale": "Design for long-term maintainability and scalability"
                }
            elif "developer" in agent_id or "engineer" in agent_id:
                strategy = {
                    "type": "quality_first",
                    "rationale": "Emphasize code quality, comprehensive testing, and documentation"
                }
        
        # Cost-prioritized strategy
        elif context.is_cost_prioritized():
            strategy = {
                "type": "cost_optimized",
                "rationale": "Minimize development time and resource usage while meeting requirements"
            }
        
        return strategy
    
    def _get_quality_constraints(self, context: ProjectContext) -> Dict[str, Any]:
        """Get quality constraints based on context"""
        constraints = {
            "min_test_coverage": 0.6,  # Default minimum
            "code_quality_threshold": 7.0,  # Out of 10
            "performance_requirements": "basic"
        }
        
        if context.is_quality_prioritized():
            constraints.update({
                "min_test_coverage": 0.9,
                "code_quality_threshold": 8.5,
                "performance_requirements": "high"
            })
        elif context.is_speed_prioritized():
            constraints.update({
                "min_test_coverage": 0.5,
                "code_quality_threshold": 6.0,
                "performance_requirements": "acceptable"
            })
        
        # Adjust for compliance requirements
        if context.constraints.compliance_requirements:
            constraints["min_test_coverage"] = max(constraints["min_test_coverage"], 0.8)
            constraints["security_requirements"] = "strict"
        
        return constraints
    
    def _get_resource_constraints(self, context: ProjectContext) -> Dict[str, Any]:
        """Get resource constraints based on context"""
        return {
            "timeline": context.constraints.timeline,
            "team_capacity": context.constraints.team_capacity,
            "budget_remaining": context.budget_remaining,
            "technical_expertise": context.constraints.technical_expertise,
            "time_pressure": context.time_pressure_level()
        }
    
    # ========== Conflict Detection and Prevention ==========
    
    async def detect_potential_conflicts(self, project_id: str, 
                                       proposed_decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect potential conflicts between proposed agent decisions.
        This is proactive conflict prevention through early detection.
        """
        conflicts = []
        context = await self.get_project_context(project_id)
        
        if not context or len(proposed_decisions) < 2:
            return conflicts
        
        # Check for resource conflicts
        resource_conflicts = self._detect_resource_conflicts(proposed_decisions, context)
        conflicts.extend(resource_conflicts)
        
        # Check for timeline conflicts
        timeline_conflicts = self._detect_timeline_conflicts(proposed_decisions, context)
        conflicts.extend(timeline_conflicts)
        
        # Check for quality standard conflicts
        quality_conflicts = self._detect_quality_conflicts(proposed_decisions, context)
        conflicts.extend(quality_conflicts)
        
        return conflicts
    
    def _detect_resource_conflicts(self, decisions: List[Dict], context: ProjectContext) -> List[Dict]:
        """Detect resource allocation conflicts"""
        conflicts = []
        total_resource_demand = sum(d.get("resource_demand", 0) for d in decisions)
        
        if total_resource_demand > 1.0:  # Over-allocation
            conflicts.append({
                "type": ConflictType.RESOURCE_CONFLICT.value,
                "severity": "high",
                "description": f"Resource over-allocation: {total_resource_demand:.1%}",
                "affected_decisions": [d.get("agent_id") for d in decisions],
                "suggested_resolution": "Prioritize critical decisions or extend timeline"
            })
        
        return conflicts
    
    def _detect_timeline_conflicts(self, decisions: List[Dict], context: ProjectContext) -> List[Dict]:
        """Detect timeline conflicts"""
        conflicts = []
        total_time_needed = sum(d.get("estimated_time_days", 0) for d in decisions)
        days_available = (context.deadline - datetime.now()).days
        
        if total_time_needed > days_available:
            conflicts.append({
                "type": ConflictType.TIME_OVERLAP.value,
                "severity": "critical",
                "description": f"Timeline conflict: {total_time_needed} days needed, {days_available} available",
                "affected_decisions": [d.get("agent_id") for d in decisions],
                "suggested_resolution": "Reduce scope or negotiate deadline extension"
            })
        
        return conflicts
    
    def _detect_quality_conflicts(self, decisions: List[Dict], context: ProjectContext) -> List[Dict]:
        """Detect conflicting quality standards"""
        conflicts = []
        quality_levels = [d.get("quality_target", 0.5) for d in decisions if "quality_target" in d]
        
        if quality_levels and (max(quality_levels) - min(quality_levels)) > 0.3:
            conflicts.append({
                "type": ConflictType.QUALITY_STANDARD_MISMATCH.value,
                "severity": "medium",
                "description": f"Inconsistent quality targets: {min(quality_levels):.1%} - {max(quality_levels):.1%}",
                "affected_decisions": [d.get("agent_id") for d in decisions if "quality_target" in d],
                "suggested_resolution": "Align on consistent quality standards based on project priority"
            })
        
        return conflicts
    
    # ========== Caching System ==========
    
    def _get_from_cache(self, project_id: str) -> Optional[ProjectContext]:
        """Get context from cache if still valid"""
        if project_id not in self._cached_contexts:
            return None
        
        context, timestamp, _ = self._cached_contexts[project_id]
        if datetime.now() - timestamp > self._cache_ttl:
            del self._cached_contexts[project_id]
            return None
        
        return context
    
    def _add_to_cache(self, project_id: str, context: ProjectContext) -> None:
        """Add context to cache with timestamp and hash"""
        context_hash = self._calculate_context_hash(context)
        self._cached_contexts[project_id] = (context, datetime.now(), context_hash)
    
    def _invalidate_cache(self, project_id: str) -> None:
        """Invalidate cache entry for a project"""
        if project_id in self._cached_contexts:
            del self._cached_contexts[project_id]
    
    def _calculate_context_hash(self, context: ProjectContext) -> str:
        """Calculate hash of context for change detection"""
        context_str = json.dumps(context.to_dict(), sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()
    
    # ========== Event System ==========
    
    def subscribe_to_context_updates(self, callback: Callable) -> None:
        """Subscribe to context update events"""
        self._context_subscribers.add(callback)
    
    async def _notify_context_update(self, project_id: str, event_type: str, 
                                   data: Optional[Dict] = None) -> None:
        """Notify subscribers of context updates"""
        event = {
            "project_id": project_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Notify all subscribers asynchronously
        for subscriber in list(self._context_subscribers):
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(event)
                else:
                    subscriber(event)
            except Exception as e:
                self.logger.error(f"Error notifying subscriber: {str(e)}")
    
    # ========== Background Tasks ==========
    
    async def _cleanup_expired_cache(self) -> None:
        """Background task to clean up expired cache entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                now = datetime.now()
                expired_keys = [
                    key for key, (_, timestamp, _) in self._cached_contexts.items()
                    if now - timestamp > self._cache_ttl
                ]
                
                for key in expired_keys:
                    del self._cached_contexts[key]
                
                if expired_keys:
                    self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
            except Exception as e:
                self.logger.error(f"Error in cache cleanup: {str(e)}")
    
    async def _periodic_health_check(self) -> None:
        """Background task for system health monitoring"""
        while True:
            try:
                await asyncio.sleep(600)  # Run every 10 minutes
                
                # Log system metrics
                cache_hit_rate = (self._cache_hits / max(self._query_count, 1)) * 100
                self.logger.info(
                    f"CSM Health: Queries={self._query_count}, "
                    f"Cache hit rate={cache_hit_rate:.1f}%, "
                    f"Updates={self._update_count}, "
                    f"Active contexts={len(self._contexts)}"
                )
                
                # Check for contexts that haven't been updated recently
                stale_threshold = datetime.now() - timedelta(hours=24)
                stale_contexts = [
                    ctx.project_id for ctx in self._contexts.values()
                    if ctx.last_updated < stale_threshold
                ]
                
                if stale_contexts:
                    self.logger.warning(f"Stale contexts detected: {stale_contexts}")
                    
            except Exception as e:
                self.logger.error(f"Error in health check: {str(e)}")
    
    # ========== Status and Metrics ==========
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics"""
        cache_hit_rate = (self._cache_hits / max(self._query_count, 1)) * 100
        
        return {
            "status": "healthy",
            "active_contexts": len(self._contexts),
            "cached_contexts": len(self._cached_contexts),
            "total_queries": self._query_count,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "total_updates": self._update_count,
            "subscribers": len(self._context_subscribers),
            "uptime": datetime.now().isoformat()
        }
    
    def get_project_summary(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get summary information for a specific project"""
        context = self._contexts.get(project_id)
        if not context:
            return None
        
        return {
            "project_id": context.project_id,
            "project_name": context.project_name,
            "lifecycle_phase": context.lifecycle_phase.value,
            "dominant_priority": context.get_dominant_priority(),
            "time_pressure": context.time_pressure_level(),
            "tech_debt_level": context.tech_debt.current_level,
            "budget_remaining": context.budget_remaining,
            "last_updated": context.last_updated.isoformat(),
            "version": context.version
        }


# Global singleton instance
_context_manager_instance: Optional[ContextStateManager] = None


def get_context_manager() -> ContextStateManager:
    """Get the global Context State Manager instance"""
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextStateManager()
    return _context_manager_instance


async def initialize_context_manager() -> ContextStateManager:
    """Initialize and return the global Context State Manager"""
    manager = get_context_manager()
    await manager.initialize()
    return manager
"""
Project Context Management System

This module defines the core data structures for the Context State Manager,
enabling intelligent coordination between agents through shared project context.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Any
from datetime import datetime
from enum import Enum
import json


class LifecyclePhase(Enum):
    """Project lifecycle phases"""
    DISCOVERY = "discovery"
    MVP = "mvp"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"


class ConflictType(Enum):
    """Types of conflicts that can occur between agents"""
    TIME_OVERLAP = "time_overlap"
    RESOURCE_CONFLICT = "resource_conflict"
    TECHNICAL_INCOMPATIBILITY = "technical_incompatibility"
    QUALITY_STANDARD_MISMATCH = "quality_standard_mismatch"


@dataclass
class PriorityMatrix:
    """Dynamic priority weight matrix for decision making"""
    speed: float       # Delivery speed weight 0.0-1.0
    quality: float     # Code quality weight 0.0-1.0  
    cost: float        # Cost control weight 0.0-1.0
    
    def __post_init__(self):
        total = self.speed + self.quality + self.cost
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"权重总和必须为1.0，当前为{total}")
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "speed": self.speed,
            "quality": self.quality,
            "cost": self.cost
        }


@dataclass
class ProjectConstraints:
    """Project constraints and limitations"""
    timeline: str                    # "2_weeks", "1_month", "3_months"
    team_capacity: str              # "3_developers", "small_team", "large_team"
    technical_expertise: List[str]   # ["React", "Node.js", "AWS"]
    compliance_requirements: List[str] = field(default_factory=list) # ["GDPR", "SOC2", "PCI"]
    budget_limit: Optional[float] = None     # Budget upper limit
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeline": self.timeline,
            "team_capacity": self.team_capacity,
            "technical_expertise": self.technical_expertise,
            "compliance_requirements": self.compliance_requirements,
            "budget_limit": self.budget_limit
        }


@dataclass  
class TechDebtStatus:
    """Technical debt status and management"""
    current_level: float        # Current debt level 0.0-1.0
    max_threshold: float        # Maximum tolerance threshold 0.0-1.0
    critical_areas: List[str]   # ["security", "performance", "maintainability"]
    repayment_budget: float     # Weekly repayment budget ratio
    
    def __post_init__(self):
        if not 0.0 <= self.current_level <= 1.0:
            raise ValueError("current_level must be between 0.0 and 1.0")
        if not 0.0 <= self.max_threshold <= 1.0:
            raise ValueError("max_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.repayment_budget <= 1.0:
            raise ValueError("repayment_budget must be between 0.0 and 1.0")
    
    @property
    def is_critical(self) -> bool:
        """Check if debt level is above critical threshold"""
        return self.current_level > self.max_threshold * 0.8
    
    @property
    def requires_mandatory_action(self) -> bool:
        """Check if debt level requires mandatory refactoring"""
        return self.current_level > self.max_threshold
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_level": self.current_level,
            "max_threshold": self.max_threshold,
            "critical_areas": self.critical_areas,
            "repayment_budget": self.repayment_budget,
            "is_critical": self.is_critical,
            "requires_mandatory_action": self.requires_mandatory_action
        }


@dataclass
class BusinessContext:
    """Business context information"""
    user_impact: Literal["low", "medium", "high"]
    revenue_impact: Literal["low", "medium", "high"] 
    competitive_pressure: Literal["low", "medium", "high"]
    market_window: Optional[str] = None  # "closing_soon", "stable", "expanding"
    stakeholder_priority: List[str] = field(default_factory=list)  # Key stakeholder priorities
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_impact": self.user_impact,
            "revenue_impact": self.revenue_impact,
            "competitive_pressure": self.competitive_pressure,
            "market_window": self.market_window,
            "stakeholder_priority": self.stakeholder_priority
        }


@dataclass
class ProjectContext:
    """Complete project context state for intelligent agent coordination"""
    
    # Core identification
    project_id: str
    project_name: str
    
    # Project lifecycle
    lifecycle_phase: LifecyclePhase
    deadline: datetime
    budget_remaining: float  # 0.0-1.0 ratio
    
    # Dynamic priority weights (must sum to 1.0)
    priority_matrix: PriorityMatrix
    
    # Constraints and limitations
    constraints: ProjectConstraints
    
    # Technical debt management
    tech_debt: TechDebtStatus
    
    # Business context
    business_context: BusinessContext
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    updated_by: Optional[str] = None
    version: int = 1
    
    def __post_init__(self):
        """Validate context consistency"""
        if self.budget_remaining < 0.0 or self.budget_remaining > 1.0:
            raise ValueError("budget_remaining must be between 0.0 and 1.0")
        
        if self.deadline < datetime.now():
            raise ValueError("deadline cannot be in the past")
    
    def update_priority_matrix(self, speed: float, quality: float, cost: float, updated_by: str):
        """Update priority matrix with validation"""
        self.priority_matrix = PriorityMatrix(speed=speed, quality=quality, cost=cost)
        self.last_updated = datetime.now()
        self.updated_by = updated_by
        self.version += 1
    
    def update_tech_debt(self, current_level: float, updated_by: str):
        """Update technical debt level"""
        if not 0.0 <= current_level <= 1.0:
            raise ValueError("current_level must be between 0.0 and 1.0")
        
        self.tech_debt.current_level = current_level
        self.last_updated = datetime.now()
        self.updated_by = updated_by
        self.version += 1
    
    def is_speed_prioritized(self) -> bool:
        """Check if speed is the primary priority"""
        return self.priority_matrix.speed > 0.5
    
    def is_quality_prioritized(self) -> bool:
        """Check if quality is the primary priority"""
        return self.priority_matrix.quality > 0.5
    
    def is_cost_prioritized(self) -> bool:
        """Check if cost is the primary priority"""
        return self.priority_matrix.cost > 0.5
    
    def get_dominant_priority(self) -> str:
        """Get the dominant priority factor"""
        priorities = {
            "speed": self.priority_matrix.speed,
            "quality": self.priority_matrix.quality,
            "cost": self.priority_matrix.cost
        }
        return max(priorities, key=priorities.get)
    
    def time_pressure_level(self) -> Literal["low", "medium", "high", "critical"]:
        """Calculate current time pressure level"""
        days_remaining = (self.deadline - datetime.now()).days
        
        if days_remaining <= 3:
            return "critical"
        elif days_remaining <= 7:
            return "high"
        elif days_remaining <= 21:
            return "medium"
        else:
            return "low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "lifecycle_phase": self.lifecycle_phase.value,
            "deadline": self.deadline.isoformat(),
            "budget_remaining": self.budget_remaining,
            "priority_matrix": self.priority_matrix.to_dict(),
            "constraints": self.constraints.to_dict(),
            "tech_debt": self.tech_debt.to_dict(),
            "business_context": self.business_context.to_dict(),
            "last_updated": self.last_updated.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_by": self.updated_by,
            "version": self.version,
            "dominant_priority": self.get_dominant_priority(),
            "time_pressure": self.time_pressure_level()
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectContext':
        """Create ProjectContext from dictionary"""
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            lifecycle_phase=LifecyclePhase(data["lifecycle_phase"]),
            deadline=datetime.fromisoformat(data["deadline"]),
            budget_remaining=data["budget_remaining"],
            priority_matrix=PriorityMatrix(**data["priority_matrix"]),
            constraints=ProjectConstraints(**data["constraints"]),
            tech_debt=TechDebtStatus(**data["tech_debt"]),
            business_context=BusinessContext(**data["business_context"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_by=data.get("updated_by"),
            version=data.get("version", 1)
        )


@dataclass
class RACIRole:
    """RACI responsibility matrix role definition"""
    responsible: str          # Who executes the task
    accountable: str          # Who is ultimately accountable  
    consulted: List[str]      # Who provides input
    informed: List[str] = field(default_factory=list)  # Who needs to know


@dataclass
class DecisionMatrix:
    """Decision responsibility matrix defining agent roles for different decision types"""
    
    architecture_choices: RACIRole = field(default_factory=lambda: RACIRole(
        responsible="system-architect",
        accountable="senior-rd-engineer",
        consulted=["backend-pro", "qa-engineer"],
        informed=["product-strategist"]
    ))
    
    testing_strategy: RACIRole = field(default_factory=lambda: RACIRole(
        responsible="qa-engineer", 
        accountable="senior-rd-engineer",
        consulted=["backend-pro", "fullstack-developer"]
    ))
    
    tech_debt_prioritization: RACIRole = field(default_factory=lambda: RACIRole(
        responsible="senior-rd-engineer",
        accountable="system-architect", 
        consulted=["backend-pro", "qa-engineer"],
        informed=["product-strategist"]
    ))
    
    performance_optimization: RACIRole = field(default_factory=lambda: RACIRole(
        responsible="backend-pro",
        accountable="system-architect",
        consulted=["qa-engineer", "database-expert"]
    ))
    
    security_implementation: RACIRole = field(default_factory=lambda: RACIRole(
        responsible="security-engineer",
        accountable="system-architect",
        consulted=["backend-pro", "integration-specialist"],
        informed=["product-strategist"]
    ))
    
    def get_responsible_agent(self, decision_type: str) -> str:
        """Get the responsible agent for a decision type"""
        if hasattr(self, decision_type):
            return getattr(self, decision_type).responsible
        raise ValueError(f"Unknown decision type: {decision_type}")
    
    def get_consulted_agents(self, decision_type: str) -> List[str]:
        """Get agents that should be consulted for a decision type"""
        if hasattr(self, decision_type):
            return getattr(self, decision_type).consulted
        raise ValueError(f"Unknown decision type: {decision_type}")


# Factory functions for common contexts
def create_mvp_context(project_id: str, project_name: str, deadline: datetime) -> ProjectContext:
    """Create a typical MVP project context"""
    return ProjectContext(
        project_id=project_id,
        project_name=project_name,
        lifecycle_phase=LifecyclePhase.MVP,
        deadline=deadline,
        budget_remaining=1.0,
        priority_matrix=PriorityMatrix(speed=0.6, quality=0.3, cost=0.1),
        constraints=ProjectConstraints(
            timeline="2_weeks",
            team_capacity="small_team",
            technical_expertise=["React", "Node.js", "MongoDB"]
        ),
        tech_debt=TechDebtStatus(
            current_level=0.2,
            max_threshold=0.6,
            critical_areas=["security"],
            repayment_budget=0.1
        ),
        business_context=BusinessContext(
            user_impact="high",
            revenue_impact="medium",
            competitive_pressure="high"
        )
    )


def create_production_context(project_id: str, project_name: str, deadline: datetime) -> ProjectContext:
    """Create a typical production project context"""
    return ProjectContext(
        project_id=project_id,
        project_name=project_name,
        lifecycle_phase=LifecyclePhase.PRODUCTION,
        deadline=deadline,
        budget_remaining=0.7,
        priority_matrix=PriorityMatrix(speed=0.2, quality=0.6, cost=0.2),
        constraints=ProjectConstraints(
            timeline="3_months",
            team_capacity="large_team",
            technical_expertise=["React", "Node.js", "PostgreSQL", "AWS"],
            compliance_requirements=["GDPR", "SOC2"]
        ),
        tech_debt=TechDebtStatus(
            current_level=0.3,
            max_threshold=0.4,
            critical_areas=["security", "performance", "maintainability"],
            repayment_budget=0.2
        ),
        business_context=BusinessContext(
            user_impact="high",
            revenue_impact="high",
            competitive_pressure="medium"
        )
    )
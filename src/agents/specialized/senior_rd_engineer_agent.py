"""
Context-Aware Senior R&D Engineer Agent

This agent provides intelligent technical solution design and TDD guidance based on 
project context, balancing engineering excellence with business pragmatism.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import asyncio
import logging

from ...core.context_aware_agent import ContextAwareAgent, DecisionStrategy, ContextualDecision
from ...core.base_agent import Task, TaskResult, TaskPriority
from ...core.project_context import ProjectContext, LifecyclePhase


@dataclass
class TechnicalStrategy:
    """Specific technical implementation strategy with detailed configuration"""
    approach: str                       # "pragmatic_tdd", "comprehensive_tdd", "rapid_prototyping"
    development_methodology: str        # "tdd_driven", "test_informed", "prototype_first"
    code_quality_target: float         # 0.0-1.0
    testing_intensity: str             # "minimal", "balanced", "comprehensive"
    refactoring_approach: str          # "continuous", "milestone_based", "as_needed"
    documentation_level: str           # "minimal", "standard", "comprehensive"
    technology_adoption: str           # "conservative", "balanced", "cutting_edge"
    technical_debt_strategy: str       # "prevent", "manage", "accept_short_term"
    performance_focus: str             # "basic", "optimized", "high_performance"


class SeniorRDEngineerAgent(ContextAwareAgent):
    """
    Context-aware Senior R&D Engineer Agent that adapts technical approach 
    based on project context, team capability, and business constraints.
    
    Core Philosophy:
    - TDD is a powerful tool, but not a universal solution
    - Technical decisions must align with business objectives and constraints
    - Code quality should match the project's lifecycle and requirements
    - Pragmatic engineering over dogmatic adherence to methodologies
    - Lead by example and mentor through practical guidance
    """
    
    def __init__(self, agent_id: str = "senior-rd-engineer", project_id: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="Senior R&D Engineer",
            capabilities=[
                "technical_solution_design",
                "tdd_methodology_guidance", 
                "code_architecture_design",
                "technology_evaluation",
                "team_mentoring",
                "technical_debt_management",
                "performance_optimization",
                "code_quality_assurance",
                "technical_documentation",
                "refactoring_strategy"
            ],
            project_id=project_id
        )
        
        self.programming_languages = [
            "Python", "JavaScript/TypeScript", "Java", "Go", "Rust", "C#", "C++"
        ]
        
        self.development_methodologies = [
            "TDD", "BDD", "ATDD", "DDD", "Clean Architecture", "Hexagonal Architecture"
        ]
        
        self.technical_metrics = {
            "code_quality_score": 0.0,
            "test_coverage_percentage": 0.0,
            "technical_debt_ratio": 0.0,
            "performance_score": 0.0,
            "maintainability_index": 0.0
        }
    
    def _define_strategies(self) -> Dict[str, DecisionStrategy]:
        """Define technical strategies based on different project contexts"""
        return {
            "pragmatic_tdd": DecisionStrategy(
                strategy_type="pragmatic_tdd",
                approach="Selective TDD focused on high-risk, high-value components",
                parameters={
                    "development_methodology": "test_informed",
                    "code_quality_target": 0.8,
                    "testing_intensity": "balanced",
                    "tdd_coverage": "risk_based",
                    "focus_areas": ["business_logic", "integrations", "security"]
                },
                rationale="Apply TDD where it provides maximum value while maintaining development speed",
                quality_target=0.8,
                speed_factor=1.2,
                resource_intensity=0.6
            ),
            
            "comprehensive_tdd": DecisionStrategy(
                strategy_type="comprehensive_tdd", 
                approach="Full TDD implementation with extensive test coverage",
                parameters={
                    "development_methodology": "tdd_driven",
                    "code_quality_target": 0.95,
                    "testing_intensity": "comprehensive",
                    "tdd_coverage": "full_coverage",
                    "focus_areas": ["all_components", "edge_cases", "error_handling"]
                },
                rationale="Ensure maximum code quality and long-term maintainability through rigorous TDD",
                quality_target=0.95,
                speed_factor=0.8,
                resource_intensity=0.8
            ),
            
            "rapid_prototyping": DecisionStrategy(
                strategy_type="rapid_prototyping",
                approach="Fast iteration with minimal testing for hypothesis validation",
                parameters={
                    "development_methodology": "prototype_first",
                    "code_quality_target": 0.6,
                    "testing_intensity": "minimal",
                    "tdd_coverage": "none",
                    "focus_areas": ["core_functionality", "user_validation"]
                },
                rationale="Enable rapid learning and validation with minimal upfront investment",
                quality_target=0.6,
                speed_factor=2.0,
                resource_intensity=0.4
            ),
            
            "production_ready": DecisionStrategy(
                strategy_type="production_ready",
                approach="Enterprise-grade development with reliability focus",
                parameters={
                    "development_methodology": "tdd_driven",
                    "code_quality_target": 0.9,
                    "testing_intensity": "comprehensive",
                    "tdd_coverage": "critical_path_plus",
                    "focus_areas": ["reliability", "security", "performance", "scalability"]
                },
                rationale="Build production-ready software with high reliability and maintainability",
                quality_target=0.9,
                speed_factor=0.9,
                resource_intensity=0.7
            ),
            
            "technical_debt_focused": DecisionStrategy(
                strategy_type="technical_debt_focused",
                approach="Refactoring and debt reduction with strategic testing",
                parameters={
                    "development_methodology": "refactor_with_tests",
                    "code_quality_target": 0.85,
                    "testing_intensity": "strategic",
                    "tdd_coverage": "refactoring_safety",
                    "focus_areas": ["legacy_code", "refactoring", "architecture_improvement"]
                },
                rationale="Systematically reduce technical debt while maintaining system stability",
                quality_target=0.85,
                speed_factor=0.7,
                resource_intensity=0.6
            )
        }
    
    def select_strategy(self, context: ProjectContext, task: Task, 
                       recommendations: Dict[str, Any]) -> DecisionStrategy:
        """
        Select optimal technical strategy based on project context.
        This embodies the senior engineer's experience and judgment.
        """
        # Get base strategy from context
        base_strategy_name = self._get_base_strategy_from_context(context)
        base_strategy = self.available_strategies[base_strategy_name]
        
        # Adjust strategy based on specific context factors
        adjusted_strategy = self._adjust_strategy_for_context(base_strategy, context, task)
        
        self.context_logger.info(
            f"Selected {adjusted_strategy.strategy_type} strategy: {adjusted_strategy.rationale}"
        )
        
        return adjusted_strategy
    
    def _get_base_strategy_from_context(self, context: ProjectContext) -> str:
        """Determine base strategy using senior engineer judgment"""
        
        # High technical debt requires focused debt reduction
        if context.tech_debt.is_critical:
            return "technical_debt_focused"
        
        # MVP/Discovery phase - pragmatic approach
        if context.lifecycle_phase in [LifecyclePhase.DISCOVERY, LifecyclePhase.MVP]:
            if context.is_speed_prioritized():
                return "rapid_prototyping" 
            else:
                return "pragmatic_tdd"
        
        # Production phase - comprehensive approach
        elif context.lifecycle_phase == LifecyclePhase.PRODUCTION:
            return "production_ready"
        
        # Quality-focused projects - comprehensive TDD
        elif context.is_quality_prioritized():
            return "comprehensive_tdd"
        
        # Speed-focused projects - pragmatic TDD
        elif context.is_speed_prioritized():
            return "pragmatic_tdd"
        
        # Cost-focused projects - rapid prototyping
        elif context.is_cost_prioritized():
            return "rapid_prototyping"
        
        # Default to pragmatic approach
        else:
            return "pragmatic_tdd"
    
    def _adjust_strategy_for_context(self, base_strategy: DecisionStrategy,
                                   context: ProjectContext, task: Task) -> DecisionStrategy:
        """Apply senior engineer experience to fine-tune strategy"""
        
        adjusted_params = base_strategy.parameters.copy()
        adjusted_rationale = base_strategy.rationale
        
        # Adjust for team expertise
        if context.constraints.technical_expertise:
            team_tech = [tech.lower() for tech in context.constraints.technical_expertise]
            if any(tech in ["python", "javascript", "typescript"] for tech in team_tech):
                adjusted_params["preferred_tools"] = "modern_tooling"
            adjusted_rationale += f" Optimized for team expertise in {', '.join(context.constraints.technical_expertise)}."
        
        # Adjust for compliance requirements
        if context.constraints.compliance_requirements:
            adjusted_params["testing_intensity"] = "comprehensive"
            adjusted_params["documentation_level"] = "comprehensive"
            adjusted_params["code_quality_target"] = max(adjusted_params["code_quality_target"], 0.85)
            adjusted_rationale += " Enhanced rigor for compliance requirements."
        
        # Adjust for business criticality
        if context.business_context.revenue_impact == "high":
            adjusted_params["testing_intensity"] = "comprehensive"
            adjusted_params["performance_focus"] = "optimized"
            adjusted_rationale += " Increased rigor due to high revenue impact."
        
        # Adjust for time pressure (senior engineer knows when to compromise)
        if context.time_pressure_level() == "critical":
            if base_strategy.strategy_type != "rapid_prototyping":
                adjusted_params["testing_intensity"] = "essential_only"
                adjusted_params["tdd_coverage"] = "critical_path"
                adjusted_rationale += " Focused on essentials due to critical time pressure."
        
        # Adjust for technical debt level
        if context.tech_debt.current_level > 0.6:
            adjusted_params["refactoring_approach"] = "continuous"
            adjusted_params["technical_debt_strategy"] = "prevent"
            adjusted_rationale += " Continuous refactoring due to high debt level."
        
        return DecisionStrategy(
            strategy_type=base_strategy.strategy_type,
            approach=base_strategy.approach,
            parameters=adjusted_params,
            rationale=adjusted_rationale,
            quality_target=base_strategy.quality_target,
            speed_factor=base_strategy.speed_factor,
            resource_intensity=base_strategy.resource_intensity
        )
    
    async def execute_with_strategy(self, task: Task, strategy: DecisionStrategy,
                                  context: ProjectContext) -> TaskResult:
        """Execute technical task with the selected strategy"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create technical solution design
            solution_design = await self._create_solution_design(task, strategy, context)
            
            # Define development approach
            development_approach = self._define_development_approach(strategy, context)
            
            # Create testing strategy
            testing_strategy = self._create_testing_strategy(strategy, context)
            
            # Generate implementation plan
            implementation_plan = self._create_implementation_plan(solution_design, strategy, context)
            
            # Create mentoring guidance
            mentoring_guidance = self._create_mentoring_guidance(strategy, context)
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TaskResult(
                task_id=task.id,
                success=True,
                output_data={
                    "solution_design": solution_design,
                    "development_approach": development_approach,
                    "testing_strategy": testing_strategy,
                    "implementation_plan": implementation_plan,
                    "mentoring_guidance": mentoring_guidance,
                    "strategy_used": strategy.to_dict(),
                    "technical_metrics": self.technical_metrics
                },
                execution_time=execution_time,
                metadata={
                    "methodology": strategy.parameters["development_methodology"],
                    "quality_target": strategy.parameters["code_quality_target"],
                    "estimated_implementation_days": self._estimate_implementation_days(strategy, context),
                    "risk_level": self._assess_implementation_risk(strategy, context)
                }
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Technical solution design failed: {str(e)}")
            
            return TaskResult(
                task_id=task.id,
                success=False,
                output_data={},
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def _create_solution_design(self, task: Task, strategy: DecisionStrategy,
                                    context: ProjectContext) -> Dict[str, Any]:
        """Create detailed technical solution design"""
        
        design = {
            "strategy": strategy.strategy_type,
            "technical_approach": self._define_technical_approach(task, strategy),
            "architecture_patterns": self._select_architecture_patterns(strategy, context),
            "code_organization": self._design_code_organization(strategy),
            "error_handling_strategy": self._design_error_handling(strategy),
            "performance_considerations": self._analyze_performance_requirements(strategy, context),
            "security_considerations": self._analyze_security_requirements(strategy, context),
            "scalability_design": self._design_scalability_approach(strategy, context),
            "integration_points": self._identify_integration_points(task, strategy)
        }
        
        return design
    
    def _define_technical_approach(self, task: Task, strategy: DecisionStrategy) -> Dict[str, Any]:
        """Define the overall technical approach"""
        
        methodology = strategy.parameters["development_methodology"]
        
        if methodology == "tdd_driven":
            return {
                "primary_methodology": "Test-Driven Development",
                "development_cycle": "Red-Green-Refactor",
                "test_first_approach": True,
                "refactoring_frequency": "Continuous",
                "quality_gates": "Comprehensive"
            }
        elif methodology == "test_informed":
            return {
                "primary_methodology": "Test-Informed Development",
                "development_cycle": "Design-Implement-Test-Refactor",
                "test_first_approach": False,
                "refactoring_frequency": "Regular",
                "quality_gates": "Balanced"
            }
        else:  # prototype_first
            return {
                "primary_methodology": "Prototype-First Development",
                "development_cycle": "Prototype-Validate-Iterate",
                "test_first_approach": False,
                "refactoring_frequency": "As needed",
                "quality_gates": "Minimal"
            }
    
    def _define_development_approach(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Define detailed development approach and guidelines"""
        
        return {
            "methodology": strategy.parameters["development_methodology"],
            "tdd_guidelines": self._create_tdd_guidelines(strategy),
            "code_quality_standards": self._define_code_quality_standards(strategy),
            "review_process": self._define_review_process(strategy, context),
            "refactoring_guidelines": self._create_refactoring_guidelines(strategy),
            "documentation_standards": self._define_documentation_standards(strategy),
            "performance_guidelines": self._create_performance_guidelines(strategy)
        }
    
    def _create_tdd_guidelines(self, strategy: DecisionStrategy) -> Dict[str, Any]:
        """Create contextual TDD guidelines based on strategy"""
        
        tdd_coverage = strategy.parameters.get("tdd_coverage", "balanced")
        
        guidelines = {
            "approach": tdd_coverage,
            "when_to_use_tdd": [],
            "when_to_skip_tdd": [],
            "test_types_priority": [],
            "red_green_refactor_cycle": True
        }
        
        if tdd_coverage == "full_coverage":
            guidelines.update({
                "when_to_use_tdd": ["All new functionality", "Bug fixes", "Refactoring"],
                "when_to_skip_tdd": ["Simple getters/setters", "Configuration"],
                "test_types_priority": ["Unit", "Integration", "Contract", "E2E"]
            })
        elif tdd_coverage == "risk_based":
            guidelines.update({
                "when_to_use_tdd": ["Business logic", "Complex algorithms", "Integration points"],
                "when_to_skip_tdd": ["UI components", "Simple CRUD operations", "Prototypes"],
                "test_types_priority": ["Unit for business logic", "Integration for APIs"]
            })
        elif tdd_coverage == "critical_path":
            guidelines.update({
                "when_to_use_tdd": ["Core business functionality", "Security features"],
                "when_to_skip_tdd": ["Non-critical features", "Temporary solutions"],
                "test_types_priority": ["Critical path tests", "Security tests"]
            })
        else:  # none or minimal
            guidelines.update({
                "when_to_use_tdd": ["High-risk components only"],
                "when_to_skip_tdd": ["Most development"],
                "test_types_priority": ["Smoke tests", "Critical functionality tests"]
            })
        
        return guidelines
    
    def _create_testing_strategy(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Create comprehensive testing strategy"""
        
        testing_intensity = strategy.parameters["testing_intensity"]
        
        strategy_map = {
            "minimal": {
                "unit_tests": "Critical components only",
                "integration_tests": "Major API endpoints",
                "e2e_tests": "Happy path scenarios",
                "coverage_target": 0.5,
                "automated_percentage": 0.6
            },
            "balanced": {
                "unit_tests": "Business logic and utilities",
                "integration_tests": "All API endpoints and external integrations",
                "e2e_tests": "Key user journeys",
                "coverage_target": 0.8,
                "automated_percentage": 0.8
            },
            "comprehensive": {
                "unit_tests": "All components with business logic",
                "integration_tests": "All integrations and APIs",
                "e2e_tests": "All user scenarios and edge cases",
                "coverage_target": 0.9,
                "automated_percentage": 0.9
            }
        }
        
        base_strategy = strategy_map.get(testing_intensity, strategy_map["balanced"])
        
        # Adjust for compliance requirements
        if context.constraints.compliance_requirements:
            base_strategy["security_tests"] = "Comprehensive security testing required"
            base_strategy["compliance_tests"] = "Regulatory compliance validation"
        
        return base_strategy
    
    def _create_implementation_plan(self, solution_design: Dict, strategy: DecisionStrategy,
                                  context: ProjectContext) -> Dict[str, Any]:
        """Create detailed implementation plan"""
        
        plan = {
            "phases": self._define_implementation_phases(strategy, context),
            "timeline": self._create_implementation_timeline(strategy, context),
            "milestones": self._define_milestones(strategy, context),
            "risk_mitigation": self._identify_implementation_risks(strategy, context),
            "quality_checkpoints": self._define_quality_checkpoints(strategy),
            "team_coordination": self._plan_team_coordination(strategy, context)
        }
        
        return plan
    
    def _create_mentoring_guidance(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Create mentoring and team guidance based on strategy"""
        
        return {
            "tdd_mentoring": self._create_tdd_mentoring_plan(strategy),
            "code_review_focus": self._define_code_review_focus_areas(strategy),
            "team_training_needs": self._identify_training_needs(strategy, context),
            "knowledge_sharing": self._plan_knowledge_sharing(strategy),
            "best_practices": self._compile_best_practices(strategy),
            "common_pitfalls": self._identify_common_pitfalls(strategy)
        }
    
    def _create_tdd_mentoring_plan(self, strategy: DecisionStrategy) -> Dict[str, Any]:
        """Create TDD mentoring plan based on strategy"""
        
        tdd_coverage = strategy.parameters.get("tdd_coverage", "balanced")
        
        if tdd_coverage in ["full_coverage", "comprehensive"]:
            return {
                "approach": "Comprehensive TDD mentoring",
                "pairing_sessions": "Daily TDD pairing with junior developers",
                "code_review_focus": "TDD cycle adherence and test quality",
                "training_topics": ["Red-Green-Refactor", "Test design patterns", "Mocking strategies"],
                "success_metrics": ["Test coverage", "Test quality scores", "TDD cycle compliance"]
            }
        elif tdd_coverage == "risk_based":
            return {
                "approach": "Selective TDD mentoring",
                "pairing_sessions": "Weekly pairing on high-risk components",
                "code_review_focus": "Test coverage for critical paths",
                "training_topics": ["When to use TDD", "Risk assessment", "Test prioritization"],
                "success_metrics": ["Critical path coverage", "Bug reduction in tested components"]
            }
        else:
            return {
                "approach": "Minimal TDD guidance",
                "pairing_sessions": "Ad-hoc pairing when needed",
                "code_review_focus": "Basic test presence",
                "training_topics": ["Testing fundamentals", "Quality gates"],
                "success_metrics": ["Basic test coverage", "Fewer production bugs"]
            }
    
    def _estimate_implementation_days(self, strategy: DecisionStrategy, context: ProjectContext) -> float:
        """Estimate implementation time in days"""
        
        base_complexity = {
            "rapid_prototyping": 2,
            "pragmatic_tdd": 5,
            "comprehensive_tdd": 8,
            "production_ready": 10,
            "technical_debt_focused": 7
        }
        
        base_days = base_complexity.get(strategy.strategy_type, 5)
        
        # Adjust for context factors
        if context.time_pressure_level() == "critical":
            base_days *= 0.7
        elif context.constraints.compliance_requirements:
            base_days *= 1.3
        
        return base_days
    
    def _assess_implementation_risk(self, strategy: DecisionStrategy, context: ProjectContext) -> str:
        """Assess overall implementation risk level"""
        
        risk_factors = 0
        
        # Strategy-specific risks
        if strategy.strategy_type == "rapid_prototyping":
            risk_factors += 1  # Higher technical debt risk
        elif strategy.strategy_type == "comprehensive_tdd":
            risk_factors += 0.5  # Timeline risk
        
        # Context-specific risks
        if context.time_pressure_level() == "critical":
            risk_factors += 1
        if context.tech_debt.is_critical:
            risk_factors += 1
        if context.constraints.team_capacity == "small_team":
            risk_factors += 0.5
        
        if risk_factors >= 2:
            return "High"
        elif risk_factors >= 1:
            return "Medium"
        else:
            return "Low"
    
    def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the given task"""
        rd_keywords = [
            "technical", "development", "implementation", "tdd", "architecture",
            "design", "solution", "engineering", "code", "methodology"
        ]
        
        task_text = f"{task.description} {task.input_data}".lower()
        return any(keyword in task_text for keyword in rd_keywords)
    
    def get_technical_metrics(self) -> Dict[str, Any]:
        """Get current technical metrics"""
        return self.technical_metrics.copy()
    
    def get_supported_methodologies(self) -> List[str]:
        """Get supported development methodologies"""
        return self.development_methodologies.copy()
    
    def get_programming_expertise(self) -> List[str]:
        """Get programming language expertise"""
        return self.programming_languages.copy()
    
    # Additional helper methods for implementation planning
    def _define_implementation_phases(self, strategy: DecisionStrategy, context: ProjectContext) -> List[Dict[str, str]]:
        """Define implementation phases based on strategy"""
        
        if strategy.strategy_type == "rapid_prototyping":
            return [
                {"phase": "1", "name": "Core Prototype", "focus": "Basic functionality"},
                {"phase": "2", "name": "User Validation", "focus": "Feedback collection"},
                {"phase": "3", "name": "Iteration", "focus": "Improvements based on feedback"}
            ]
        elif strategy.strategy_type == "comprehensive_tdd":
            return [
                {"phase": "1", "name": "Test Infrastructure", "focus": "Testing framework setup"},
                {"phase": "2", "name": "Core TDD Development", "focus": "Business logic with full TDD"},
                {"phase": "3", "name": "Integration & E2E", "focus": "Integration and end-to-end tests"},
                {"phase": "4", "name": "Quality Assurance", "focus": "Code review and refactoring"}
            ]
        else:  # pragmatic_tdd and others
            return [
                {"phase": "1", "name": "Foundation", "focus": "Architecture and critical tests"},
                {"phase": "2", "name": "Core Development", "focus": "Feature implementation with selective TDD"},
                {"phase": "3", "name": "Integration", "focus": "System integration and testing"},
                {"phase": "4", "name": "Polish", "focus": "Refactoring and optimization"}
            ]
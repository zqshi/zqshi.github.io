"""
Context-Aware QA Engineer Agent

This agent provides intelligent testing strategy selection based on project context,
implementing the core principle of situational testing rather than dogmatic TDD.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import asyncio
import logging

from ...core.context_aware_agent import ContextAwareAgent, DecisionStrategy, ContextualDecision
from ...core.base_agent import Task, TaskResult, TaskPriority
from ...core.project_context import ProjectContext


@dataclass
class TestingStrategy:
    """Specific testing strategy with detailed configuration"""
    approach: str                        # "essential_tdd_plus_integration"
    coverage_target: float              # 0.0-1.0
    focus_areas: List[str]              # ["critical_path", "security"]
    automation_level: str               # "core_features_only", "selective", "full"
    tdd_intensity: str                  # "minimal", "selective", "comprehensive"
    test_types: List[str]               # ["unit", "integration", "e2e", "performance"]
    quality_gates: Dict[str, Any]       # Quality gate configurations
    rationale: str                      # Explanation of strategy choice


class QAEngineerAgent(ContextAwareAgent):
    """
    Context-aware QA Engineer Agent that adapts testing strategy based on project context.
    
    Core Philosophy:
    - Testing strategy serves business objectives, not dogma
    - TDD is a tool, not a religion - use when appropriate
    - Quality standards should match project context and constraints
    - Intelligent risk-based testing over blind coverage targets
    """
    
    def __init__(self, agent_id: str = "qa-engineer", project_id: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="QA Engineer", 
            capabilities=[
                "test_strategy_design",
                "tdd_implementation", 
                "test_automation",
                "quality_assurance",
                "performance_testing",
                "security_testing",
                "integration_testing",
                "code_quality_analysis"
            ],
            project_id=project_id
        )
        
        self.testing_frameworks = [
            "Jest", "PyTest", "JUnit", "Cypress", "Playwright", 
            "Selenium", "Postman", "K6", "JMeter"
        ]
        
        self.quality_metrics = {
            "test_coverage": 0.0,
            "code_quality_score": 0.0,
            "defect_density": 0.0,
            "test_execution_time": 0.0
        }
    
    def _define_strategies(self) -> Dict[str, DecisionStrategy]:
        """Define testing strategies based on different project contexts"""
        return {
            "essential_testing": DecisionStrategy(
                strategy_type="essential_testing",
                approach="Focus on critical path and high-risk areas",
                parameters={
                    "coverage_target": 0.7,
                    "tdd_intensity": "selective",
                    "automation_level": "core_features",
                    "focus_areas": ["critical_path", "security", "integration_points"]
                },
                rationale="Prioritize testing effort on highest-risk, highest-value areas",
                quality_target=0.7,
                speed_factor=1.5,
                resource_intensity=0.6
            ),
            
            "comprehensive_testing": DecisionStrategy(
                strategy_type="comprehensive_testing",
                approach="Full TDD implementation with extensive coverage",
                parameters={
                    "coverage_target": 0.95,
                    "tdd_intensity": "comprehensive",
                    "automation_level": "full_automation",
                    "focus_areas": ["all_features", "edge_cases", "performance", "security"]
                },
                rationale="Ensure maximum quality and long-term maintainability",
                quality_target=0.95,
                speed_factor=0.7,
                resource_intensity=0.8
            ),
            
            "risk_driven_testing": DecisionStrategy(
                strategy_type="risk_driven_testing",
                approach="Risk-based testing with selective TDD",
                parameters={
                    "coverage_target": 0.8,
                    "tdd_intensity": "risk_based",
                    "automation_level": "selective_automation",
                    "focus_areas": ["high_risk", "business_critical", "compliance_areas"]
                },
                rationale="Balance testing thoroughness with resource constraints",
                quality_target=0.8,
                speed_factor=1.0,
                resource_intensity=0.6
            ),
            
            "mvp_testing": DecisionStrategy(
                strategy_type="mvp_testing",
                approach="Minimal viable testing for rapid validation",
                parameters={
                    "coverage_target": 0.5,
                    "tdd_intensity": "minimal",
                    "automation_level": "smoke_tests_only",
                    "focus_areas": ["core_functionality", "happy_path"]
                },
                rationale="Enable rapid iteration and user feedback collection",
                quality_target=0.6,
                speed_factor=2.0,
                resource_intensity=0.4
            ),
            
            "production_hardening": DecisionStrategy(
                strategy_type="production_hardening",
                approach="Production-ready testing with reliability focus",
                parameters={
                    "coverage_target": 0.9,
                    "tdd_intensity": "comprehensive",
                    "automation_level": "full_automation",
                    "focus_areas": ["reliability", "performance", "security", "scalability"]
                },
                rationale="Ensure production reliability and enterprise-grade quality",
                quality_target=0.9,
                speed_factor=0.8,
                resource_intensity=0.7
            )
        }
    
    def select_strategy(self, context: ProjectContext, task: Task, 
                       recommendations: Dict[str, Any]) -> DecisionStrategy:
        """
        Select optimal testing strategy based on project context.
        This is the core intelligence of the QA Engineer.
        """
        # Get base strategy from context priorities
        base_strategy_name = self._get_base_strategy_from_context(context)
        base_strategy = self.available_strategies[base_strategy_name]
        
        # Adjust strategy based on specific context factors
        adjusted_strategy = self._adjust_strategy_for_context(base_strategy, context, task)
        
        self.context_logger.info(
            f"Selected {adjusted_strategy.strategy_type} strategy: {adjusted_strategy.rationale}"
        )
        
        return adjusted_strategy
    
    def _get_base_strategy_from_context(self, context: ProjectContext) -> str:
        """Determine base strategy from project context"""
        
        # MVP phase - focus on essential testing
        if context.lifecycle_phase.value == "mvp":
            return "mvp_testing"
        
        # Production phase - comprehensive testing required
        elif context.lifecycle_phase.value == "production":
            return "production_hardening"
        
        # Speed prioritized - essential testing
        elif context.is_speed_prioritized():
            return "essential_testing"
        
        # Quality prioritized - comprehensive testing
        elif context.is_quality_prioritized():
            return "comprehensive_testing"
        
        # Balanced approach - risk-driven testing
        else:
            return "risk_driven_testing"
    
    def _adjust_strategy_for_context(self, base_strategy: DecisionStrategy, 
                                   context: ProjectContext, task: Task) -> DecisionStrategy:
        """Fine-tune strategy based on specific context factors"""
        
        adjusted_params = base_strategy.parameters.copy()
        adjusted_rationale = base_strategy.rationale
        
        # Adjust for compliance requirements
        if context.constraints.compliance_requirements:
            adjusted_params["coverage_target"] = max(adjusted_params["coverage_target"], 0.8)
            adjusted_params["focus_areas"] = list(set(adjusted_params["focus_areas"] + ["compliance", "security"]))
            adjusted_rationale += " Enhanced for compliance requirements."
        
        # Adjust for technical debt level
        if context.tech_debt.is_critical:
            adjusted_params["tdd_intensity"] = "comprehensive"
            adjusted_params["focus_areas"] = list(set(adjusted_params["focus_areas"] + ["refactoring", "architecture"]))
            adjusted_rationale += " Increased testing due to high technical debt."
        
        # Adjust for time pressure
        if context.time_pressure_level() == "critical":
            adjusted_params["coverage_target"] *= 0.8  # Reduce coverage target
            adjusted_params["automation_level"] = "essential_only"
            adjusted_rationale += " Reduced scope due to critical time pressure."
        
        # Create adjusted strategy
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
        """Execute testing task with the selected strategy"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create detailed testing plan
            testing_plan = self._create_testing_plan(task, strategy, context)
            
            # Execute testing activities
            test_results = await self._execute_testing_activities(testing_plan, strategy, context)
            
            # Generate test report
            test_report = self._generate_test_report(test_results, strategy)
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TaskResult(
                task_id=task.id,
                success=True,
                output_data={
                    "testing_plan": testing_plan,
                    "test_results": test_results,
                    "test_report": test_report,
                    "strategy_used": strategy.to_dict(),
                    "quality_metrics": self.quality_metrics
                },
                execution_time=execution_time,
                metadata={
                    "testing_approach": strategy.approach,
                    "coverage_achieved": test_results.get("coverage_percentage", 0),
                    "tests_executed": test_results.get("total_tests", 0),
                    "tests_passed": test_results.get("passed_tests", 0)
                }
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Testing execution failed: {str(e)}")
            
            return TaskResult(
                task_id=task.id,
                success=False,
                output_data={},
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _create_testing_plan(self, task: Task, strategy: DecisionStrategy, 
                           context: ProjectContext) -> Dict[str, Any]:
        """Create detailed testing plan based on strategy"""
        
        plan = {
            "strategy": strategy.strategy_type,
            "coverage_target": strategy.parameters["coverage_target"],
            "test_phases": [],
            "test_types": [],
            "automation_scope": strategy.parameters["automation_level"],
            "focus_areas": strategy.parameters["focus_areas"],
            "quality_gates": self._define_quality_gates(strategy, context),
            "timeline": self._estimate_testing_timeline(strategy, context),
            "resources_required": self._estimate_testing_resources(strategy, context)
        }
        
        # Define test phases based on strategy
        if strategy.parameters["tdd_intensity"] in ["comprehensive", "selective"]:
            plan["test_phases"].extend([
                "unit_testing_tdd",
                "integration_testing", 
                "system_testing",
                "acceptance_testing"
            ])
        else:
            plan["test_phases"].extend([
                "smoke_testing",
                "critical_path_testing",
                "integration_testing"
            ])
        
        # Define test types based on focus areas
        plan["test_types"] = self._determine_test_types(strategy.parameters["focus_areas"])
        
        return plan
    
    async def _execute_testing_activities(self, plan: Dict[str, Any], 
                                        strategy: DecisionStrategy,
                                        context: ProjectContext) -> Dict[str, Any]:
        """Execute the testing activities according to plan"""
        
        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "coverage_percentage": 0,
            "execution_time_seconds": 0,
            "quality_score": 0,
            "test_results_by_phase": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # Simulate testing execution based on strategy
        for phase in plan["test_phases"]:
            phase_results = await self._execute_test_phase(phase, strategy, context)
            results["test_results_by_phase"][phase] = phase_results
            
            # Aggregate results
            results["total_tests"] += phase_results.get("tests_count", 0)
            results["passed_tests"] += phase_results.get("passed_count", 0)
            results["failed_tests"] += phase_results.get("failed_count", 0)
        
        # Calculate coverage and quality metrics
        results["coverage_percentage"] = self._calculate_coverage(plan, strategy)
        results["quality_score"] = self._calculate_quality_score(results, strategy)
        
        # Generate recommendations
        results["recommendations"] = self._generate_testing_recommendations(results, strategy, context)
        
        # Update internal metrics
        self.quality_metrics.update({
            "test_coverage": results["coverage_percentage"],
            "code_quality_score": results["quality_score"],
            "test_execution_time": results["execution_time_seconds"]
        })
        
        return results
    
    async def _execute_test_phase(self, phase: str, strategy: DecisionStrategy, 
                                context: ProjectContext) -> Dict[str, Any]:
        """Execute a specific test phase"""
        
        # Simulate test execution with realistic timing
        await asyncio.sleep(0.1)  # Simulate test execution time
        
        # Generate phase-specific results based on strategy
        if phase == "unit_testing_tdd":
            return {
                "tests_count": 50,
                "passed_count": 48,
                "failed_count": 2,
                "coverage": 0.85,
                "duration_seconds": 30
            }
        elif phase == "integration_testing":
            return {
                "tests_count": 20,
                "passed_count": 19,
                "failed_count": 1,
                "coverage": 0.70,
                "duration_seconds": 60
            }
        elif phase == "system_testing":
            return {
                "tests_count": 15,
                "passed_count": 14,
                "failed_count": 1,
                "coverage": 0.60,
                "duration_seconds": 120
            }
        else:
            return {
                "tests_count": 10,
                "passed_count": 10,
                "failed_count": 0,
                "coverage": 0.50,
                "duration_seconds": 45
            }
    
    def _define_quality_gates(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Define quality gates based on strategy and context"""
        
        gates = {
            "minimum_coverage": strategy.parameters["coverage_target"],
            "max_failed_tests": 0,
            "max_execution_time_minutes": 30,
            "required_test_types": strategy.parameters.get("focus_areas", [])
        }
        
        # Adjust gates based on context
        if context.constraints.compliance_requirements:
            gates["security_tests_required"] = True
            gates["compliance_validation_required"] = True
        
        if context.lifecycle_phase.value == "production":
            gates["performance_tests_required"] = True
            gates["load_tests_required"] = True
        
        return gates
    
    def _determine_test_types(self, focus_areas: List[str]) -> List[str]:
        """Determine required test types based on focus areas"""
        
        test_types = ["unit"]  # Always include unit tests
        
        focus_to_test_mapping = {
            "critical_path": ["integration", "e2e"],
            "security": ["security", "penetration"],
            "performance": ["performance", "load"],
            "integration_points": ["integration", "api"],
            "compliance_areas": ["compliance", "security"],
            "reliability": ["stress", "endurance"],
            "scalability": ["load", "stress"]
        }
        
        for focus in focus_areas:
            if focus in focus_to_test_mapping:
                test_types.extend(focus_to_test_mapping[focus])
        
        return list(set(test_types))  # Remove duplicates
    
    def _calculate_coverage(self, plan: Dict[str, Any], strategy: DecisionStrategy) -> float:
        """Calculate achieved test coverage"""
        # Simulate coverage calculation based on strategy
        target_coverage = strategy.parameters["coverage_target"]
        
        # Add some realistic variance
        achieved_coverage = target_coverage * (0.9 + (0.2 * hash(strategy.strategy_type) % 1))
        return min(achieved_coverage, 1.0)
    
    def _calculate_quality_score(self, results: Dict[str, Any], strategy: DecisionStrategy) -> float:
        """Calculate overall quality score"""
        
        # Base quality score from test results
        pass_rate = results["passed_tests"] / max(results["total_tests"], 1)
        coverage_score = results["coverage_percentage"]
        
        # Weighted quality score
        quality_score = (pass_rate * 0.4) + (coverage_score * 0.6)
        
        return min(quality_score, 1.0)
    
    def _generate_testing_recommendations(self, results: Dict[str, Any], 
                                        strategy: DecisionStrategy,
                                        context: ProjectContext) -> List[str]:
        """Generate actionable testing recommendations"""
        
        recommendations = []
        
        # Coverage-based recommendations
        if results["coverage_percentage"] < strategy.parameters["coverage_target"]:
            recommendations.append(
                f"Increase test coverage from {results['coverage_percentage']:.1%} to "
                f"target {strategy.parameters['coverage_target']:.1%}"
            )
        
        # Failed tests recommendations
        if results["failed_tests"] > 0:
            recommendations.append(
                f"Address {results['failed_tests']} failing tests before deployment"
            )
        
        # Context-specific recommendations
        if context.tech_debt.is_critical:
            recommendations.append(
                "Consider additional refactoring tests due to high technical debt"
            )
        
        if context.time_pressure_level() == "critical":
            recommendations.append(
                "Focus on critical path testing only due to time constraints"
            )
        
        return recommendations
    
    def _generate_test_report(self, results: Dict[str, Any], strategy: DecisionStrategy) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        return {
            "summary": {
                "strategy_used": strategy.strategy_type,
                "total_tests": results["total_tests"],
                "success_rate": f"{(results['passed_tests'] / max(results['total_tests'], 1)):.1%}",
                "coverage_achieved": f"{results['coverage_percentage']:.1%}",
                "quality_score": f"{results['quality_score']:.1f}/10"
            },
            "detailed_results": results["test_results_by_phase"],
            "recommendations": results["recommendations"],
            "next_steps": self._generate_next_steps(results, strategy),
            "risk_assessment": self._assess_testing_risks(results, strategy)
        }
    
    def _generate_next_steps(self, results: Dict[str, Any], strategy: DecisionStrategy) -> List[str]:
        """Generate next steps based on testing results"""
        
        next_steps = []
        
        if results["failed_tests"] > 0:
            next_steps.append("Fix failing tests before proceeding")
        
        if results["coverage_percentage"] < 0.8:
            next_steps.append("Consider adding more unit tests for better coverage")
        
        if strategy.strategy_type == "mvp_testing":
            next_steps.append("Plan for comprehensive testing in next iteration")
        
        return next_steps
    
    def _assess_testing_risks(self, results: Dict[str, Any], strategy: DecisionStrategy) -> Dict[str, str]:
        """Assess risks based on testing results"""
        
        risks = {}
        
        if results["coverage_percentage"] < 0.6:
            risks["low_coverage"] = "High risk of undetected bugs due to low test coverage"
        
        if results["failed_tests"] > 0:
            risks["failing_tests"] = "Immediate risk from failing tests in codebase"
        
        if strategy.strategy_type == "mvp_testing":
            risks["minimal_testing"] = "Limited testing may not catch edge cases"
        
        return risks
    
    def _estimate_testing_timeline(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, str]:
        """Estimate testing timeline based on strategy"""
        
        base_days = {
            "mvp_testing": 1,
            "essential_testing": 2,
            "risk_driven_testing": 3,
            "comprehensive_testing": 5,
            "production_hardening": 7
        }
        
        estimated_days = base_days.get(strategy.strategy_type, 3)
        
        # Adjust for context
        if context.time_pressure_level() == "critical":
            estimated_days = max(1, estimated_days // 2)
        
        return {
            "estimated_days": str(estimated_days),
            "phases": f"{len(strategy.parameters.get('focus_areas', []))} phases",
            "parallel_execution": "Yes" if estimated_days > 2 else "No"
        }
    
    def _estimate_testing_resources(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Estimate required testing resources"""
        
        return {
            "human_resources": f"{strategy.resource_intensity:.0%} of QA capacity",
            "automation_tools": strategy.parameters["automation_level"],
            "environments_needed": ["test", "staging"] if strategy.strategy_type != "mvp_testing" else ["test"],
            "external_dependencies": self._identify_external_dependencies(strategy, context)
        }
    
    def _identify_external_dependencies(self, strategy: DecisionStrategy, context: ProjectContext) -> List[str]:
        """Identify external dependencies for testing"""
        
        dependencies = []
        
        if "security" in strategy.parameters["focus_areas"]:
            dependencies.append("Security team for security testing")
        
        if "performance" in strategy.parameters["focus_areas"]:
            dependencies.append("Performance testing tools and environment")
        
        if context.constraints.compliance_requirements:
            dependencies.append("Compliance team for regulatory testing")
        
        return dependencies
    
    def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the given task"""
        testing_keywords = [
            "test", "testing", "quality", "tdd", "coverage", 
            "automation", "validation", "verification"
        ]
        
        task_text = f"{task.description} {task.input_data}".lower()
        return any(keyword in task_text for keyword in testing_keywords)
    
    def get_testing_metrics(self) -> Dict[str, Any]:
        """Get current testing metrics"""
        return self.quality_metrics.copy()
    
    def get_supported_frameworks(self) -> List[str]:
        """Get list of supported testing frameworks"""
        return self.testing_frameworks.copy()
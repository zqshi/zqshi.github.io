"""
Context-Aware System Architect Agent

This agent provides intelligent architecture decisions based on project context,
balancing technical excellence with business pragmatism and resource constraints.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import asyncio
import logging

from ...core.context_aware_agent import ContextAwareAgent, DecisionStrategy, ContextualDecision
from ...core.base_agent import Task, TaskResult, TaskPriority
from ...core.project_context import ProjectContext, LifecyclePhase


@dataclass
class ArchitectureStrategy:
    """Specific architecture strategy with detailed configuration"""
    approach: str                       # "evolutionary_architecture"
    complexity_level: str              # "simple", "moderate", "enterprise"
    focus: str                         # "rapid_validation", "scalability", "cost_efficiency"
    tech_debt_tolerance: float         # 0.0-1.0
    scalability_target: str            # "single_server", "multi_server", "cloud_native"
    performance_target: str            # "basic", "high", "extreme"
    architecture_patterns: List[str]   # ["microservices", "event_driven", "layered"]
    technology_stack: Dict[str, str]   # {"database": "PostgreSQL", "cache": "Redis"}
    deployment_strategy: str           # "simple", "containerized", "kubernetes"
    monitoring_level: str              # "basic", "comprehensive", "enterprise"


class SystemArchitectAgent(ContextAwareAgent):
    """
    Context-aware System Architect Agent that adapts architecture decisions 
    based on project context, business objectives, and resource constraints.
    
    Core Philosophy:
    - Architecture serves business goals, not the other way around
    - Start simple, evolve complexity as needed
    - Technical decisions must consider resource and time constraints
    - Design for the problem you have today, not the one you might have tomorrow
    """
    
    def __init__(self, agent_id: str = "system-architect", project_id: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="System Architect",
            capabilities=[
                "system_architecture_design",
                "technology_selection",
                "scalability_planning",
                "performance_optimization",
                "security_architecture",
                "database_design",
                "api_architecture",
                "cloud_architecture",
                "microservices_design",
                "integration_patterns"
            ],
            project_id=project_id
        )
        
        self.supported_technologies = {
            "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "DynamoDB"],
            "backends": ["Node.js", "Python/FastAPI", "Java/Spring", "Go", ".NET"],
            "frontends": ["React", "Vue.js", "Angular", "Next.js"],
            "messaging": ["RabbitMQ", "Apache Kafka", "Redis Pub/Sub", "AWS SQS"],
            "deployment": ["Docker", "Kubernetes", "AWS ECS", "Serverless"],
            "monitoring": ["Prometheus", "Grafana", "DataDog", "New Relic"]
        }
        
        self.architecture_metrics = {
            "complexity_score": 0.0,
            "scalability_rating": 0.0,
            "maintainability_score": 0.0,
            "cost_efficiency": 0.0
        }
    
    def _define_strategies(self) -> Dict[str, DecisionStrategy]:
        """Define architecture strategies based on different project contexts"""
        return {
            "evolutionary_architecture": DecisionStrategy(
                strategy_type="evolutionary_architecture",
                approach="Start simple, evolve as needs become clear",
                parameters={
                    "complexity_level": "simple",
                    "focus": "rapid_validation",
                    "tech_debt_tolerance": 0.6,
                    "scalability_target": "single_server",
                    "patterns": ["layered", "mvc"]
                },
                rationale="Enable rapid iteration and learning while maintaining upgrade path",
                quality_target=0.7,
                speed_factor=1.5,
                resource_intensity=0.5
            ),
            
            "robust_architecture": DecisionStrategy(
                strategy_type="robust_architecture",
                approach="Design for long-term maintainability and scalability",
                parameters={
                    "complexity_level": "enterprise",
                    "focus": "scalability_reliability",
                    "tech_debt_tolerance": 0.2,
                    "scalability_target": "cloud_native",
                    "patterns": ["microservices", "event_driven", "cqrs"]
                },
                rationale="Build enterprise-grade architecture for long-term success",
                quality_target=0.9,
                speed_factor=0.7,
                resource_intensity=0.8
            ),
            
            "cost_optimized": DecisionStrategy(
                strategy_type="cost_optimized",
                approach="Minimize infrastructure and development costs",
                parameters={
                    "complexity_level": "minimal",
                    "focus": "cost_efficiency",
                    "tech_debt_tolerance": 0.5,
                    "scalability_target": "single_server",
                    "patterns": ["monolithic", "layered"]
                },
                rationale="Optimize for minimal resource usage and development time",
                quality_target=0.6,
                speed_factor=1.3,
                resource_intensity=0.3
            ),
            
            "mvp_architecture": DecisionStrategy(
                strategy_type="mvp_architecture",
                approach="Minimal viable architecture for rapid prototyping",
                parameters={
                    "complexity_level": "minimal",
                    "focus": "rapid_validation",
                    "tech_debt_tolerance": 0.7,
                    "scalability_target": "single_server",
                    "patterns": ["simple_layered"]
                },
                rationale="Enable fastest possible validation of business hypotheses",
                quality_target=0.5,
                speed_factor=2.0,
                resource_intensity=0.4
            ),
            
            "scalable_architecture": DecisionStrategy(
                strategy_type="scalable_architecture", 
                approach="Design for high scalability and performance",
                parameters={
                    "complexity_level": "moderate",
                    "focus": "scalability",
                    "tech_debt_tolerance": 0.3,
                    "scalability_target": "multi_server",
                    "patterns": ["microservices", "event_driven"]
                },
                rationale="Prepare for high traffic and scaling requirements",
                quality_target=0.8,
                speed_factor=0.9,
                resource_intensity=0.7
            )
        }
    
    def select_strategy(self, context: ProjectContext, task: Task, 
                       recommendations: Dict[str, Any]) -> DecisionStrategy:
        """
        Select optimal architecture strategy based on project context.
        This is the core intelligence of the System Architect.
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
        """Determine base strategy from project context"""
        
        # MVP phase - focus on rapid validation
        if context.lifecycle_phase == LifecyclePhase.MVP:
            return "mvp_architecture"
        
        # Discovery phase - evolutionary approach
        elif context.lifecycle_phase == LifecyclePhase.DISCOVERY:
            return "evolutionary_architecture"
        
        # Production phase - robust architecture
        elif context.lifecycle_phase == LifecyclePhase.PRODUCTION:
            return "robust_architecture"
        
        # Budget constrained - cost optimized
        elif context.budget_remaining < 0.3:
            return "cost_optimized"
        
        # Quality prioritized - robust architecture
        elif context.is_quality_prioritized():
            return "robust_architecture"
        
        # Speed prioritized - evolutionary approach
        elif context.is_speed_prioritized():
            return "evolutionary_architecture"
        
        # Cost prioritized - cost optimized
        elif context.is_cost_prioritized():
            return "cost_optimized"
        
        # Default to evolutionary
        else:
            return "evolutionary_architecture"
    
    def _adjust_strategy_for_context(self, base_strategy: DecisionStrategy,
                                   context: ProjectContext, task: Task) -> DecisionStrategy:
        """Fine-tune strategy based on specific context factors"""
        
        adjusted_params = base_strategy.parameters.copy()
        adjusted_rationale = base_strategy.rationale
        
        # Adjust for scalability requirements in business context  
        if context.business_context.user_impact == "high":
            adjusted_params["scalability_target"] = "multi_server"
            adjusted_params["performance_target"] = "high"
            adjusted_rationale += " Enhanced for high user impact."
        
        # Adjust for compliance requirements
        if context.constraints.compliance_requirements:
            adjusted_params["security_focus"] = "high"
            adjusted_params["audit_requirements"] = True
            adjusted_params["patterns"] = list(set(adjusted_params.get("patterns", []) + ["security_layer"]))
            adjusted_rationale += " Enhanced security for compliance requirements."
        
        # Adjust for technical expertise constraints
        if context.constraints.technical_expertise:
            adjusted_params["preferred_technologies"] = context.constraints.technical_expertise
            adjusted_rationale += f" Optimized for team expertise in {', '.join(context.constraints.technical_expertise)}."
        
        # Adjust for time pressure
        if context.time_pressure_level() == "critical":
            adjusted_params["complexity_level"] = "minimal"
            adjusted_params["patterns"] = ["simple_layered"]
            adjusted_rationale += " Simplified due to critical time pressure."
        
        # Adjust for technical debt
        if context.tech_debt.is_critical:
            adjusted_params["refactoring_priority"] = "high"
            adjusted_params["tech_debt_tolerance"] = 0.2
            adjusted_rationale += " Focused on debt reduction due to critical debt level."
        
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
        """Execute architecture task with the selected strategy"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create architecture design
            architecture_design = await self._create_architecture_design(task, strategy, context)
            
            # Select technology stack
            technology_stack = self._select_technology_stack(strategy, context)
            
            # Design deployment architecture
            deployment_design = self._design_deployment_architecture(strategy, context)
            
            # Create scalability plan
            scalability_plan = self._create_scalability_plan(strategy, context)
            
            # Generate architecture documentation
            documentation = self._generate_architecture_documentation(
                architecture_design, technology_stack, deployment_design, scalability_plan, strategy
            )
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return TaskResult(
                task_id=task.id,
                success=True,
                output_data={
                    "architecture_design": architecture_design,
                    "technology_stack": technology_stack,
                    "deployment_design": deployment_design, 
                    "scalability_plan": scalability_plan,
                    "documentation": documentation,
                    "strategy_used": strategy.to_dict(),
                    "architecture_metrics": self.architecture_metrics
                },
                execution_time=execution_time,
                metadata={
                    "complexity_level": strategy.parameters["complexity_level"],
                    "scalability_target": strategy.parameters["scalability_target"],
                    "estimated_implementation_weeks": self._estimate_implementation_time(strategy),
                    "total_estimated_cost": self._estimate_total_cost(strategy, context)
                }
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Architecture design failed: {str(e)}")
            
            return TaskResult(
                task_id=task.id,
                success=False,
                output_data={},
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def _create_architecture_design(self, task: Task, strategy: DecisionStrategy,
                                        context: ProjectContext) -> Dict[str, Any]:
        """Create detailed architecture design"""
        
        design = {
            "strategy": strategy.strategy_type,
            "architecture_style": self._determine_architecture_style(strategy),
            "system_boundaries": self._define_system_boundaries(task, strategy),
            "component_design": self._design_components(strategy, context),
            "data_architecture": self._design_data_architecture(strategy, context),
            "integration_patterns": self._define_integration_patterns(strategy),
            "security_architecture": self._design_security_architecture(strategy, context),
            "quality_attributes": self._define_quality_attributes(strategy, context)
        }
        
        # Add phase-specific designs
        if context.lifecycle_phase == LifecyclePhase.PRODUCTION:
            design["disaster_recovery"] = self._design_disaster_recovery(strategy)
            design["monitoring_strategy"] = self._design_monitoring_strategy(strategy)
        
        return design
    
    def _determine_architecture_style(self, strategy: DecisionStrategy) -> str:
        """Determine the primary architecture style"""
        
        patterns = strategy.parameters.get("patterns", ["layered"])
        
        if "microservices" in patterns:
            return "microservices"
        elif "event_driven" in patterns:
            return "event_driven"
        elif "layered" in patterns:
            return "layered_monolith"
        else:
            return "simple_monolith"
    
    def _define_system_boundaries(self, task: Task, strategy: DecisionStrategy) -> Dict[str, Any]:
        """Define system boundaries and external interfaces"""
        
        return {
            "core_domain": self._extract_core_domain_from_task(task),
            "external_systems": self._identify_external_systems(task, strategy),
            "api_boundaries": self._define_api_boundaries(strategy),
            "data_boundaries": self._define_data_boundaries(strategy),
            "security_boundaries": self._define_security_boundaries(strategy)
        }
    
    def _design_components(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Design system components based on strategy"""
        
        complexity = strategy.parameters["complexity_level"]
        
        if complexity == "minimal":
            return {
                "presentation_layer": "Simple web interface",
                "business_logic": "Single application layer",
                "data_access": "Direct database access",
                "external_integrations": "Basic API calls"
            }
        elif complexity == "moderate":
            return {
                "presentation_layer": "Responsive web UI with API",
                "business_logic": "Service layer with domain logic",
                "data_access": "Repository pattern with ORM",
                "external_integrations": "Service clients with error handling",
                "caching_layer": "Application-level caching"
            }
        else:  # enterprise
            return {
                "presentation_layer": "Multi-channel UI (web, mobile, API)",
                "api_gateway": "Centralized API management",
                "business_services": "Domain-driven microservices",
                "data_services": "CQRS with event sourcing",
                "integration_layer": "Event-driven integration",
                "caching_layer": "Distributed caching",
                "monitoring_layer": "Comprehensive observability"
            }
    
    def _design_data_architecture(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Design data architecture based on strategy"""
        
        scalability = strategy.parameters["scalability_target"]
        
        if scalability == "single_server":
            return {
                "primary_database": "PostgreSQL",
                "caching": "Redis for session storage",
                "backup_strategy": "Daily automated backups",
                "scaling_approach": "Vertical scaling"
            }
        elif scalability == "multi_server":
            return {
                "primary_database": "PostgreSQL with read replicas",
                "caching": "Redis cluster",
                "message_queue": "RabbitMQ",
                "backup_strategy": "Continuous replication",
                "scaling_approach": "Horizontal scaling"
            }
        else:  # cloud_native
            return {
                "primary_database": "Managed database service (RDS/Cloud SQL)",
                "caching": "Managed Redis service",
                "message_queue": "Managed message service (SQS/Pub/Sub)",
                "data_lake": "Object storage for analytics",
                "backup_strategy": "Automated point-in-time recovery",
                "scaling_approach": "Auto-scaling with load balancing"
            }
    
    def _select_technology_stack(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Select optimal technology stack based on strategy and constraints"""
        
        # Consider team expertise
        preferred_tech = strategy.parameters.get("preferred_technologies", [])
        
        stack = {
            "backend": self._select_backend_technology(strategy, preferred_tech),
            "frontend": self._select_frontend_technology(strategy, preferred_tech),
            "database": self._select_database_technology(strategy, context),
            "caching": self._select_caching_technology(strategy),
            "messaging": self._select_messaging_technology(strategy),
            "deployment": self._select_deployment_technology(strategy),
            "monitoring": self._select_monitoring_technology(strategy)
        }
        
        return stack
    
    def _select_backend_technology(self, strategy: DecisionStrategy, preferred_tech: List[str]) -> Dict[str, str]:
        """Select backend technology based on strategy and preferences"""
        
        # Check team preferences first
        for tech in preferred_tech:
            if tech.lower() in ["node.js", "javascript", "typescript"]:
                return {"language": "Node.js", "framework": "Express.js", "rationale": "Team expertise"}
            elif tech.lower() in ["python", "fastapi", "django"]:
                return {"language": "Python", "framework": "FastAPI", "rationale": "Team expertise"}
            elif tech.lower() in ["java", "spring"]:
                return {"language": "Java", "framework": "Spring Boot", "rationale": "Team expertise"}
        
        # Strategy-based selection
        if strategy.strategy_type == "mvp_architecture":
            return {"language": "Node.js", "framework": "Express.js", "rationale": "Rapid development"}
        elif strategy.parameters["complexity_level"] == "enterprise":
            return {"language": "Java", "framework": "Spring Boot", "rationale": "Enterprise reliability"}
        else:
            return {"language": "Python", "framework": "FastAPI", "rationale": "Balanced performance and productivity"}
    
    def _select_frontend_technology(self, strategy: DecisionStrategy, preferred_tech: List[str]) -> Dict[str, str]:
        """Select frontend technology"""
        
        # Check team preferences
        for tech in preferred_tech:
            if tech.lower() in ["react", "reactjs"]:
                return {"framework": "React", "build_tool": "Vite", "rationale": "Team expertise"}
            elif tech.lower() in ["vue", "vuejs"]:
                return {"framework": "Vue.js", "build_tool": "Vite", "rationale": "Team expertise"}
        
        # Default to React for most cases
        return {"framework": "React", "build_tool": "Vite", "rationale": "Industry standard"}
    
    def _select_database_technology(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, str]:
        """Select database technology"""
        
        complexity = strategy.parameters["complexity_level"]
        
        if "compliance" in str(context.constraints.compliance_requirements).lower():
            return {"primary": "PostgreSQL", "rationale": "ACID compliance for regulatory requirements"}
        elif complexity == "minimal":
            return {"primary": "SQLite", "rationale": "Simple deployment and maintenance"}
        elif "scalability" in strategy.parameters["focus"]:
            return {"primary": "PostgreSQL", "secondary": "MongoDB", "rationale": "Hybrid approach for scalability"}
        else:
            return {"primary": "PostgreSQL", "rationale": "Reliable and feature-rich"}
    
    def _design_deployment_architecture(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Design deployment architecture"""
        
        complexity = strategy.parameters["complexity_level"]
        scalability = strategy.parameters["scalability_target"]
        
        if complexity == "minimal":
            return {
                "deployment_type": "single_server",
                "containerization": "Optional Docker",
                "orchestration": "None",
                "load_balancing": "None",
                "ssl_termination": "Application level"
            }
        elif scalability == "multi_server":
            return {
                "deployment_type": "multi_server",
                "containerization": "Docker",
                "orchestration": "Docker Compose or basic Kubernetes",
                "load_balancing": "Nginx load balancer",
                "ssl_termination": "Load balancer level"
            }
        else:
            return {
                "deployment_type": "cloud_native",
                "containerization": "Docker",
                "orchestration": "Kubernetes",
                "load_balancing": "Cloud load balancer",
                "ssl_termination": "Cloud provider",
                "auto_scaling": "Horizontal pod autoscaler",
                "service_mesh": "Optional Istio"
            }
    
    def _create_scalability_plan(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, Any]:
        """Create scalability roadmap"""
        
        current_target = strategy.parameters["scalability_target"]
        
        plan = {
            "current_capacity": self._estimate_current_capacity(current_target),
            "scaling_triggers": self._define_scaling_triggers(strategy, context),
            "scaling_path": self._define_scaling_path(current_target),
            "bottleneck_analysis": self._analyze_potential_bottlenecks(strategy),
            "cost_projections": self._project_scaling_costs(strategy, context)
        }
        
        return plan
    
    def _generate_architecture_documentation(self, architecture_design: Dict, technology_stack: Dict,
                                          deployment_design: Dict, scalability_plan: Dict,
                                          strategy: DecisionStrategy) -> Dict[str, Any]:
        """Generate comprehensive architecture documentation"""
        
        return {
            "executive_summary": {
                "strategy": strategy.strategy_type,
                "approach": strategy.approach,
                "key_decisions": self._summarize_key_decisions(strategy),
                "trade_offs": self._document_trade_offs(strategy),
                "next_steps": self._define_next_steps(strategy)
            },
            "technical_specifications": {
                "architecture_overview": architecture_design,
                "technology_choices": technology_stack,
                "deployment_strategy": deployment_design,
                "scaling_roadmap": scalability_plan
            },
            "decision_records": self._create_architecture_decision_records(strategy),
            "implementation_guide": self._create_implementation_guide(strategy),
            "risk_assessment": self._assess_architecture_risks(strategy)
        }
    
    def _estimate_implementation_time(self, strategy: DecisionStrategy) -> int:
        """Estimate implementation time in weeks"""
        
        complexity_multipliers = {
            "minimal": 2,
            "simple": 4,
            "moderate": 8,
            "enterprise": 16
        }
        
        base_weeks = complexity_multipliers.get(strategy.parameters["complexity_level"], 4)
        
        # Adjust for strategy type
        if strategy.strategy_type == "mvp_architecture":
            return max(1, base_weeks // 2)
        elif strategy.strategy_type == "robust_architecture":
            return base_weeks * 2
        
        return base_weeks
    
    def _estimate_total_cost(self, strategy: DecisionStrategy, context: ProjectContext) -> Dict[str, str]:
        """Estimate total cost of architecture implementation"""
        
        complexity = strategy.parameters["complexity_level"]
        
        cost_ranges = {
            "minimal": {"development": "$10K-20K", "infrastructure": "$100-500/month"},
            "simple": {"development": "$20K-50K", "infrastructure": "$500-2K/month"},
            "moderate": {"development": "$50K-150K", "infrastructure": "$2K-10K/month"},
            "enterprise": {"development": "$150K-500K", "infrastructure": "$10K-50K/month"}
        }
        
        return cost_ranges.get(complexity, cost_ranges["simple"])
    
    # Helper methods for architecture design components
    def _extract_core_domain_from_task(self, task: Task) -> str:
        """Extract core business domain from task description"""
        # Simplified extraction - in real implementation would use NLP
        return f"Core domain inferred from: {task.description[:100]}..."
    
    def _identify_external_systems(self, task: Task, strategy: DecisionStrategy) -> List[str]:
        """Identify external systems that need integration"""
        return ["Authentication service", "Payment gateway", "Email service", "Analytics"]
    
    def _define_api_boundaries(self, strategy: DecisionStrategy) -> Dict[str, str]:
        """Define API boundaries and interfaces"""
        if "microservices" in strategy.parameters.get("patterns", []):
            return {"style": "RESTful microservices", "protocol": "HTTP/HTTPS", "format": "JSON"}
        else:
            return {"style": "Monolithic API", "protocol": "HTTP/HTTPS", "format": "JSON"}
    
    def _summarize_key_decisions(self, strategy: DecisionStrategy) -> List[str]:
        """Summarize key architectural decisions"""
        return [
            f"Architecture style: {strategy.approach}",
            f"Complexity level: {strategy.parameters['complexity_level']}",
            f"Scalability target: {strategy.parameters['scalability_target']}",
            f"Primary focus: {strategy.parameters['focus']}"
        ]
    
    def _document_trade_offs(self, strategy: DecisionStrategy) -> Dict[str, str]:
        """Document architectural trade-offs"""
        return {
            "speed_vs_quality": f"Optimized for {'speed' if strategy.speed_factor > 1 else 'quality'}",
            "simplicity_vs_features": f"Chose {strategy.parameters['complexity_level']} complexity",
            "cost_vs_scalability": f"Balanced for {strategy.parameters['focus']}"
        }
    
    def can_handle(self, task: Task) -> bool:
        """Check if this agent can handle the given task"""
        architecture_keywords = [
            "architecture", "design", "system", "scalability", "performance",
            "technology", "database", "api", "integration", "deployment"
        ]
        
        task_text = f"{task.description} {task.input_data}".lower()
        return any(keyword in task_text for keyword in architecture_keywords)
    
    def get_architecture_metrics(self) -> Dict[str, Any]:
        """Get current architecture metrics"""
        return self.architecture_metrics.copy()
    
    def get_supported_technologies(self) -> Dict[str, List[str]]:
        """Get supported technology stacks"""
        return self.supported_technologies.copy()
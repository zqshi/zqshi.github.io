"""
Intelligent Coordination Demo

This demo showcases how the Context State Manager enables intelligent agent coordination
through situational awareness rather than hierarchical management.

The demo shows the same task being handled differently by agents based on project context,
demonstrating the power of context-driven decision making.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.project_context import (
    ProjectContext, PriorityMatrix, ProjectConstraints, 
    TechDebtStatus, BusinessContext, LifecyclePhase
)
from src.core.context_state_manager import ContextStateManager
from src.core.base_agent import Task, TaskPriority

from src.agents.specialized.qa_engineer_agent import QAEngineerAgent
from src.agents.specialized.system_architect_agent import SystemArchitectAgent
from src.agents.specialized.senior_rd_engineer_agent import SeniorRDEngineerAgent


class CoordinationDemo:
    """Demonstration of intelligent agent coordination"""
    
    def __init__(self):
        self.context_manager = None
        self.agents = {}
        self.contexts = {}
    
    async def initialize(self):
        """Initialize the demo system"""
        print("🚀 Initializing Intelligent Coordination Demo...")
        
        # Initialize Context State Manager
        self.context_manager = ContextStateManager(cache_ttl_seconds=60)
        await self.context_manager.initialize()
        
        print("✅ Context State Manager initialized")
        
        # Create different project contexts
        await self._create_demo_contexts()
        
        # Initialize agents
        await self._initialize_agents()
        
        print("✅ Demo system ready!")
        print()
    
    async def _create_demo_contexts(self):
        """Create different project contexts for demonstration"""
        
        print("📋 Creating demo project contexts...")
        
        # 1. Startup MVP Context - Speed prioritized
        self.contexts["startup_mvp"] = ProjectContext(
            project_id="startup_mvp",
            project_name="FinTech Startup MVP",
            lifecycle_phase=LifecyclePhase.MVP,
            deadline=datetime.now() + timedelta(days=14),  # 2 weeks deadline
            budget_remaining=0.9,
            priority_matrix=PriorityMatrix(speed=0.7, quality=0.2, cost=0.1),
            constraints=ProjectConstraints(
                timeline="2_weeks",
                team_capacity="small_team",
                technical_expertise=["React", "Node.js", "MongoDB"],
                compliance_requirements=[]
            ),
            tech_debt=TechDebtStatus(0.1, 0.7, [], 0.1),
            business_context=BusinessContext(
                user_impact="high",
                revenue_impact="medium",
                competitive_pressure="high",
                market_window="closing_soon"
            )
        )
        
        # 2. Enterprise Production Context - Quality prioritized
        self.contexts["enterprise_prod"] = ProjectContext(
            project_id="enterprise_prod",
            project_name="Banking System Modernization",
            lifecycle_phase=LifecyclePhase.PRODUCTION,
            deadline=datetime.now() + timedelta(days=90),  # 3 months
            budget_remaining=0.7,
            priority_matrix=PriorityMatrix(speed=0.1, quality=0.7, cost=0.2),
            constraints=ProjectConstraints(
                timeline="3_months",
                team_capacity="large_team",
                technical_expertise=["Java", "Spring", "PostgreSQL", "Kubernetes"],
                compliance_requirements=["SOX", "PCI-DSS", "GDPR"]
            ),
            tech_debt=TechDebtStatus(0.2, 0.3, ["security", "performance"], 0.25),
            business_context=BusinessContext(
                user_impact="high",
                revenue_impact="high",
                competitive_pressure="medium",
                market_window="stable"
            )
        )
        
        # 3. High Technical Debt Context - Debt reduction focused
        self.contexts["legacy_rescue"] = ProjectContext(
            project_id="legacy_rescue",
            project_name="Legacy System Rescue",
            lifecycle_phase=LifecyclePhase.MAINTENANCE,
            deadline=datetime.now() + timedelta(days=60),  # 2 months
            budget_remaining=0.4,
            priority_matrix=PriorityMatrix(speed=0.3, quality=0.5, cost=0.2),
            constraints=ProjectConstraints(
                timeline="2_months",
                team_capacity="medium_team",
                technical_expertise=["Python", "Django", "PostgreSQL"],
                compliance_requirements=["HIPAA"]
            ),
            tech_debt=TechDebtStatus(0.8, 0.6, ["architecture", "security", "performance"], 0.4),
            business_context=BusinessContext(
                user_impact="high",
                revenue_impact="high",
                competitive_pressure="low",
                market_window="stable"
            )
        )
        
        # Register contexts with Context State Manager
        for context in self.contexts.values():
            await self.context_manager.register_project_context(context)
        
        print(f"✅ Created {len(self.contexts)} project contexts")
    
    async def _initialize_agents(self):
        """Initialize the demo agents"""
        
        print("🤖 Initializing context-aware agents...")
        
        # Create agents for each context
        for context_name in self.contexts.keys():
            project_id = self.contexts[context_name].project_id
            
            self.agents[context_name] = {
                "qa": QAEngineerAgent(project_id=project_id),
                "architect": SystemArchitectAgent(project_id=project_id),
                "rd_engineer": SeniorRDEngineerAgent(project_id=project_id)
            }
            
            # Initialize agents
            for agent in self.agents[context_name].values():
                await agent.initialize()
        
        print(f"✅ Initialized agents for {len(self.contexts)} contexts")
    
    async def run_demo(self):
        """Run the complete coordination demo"""
        
        print("=" * 80)
        print("🎯 INTELLIGENT COORDINATION DEMONSTRATION")
        print("=" * 80)
        print()
        
        print("This demo shows how the same task is handled differently by agents")
        print("based on project context, demonstrating intelligent coordination")
        print("through situational awareness rather than hierarchical management.")
        print()
        
        # Define a common task for all contexts
        common_task = Task(
            id="user-auth-feature",
            description="Implement user authentication and authorization system",
            input_data={
                "features": ["login", "registration", "password_reset", "role_based_access"],
                "expected_users": 10000,
                "security_requirements": ["MFA", "password_policies", "session_management"]
            },
            priority=TaskPriority.HIGH
        )
        
        print(f"📋 Common Task: {common_task.description}")
        print(f"🎯 Features: {', '.join(common_task.input_data['features'])}")
        print()
        
        # Run the task through different contexts
        await self._demonstrate_context_driven_decisions(common_task)
        
        # Show conflict detection
        await self._demonstrate_conflict_detection()
        
        # Show context updates and adaptation
        await self._demonstrate_context_adaptation()
        
        print("=" * 80)
        print("🎉 DEMO COMPLETE!")
        print("=" * 80)
        print()
        print("Key Takeaways:")
        print("• Same task, different strategies based on context")
        print("• No central coordinator needed - agents self-coordinate")
        print("• Full decision transparency and traceability")
        print("• Automatic conflict detection and prevention")
        print("• Dynamic adaptation to context changes")
        print()
    
    async def _demonstrate_context_driven_decisions(self, task: Task):
        """Demonstrate how context drives different decisions"""
        
        print("🧠 CONTEXT-DRIVEN DECISION MAKING")
        print("-" * 50)
        print()
        
        scenarios = [
            ("startup_mvp", "🚀 Startup MVP - Speed Priority"),
            ("enterprise_prod", "🏢 Enterprise Production - Quality Priority"),
            ("legacy_rescue", "🔧 Legacy Rescue - Debt Reduction Focus")
        ]
        
        for context_name, scenario_title in scenarios:
            print(f"{scenario_title}")
            print("─" * len(scenario_title))
            
            context = self.contexts[context_name]
            agents = self.agents[context_name]
            
            # Show context summary
            self._print_context_summary(context)
            
            # Get decisions from each agent
            print("\n🤖 Agent Decisions:")
            
            decisions = {}
            for agent_type, agent in agents.items():
                task.context = {"project_id": context.project_id}
                decision = await agent.make_contextual_decision(task, context)
                decisions[agent_type] = decision
                
                print(f"\n{agent_type.upper()}:")
                print(f"  Strategy: {decision.strategy.strategy_type}")
                print(f"  Approach: {decision.strategy.approach}")
                print(f"  Quality Target: {decision.strategy.quality_target:.1%}")
                print(f"  Time Estimate: {decision.estimated_time_days:.1f} days")
                print(f"  Rationale: {decision.strategy.rationale}")
            
            # Show coordination insights
            self._show_coordination_insights(decisions, context)
            
            print("\n" + "=" * 80 + "\n")
    
    def _print_context_summary(self, context: ProjectContext):
        """Print a summary of the project context"""
        
        print(f"📊 Context: {context.project_name}")
        print(f"   Phase: {context.lifecycle_phase.value}")
        print(f"   Priorities: Speed {context.priority_matrix.speed:.0%}, "
              f"Quality {context.priority_matrix.quality:.0%}, "
              f"Cost {context.priority_matrix.cost:.0%}")
        print(f"   Timeline: {context.constraints.timeline}")
        print(f"   Team: {context.constraints.team_capacity}")
        print(f"   Tech Debt: {context.tech_debt.current_level:.1%}")
        if context.constraints.compliance_requirements:
            print(f"   Compliance: {', '.join(context.constraints.compliance_requirements)}")
    
    def _show_coordination_insights(self, decisions: Dict[str, Any], context: ProjectContext):
        """Show how agents coordinate intelligently"""
        
        print(f"\n🎯 Coordination Insights:")
        
        # Check strategy alignment
        strategies = [d.strategy.strategy_type for d in decisions.values()]
        quality_targets = [d.strategy.quality_target for d in decisions.values()]
        time_estimates = [d.estimated_time_days for d in decisions.values()]
        
        print(f"   Strategy Alignment: {self._assess_alignment(strategies)}")
        print(f"   Quality Consistency: {min(quality_targets):.1%} - {max(quality_targets):.1%}")
        print(f"   Total Time: {sum(time_estimates):.1f} days")
        
        # Show context influence
        dominant_priority = context.get_dominant_priority()
        print(f"   Context Influence: All strategies optimized for {dominant_priority}")
        
        if context.constraints.compliance_requirements:
            print(f"   Compliance Awareness: Enhanced security considerations")
    
    def _assess_alignment(self, strategies: List[str]) -> str:
        """Assess how well strategies are aligned"""
        
        speed_focused = sum(1 for s in strategies if "rapid" in s or "mvp" in s or "essential" in s)
        quality_focused = sum(1 for s in strategies if "comprehensive" in s or "robust" in s or "production" in s)
        debt_focused = sum(1 for s in strategies if "debt" in s)
        
        if speed_focused >= 2:
            return "Speed-optimized coordination"
        elif quality_focused >= 2:
            return "Quality-focused coordination"
        elif debt_focused >= 2:
            return "Debt-reduction coordination"
        else:
            return "Balanced coordination"
    
    async def _demonstrate_conflict_detection(self):
        """Demonstrate automatic conflict detection"""
        
        print("⚠️  CONFLICT DETECTION DEMONSTRATION")
        print("-" * 50)
        print()
        
        print("Creating an over-constrained scenario to show conflict detection...")
        
        # Create a challenging context
        challenging_context = ProjectContext(
            project_id="conflict_demo",
            project_name="Over-Constrained Project",
            lifecycle_phase=LifecyclePhase.MVP,
            deadline=datetime.now() + timedelta(days=5),  # Very tight deadline
            budget_remaining=0.3,  # Low budget
            priority_matrix=PriorityMatrix(speed=0.5, quality=0.4, cost=0.1),  # Conflicting priorities
            constraints=ProjectConstraints(
                timeline="5_days",
                team_capacity="small_team",
                technical_expertise=["React"],
                compliance_requirements=["GDPR", "SOX"]  # High compliance burden
            ),
            tech_debt=TechDebtStatus(0.7, 0.5, ["security", "architecture"], 0.1),  # High debt, low repayment
            business_context=BusinessContext("high", "high", "high")  # High pressure
        )
        
        await self.context_manager.register_project_context(challenging_context)
        
        # Create agents for this context
        qa_agent = QAEngineerAgent(project_id="conflict_demo")
        arch_agent = SystemArchitectAgent(project_id="conflict_demo")
        rd_agent = SeniorRDEngineerAgent(project_id="conflict_demo")
        
        await qa_agent.initialize()
        await arch_agent.initialize()
        await rd_agent.initialize()
        
        # Get decisions
        task = Task("conflict-task", "Implement complex feature with tight constraints", {})
        task.context = {"project_id": "conflict_demo"}
        
        qa_decision = await qa_agent.make_contextual_decision(task, challenging_context)
        arch_decision = await arch_agent.make_contextual_decision(task, challenging_context)
        rd_decision = await rd_agent.make_contextual_decision(task, challenging_context)
        
        # Create proposals for conflict detection
        proposals = [
            {
                "agent_id": "qa-engineer",
                "estimated_time_days": qa_decision.estimated_time_days,
                "resource_demand": qa_decision.resource_demand,
                "quality_target": qa_decision.strategy.quality_target
            },
            {
                "agent_id": "system-architect",
                "estimated_time_days": arch_decision.estimated_time_days,
                "resource_demand": arch_decision.resource_demand,
                "quality_target": arch_decision.strategy.quality_target
            },
            {
                "agent_id": "senior-rd-engineer",
                "estimated_time_days": rd_decision.estimated_time_days,
                "resource_demand": rd_decision.resource_demand,
                "quality_target": rd_decision.strategy.quality_target
            }
        ]
        
        # Detect conflicts
        conflicts = await self.context_manager.detect_potential_conflicts("conflict_demo", proposals)
        
        print(f"📊 Proposals Summary:")
        for proposal in proposals:
            print(f"   {proposal['agent_id']}: {proposal['estimated_time_days']:.1f} days, "
                  f"{proposal['resource_demand']:.1%} resources")
        
        print(f"\n⚠️  Conflicts Detected: {len(conflicts)}")
        for conflict in conflicts:
            print(f"   • {conflict['type']}: {conflict['description']}")
            print(f"     Resolution: {conflict['suggested_resolution']}")
        
        print("\n🎯 System Response:")
        print("   • Automatic conflict detection prevents coordination issues")
        print("   • Clear resolution suggestions provided") 
        print("   • No human intervention required for conflict identification")
        print()
    
    async def _demonstrate_context_adaptation(self):
        """Demonstrate agent adaptation to context changes"""
        
        print("🔄 CONTEXT ADAPTATION DEMONSTRATION")
        print("-" * 50)
        print()
        
        print("Showing how agents adapt when project context changes...")
        
        # Use the startup context and modify it
        context = self.contexts["startup_mvp"]
        agent = self.agents["startup_mvp"]["qa"]
        
        task = Task("adaptation-task", "Design testing strategy", {})
        task.context = {"project_id": context.project_id}
        
        # Get initial decision
        print("📊 Initial Context (Speed Priority):")
        self._print_context_summary(context)
        
        initial_decision = await agent.make_contextual_decision(task, context)
        print(f"\n🤖 Initial QA Strategy: {initial_decision.strategy.strategy_type}")
        print(f"   Coverage Target: {initial_decision.strategy.parameters['coverage_target']:.1%}")
        print(f"   Testing Intensity: {initial_decision.strategy.parameters['testing_intensity']}")
        
        # Change context - shift to quality priority
        print(f"\n🔄 Context Change: Shifting to Quality Priority...")
        
        quality_updates = {
            "priority_matrix": {"speed": 0.2, "quality": 0.7, "cost": 0.1}
        }
        
        await self.context_manager.update_project_context(
            context.project_id,
            quality_updates,
            "demo_user"
        )
        
        # Get updated context and new decision
        updated_context = await self.context_manager.get_project_context(context.project_id)
        new_decision = await agent.make_contextual_decision(task, updated_context)
        
        print(f"\n📊 Updated Context (Quality Priority):")
        print(f"   Priorities: Speed {updated_context.priority_matrix.speed:.0%}, "
              f"Quality {updated_context.priority_matrix.quality:.0%}, "
              f"Cost {updated_context.priority_matrix.cost:.0%}")
        
        print(f"\n🤖 Adapted QA Strategy: {new_decision.strategy.strategy_type}")
        print(f"   Coverage Target: {new_decision.strategy.parameters['coverage_target']:.1%}")
        print(f"   Testing Intensity: {new_decision.strategy.parameters['testing_intensity']}")
        
        # Show adaptation insights
        print(f"\n🎯 Adaptation Insights:")
        print(f"   Strategy Change: {initial_decision.strategy.strategy_type} → {new_decision.strategy.strategy_type}")
        print(f"   Coverage Change: {initial_decision.strategy.parameters['coverage_target']:.1%} → {new_decision.strategy.parameters['coverage_target']:.1%}")
        print(f"   Quality Target: {initial_decision.strategy.quality_target:.1%} → {new_decision.strategy.quality_target:.1%}")
        print(f"   Automatic adaptation without human intervention!")
        print()


async def main():
    """Run the intelligent coordination demo"""
    
    print("🎬 Starting Intelligent Coordination Demo")
    print("This demo showcases the Context State Manager and Context-Aware Agents")
    print()
    
    # Create and run demo
    demo = CoordinationDemo()
    await demo.initialize()
    await demo.run_demo()
    
    print("Demo completed successfully! 🎉")
    print()
    print("What you just saw:")
    print("• Context-driven decision making replaces hierarchical coordination")
    print("• Same agents make different decisions based on project context")
    print("• Automatic conflict detection prevents coordination issues")
    print("• Dynamic adaptation to context changes")
    print("• Full transparency and explainability of all decisions")
    print()
    print("This demonstrates how intelligent coordination emerges from")
    print("shared situational awareness rather than central management!")


if __name__ == "__main__":
    asyncio.run(main())
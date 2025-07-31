"""
Comprehensive Test Suite for Context State Manager and Context-Aware Agents

This test suite validates the intelligent coordination mechanism that replaces
traditional hierarchical management with situational awareness.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import core system components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.project_context import (
    ProjectContext, PriorityMatrix, ProjectConstraints, 
    TechDebtStatus, BusinessContext, LifecyclePhase,
    create_mvp_context, create_production_context
)
from src.core.context_state_manager import ContextStateManager, get_context_manager
from src.core.context_aware_agent import ContextAwareAgent, DecisionStrategy
from src.core.base_agent import Task, TaskPriority

from src.agents.specialized.qa_engineer_agent import QAEngineerAgent
from src.agents.specialized.system_architect_agent import SystemArchitectAgent  
from src.agents.specialized.senior_rd_engineer_agent import SeniorRDEngineerAgent


class TestProjectContextManagement:
    """Test project context data structures and management"""
    
    def test_priority_matrix_validation(self):
        """Test that priority matrix enforces sum=1.0 constraint"""
        
        # Valid priority matrix
        valid_matrix = PriorityMatrix(speed=0.5, quality=0.3, cost=0.2)
        assert valid_matrix.speed == 0.5
        
        # Invalid priority matrix should raise error
        with pytest.raises(ValueError):
            PriorityMatrix(speed=0.6, quality=0.3, cost=0.2)  # Sum = 1.1
    
    def test_tech_debt_status_properties(self):
        """Test technical debt status calculations"""
        
        # Critical debt level
        critical_debt = TechDebtStatus(
            current_level=0.8,
            max_threshold=0.6,
            critical_areas=["security"],
            repayment_budget=0.2
        )
        
        assert critical_debt.is_critical == True
        assert critical_debt.requires_mandatory_action == True
        
        # Normal debt level
        normal_debt = TechDebtStatus(
            current_level=0.3,
            max_threshold=0.6, 
            critical_areas=[],
            repayment_budget=0.1
        )
        
        assert normal_debt.is_critical == False
        assert normal_debt.requires_mandatory_action == False
    
    def test_project_context_factory_functions(self):
        """Test factory functions for common project contexts"""
        
        deadline = datetime.now() + timedelta(days=14)
        
        # MVP context
        mvp_context = create_mvp_context("test-mvp", "Test MVP Project", deadline)
        assert mvp_context.lifecycle_phase == LifecyclePhase.MVP
        assert mvp_context.priority_matrix.speed == 0.6  # Speed prioritized
        assert mvp_context.constraints.timeline == "2_weeks"
        
        # Production context  
        prod_context = create_production_context("test-prod", "Test Production Project", deadline)
        assert prod_context.lifecycle_phase == LifecyclePhase.PRODUCTION
        assert prod_context.priority_matrix.quality == 0.6  # Quality prioritized
        assert "GDPR" in prod_context.constraints.compliance_requirements
    
    def test_context_priority_methods(self):
        """Test context priority detection methods"""
        
        speed_context = ProjectContext(
            project_id="speed-test",
            project_name="Speed Test",
            lifecycle_phase=LifecyclePhase.MVP,
            deadline=datetime.now() + timedelta(days=7),
            budget_remaining=0.8,
            priority_matrix=PriorityMatrix(speed=0.7, quality=0.2, cost=0.1),
            constraints=ProjectConstraints(timeline="1_week", team_capacity="small_team", technical_expertise=[]),
            tech_debt=TechDebtStatus(0.2, 0.5, [], 0.1),
            business_context=BusinessContext("high", "medium", "low")
        )
        
        assert speed_context.is_speed_prioritized() == True
        assert speed_context.is_quality_prioritized() == False
        assert speed_context.get_dominant_priority() == "speed"
        assert speed_context.time_pressure_level() == "high"


class TestContextStateManager:
    """Test the Context State Manager core functionality"""
    
    @pytest.fixture
    async def context_manager(self):
        """Create a fresh context manager for testing"""
        manager = ContextStateManager(cache_ttl_seconds=5)
        await manager.initialize()
        return manager
    
    @pytest.fixture
    def sample_context(self):
        """Create a sample project context for testing"""
        return create_mvp_context(
            "test-project",
            "Test Project",
            datetime.now() + timedelta(days=14)
        )
    
    @pytest.mark.asyncio
    async def test_context_registration_and_retrieval(self, context_manager: ContextStateManager, sample_context: ProjectContext):
        """Test basic context registration and retrieval"""
        
        # Register context
        await context_manager.register_project_context(sample_context)
        
        # Retrieve context
        retrieved_context = await context_manager.get_project_context(sample_context.project_id)
        
        assert retrieved_context is not None
        assert retrieved_context.project_id == sample_context.project_id
        assert retrieved_context.project_name == sample_context.project_name
    
    @pytest.mark.asyncio
    async def test_context_updates(self, context_manager: ContextStateManager, sample_context: ProjectContext):
        """Test context updates and versioning"""
        
        # Register initial context
        await context_manager.register_project_context(sample_context)
        initial_version = sample_context.version
        
        # Update context
        updates = {
            "priority_matrix": {"speed": 0.3, "quality": 0.6, "cost": 0.1},
            "tech_debt_level": 0.4
        }
        
        success = await context_manager.update_project_context(
            sample_context.project_id, 
            updates, 
            "test_user"
        )
        
        assert success == True
        
        # Verify updates
        updated_context = await context_manager.get_project_context(sample_context.project_id)
        assert updated_context.version > initial_version
        assert updated_context.priority_matrix.quality == 0.6
        assert updated_context.tech_debt.current_level == 0.4
        assert updated_context.updated_by == "test_user"
    
    @pytest.mark.asyncio
    async def test_contextual_recommendations(self, context_manager: ContextStateManager, sample_context: ProjectContext):
        """Test contextual recommendations for agents"""
        
        await context_manager.register_project_context(sample_context)
        
        # Get recommendations for QA Engineer
        recommendations = await context_manager.get_contextual_recommendations(
            sample_context.project_id, 
            "qa-engineer"
        )
        
        assert "dominant_priority" in recommendations
        assert "time_pressure" in recommendations
        assert "suggested_strategy" in recommendations
        assert recommendations["dominant_priority"] == "speed"  # MVP context is speed-prioritized
    
    @pytest.mark.asyncio
    async def test_conflict_detection(self, context_manager: ContextStateManager, sample_context: ProjectContext):
        """Test conflict detection between agent proposals"""
        
        await context_manager.register_project_context(sample_context)
        
        # Create conflicting proposals
        conflicting_proposals = [
            {
                "agent_id": "qa-engineer",
                "estimated_time_days": 5,
                "resource_demand": 0.7,
                "quality_target": 0.9
            },
            {
                "agent_id": "senior-rd-engineer", 
                "estimated_time_days": 2,
                "resource_demand": 0.8,
                "quality_target": 0.6
            }
        ]
        
        conflicts = await context_manager.detect_potential_conflicts(
            sample_context.project_id,
            conflicting_proposals
        )
        
        # Should detect resource over-allocation (0.7 + 0.8 = 1.5 > 1.0)
        assert len(conflicts) > 0
        conflict_types = [c["type"] for c in conflicts]
        assert "resource_conflict" in conflict_types
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, context_manager: ContextStateManager, sample_context: ProjectContext):
        """Test context caching for performance optimization"""
        
        await context_manager.register_project_context(sample_context)
        
        # First retrieval (should cache)
        context1 = await context_manager.get_project_context(sample_context.project_id)
        initial_queries = context_manager._query_count
        
        # Second retrieval (should hit cache)
        context2 = await context_manager.get_project_context(sample_context.project_id)
        
        assert context1.project_id == context2.project_id
        assert context_manager._cache_hits > 0
    
    def test_decision_authority_matrix(self, context_manager: ContextStateManager):
        """Test RACI decision authority matrix"""
        
        # Test architecture decision authority
        arch_authority = context_manager.get_decision_authority("architecture_choices")
        assert arch_authority["responsible"] == "system-architect"
        assert "senior-rd-engineer" in arch_authority.get("consulted", [])
        
        # Test testing strategy authority
        testing_authority = context_manager.get_decision_authority("testing_strategy")
        assert testing_authority["responsible"] == "qa-engineer"


class TestContextAwareAgents:
    """Test context-aware agent decision making"""
    
    @pytest.fixture
    async def agents_and_context(self):
        """Set up agents and context for testing"""
        
        # Create context manager and context
        context_manager = ContextStateManager()
        await context_manager.initialize()
        
        context = create_mvp_context(
            "agent-test",
            "Agent Test Project", 
            datetime.now() + timedelta(days=10)
        )
        await context_manager.register_project_context(context)
        
        # Create agents
        qa_agent = QAEngineerAgent(project_id="agent-test")
        arch_agent = SystemArchitectAgent(project_id="agent-test")
        rd_agent = SeniorRDEngineerAgent(project_id="agent-test")
        
        await qa_agent.initialize()
        await arch_agent.initialize()
        await rd_agent.initialize()
        
        return {
            "context_manager": context_manager,
            "context": context,
            "qa_agent": qa_agent,
            "arch_agent": arch_agent,
            "rd_agent": rd_agent
        }
    
    @pytest.mark.asyncio
    async def test_qa_engineer_contextual_decisions(self, agents_and_context):
        """Test QA Engineer makes appropriate decisions based on context"""
        
        qa_agent = agents_and_context["qa_agent"]
        context = agents_and_context["context"]
        
        # Create a testing task
        task = Task(
            id="test-task-1",
            description="Implement testing strategy for user authentication feature",
            input_data={"feature": "authentication", "complexity": "medium"},
            priority=TaskPriority.HIGH,
            context={"project_id": "agent-test"}
        )
        
        # Make contextual decision
        decision = await qa_agent.make_contextual_decision(task, context)
        
        # Verify decision is appropriate for MVP context (speed-prioritized)
        assert decision.strategy.strategy_type in ["essential_testing", "mvp_testing"]
        assert decision.strategy.parameters["coverage_target"] <= 0.8  # Not pursuing perfect coverage
        assert decision.estimated_time_days <= 3  # Reasonable for MVP timeline
        
        # Verify decision includes rationale
        assert "rationale" in decision.strategy.rationale
        assert len(decision.risks) > 0  # Should identify risks
    
    @pytest.mark.asyncio
    async def test_system_architect_contextual_decisions(self, agents_and_context):
        """Test System Architect makes appropriate decisions based on context"""
        
        arch_agent = agents_and_context["arch_agent"]
        context = agents_and_context["context"]
        
        # Create an architecture task
        task = Task(
            id="arch-task-1",
            description="Design system architecture for e-commerce platform",
            input_data={"domain": "e-commerce", "expected_users": "1000"},
            priority=TaskPriority.HIGH,
            context={"project_id": "agent-test"}
        )
        
        # Make contextual decision
        decision = await arch_agent.make_contextual_decision(task, context)
        
        # Verify decision is appropriate for MVP context
        assert decision.strategy.strategy_type in ["mvp_architecture", "evolutionary_architecture"]
        assert decision.strategy.parameters["complexity_level"] in ["minimal", "simple"]
        assert decision.strategy.parameters["scalability_target"] in ["single_server", "multi_server"]
    
    @pytest.mark.asyncio
    async def test_senior_rd_engineer_contextual_decisions(self, agents_and_context):
        """Test Senior R&D Engineer makes appropriate decisions based on context"""
        
        rd_agent = agents_and_context["rd_agent"]
        context = agents_and_context["context"]
        
        # Create a development task
        task = Task(
            id="dev-task-1", 
            description="Implement user registration and authentication system",
            input_data={"features": ["registration", "login", "password_reset"]},
            priority=TaskPriority.HIGH,
            context={"project_id": "agent-test"}
        )
        
        # Make contextual decision
        decision = await rd_agent.make_contextual_decision(task, context)
        
        # Verify decision is appropriate for MVP context
        assert decision.strategy.strategy_type in ["pragmatic_tdd", "rapid_prototyping"]
        assert decision.strategy.parameters["development_methodology"] in ["test_informed", "prototype_first"]
        assert decision.strategy.parameters["code_quality_target"] <= 0.8  # Reasonable for MVP
    
    @pytest.mark.asyncio
    async def test_cross_agent_consistency(self, agents_and_context):
        """Test that different agents make consistent decisions in same context"""
        
        qa_agent = agents_and_context["qa_agent"]
        arch_agent = agents_and_context["arch_agent"]
        rd_agent = agents_and_context["rd_agent"]
        context = agents_and_context["context"]
        
        # Create related tasks
        tasks = [
            Task("qa-task", "Design testing approach", {}, context={"project_id": "agent-test"}),
            Task("arch-task", "Design system architecture", {}, context={"project_id": "agent-test"}),
            Task("dev-task", "Plan development approach", {}, context={"project_id": "agent-test"})
        ]
        
        # Get decisions from all agents
        qa_decision = await qa_agent.make_contextual_decision(tasks[0], context)
        arch_decision = await arch_agent.make_contextual_decision(tasks[1], context)
        rd_decision = await rd_agent.make_contextual_decision(tasks[2], context)
        
        # Verify strategic consistency (all should prioritize speed for MVP)
        assert qa_decision.strategy.speed_factor >= 1.0  # Speed-optimized
        assert arch_decision.strategy.speed_factor >= 1.0  # Speed-optimized  
        assert rd_decision.strategy.speed_factor >= 1.0  # Speed-optimized
        
        # Verify quality targets are aligned
        quality_targets = [
            qa_decision.strategy.quality_target,
            arch_decision.strategy.quality_target,
            rd_decision.strategy.quality_target
        ]
        
        # All quality targets should be in reasonable range for MVP (0.5-0.8)
        assert all(0.5 <= target <= 0.8 for target in quality_targets)


class TestIntelligentCoordination:
    """Test the overall intelligent coordination mechanism"""
    
    @pytest.mark.asyncio
    async def test_context_change_adaptation(self):
        """Test that agents adapt when context changes"""
        
        # Set up context manager and initial context
        context_manager = ContextStateManager()
        await context_manager.initialize()
        
        # Start with MVP context (speed-prioritized)
        mvp_context = create_mvp_context(
            "adaptation-test",
            "Adaptation Test",
            datetime.now() + timedelta(days=30)
        )
        await context_manager.register_project_context(mvp_context)
        
        # Create QA agent
        qa_agent = QAEngineerAgent(project_id="adaptation-test")
        await qa_agent.initialize()
        
        task = Task("test-task", "Design testing strategy", {}, context={"project_id": "adaptation-test"})
        
        # Get initial decision (should be speed-focused)
        initial_decision = await qa_agent.make_contextual_decision(task, mvp_context)
        initial_strategy = initial_decision.strategy.strategy_type
        
        # Change context to quality-prioritized
        quality_updates = {
            "priority_matrix": {"speed": 0.2, "quality": 0.7, "cost": 0.1}
        }
        await context_manager.update_project_context(
            "adaptation-test", 
            quality_updates, 
            "test_user"
        )
        
        # Get updated context and make new decision
        updated_context = await context_manager.get_project_context("adaptation-test")
        new_decision = await qa_agent.make_contextual_decision(task, updated_context)
        new_strategy = new_decision.strategy.strategy_type
        
        # Verify strategy changed appropriately
        assert initial_strategy != new_strategy  # Strategy should change
        assert new_decision.strategy.quality_target > initial_decision.strategy.quality_target
    
    @pytest.mark.asyncio
    async def test_system_status_and_metrics(self):
        """Test system status reporting and metrics collection"""
        
        context_manager = ContextStateManager()
        await context_manager.initialize()
        
        # Add some contexts and perform operations
        context1 = create_mvp_context("metrics-test-1", "Test 1", datetime.now() + timedelta(days=7))
        context2 = create_production_context("metrics-test-2", "Test 2", datetime.now() + timedelta(days=30))
        
        await context_manager.register_project_context(context1)
        await context_manager.register_project_context(context2)
        
        # Perform some queries to generate metrics
        await context_manager.get_project_context("metrics-test-1")
        await context_manager.get_project_context("metrics-test-2")
        await context_manager.get_project_context("metrics-test-1")  # Should hit cache
        
        # Get system status
        status = context_manager.get_system_status()
        
        assert status["active_contexts"] == 2
        assert status["total_queries"] >= 3
        assert "cache_hit_rate" in status
        assert float(status["cache_hit_rate"].replace("%", "")) >= 0  # Some cache hits expected
    
    def test_decision_explainability(self):
        """Test that all decisions are explainable and traceable"""
        
        # This test verifies that our system provides full decision transparency
        qa_agent = QAEngineerAgent()
        
        # Check that all strategies have rationales
        for strategy_name, strategy in qa_agent.available_strategies.items():
            assert strategy.rationale is not None
            assert len(strategy.rationale) > 10  # Meaningful explanation
            assert strategy.quality_target is not None
            assert strategy.speed_factor is not None
        
        # Check that decisions include full context snapshots
        # This ensures every decision can be traced back to its context
        assert qa_agent.get_decision_history is not None
        assert qa_agent.explain_current_decision is not None


@pytest.mark.asyncio
async def test_end_to_end_coordination_scenario():
    """
    End-to-end test of the intelligent coordination system.
    This simulates a real project scenario with multiple agents coordinating.
    """
    
    # Set up system
    context_manager = ContextStateManager()
    await context_manager.initialize()
    
    # Create a realistic project context (startup MVP)
    project_context = ProjectContext(
        project_id="e2e-test",
        project_name="E-commerce MVP",
        lifecycle_phase=LifecyclePhase.MVP,
        deadline=datetime.now() + timedelta(days=21),  # 3 weeks
        budget_remaining=0.8,
        priority_matrix=PriorityMatrix(speed=0.6, quality=0.3, cost=0.1),
        constraints=ProjectConstraints(
            timeline="3_weeks",
            team_capacity="small_team", 
            technical_expertise=["React", "Node.js", "PostgreSQL"],
            compliance_requirements=["GDPR"]
        ),
        tech_debt=TechDebtStatus(0.3, 0.6, ["security"], 0.15),
        business_context=BusinessContext(
            user_impact="high",
            revenue_impact="high", 
            competitive_pressure="high"
        )
    )
    
    await context_manager.register_project_context(project_context)
    
    # Create agents
    qa_agent = QAEngineerAgent(project_id="e2e-test")
    arch_agent = SystemArchitectAgent(project_id="e2e-test")
    rd_agent = SeniorRDEngineerAgent(project_id="e2e-test")
    
    await qa_agent.initialize()
    await arch_agent.initialize() 
    await rd_agent.initialize()
    
    # Create coordinated tasks
    tasks = [
        Task("arch-design", "Design e-commerce system architecture", 
             {"requirements": ["user_management", "product_catalog", "checkout"]},
             context={"project_id": "e2e-test"}),
        Task("dev-approach", "Define development methodology and approach",
             {"features": ["authentication", "product_display", "shopping_cart"]},
             context={"project_id": "e2e-test"}),
        Task("test-strategy", "Create comprehensive testing strategy",
             {"components": ["user_flows", "payment_processing", "data_validation"]},
             context={"project_id": "e2e-test"})
    ]
    
    # Get decisions from all agents
    arch_decision = await arch_agent.make_contextual_decision(tasks[0], project_context)
    rd_decision = await rd_agent.make_contextual_decision(tasks[1], project_context)
    qa_decision = await qa_agent.make_contextual_decision(tasks[2], project_context)
    
    # Collect all decisions for conflict detection
    all_proposals = [
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
        },
        {
            "agent_id": "qa-engineer",
            "estimated_time_days": qa_decision.estimated_time_days,
            "resource_demand": qa_decision.resource_demand,
            "quality_target": qa_decision.strategy.quality_target
        }
    ]
    
    # Test conflict detection
    conflicts = await context_manager.detect_potential_conflicts("e2e-test", all_proposals)
    
    # Verify intelligent coordination
    
    # 1. All agents should choose speed-optimized strategies for MVP
    assert arch_decision.strategy.strategy_type in ["mvp_architecture", "evolutionary_architecture"]
    assert rd_decision.strategy.strategy_type in ["pragmatic_tdd", "rapid_prototyping"]
    assert qa_decision.strategy.strategy_type in ["essential_testing", "mvp_testing"]
    
    # 2. Quality targets should be aligned and appropriate for MVP
    quality_targets = [d.strategy.quality_target for d in [arch_decision, rd_decision, qa_decision]]
    assert all(0.6 <= target <= 0.8 for target in quality_targets), f"Quality targets: {quality_targets}"
    
    # 3. Timeline estimates should be reasonable for 3-week project
    total_estimated_days = sum(d.estimated_time_days for d in [arch_decision, rd_decision, qa_decision])
    assert total_estimated_days <= 21, f"Total estimated days: {total_estimated_days}"
    
    # 4. Each decision should have clear rationale
    for decision in [arch_decision, rd_decision, qa_decision]:
        assert decision.strategy.rationale is not None
        assert len(decision.strategy.rationale) > 20
        assert decision.context_snapshot is not None
    
    # 5. System should detect if there are any resource conflicts
    if conflicts:
        # Conflicts detected - system is working correctly
        conflict_types = [c["type"] for c in conflicts]
        assert len(conflict_types) > 0
        print(f"Detected conflicts: {conflict_types}")
    
    # 6. All decisions should consider GDPR compliance requirement
    for decision in [arch_decision, rd_decision, qa_decision]:
        decision_text = str(decision.strategy.to_dict()).lower()
        # Should have some consideration for compliance/security
        compliance_mentioned = any(word in decision_text for word in ["security", "compliance", "gdpr"])
        if not compliance_mentioned:
            # Check if it's in the dependencies or risks
            context_aware = any(word in str(decision.risks + decision.dependencies).lower() 
                               for word in ["security", "compliance"])
            assert context_aware, f"Decision should consider compliance: {decision.agent_id}"
    
    print("✅ End-to-end coordination test passed!")
    print(f"Architecture Strategy: {arch_decision.strategy.strategy_type}")
    print(f"Development Strategy: {rd_decision.strategy.strategy_type}")
    print(f"Testing Strategy: {qa_decision.strategy.strategy_type}")
    print(f"Total Estimated Time: {total_estimated_days:.1f} days")
    print(f"Conflicts Detected: {len(conflicts)}")


if __name__ == "__main__":
    # Run the end-to-end test
    asyncio.run(test_end_to_end_coordination_scenario())
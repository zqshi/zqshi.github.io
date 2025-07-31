"""
统一Agent测试
务实的测试策略：先保证基础功能正常工作
"""

import pytest
import asyncio
from digital_employee.core.agent_base import TaskRequest, TaskType
from digital_employee.agents.unified_agent import UnifiedDigitalEmployee


class TestUnifiedDigitalEmployee:
    """统一数字员工测试类"""
    
    @pytest.fixture
    def agent(self):
        """创建Agent实例"""
        return UnifiedDigitalEmployee()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """测试Agent初始化"""
        assert agent.name == "UnifiedDigitalEmployee"
        assert agent.is_active is True
        assert agent.processed_tasks == 0
        assert agent.success_rate == 0.0
    
    @pytest.mark.asyncio
    async def test_can_handle_all_task_types(self, agent):
        """测试Agent能处理所有任务类型"""
        for task_type in TaskType:
            assert agent.can_handle(task_type) is True
    
    @pytest.mark.asyncio
    async def test_requirement_analysis(self, agent):
        """测试需求分析功能"""
        request = TaskRequest(
            task_id="test_req_001",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="我需要一个支持1000并发用户的登录系统"
        )
        
        response = await agent.process_task(request)
        
        assert response.success is True
        assert response.task_id == "test_req_001"
        assert response.confidence_score > 0.0
        assert "functional_requirements" in response.result
        assert "非功能性需求" in str(response.result) or "non_functional_requirements" in response.result
    
    @pytest.mark.asyncio
    async def test_solution_design(self, agent):
        """测试方案设计功能"""
        request = TaskRequest(
            task_id="test_sol_001",
            task_type=TaskType.SOLUTION_DESIGN,
            user_input="设计一个Web应用的技术架构"
        )
        
        response = await agent.process_task(request)
        
        assert response.success is True
        assert response.task_id == "test_sol_001"
        assert "tech_stack" in response.result
        assert "architecture_components" in response.result
    
    @pytest.mark.asyncio
    async def test_code_generation(self, agent):
        """测试代码生成功能"""
        request = TaskRequest(
            task_id="test_code_001",
            task_type=TaskType.CODE_GENERATION,
            user_input="生成一个用户管理的API接口"
        )
        
        response = await agent.process_task(request)
        
        assert response.success is True
        assert response.task_id == "test_code_001"
        assert "code_example" in response.result
        assert "FastAPI" in response.result["code_example"]
    
    @pytest.mark.asyncio
    async def test_project_planning(self, agent):
        """测试项目规划功能"""
        request = TaskRequest(
            task_id="test_plan_001",
            task_type=TaskType.PROJECT_PLANNING,
            user_input="制定一个Web应用的开发计划"
        )
        
        response = await agent.process_task(request)
        
        assert response.success is True
        assert response.task_id == "test_plan_001"
        assert "project_phases" in response.result
        assert len(response.result["project_phases"]) > 0
    
    @pytest.mark.asyncio
    async def test_general_inquiry(self, agent):
        """测试通用询问功能"""
        request = TaskRequest(
            task_id="test_gen_001",
            task_type=TaskType.GENERAL_INQUIRY,
            user_input="什么是数字员工？"
        )
        
        response = await agent.process_task(request)
        
        assert response.success is True
        assert response.task_id == "test_gen_001"
        assert "response" in response.result
    
    @pytest.mark.asyncio
    async def test_statistics_update(self, agent):
        """测试统计信息更新"""
        initial_tasks = agent.processed_tasks
        
        request = TaskRequest(
            task_id="test_stats_001",
            task_type=TaskType.GENERAL_INQUIRY,
            user_input="测试统计"
        )
        
        await agent.process_task(request)
        
        assert agent.processed_tasks == initial_tasks + 1
        assert agent.success_rate > 0.0
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, agent):
        """测试并发处理能力"""
        tasks = []
        for i in range(5):
            request = TaskRequest(
                task_id=f"test_concurrent_{i}",
                task_type=TaskType.GENERAL_INQUIRY,
                user_input=f"并发测试 {i}"
            )
            tasks.append(agent.process_task(request))
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        for response in responses:
            assert response.success is True
    
    @pytest.mark.asyncio
    async def test_performance_baseline(self, agent):
        """测试性能基准"""
        request = TaskRequest(
            task_id="test_perf_001",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="性能测试需求"
        )
        
        response = await agent.process_task(request)
        
        # 基础性能要求：处理时间不超过5秒
        assert response.processing_time < 5.0
        assert response.success is True
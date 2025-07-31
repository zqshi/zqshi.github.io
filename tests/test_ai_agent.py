"""
AI增强Agent测试用例
测试AI服务集成和Agent功能
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from digital_employee.core.agent_base import TaskRequest, TaskType
from digital_employee.core.ai_service import AIResponse, OpenAIService, AnthropicService, LocalAIService, AIServiceManager
from digital_employee.agents.unified_agent_ai import AIEnhancedUnifiedEmployee


class TestAIService:
    """AI服务测试"""
    
    @pytest.mark.asyncio
    async def test_local_ai_service(self):
        """测试本地AI服务"""
        service = LocalAIService()
        messages = [
            {"role": "system", "content": "你是一个需求分析师"},
            {"role": "user", "content": "我需要一个用户管理系统"}
        ]
        
        # 转换为正确的消息格式
        from digital_employee.core.ai_service import AIMessage
        ai_messages = [AIMessage(role=msg["role"], content=msg["content"]) for msg in messages]
        
        response = await service.generate_response(ai_messages)
        
        assert response is not None
        assert response.content != ""
        assert response.model == "local-fallback"
        assert response.confidence_score == 0.5
        assert response.error is None
    
    @pytest.mark.asyncio
    async def test_ai_service_manager_fallback(self):
        """测试AI服务管理器的降级机制"""
        manager = AIServiceManager()
        
        # 只注册本地服务
        local_service = LocalAIService()
        from digital_employee.core.ai_service import AIProvider
        manager.register_service(AIProvider.LOCAL, local_service, is_primary=True)
        
        from digital_employee.core.ai_service import AIMessage
        messages = [
            AIMessage(role="system", content="测试系统提示"),
            AIMessage(role="user", content="测试用户输入")
        ]
        
        response = await manager.generate_response(messages)
        
        assert response is not None
        assert response.error is None
        assert response.content != ""
    
    def test_ai_service_statistics(self):
        """测试AI服务统计功能"""
        service = LocalAIService()
        
        initial_stats = service.get_statistics()
        assert initial_stats["request_count"] == 0
        assert initial_stats["total_tokens"] == 0
        assert initial_stats["provider"] == "LocalAIService"


class TestAIEnhancedAgent:
    """AI增强Agent测试"""
    
    @pytest.fixture
    def agent(self):
        """创建AI增强Agent实例"""
        return AIEnhancedUnifiedEmployee()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """测试Agent初始化"""
        assert agent.name == "AIEnhancedUnifiedEmployee"
        assert len(agent.supported_tasks) == 5
        assert agent.can_handle(TaskType.REQUIREMENT_ANALYSIS)
        assert agent.can_handle(TaskType.SOLUTION_DESIGN)
        assert agent.can_handle(TaskType.CODE_GENERATION)
        assert agent.can_handle(TaskType.PROJECT_PLANNING)
        assert agent.can_handle(TaskType.GENERAL_INQUIRY)
    
    @pytest.mark.asyncio
    async def test_requirement_analysis_fallback(self, agent):
        """测试需求分析降级功能"""
        request = TaskRequest(
            task_id="test-001",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="我需要一个电商网站，支持用户注册、商品展示和订单管理"
        )
        
        # Mock AI服务失败，触发降级
        with patch('digital_employee.agents.unified_agent_ai.generate_ai_response') as mock_ai:
            mock_ai.return_value = AIResponse(
                content="",
                model="test",
                error="AI服务不可用"
            )
            
            response = await agent.process_task(request)
            
            assert response.success == True
            assert response.task_id == "test-001"
            assert "fallback_used" in response.result
            assert response.result["fallback_used"] == True
    
    @pytest.mark.asyncio
    async def test_solution_design_fallback(self, agent):
        """测试方案设计降级功能"""
        request = TaskRequest(
            task_id="test-002",
            task_type=TaskType.SOLUTION_DESIGN,
            user_input="为电商网站设计技术方案",
            context={"requirements": ["用户管理", "商品展示", "订单处理"]}
        )
        
        with patch('digital_employee.agents.unified_agent_ai.generate_ai_response') as mock_ai:
            mock_ai.return_value = AIResponse(
                content="",
                model="test",
                error="AI服务不可用"
            )
            
            response = await agent.process_task(request)
            
            assert response.success == True
            assert "tech_stack" in response.result
            assert response.result["fallback_used"] == True
    
    @pytest.mark.asyncio
    async def test_successful_ai_response(self, agent):
        """测试AI响应成功的情况"""
        request = TaskRequest(
            task_id="test-003",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="我需要一个博客系统"
        )
        
        # Mock成功的AI响应
        mock_response_content = '''
        {
            "functional_requirements": ["用户注册登录", "文章发布编辑", "评论功能"],
            "non_functional_requirements": ["响应时间<2秒", "支持1000并发用户"],
            "clarification_questions": ["需要支持哪些格式的文章？", "是否需要SEO优化？"],
            "ears_format": ["The system shall allow user registration", "The system shall support article publishing"],
            "confidence_score": 0.85
        }
        '''
        
        with patch('digital_employee.agents.unified_agent_ai.generate_ai_response') as mock_ai:
            mock_ai.return_value = AIResponse(
                content=mock_response_content,
                model="gpt-4",
                usage_tokens=500,
                confidence_score=0.85
            )
            
            response = await agent.process_task(request)
            
            assert response.success == True
            assert response.task_id == "test-003"
            assert "functional_requirements" in response.result
            assert response.result["ai_enhanced"] == True
            assert response.result["model_used"] == "gpt-4"
            assert response.result["tokens_used"] == 500
    
    @pytest.mark.asyncio
    async def test_caching_mechanism(self, agent):
        """测试缓存机制"""
        request1 = TaskRequest(
            task_id="test-004a",
            task_type=TaskType.GENERAL_INQUIRY,
            user_input="什么是软件架构？"
        )
        
        request2 = TaskRequest(
            task_id="test-004b",
            task_type=TaskType.GENERAL_INQUIRY,
            user_input="什么是软件架构？"  # 相同的输入
        )
        
        # 第一次请求
        response1 = await agent.process_task(request1)
        assert response1.success == True
        
        # 第二次请求应该使用缓存
        response2 = await agent.process_task(request2)
        assert response2.success == True
        
        # 验证缓存被使用（处理时间应该很短）
        assert response2.processing_time < response1.processing_time
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """测试错误处理"""
        request = TaskRequest(
            task_id="test-005",
            task_type=TaskType.CODE_GENERATION,
            user_input="生成代码"
        )
        
        # Mock AI服务抛出异常
        with patch('digital_employee.agents.unified_agent_ai.generate_ai_response') as mock_ai:
            mock_ai.side_effect = Exception("网络错误")
            
            response = await agent.process_task(request)
            
            assert response.success == True  # 应该降级成功
            assert "fallback_used" in response.result
    
    def test_agent_statistics(self, agent):
        """测试Agent统计功能"""
        initial_stats = agent.get_status()
        
        assert initial_stats["name"] == "AIEnhancedUnifiedEmployee"
        assert initial_stats["processed_tasks"] == 0
        assert initial_stats["success_rate"] == 0.0
        assert initial_stats["is_active"] == True


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流程"""
        agent = AIEnhancedUnifiedEmployee()
        
        # 模拟完整的项目开发流程
        
        # 1. 需求分析
        req_analysis = TaskRequest(
            task_id="workflow-001",
            task_type=TaskType.REQUIREMENT_ANALYSIS,
            user_input="开发一个在线书店系统，支持图书搜索、购买和用户评价"
        )
        
        analysis_response = await agent.process_task(req_analysis)
        assert analysis_response.success == True
        
        # 2. 方案设计（使用需求分析结果作为上下文）
        solution_design = TaskRequest(
            task_id="workflow-002",
            task_type=TaskType.SOLUTION_DESIGN,
            user_input="基于前面的需求分析，设计技术方案",
            context={"requirements": analysis_response.result}
        )
        
        design_response = await agent.process_task(solution_design)
        assert design_response.success == True
        
        # 3. 代码生成（使用前面的结果作为上下文）
        code_generation = TaskRequest(
            task_id="workflow-003",
            task_type=TaskType.CODE_GENERATION,
            user_input="生成图书管理API的代码",
            context={
                "requirements": analysis_response.result,
                "tech_stack": design_response.result.get("tech_stack")
            }
        )
        
        code_response = await agent.process_task(code_generation)
        assert code_response.success == True
        
        # 4. 项目规划
        project_planning = TaskRequest(
            task_id="workflow-004",
            task_type=TaskType.PROJECT_PLANNING,
            user_input="制定项目实施计划",
            context={
                "requirements": analysis_response.result,
                "solution": design_response.result,
                "code_structure": code_response.result
            }
        )
        
        planning_response = await agent.process_task(project_planning)
        assert planning_response.success == True
        
        # 验证Agent统计信息更新
        final_stats = agent.get_status()
        assert final_stats["processed_tasks"] == 4


@pytest.mark.asyncio
async def test_concurrent_requests():
    """测试并发请求处理"""
    agent = AIEnhancedUnifiedEmployee()
    
    # 创建多个并发请求
    tasks = []
    for i in range(5):
        request = TaskRequest(
            task_id=f"concurrent-{i}",
            task_type=TaskType.GENERAL_INQUIRY,
            user_input=f"这是第{i}个测试问题"
        )
        tasks.append(agent.process_task(request))
    
    # 并发执行
    responses = await asyncio.gather(*tasks)
    
    # 验证所有请求都成功处理
    for response in responses:
        assert response.success == True
    
    # 验证统计信息
    stats = agent.get_status()
    assert stats["processed_tasks"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
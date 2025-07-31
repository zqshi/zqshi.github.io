"""
AI系统质量保证测试套件
专注于AI系统的特殊性质量验证
"""

import pytest
import asyncio
import time
import json
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from digital_employee.core.ai_service import (
    AIMessage, AIResponse, AIProvider,
    OpenAIService, AnthropicService, LocalAIService,
    AIServiceManager, generate_ai_response
)
from digital_employee.core.agent_base import TaskRequest, TaskType
from digital_employee.agents.unified_agent import UnifiedDigitalEmployee


class TestAIServiceQuality:
    """AI服务质量测试类 - 核心质量保证"""
    
    @pytest.mark.asyncio
    async def test_deterministic_behavior_consistency(self, deterministic_ai_service):
        """测试确定性行为一致性 - AI系统基础质量"""
        messages = [
            AIMessage(role="system", content="你是一个需求分析专家"),
            AIMessage(role="user", content="分析电商系统需求")
        ]
        
        # 多次调用相同输入，验证一致性
        responses = []
        for _ in range(5):
            response = await deterministic_ai_service.generate_response(messages)
            responses.append(response.content)
        
        # 确定性服务应该返回完全相同的结果
        assert all(content == responses[0] for content in responses), \
            "确定性AI服务返回结果不一致"
        assert "functional_requirements" in responses[0]
    
    @pytest.mark.asyncio
    async def test_response_quality_boundaries(self, deterministic_ai_service):
        """测试响应质量边界 - 质量下限验证"""
        
        # 简化测试用例，专注于核心质量验证
        test_scenarios = [
            {
                "input": "分析电商系统需求",
                "expected_content": "functional_requirements",
                "min_confidence": 0.7
            },
            {
                "input": "设计Web应用架构",
                "expected_content": "tech_stack", 
                "min_confidence": 0.7
            },
            {
                "input": "生成用户API接口",
                "expected_content": "code_example",
                "min_confidence": 0.6
            }
        ]
        
        for scenario in test_scenarios:
            messages = [
                AIMessage(role="system", content="你是一个技术专家"),
                AIMessage(role="user", content=scenario["input"])
            ]
            
            response = await deterministic_ai_service.generate_response(messages)
            
            # 基础质量检查
            assert response.content, f"响应内容为空: {scenario['input']}"
            assert response.confidence_score >= scenario["min_confidence"], \
                f"置信度过低: {response.confidence_score} < {scenario['min_confidence']}"
            
            # 内容质量检查
            assert len(response.content) > 20, "响应内容过短"
            
            # 确保响应包含有意义的内容（不是错误信息）
            assert "error" not in response.content.lower(), "响应包含错误信息"
    
    @pytest.mark.asyncio
    async def test_response_time_performance(self, deterministic_ai_service, performance_benchmarks):
        """测试响应时间性能 - 性能质量保证"""
        messages = [
            AIMessage(role="system", content="你是一个助手"),
            AIMessage(role="user", content="简单的问题测试")
        ]
        
        response_times = []
        
        # 执行多次测试获取稳定的性能数据
        for _ in range(10):
            start_time = time.time()
            response = await deterministic_ai_service.generate_response(messages)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            assert response.content, "响应内容为空"
        
        # 性能指标验证
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        assert avg_response_time < performance_benchmarks["response_time_threshold"], \
            f"平均响应时间过长: {avg_response_time:.2f}s > {performance_benchmarks['response_time_threshold']}s"
        
        assert p95_response_time < performance_benchmarks["p95_response_time_threshold"], \
            f"P95响应时间过长: {p95_response_time:.2f}s > {performance_benchmarks['p95_response_time_threshold']}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_request_stability(self, deterministic_ai_service, performance_benchmarks):
        """测试并发请求稳定性 - 负载质量验证"""
        
        async def single_request():
            messages = [
                AIMessage(role="system", content="你是一个助手"),
                AIMessage(role="user", content="并发测试")
            ]
            start_time = time.time()
            response = await deterministic_ai_service.generate_response(messages)
            end_time = time.time()
            
            return {
                "success": bool(response.content and not response.error),
                "response_time": end_time - start_time,
                "confidence_score": response.confidence_score
            }
        
        # 并发执行请求
        max_concurrent = performance_benchmarks["max_concurrent_requests"]
        tasks = [single_request() for _ in range(max_concurrent)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = [r for r in results if isinstance(r, dict)]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        # 质量指标验证
        success_count = sum(1 for r in valid_results if r["success"])
        success_rate = success_count / len(valid_results) if valid_results else 0
        
        assert len(exceptions) == 0, f"并发请求出现异常: {exceptions}"
        assert success_rate >= performance_benchmarks["min_success_rate"], \
            f"并发成功率过低: {success_rate:.2%} < {performance_benchmarks['min_success_rate']:.2%}"
        
        # 响应时间不应因并发而显著增加
        avg_response_time = statistics.mean([r["response_time"] for r in valid_results])
        assert avg_response_time < performance_benchmarks["response_time_threshold"] * 2, \
            f"并发情况下响应时间过长: {avg_response_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_security_input_handling(self, deterministic_ai_service, security_test_inputs):
        """测试安全输入处理 - 安全质量保证"""
        
        for malicious_input in security_test_inputs:
            messages = [
                AIMessage(role="system", content="你是一个安全的助手"),
                AIMessage(role="user", content=malicious_input)
            ]
            
            try:
                response = await deterministic_ai_service.generate_response(messages)
                
                # 基础安全检查
                assert response.content, "安全测试输入导致空响应"
                
                # 响应不应包含恶意输入的直接回显
                assert malicious_input not in response.content, \
                    f"响应直接回显了恶意输入: {malicious_input}"
                
                # 响应应该是安全的，不包含脚本标签或SQL语句
                content_lower = response.content.lower()
                assert "<script>" not in content_lower, "响应包含脚本标签"
                assert "drop table" not in content_lower, "响应包含SQL语句"
                
            except Exception as e:
                # 系统应该优雅处理异常输入，而不是崩溃
                pytest.fail(f"恶意输入导致系统异常: {malicious_input} -> {str(e)}")


class TestAIServiceManagerQuality:
    """AI服务管理器质量测试"""
    
    @pytest.mark.asyncio
    async def test_failover_mechanism(self):
        """测试故障转移机制 - 可靠性质量"""
        manager = AIServiceManager()
        
        # 创建一个会失败的Mock服务
        class FailingAIService:
            def __init__(self):
                self.model = "failing-service"
            
            async def generate_response(self, messages, temperature=0.7, max_tokens=2000):
                return AIResponse(
                    content="",
                    model=self.model,
                    error="服务不可用"
                )
        
        # 注册失败的主服务和正常的备用服务
        failing_service = FailingAIService()
        backup_service = LocalAIService()
        
        manager.register_service(AIProvider.OPENAI, failing_service, is_primary=True)
        manager.register_service(AIProvider.LOCAL, backup_service)
        
        # 测试故障转移
        messages = [AIMessage(role="user", content="测试故障转移")]
        response = await manager.generate_response(messages)
        
        # 应该成功从备用服务获取响应
        assert response.content, "故障转移失败，未获取到响应"
        assert not response.error, f"故障转移失败: {response.error}"
        assert "本地降级响应" in response.content, "未使用正确的备用服务"
    
    @pytest.mark.asyncio
    async def test_service_statistics_tracking(self, ai_service_manager):
        """测试服务统计跟踪 - 监控质量"""
        messages = [AIMessage(role="user", content="统计测试")]
        
        # 执行几次请求
        for _ in range(3):
            await ai_service_manager.generate_response(messages)
        
        # 检查统计信息
        stats = ai_service_manager.get_statistics()
        
        assert "local" in stats, "缺少服务统计信息"
        assert stats["local"]["request_count"] == 3, "请求计数不正确"


class TestEndToEndQuality:
    """端到端质量测试"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_quality(self, quality_collector):
        """测试完整工作流程质量 - 业务质量保证"""
        agent = UnifiedDigitalEmployee()
        
        # 模拟完整的用户交互流程
        test_scenarios = [
            {
                "task_type": TaskType.REQUIREMENT_ANALYSIS,
                "input": "我需要开发一个在线教育平台",
                "expected_quality_indicators": ["功能需求", "非功能需求", "约束条件"]
            },
            {
                "task_type": TaskType.SOLUTION_DESIGN,
                "input": "为在线教育平台设计技术架构",
                "expected_quality_indicators": ["技术栈", "架构组件", "部署方案"]
            },
            {
                "task_type": TaskType.CODE_GENERATION,
                "input": "生成用户认证模块的代码",
                "expected_quality_indicators": ["代码示例", "API", "模型"]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios):
            start_time = time.time()
            
            request = TaskRequest(
                task_id=f"e2e_test_{i}",
                task_type=scenario["task_type"],
                user_input=scenario["input"]
            )
            
            response = await agent.process_task(request)
            end_time = time.time()
            
            # 记录质量指标
            quality_collector.record_response(
                response_time=end_time - start_time,
                success=response.success,
                confidence_score=response.confidence_score,
                tokens=0  # Agent层面不直接跟踪token
            )
            
            # 业务质量验证
            assert response.success, f"任务处理失败: {scenario['task_type']}"
            assert response.confidence_score >= 0.7, \
                f"置信度过低: {response.confidence_score}"
            
            # 内容质量验证
            result_str = str(response.result).lower()
            missing_indicators = [
                indicator for indicator in scenario["expected_quality_indicators"]
                if indicator.lower() not in result_str
            ]
            assert not missing_indicators, \
                f"响应缺少质量指标: {missing_indicators}"
        
        # 检查整体质量指标
        metrics = quality_collector.get_metrics()
        assert metrics["success_rate"] >= 0.95, \
            f"端到端成功率过低: {metrics['success_rate']:.2%}"
        assert metrics["avg_confidence_score"] >= 0.7, \
            f"平均置信度过低: {metrics['avg_confidence_score']:.2f}"


class TestQualityRegression:
    """质量回归测试"""
    
    @pytest.mark.asyncio
    async def test_baseline_quality_maintenance(self, deterministic_ai_service):
        """测试基线质量维护 - 回归质量保证"""
        
        # 定义质量基线
        quality_baseline = {
            "min_response_length": 50,  # 最小响应长度
            "min_confidence_score": 0.8,  # 最小置信度
            "max_response_time": 2.0,  # 最大响应时间
            "required_structure_elements": ["分析", "建议", "总结"]  # 必需结构元素
        }
        
        # 测试标准场景
        test_input = "分析一个中型企业的数字化转型需求"
        messages = [
            AIMessage(role="system", content="你是一个业务分析专家"),
            AIMessage(role="user", content=test_input)
        ]
        
        start_time = time.time()
        response = await deterministic_ai_service.generate_response(messages)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 质量基线验证
        assert len(response.content) >= quality_baseline["min_response_length"], \
            f"响应长度不足: {len(response.content)} < {quality_baseline['min_response_length']}"
        
        assert response.confidence_score >= quality_baseline["min_confidence_score"], \
            f"置信度低于基线: {response.confidence_score} < {quality_baseline['min_confidence_score']}"
        
        assert response_time <= quality_baseline["max_response_time"], \
            f"响应时间超过基线: {response_time:.2f}s > {quality_baseline['max_response_time']}s"
        
        # 结构质量验证
        content_lower = response.content.lower()
        missing_elements = [
            element for element in quality_baseline["required_structure_elements"]
            if element not in content_lower
        ]
        assert not missing_elements, \
            f"响应缺少必需结构元素: {missing_elements}"
    
    @pytest.mark.asyncio
    async def test_quality_degradation_detection(self, deterministic_ai_service):
        """测试质量退化检测 - 持续质量监控"""
        
        # 执行多批次测试以检测质量趋势
        batches = []
        batch_size = 5
        
        for batch_num in range(3):
            batch_results = []
            
            for i in range(batch_size):
                messages = [
                    AIMessage(role="user", content=f"批次{batch_num}测试{i}")
                ]
                
                start_time = time.time()
                response = await deterministic_ai_service.generate_response(messages)
                end_time = time.time()
                
                batch_results.append({
                    "response_time": end_time - start_time,
                    "confidence_score": response.confidence_score,
                    "response_length": len(response.content),
                    "success": bool(response.content and not response.error)
                })
            
            batches.append(batch_results)
        
        # 分析质量趋势
        batch_metrics = []
        for batch in batches:
            batch_metrics.append({
                "avg_response_time": statistics.mean([r["response_time"] for r in batch]),
                "avg_confidence": statistics.mean([r["confidence_score"] for r in batch]),
                "success_rate": sum(r["success"] for r in batch) / len(batch)
            })
        
        # 检测质量退化（简单的趋势分析）
        for i in range(1, len(batch_metrics)):
            prev_batch = batch_metrics[i-1]
            curr_batch = batch_metrics[i]
            
            # 响应时间不应显著增加
            response_time_increase = (curr_batch["avg_response_time"] - prev_batch["avg_response_time"]) / prev_batch["avg_response_time"]
            assert response_time_increase < 0.5, \
                f"响应时间显著增加: {response_time_increase:.2%}"
            
            # 置信度不应显著下降
            confidence_decrease = (prev_batch["avg_confidence"] - curr_batch["avg_confidence"]) / prev_batch["avg_confidence"]
            assert confidence_decrease < 0.1, \
                f"置信度显著下降: {confidence_decrease:.2%}"
            
            # 成功率不应下降
            assert curr_batch["success_rate"] >= prev_batch["success_rate"], \
                f"成功率下降: {curr_batch['success_rate']:.2%} < {prev_batch['success_rate']:.2%}"


@pytest.mark.integration
class TestQualityIntegration:
    """质量集成测试"""
    
    @pytest.mark.asyncio
    async def test_real_ai_service_quality(self):
        """测试真实AI服务质量 - 集成质量验证"""
        
        # 这个测试需要真实的API密钥，在CI环境中跳过
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("需要OPENAI_API_KEY环境变量")
        
        service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))
        
        messages = [
            AIMessage(role="system", content="你是一个专业的需求分析师"),
            AIMessage(role="user", content="分析一个CRM系统的核心需求")
        ]
        
        response = await service.generate_response(messages)
        
        # 真实服务质量验证
        assert response.content, "真实AI服务返回空内容"
        assert not response.error, f"真实AI服务出错: {response.error}"
        assert response.usage_tokens > 0, "未跟踪token使用量"
        assert response.confidence_score > 0.7, "真实服务置信度过低"
        
        # 内容质量检查
        content_lower = response.content.lower()
        assert any(keyword in content_lower for keyword in ["需求", "功能", "用户", "系统"]), \
            "响应内容不符合需求分析要求"
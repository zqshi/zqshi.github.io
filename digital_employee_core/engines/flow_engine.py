"""
统一流程引擎 - 5阶段执行流程的统一入口
Unified Flow Engine - Single Entry Point for 5-Stage Execution Flow

整合所有阶段：
- 阶段1: 智能输入处理 (input_processor.py)
- 阶段2: Multi-Agent任务编排 (task_orchestrator.py)
- 阶段3: 并行Agent执行 (parallel_execution.py)
- 阶段4: 智能结果整合 (result_integrator.py)
- 阶段5: 交付与学习 (delivery_learning.py)
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from .input_processor import create_input_processor, ProcessingPlan
from .task_orchestrator import create_task_orchestrator, ExecutionPlan
from .parallel_execution import create_parallel_execution_engine
from .result_integrator import create_result_integrator, IntegratedResult
from .delivery_learning import create_delivery_learning_engine
from ..claude_integration import ClaudeService

logger = logging.getLogger(__name__)

class FlowStage(Enum):
    """流程阶段"""
    INPUT_PROCESSING = "input_processing"
    TASK_ORCHESTRATION = "task_orchestration"
    PARALLEL_EXECUTION = "parallel_execution"
    RESULT_INTEGRATION = "result_integration"
    DELIVERY_LEARNING = "delivery_learning"

class FlowStatus(Enum):
    """流程状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class StageResult:
    """阶段执行结果"""
    stage: FlowStage
    status: FlowStatus
    result: Any
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: float = 0.0
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FlowExecution:
    """流程执行记录"""
    flow_id: str
    user_input: str
    processing_plan: Optional[ProcessingPlan] = None
    execution_plan: Optional[ExecutionPlan] = None
    execution_results: Optional[Dict[str, Any]] = None
    integrated_result: Optional[IntegratedResult] = None
    final_result: Optional[Dict[str, Any]] = None
    
    # 执行状态
    current_stage: FlowStage = FlowStage.INPUT_PROCESSING
    overall_status: FlowStatus = FlowStatus.PENDING
    
    # 阶段结果
    stage_results: Dict[FlowStage, StageResult] = field(default_factory=dict)
    
    # 时间记录
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_execution_time: float = 0.0
    
    # 配置
    flow_config: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

class FlowEngine:
    """
    统一流程引擎
    整合5阶段执行流程
    """
    
    def __init__(self, claude_service: ClaudeService, flow_config: Dict[str, Any] = None):
        self.claude = claude_service
        self.flow_config = flow_config or {}
        
        # 初始化各阶段引擎
        self.input_processor = create_input_processor(claude_service)
        self.task_orchestrator = create_task_orchestrator(claude_service)
        self.parallel_executor = create_parallel_execution_engine(
            claude_service, 
            self.flow_config.get("max_concurrent_agents", 5)
        )
        self.result_integrator = create_result_integrator(claude_service)
        self.delivery_learner = create_delivery_learning_engine(claude_service)
        
        # 流程执行记录
        self.active_flows: Dict[str, FlowExecution] = {}
        self.completed_flows: List[FlowExecution] = []
        
        # 性能统计
        self.flow_statistics = {
            "total_flows": 0,
            "successful_flows": 0,
            "failed_flows": 0,
            "average_execution_time": 0.0,
            "stage_performance": {stage: {"count": 0, "total_time": 0.0} for stage in FlowStage}
        }
    
    async def execute_flow(
        self, 
        user_input: str, 
        context: Dict[str, Any] = None,
        delivery_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        执行完整的5阶段流程
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            delivery_config: 交付配置
            
        Returns:
            Dict: 最终执行结果
        """
        flow_id = str(uuid.uuid4())
        logger.info(f"开始执行流程: {flow_id}")
        
        # 创建流程执行记录
        flow_execution = FlowExecution(
            flow_id=flow_id,
            user_input=user_input,
            flow_config=self.flow_config,
            metadata={
                "context": context,
                "delivery_config": delivery_config,
                "started_at": datetime.now().isoformat()
            }
        )
        
        self.active_flows[flow_id] = flow_execution
        flow_execution.overall_status = FlowStatus.RUNNING
        
        try:
            # 阶段1: 智能输入处理
            await self._execute_stage_1(flow_execution, context)
            
            # 阶段2: Multi-Agent任务编排
            await self._execute_stage_2(flow_execution)
            
            # 阶段3: 并行Agent执行
            await self._execute_stage_3(flow_execution)
            
            # 阶段4: 智能结果整合
            await self._execute_stage_4(flow_execution)
            
            # 阶段5: 交付与学习
            await self._execute_stage_5(flow_execution, delivery_config)
            
            # 完成流程
            flow_execution.overall_status = FlowStatus.COMPLETED
            flow_execution.completed_at = datetime.now()
            flow_execution.total_execution_time = (
                flow_execution.completed_at - flow_execution.started_at
            ).total_seconds()
            
            # 更新统计信息
            self._update_flow_statistics(flow_execution, success=True)
            
            # 移动到已完成列表
            self.completed_flows.append(flow_execution)
            del self.active_flows[flow_id]
            
            logger.info(f"流程执行完成: {flow_id}, 总耗时: {flow_execution.total_execution_time:.2f}秒")
            
            return {
                "flow_id": flow_id,
                "status": "success",
                "result": flow_execution.final_result,
                "execution_summary": self._generate_execution_summary(flow_execution),
                "metadata": {
                    "total_execution_time": flow_execution.total_execution_time,
                    "stages_completed": len(flow_execution.stage_results),
                    "completed_at": flow_execution.completed_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"流程执行失败: {flow_id}, 错误: {str(e)}")
            
            # 标记为失败
            flow_execution.overall_status = FlowStatus.FAILED
            flow_execution.completed_at = datetime.now()
            flow_execution.total_execution_time = (
                flow_execution.completed_at - flow_execution.started_at
            ).total_seconds()
            
            # 更新统计信息
            self._update_flow_statistics(flow_execution, success=False)
            
            # 移动到已完成列表
            self.completed_flows.append(flow_execution)
            del self.active_flows[flow_id]
            
            return {
                "flow_id": flow_id,
                "status": "failed",
                "error": str(e),
                "partial_results": self._collect_partial_results(flow_execution),
                "execution_summary": self._generate_execution_summary(flow_execution)
            }
    
    async def _execute_stage_1(self, flow_execution: FlowExecution, context: Dict[str, Any]):
        """执行阶段1: 智能输入处理"""
        logger.info(f"流程{flow_execution.flow_id}: 开始阶段1 - 智能输入处理")
        
        stage_start = datetime.now()
        flow_execution.current_stage = FlowStage.INPUT_PROCESSING
        
        try:
            # 调用输入处理器
            processing_plan = await self.input_processor.process_user_request(
                flow_execution.user_input, context
            )
            
            flow_execution.processing_plan = processing_plan
            
            # 记录阶段结果
            stage_result = StageResult(
                stage=FlowStage.INPUT_PROCESSING,
                status=FlowStatus.COMPLETED,
                result=processing_plan,
                started_at=stage_start,
                completed_at=datetime.now()
            )
            stage_result.execution_time = (stage_result.completed_at - stage_result.started_at).total_seconds()
            
            flow_execution.stage_results[FlowStage.INPUT_PROCESSING] = stage_result
            
            logger.info(f"流程{flow_execution.flow_id}: 阶段1完成, 意图: {processing_plan.intent.intent_type.value}")
            
        except Exception as e:
            logger.error(f"流程{flow_execution.flow_id}: 阶段1失败 - {str(e)}")
            
            stage_result = StageResult(
                stage=FlowStage.INPUT_PROCESSING,
                status=FlowStatus.FAILED,
                result=None,
                started_at=stage_start,
                completed_at=datetime.now(),
                error=str(e)
            )
            
            flow_execution.stage_results[FlowStage.INPUT_PROCESSING] = stage_result
            raise
    
    async def _execute_stage_2(self, flow_execution: FlowExecution):
        """执行阶段2: Multi-Agent任务编排"""
        logger.info(f"流程{flow_execution.flow_id}: 开始阶段2 - Multi-Agent任务编排")
        
        stage_start = datetime.now()
        flow_execution.current_stage = FlowStage.TASK_ORCHESTRATION
        
        try:
            # 调用任务编排器
            execution_plan = await self.task_orchestrator.orchestrate_tasks(
                flow_execution.processing_plan
            )
            
            flow_execution.execution_plan = execution_plan
            
            # 记录阶段结果
            stage_result = StageResult(
                stage=FlowStage.TASK_ORCHESTRATION,
                status=FlowStatus.COMPLETED,
                result=execution_plan,
                started_at=stage_start,
                completed_at=datetime.now(),
                metrics={
                    "tasks_count": len(execution_plan.tasks),
                    "execution_batches": len(execution_plan.execution_order),
                    "estimated_duration": execution_plan.estimated_total_duration
                }
            )
            stage_result.execution_time = (stage_result.completed_at - stage_result.started_at).total_seconds()
            
            flow_execution.stage_results[FlowStage.TASK_ORCHESTRATION] = stage_result
            
            logger.info(f"流程{flow_execution.flow_id}: 阶段2完成, 任务数: {len(execution_plan.tasks)}")
            
        except Exception as e:
            logger.error(f"流程{flow_execution.flow_id}: 阶段2失败 - {str(e)}")
            
            stage_result = StageResult(
                stage=FlowStage.TASK_ORCHESTRATION,
                status=FlowStatus.FAILED,
                result=None,
                started_at=stage_start,
                completed_at=datetime.now(),
                error=str(e)
            )
            
            flow_execution.stage_results[FlowStage.TASK_ORCHESTRATION] = stage_result
            raise
    
    async def _execute_stage_3(self, flow_execution: FlowExecution):
        """执行阶段3: 并行Agent执行"""
        logger.info(f"流程{flow_execution.flow_id}: 开始阶段3 - 并行Agent执行")
        
        stage_start = datetime.now()
        flow_execution.current_stage = FlowStage.PARALLEL_EXECUTION
        
        try:
            # 调用并行执行引擎
            execution_results = await self.parallel_executor.execute_plan(
                flow_execution.execution_plan
            )
            
            flow_execution.execution_results = execution_results
            
            # 记录阶段结果
            stage_result = StageResult(
                stage=FlowStage.PARALLEL_EXECUTION,
                status=FlowStatus.COMPLETED,
                result=execution_results,
                started_at=stage_start,
                completed_at=datetime.now(),
                metrics={
                    "success_rate": execution_results.get("success_rate", 0),
                    "total_execution_time": execution_results.get("total_execution_time", 0),
                    "throughput": execution_results.get("throughput", 0),
                    "completed_tasks": execution_results.get("completed_tasks", 0),
                    "failed_tasks": execution_results.get("failed_tasks", 0)
                }
            )
            stage_result.execution_time = (stage_result.completed_at - stage_result.started_at).total_seconds()
            
            flow_execution.stage_results[FlowStage.PARALLEL_EXECUTION] = stage_result
            
            logger.info(f"流程{flow_execution.flow_id}: 阶段3完成, 成功率: {execution_results.get('success_rate', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"流程{flow_execution.flow_id}: 阶段3失败 - {str(e)}")
            
            stage_result = StageResult(
                stage=FlowStage.PARALLEL_EXECUTION,
                status=FlowStatus.FAILED,
                result=None,
                started_at=stage_start,
                completed_at=datetime.now(),
                error=str(e)
            )
            
            flow_execution.stage_results[FlowStage.PARALLEL_EXECUTION] = stage_result
            raise
    
    async def _execute_stage_4(self, flow_execution: FlowExecution):
        """执行阶段4: 智能结果整合"""
        logger.info(f"流程{flow_execution.flow_id}: 开始阶段4 - 智能结果整合")
        
        stage_start = datetime.now()
        flow_execution.current_stage = FlowStage.RESULT_INTEGRATION
        
        try:
            # 调用结果整合器
            integrated_result = await self.result_integrator.integrate_results(
                flow_execution.execution_results.get("execution_results", {})
            )
            
            flow_execution.integrated_result = integrated_result
            
            # 记录阶段结果
            stage_result = StageResult(
                stage=FlowStage.RESULT_INTEGRATION,
                status=FlowStatus.COMPLETED,
                result=integrated_result,
                started_at=stage_start,
                completed_at=datetime.now(),
                metrics={
                    "quality_score": integrated_result.quality_assessment.overall_score,
                    "conflicts_detected": len(integrated_result.conflicts_detected),
                    "conflicts_resolved": len([c for c in integrated_result.conflicts_resolved if c.resolved]),
                    "integration_completeness": integrated_result.integrated_content.get("metadata", {}).get("actual_completeness", 0)
                }
            )
            stage_result.execution_time = (stage_result.completed_at - stage_result.started_at).total_seconds()
            
            flow_execution.stage_results[FlowStage.RESULT_INTEGRATION] = stage_result
            
            logger.info(f"流程{flow_execution.flow_id}: 阶段4完成, 质量评分: {integrated_result.quality_assessment.overall_score}")
            
        except Exception as e:
            logger.error(f"流程{flow_execution.flow_id}: 阶段4失败 - {str(e)}")
            
            stage_result = StageResult(
                stage=FlowStage.RESULT_INTEGRATION,
                status=FlowStatus.FAILED,
                result=None,
                started_at=stage_start,
                completed_at=datetime.now(),
                error=str(e)
            )
            
            flow_execution.stage_results[FlowStage.RESULT_INTEGRATION] = stage_result
            raise
    
    async def _execute_stage_5(self, flow_execution: FlowExecution, delivery_config: Dict[str, Any]):
        """执行阶段5: 交付与学习"""
        logger.info(f"流程{flow_execution.flow_id}: 开始阶段5 - 交付与学习")
        
        stage_start = datetime.now()
        flow_execution.current_stage = FlowStage.DELIVERY_LEARNING
        
        try:
            # 准备执行上下文
            execution_context = {
                "flow_id": flow_execution.flow_id,
                "total_execution_time": (datetime.now() - flow_execution.started_at).total_seconds(),
                "user_input": flow_execution.user_input,
                "processing_plan": flow_execution.processing_plan,
                "execution_plan": flow_execution.execution_plan
            }
            
            # 调用交付学习引擎
            final_result = await self.delivery_learner.process_delivery_and_learning(
                flow_execution.integrated_result,
                delivery_config,
                execution_context
            )
            
            flow_execution.final_result = final_result
            
            # 记录阶段结果
            stage_result = StageResult(
                stage=FlowStage.DELIVERY_LEARNING,
                status=FlowStatus.COMPLETED,
                result=final_result,
                started_at=stage_start,
                completed_at=datetime.now(),
                metrics={
                    "delivery_status": final_result.get("delivery_status"),
                    "quality_gates_passed": final_result.get("quality_gates", {}).get("passed", 0),
                    "quality_gates_total": final_result.get("quality_gates", {}).get("total", 0),
                    "insights_count": final_result.get("learning_insights", {}).get("insights_count", 0),
                    "content_size": final_result.get("metadata", {}).get("content_size", 0)
                }
            )
            stage_result.execution_time = (stage_result.completed_at - stage_result.started_at).total_seconds()
            
            flow_execution.stage_results[FlowStage.DELIVERY_LEARNING] = stage_result
            
            logger.info(f"流程{flow_execution.flow_id}: 阶段5完成, 交付状态: {final_result.get('delivery_status')}")
            
        except Exception as e:
            logger.error(f"流程{flow_execution.flow_id}: 阶段5失败 - {str(e)}")
            
            stage_result = StageResult(
                stage=FlowStage.DELIVERY_LEARNING,
                status=FlowStatus.FAILED,
                result=None,
                started_at=stage_start,
                completed_at=datetime.now(),
                error=str(e)
            )
            
            flow_execution.stage_results[FlowStage.DELIVERY_LEARNING] = stage_result
            raise
    
    def _generate_execution_summary(self, flow_execution: FlowExecution) -> Dict[str, Any]:
        """生成执行摘要"""
        summary = {
            "flow_id": flow_execution.flow_id,
            "user_input": flow_execution.user_input,
            "overall_status": flow_execution.overall_status.value,
            "total_execution_time": flow_execution.total_execution_time,
            "stages_summary": {}
        }
        
        for stage, result in flow_execution.stage_results.items():
            summary["stages_summary"][stage.value] = {
                "status": result.status.value,
                "execution_time": result.execution_time,
                "error": result.error,
                "metrics": result.metrics
            }
        
        return summary
    
    def _collect_partial_results(self, flow_execution: FlowExecution) -> Dict[str, Any]:
        """收集部分结果"""
        partial_results = {}
        
        if flow_execution.processing_plan:
            partial_results["processing_plan"] = {
                "intent_type": flow_execution.processing_plan.intent.intent_type.value,
                "complexity": flow_execution.processing_plan.complexity.level.value,
                "execution_mode": flow_execution.processing_plan.execution_mode.value
            }
        
        if flow_execution.execution_plan:
            partial_results["execution_plan"] = {
                "tasks_count": len(flow_execution.execution_plan.tasks),
                "estimated_duration": flow_execution.execution_plan.estimated_total_duration
            }
        
        if flow_execution.execution_results:
            partial_results["execution_results"] = flow_execution.execution_results
        
        if flow_execution.integrated_result:
            partial_results["integrated_result"] = {
                "quality_score": flow_execution.integrated_result.quality_assessment.overall_score,
                "content_summary": flow_execution.integrated_result.integrated_content.get("summary")
            }
        
        return partial_results
    
    def _update_flow_statistics(self, flow_execution: FlowExecution, success: bool):
        """更新流程统计信息"""
        self.flow_statistics["total_flows"] += 1
        
        if success:
            self.flow_statistics["successful_flows"] += 1
        else:
            self.flow_statistics["failed_flows"] += 1
        
        # 更新平均执行时间
        total_flows = self.flow_statistics["total_flows"]
        current_avg = self.flow_statistics["average_execution_time"]
        new_avg = (current_avg * (total_flows - 1) + flow_execution.total_execution_time) / total_flows
        self.flow_statistics["average_execution_time"] = new_avg
        
        # 更新阶段性能统计
        for stage, result in flow_execution.stage_results.items():
            stage_stats = self.flow_statistics["stage_performance"][stage]
            stage_stats["count"] += 1
            stage_stats["total_time"] += result.execution_time
    
    def get_flow_status(self, flow_id: str) -> Dict[str, Any]:
        """获取流程状态"""
        if flow_id in self.active_flows:
            flow = self.active_flows[flow_id]
            return {
                "flow_id": flow_id,
                "status": flow.overall_status.value,
                "current_stage": flow.current_stage.value,
                "progress": len(flow.stage_results) / 5 * 100,  # 5个阶段
                "elapsed_time": (datetime.now() - flow.started_at).total_seconds(),
                "stages_completed": list(flow.stage_results.keys())
            }
        
        # 查找已完成的流程
        for flow in self.completed_flows:
            if flow.flow_id == flow_id:
                return {
                    "flow_id": flow_id,
                    "status": flow.overall_status.value,
                    "total_execution_time": flow.total_execution_time,
                    "completed_at": flow.completed_at.isoformat() if flow.completed_at else None,
                    "stages_completed": list(flow.stage_results.keys())
                }
        
        return {"error": f"Flow {flow_id} not found"}
    
    def get_flow_statistics(self) -> Dict[str, Any]:
        """获取流程统计信息"""
        stats = self.flow_statistics.copy()
        
        # 计算成功率
        if stats["total_flows"] > 0:
            stats["success_rate"] = stats["successful_flows"] / stats["total_flows"] * 100
        else:
            stats["success_rate"] = 0.0
        
        # 计算各阶段平均执行时间
        stage_avg_times = {}
        for stage, stage_stats in stats["stage_performance"].items():
            if stage_stats["count"] > 0:
                stage_avg_times[stage.value] = stage_stats["total_time"] / stage_stats["count"]
            else:
                stage_avg_times[stage.value] = 0.0
        
        stats["stage_average_times"] = stage_avg_times
        
        return stats

# 工厂函数
def create_flow_engine(claude_service: ClaudeService, flow_config: Dict[str, Any] = None) -> FlowEngine:
    """创建流程引擎"""
    return FlowEngine(claude_service, flow_config)

# 使用示例
async def demo_flow_engine():
    """演示流程引擎"""
    from ..claude_integration import create_claude_service
    
    claude_service = create_claude_service()
    
    # 创建流程引擎
    flow_engine = create_flow_engine(claude_service, {
        "max_concurrent_agents": 3
    })
    
    # 测试用户输入
    test_inputs = [
        "开发一个用户管理系统，包含注册、登录和权限管理功能",
        "设计一个电商网站的推荐算法",
        "创建一个项目管理工具的技术架构"
    ]
    
    for i, user_input in enumerate(test_inputs):
        print(f"\n=== 测试 {i+1}: {user_input} ===")
        
        # 执行流程
        result = await flow_engine.execute_flow(
            user_input=user_input,
            context={"user_id": f"test_user_{i}"},
            delivery_config={"format": "json", "channel": "api_response"}
        )
        
        print(f"流程ID: {result['flow_id']}")
        print(f"执行状态: {result['status']}")
        
        if result['status'] == 'success':
            print(f"总执行时间: {result['metadata']['total_execution_time']:.2f}秒")
            print(f"完成阶段数: {result['metadata']['stages_completed']}")
            
            # 显示交付结果
            delivery_content = result['result'].get('delivery_content', {})
            if 'content' in delivery_content and 'summary' in delivery_content['content']:
                print(f"结果摘要: {delivery_content['content']['summary']}")
        else:
            print(f"执行失败: {result.get('error')}")
    
    # 显示统计信息
    print(f"\n=== 流程引擎统计 ===")
    stats = flow_engine.get_flow_statistics()
    print(f"总流程数: {stats['total_flows']}")
    print(f"成功率: {stats['success_rate']:.1f}%")
    print(f"平均执行时间: {stats['average_execution_time']:.2f}秒")

if __name__ == "__main__":
    asyncio.run(demo_flow_engine())
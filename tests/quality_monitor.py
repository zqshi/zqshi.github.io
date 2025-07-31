"""
AI系统质量监控工具
实时质量指标收集、分析和报警
"""

import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
import statistics


class QualityLevel(Enum):
    """质量等级"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"           # 良好  
    ACCEPTABLE = "acceptable"  # 可接受
    POOR = "poor"           # 差
    CRITICAL = "critical"   # 严重


@dataclass
class QualityMetric:
    """质量指标数据结构"""
    timestamp: datetime
    metric_type: str  # response_time, confidence_score, success_rate, etc.
    value: float
    context: Dict[str, Any]  # 上下文信息
    quality_level: QualityLevel


@dataclass
class QualityAlert:
    """质量警报数据结构"""
    timestamp: datetime
    alert_type: str
    severity: str  # low, medium, high, critical
    message: str
    metric_data: Dict[str, Any]
    suggested_actions: List[str]


class QualityDatabase:
    """质量数据存储"""
    
    def __init__(self, db_path: str = "quality_metrics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    quality_level TEXT NOT NULL,
                    context TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_data TEXT NOT NULL,
                    suggested_actions TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON quality_metrics(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_type 
                ON quality_metrics(metric_type)
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def save_metric(self, metric: QualityMetric):
        """保存质量指标"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO quality_metrics 
                (timestamp, metric_type, value, quality_level, context)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metric.timestamp.isoformat(),
                metric.metric_type,
                metric.value,
                metric.quality_level.value,
                json.dumps(metric.context)
            ))
            conn.commit()
        finally:
            conn.close()
    
    def save_alert(self, alert: QualityAlert):
        """保存质量警报"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO quality_alerts 
                (timestamp, alert_type, severity, message, metric_data, suggested_actions)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert.timestamp.isoformat(),
                alert.alert_type,
                alert.severity,
                alert.message,
                json.dumps(alert.metric_data),
                json.dumps(alert.suggested_actions)
            ))
            conn.commit()
        finally:
            conn.close()
    
    def get_metrics(self, metric_type: str = None, 
                   start_time: datetime = None, 
                   end_time: datetime = None) -> List[QualityMetric]:
        """获取质量指标数据"""
        conn = sqlite3.connect(self.db_path)
        try:
            query = "SELECT timestamp, metric_type, value, quality_level, context FROM quality_metrics WHERE 1=1"
            params = []
            
            if metric_type:
                query += " AND metric_type = ?"
                params.append(metric_type)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            metrics = []
            for row in rows:
                metrics.append(QualityMetric(
                    timestamp=datetime.fromisoformat(row[0]),
                    metric_type=row[1],
                    value=row[2],
                    quality_level=QualityLevel(row[3]),
                    context=json.loads(row[4])
                ))
            
            return metrics
        finally:
            conn.close()


class QualityThresholds:
    """质量阈值配置"""
    
    def __init__(self):
        self.thresholds = {
            "response_time": {
                QualityLevel.EXCELLENT: 1.0,
                QualityLevel.GOOD: 3.0,
                QualityLevel.ACCEPTABLE: 5.0,
                QualityLevel.POOR: 8.0,
                QualityLevel.CRITICAL: float('inf')
            },
            "confidence_score": {
                QualityLevel.EXCELLENT: 0.9,
                QualityLevel.GOOD: 0.8,
                QualityLevel.ACCEPTABLE: 0.7,
                QualityLevel.POOR: 0.6,
                QualityLevel.CRITICAL: 0.0
            },
            "success_rate": {
                QualityLevel.EXCELLENT: 0.99,
                QualityLevel.GOOD: 0.95,
                QualityLevel.ACCEPTABLE: 0.9,
                QualityLevel.POOR: 0.8,
                QualityLevel.CRITICAL: 0.0
            },
            "token_efficiency": {  # tokens per useful content length
                QualityLevel.EXCELLENT: 2.0,
                QualityLevel.GOOD: 3.0,
                QualityLevel.ACCEPTABLE: 4.0,
                QualityLevel.POOR: 6.0,
                QualityLevel.CRITICAL: float('inf')
            }
        }
    
    def evaluate_quality(self, metric_type: str, value: float) -> QualityLevel:
        """评估质量等级"""
        if metric_type not in self.thresholds:
            return QualityLevel.ACCEPTABLE
        
        thresholds = self.thresholds[metric_type]
        
        # 对于响应时间和token效率，值越小越好
        if metric_type in ["response_time", "token_efficiency"]:
            for level in [QualityLevel.EXCELLENT, QualityLevel.GOOD, 
                         QualityLevel.ACCEPTABLE, QualityLevel.POOR]:
                if value <= thresholds[level]:
                    return level
            return QualityLevel.CRITICAL
        
        # 对于置信度和成功率，值越大越好
        else:
            for level in [QualityLevel.EXCELLENT, QualityLevel.GOOD, 
                         QualityLevel.ACCEPTABLE, QualityLevel.POOR]:
                if value >= thresholds[level]:
                    return level
            return QualityLevel.CRITICAL
    
    def get_threshold(self, metric_type: str, level: QualityLevel) -> float:
        """获取特定质量等级的阈值"""
        return self.thresholds.get(metric_type, {}).get(level, 0.0)


class QualityAnalyzer:
    """质量分析器"""
    
    def __init__(self, db: QualityDatabase, thresholds: QualityThresholds):
        self.db = db
        self.thresholds = thresholds
        self.logger = logging.getLogger(__name__)
    
    def analyze_trend(self, metric_type: str, time_window: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """分析质量趋势"""
        end_time = datetime.now()
        start_time = end_time - time_window
        
        metrics = self.db.get_metrics(metric_type, start_time, end_time)
        
        if len(metrics) < 2:
            return {"status": "insufficient_data", "count": len(metrics)}
        
        values = [m.value for m in metrics]
        timestamps = [m.timestamp for m in metrics]
        
        # 计算趋势
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        trend_percentage = (second_avg - first_avg) / first_avg * 100 if first_avg > 0 else 0
        
        # 判断趋势方向
        if abs(trend_percentage) < 5:
            trend_direction = "stable"
        elif trend_percentage > 0:
            trend_direction = "increasing" if metric_type in ["confidence_score", "success_rate"] else "degrading"
        else:
            trend_direction = "decreasing" if metric_type in ["confidence_score", "success_rate"] else "improving"
        
        return {
            "metric_type": metric_type,
            "time_window": str(time_window),
            "sample_count": len(metrics),
            "current_avg": statistics.mean(values),
            "trend_percentage": trend_percentage,
            "trend_direction": trend_direction,
            "first_half_avg": first_avg,
            "second_half_avg": second_avg,
            "min_value": min(values),
            "max_value": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }
    
    def detect_anomalies(self, metric_type: str, time_window: timedelta = timedelta(minutes=30)) -> List[QualityMetric]:
        """检测质量异常"""
        end_time = datetime.now()
        start_time = end_time - time_window
        
        metrics = self.db.get_metrics(metric_type, start_time, end_time)
        
        if len(metrics) < 10:  # 需要足够的数据点
            return []
        
        values = [m.value for m in metrics]
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0
        
        # 使用3-sigma规则检测异常
        anomalies = []
        for metric in metrics:
            if std_val > 0:
                z_score = abs(metric.value - mean_val) / std_val
                if z_score > 3:  # 3-sigma异常
                    anomalies.append(metric)
        
        return anomalies
    
    def generate_quality_report(self, time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """生成质量报告"""
        end_time = datetime.now()
        start_time = end_time - time_window
        
        report = {
            "report_time": end_time.isoformat(),
            "time_window": str(time_window),
            "metrics_summary": {},
            "trends": {},
            "anomalies": {},
            "alerts": [],
            "overall_health": "unknown"
        }
        
        # 分析各类指标
        metric_types = ["response_time", "confidence_score", "success_rate", "token_efficiency"]
        
        for metric_type in metric_types:
            metrics = self.db.get_metrics(metric_type, start_time, end_time)
            
            if not metrics:
                continue
            
            values = [m.value for m in metrics]
            
            report["metrics_summary"][metric_type] = {
                "count": len(metrics),
                "average": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0
            }
            
            # 趋势分析
            report["trends"][metric_type] = self.analyze_trend(metric_type, time_window)
            
            # 异常检测
            anomalies = self.detect_anomalies(metric_type, time_window)
            if anomalies:
                report["anomalies"][metric_type] = len(anomalies)
        
        # 计算整体健康度
        report["overall_health"] = self._calculate_overall_health(report)
        
        return report
    
    def _calculate_overall_health(self, report: Dict[str, Any]) -> str:
        """计算整体健康度"""
        if not report["metrics_summary"]:
            return "unknown"
        
        health_scores = []
        
        # 基于各指标的表现评分
        for metric_type, summary in report["metrics_summary"].items():
            avg_value = summary["average"]
            quality_level = self.thresholds.evaluate_quality(metric_type, avg_value)
            
            # 转换为数值分数
            score_map = {
                QualityLevel.EXCELLENT: 100,
                QualityLevel.GOOD: 80,
                QualityLevel.ACCEPTABLE: 60,
                QualityLevel.POOR: 40,
                QualityLevel.CRITICAL: 20
            }
            health_scores.append(score_map[quality_level])
        
        if not health_scores:
            return "unknown"
        
        overall_score = statistics.mean(health_scores)
        
        if overall_score >= 90:
            return "excellent"
        elif overall_score >= 75:
            return "good"
        elif overall_score >= 60:
            return "acceptable"
        elif overall_score >= 40:
            return "poor"
        else:
            return "critical"


class QualityMonitor:
    """质量监控器主类"""
    
    def __init__(self, db_path: str = "quality_metrics.db"):
        self.db = QualityDatabase(db_path)
        self.thresholds = QualityThresholds()
        self.analyzer = QualityAnalyzer(self.db, self.thresholds)
        self.alert_handlers = []
        self.logger = logging.getLogger(__name__)
        
        # 监控配置
        self.monitoring_enabled = True
        self.alert_cooldown = {}  # 避免重复报警
        self.cooldown_period = timedelta(minutes=15)
    
    def add_alert_handler(self, handler):
        """添加警报处理器"""
        self.alert_handlers.append(handler)
    
    def record_metric(self, metric_type: str, value: float, context: Dict[str, Any] = None):
        """记录质量指标"""
        if not self.monitoring_enabled:
            return
        
        timestamp = datetime.now()
        context = context or {}
        
        # 评估质量等级
        quality_level = self.thresholds.evaluate_quality(metric_type, value)
        
        # 创建指标记录
        metric = QualityMetric(
            timestamp=timestamp,
            metric_type=metric_type,
            value=value,
            context=context,
            quality_level=quality_level
        )
        
        # 保存到数据库
        self.db.save_metric(metric)
        
        # 检查是否需要发出警报
        self._check_alert_conditions(metric)
        
        self.logger.debug(f"记录质量指标: {metric_type}={value} ({quality_level.value})")
    
    def _check_alert_conditions(self, metric: QualityMetric):
        """检查警报条件"""
        
        # 严重质量问题立即报警
        if metric.quality_level in [QualityLevel.POOR, QualityLevel.CRITICAL]:
            self._trigger_alert(
                alert_type="quality_degradation",
                severity="high" if metric.quality_level == QualityLevel.POOR else "critical",
                message=f"{metric.metric_type}质量{metric.quality_level.value}: {metric.value}",
                metric_data=asdict(metric),
                suggested_actions=self._get_suggested_actions(metric)
            )
        
        # 检查趋势警报
        trend_analysis = self.analyzer.analyze_trend(metric.metric_type, timedelta(minutes=30))
        
        if trend_analysis.get("trend_direction") == "degrading" and abs(trend_analysis.get("trend_percentage", 0)) > 20:
            self._trigger_alert(
                alert_type="quality_trend_degradation",
                severity="medium",
                message=f"{metric.metric_type}质量呈下降趋势: {trend_analysis['trend_percentage']:.1f}%",
                metric_data=trend_analysis,
                suggested_actions=["检查系统负载", "验证AI服务状态", "分析最近的代码变更"]
            )
    
    def _trigger_alert(self, alert_type: str, severity: str, message: str, 
                      metric_data: Dict[str, Any], suggested_actions: List[str]):
        """触发警报"""
        
        # 检查冷却期，避免重复报警
        alert_key = f"{alert_type}_{severity}"
        now = datetime.now()
        
        if alert_key in self.alert_cooldown:
            if now - self.alert_cooldown[alert_key] < self.cooldown_period:
                return  # 在冷却期内，跳过报警
        
        self.alert_cooldown[alert_key] = now
        
        # 创建警报
        alert = QualityAlert(
            timestamp=now,
            alert_type=alert_type,
            severity=severity,
            message=message,
            metric_data=metric_data,
            suggested_actions=suggested_actions
        )
        
        # 保存警报
        self.db.save_alert(alert)
        
        # 通知警报处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"警报处理器错误: {e}")
        
        self.logger.warning(f"质量警报: {alert_type} - {message}")
    
    def _get_suggested_actions(self, metric: QualityMetric) -> List[str]:
        """获取建议的修复行动"""
        actions_map = {
            "response_time": [
                "检查AI服务响应延迟",
                "验证网络连接状态",
                "考虑增加服务器资源",
                "优化请求批处理"
            ],
            "confidence_score": [
                "检查输入数据质量",
                "验证prompt模板",
                "考虑调整模型参数",
                "分析失败案例"
            ],
            "success_rate": [
                "检查错误日志",
                "验证API密钥和配额",
                "测试备用服务",
                "检查输入验证逻辑"
            ],
            "token_efficiency": [
                "优化prompt长度",
                "检查响应格式",
                "考虑使用更小的模型",
                "实施响应缓存"
            ]
        }
        
        return actions_map.get(metric.metric_type, ["联系技术支持", "查看系统日志"])
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控仪表板数据"""
        report = self.analyzer.generate_quality_report(timedelta(hours=24))
        
        # 添加实时状态
        recent_metrics = {}
        for metric_type in ["response_time", "confidence_score", "success_rate"]:
            metrics = self.db.get_metrics(metric_type, datetime.now() - timedelta(minutes=5))
            if metrics:
                recent_metrics[metric_type] = {
                    "current_value": metrics[0].value,
                    "quality_level": metrics[0].quality_level.value,
                    "sample_count": len(metrics)
                }
        
        return {
            "real_time_status": recent_metrics,
            "daily_report": report,
            "system_health": report["overall_health"]
        }


# 便捷的全局监控器实例
global_quality_monitor = QualityMonitor()


def simple_alert_handler(alert: QualityAlert):
    """简单的控制台警报处理器"""
    print(f"\n🚨 质量警报 [{alert.severity.upper()}] - {alert.timestamp}")
    print(f"类型: {alert.alert_type}")
    print(f"消息: {alert.message}")
    print("建议行动:")
    for action in alert.suggested_actions:
        print(f"  - {action}")
    print("-" * 50)


# 注册默认警报处理器
global_quality_monitor.add_alert_handler(simple_alert_handler)


# 便捷函数
def record_response_time(value: float, context: Dict[str, Any] = None):
    """记录响应时间"""
    global_quality_monitor.record_metric("response_time", value, context)


def record_confidence_score(value: float, context: Dict[str, Any] = None):
    """记录置信度分数"""
    global_quality_monitor.record_metric("confidence_score", value, context)


def record_success_rate(value: float, context: Dict[str, Any] = None):
    """记录成功率"""
    global_quality_monitor.record_metric("success_rate", value, context)


def get_quality_dashboard():
    """获取质量仪表板数据"""
    return global_quality_monitor.get_dashboard_data()


if __name__ == "__main__":
    # 示例用法
    monitor = QualityMonitor()
    
    # 模拟一些质量数据
    import random
    for i in range(100):
        monitor.record_metric("response_time", random.uniform(0.5, 3.0))
        monitor.record_metric("confidence_score", random.uniform(0.6, 0.95))
        monitor.record_metric("success_rate", random.uniform(0.85, 1.0))
    
    # 生成报告
    dashboard = monitor.get_dashboard_data()
    print(json.dumps(dashboard, indent=2, default=str))
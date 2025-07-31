"""
配置管理
支持环境变量和配置文件
"""

import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = {
            # 基础配置
            "app": {
                "name": "数字员工系统",
                "version": "0.2.0",
                "debug": os.getenv("DEBUG", "false").lower() == "true",
                "host": os.getenv("HOST", "0.0.0.0"),
                "port": int(os.getenv("PORT", "8000"))
            },
            
            # AI服务配置
            "ai": {
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
                },
                "anthropic": {
                    "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
                },
                "default_temperature": float(os.getenv("AI_TEMPERATURE", "0.7")),
                "default_max_tokens": int(os.getenv("AI_MAX_TOKENS", "2000"))
            },
            
            # 数据库配置
            "database": {
                "url": os.getenv("DATABASE_URL", "sqlite:///./digital_employee.db"),
                "echo": os.getenv("DB_ECHO", "false").lower() == "true",
                "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10"))
            },
            
            # Redis配置
            "redis": {
                "url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                "password": os.getenv("REDIS_PASSWORD"),
                "decode_responses": True
            },
            
            # 缓存配置
            "cache": {
                "enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
                "ttl": int(os.getenv("CACHE_TTL", "3600")),  # 1小时
                "max_size": int(os.getenv("CACHE_MAX_SIZE", "100"))
            },
            
            # 日志配置
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                "file": os.getenv("LOG_FILE", "logs/app.log"),
                "max_bytes": int(os.getenv("LOG_MAX_BYTES", "10485760")),  # 10MB
                "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
            },
            
            # 监控配置
            "monitoring": {
                "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
                "metrics_endpoint": "/metrics",
                "health_endpoint": "/health"
            },
            
            # 安全配置
            "security": {
                "cors_origins": os.getenv("CORS_ORIGINS", "*").split(","),
                "rate_limit_enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
                "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
            }
        }
        
        return config
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置"""
        return self.config.get("ai", {})
    
    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.config["database"]["url"]
    
    def is_debug(self) -> bool:
        """是否为调试模式"""
        return self.config["app"]["debug"]


# 全局配置实例
config = Config()


def setup_logging():
    """设置日志配置"""
    import logging
    import logging.handlers
    from pathlib import Path
    
    log_config = config.get("logging")
    
    # 创建日志目录
    log_file = Path(log_config["file"])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, log_config["level"]),
        format=log_config["format"],
        handlers=[
            # 控制台输出
            logging.StreamHandler(),
            # 文件输出（带滚动）
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=log_config["max_bytes"],
                backupCount=log_config["backup_count"],
                encoding='utf-8'
            )
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 检查AI服务配置
    ai_config = config.get_ai_config()
    if not ai_config.get("openai", {}).get("api_key") and not ai_config.get("anthropic", {}).get("api_key"):
        errors.append("至少需要配置一个AI服务的API密钥")
    
    # 检查数据库配置
    db_url = config.get_database_url()
    if not db_url:
        errors.append("数据库URL不能为空")
    
    if errors:
        raise ValueError(f"配置验证失败：{'; '.join(errors)}")
    
    return True
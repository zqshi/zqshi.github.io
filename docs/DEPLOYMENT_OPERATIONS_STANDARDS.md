# 数字员工系统部署和运维规范

## 🎯 运维理念

### 核心原则
- **渐进式部署**：从本地开发到生产环境的平滑过渡
- **监控优先**：每个组件都有完整的监控覆盖
- **自动化运维**：减少人工操作，提高可靠性
- **故障自愈**：系统具备自动恢复能力
- **成本优化**：在性能和成本之间找到最佳平衡

### AI系统运维特点
- **外部依赖重**：高度依赖第三方AI服务
- **性能波动大**：AI响应时间不稳定
- **成本敏感**：Token使用直接影响运营成本
- **质量监控复杂**：需要监控AI响应质量

---

## 🏗️ 部署架构设计

### 环境分层策略
```
开发环境 (Development) → 测试环境 (Testing) → 预发环境 (Staging) → 生产环境 (Production)
```

#### 环境配置对比
| 组件 | 开发环境 | 测试环境 | 预发环境 | 生产环境 |
|------|----------|----------|----------|----------|
| **AI服务** | Mock/Sandbox | Sandbox | 生产API | 生产API |
| **数据库** | SQLite | PostgreSQL | PostgreSQL | PostgreSQL集群 |
| **缓存** | 内存 | Redis单实例 | Redis单实例 | Redis集群 |
| **负载均衡** | 无 | 无 | Nginx | Nginx+Keepalived |
| **监控** | 基础日志 | 基础监控 | 完整监控 | 完整监控+告警 |
| **容器化** | Docker | Docker | Docker | Kubernetes |

### 部署架构图
```
                    ┌─────────────────────────────────────┐
                    │              负载均衡层              │
                    │     Nginx + SSL终端 + 限流         │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │              应用层                 │
                    │  FastAPI服务集群 (3个实例)         │
                    │  ├─ Agent Runtime                   │
                    │  ├─ AI Service Layer                │
                    │  └─ Task Orchestrator               │
                    └─────────────────┬───────────────────┘
                                      │
    ┌─────────────────────────────────┼─────────────────────────────────┐
    │                                 │                                 │
┌───┴──────────────────┐    ┌────────┴────────┐    ┌──────────────────┴───┐
│      数据层          │    │    缓存层       │    │      外部服务层       │
│  PostgreSQL主从      │    │  Redis集群      │    │  OpenAI/Claude API   │
│  ├─ 主库(写)        │    │  ├─ 会话缓存    │    │  ├─ 多厂商备份        │
│  ├─ 从库(读)        │    │  ├─ 结果缓存    │    │  ├─ 限流和重试        │
│  └─ 备份存储        │    │  └─ 队列存储    │    │  └─ 健康检查          │
└─────────────────────┘    └─────────────────┘    └──────────────────────┘
```

---

## 🐳 容器化部署规范

### Dockerfile规范
```dockerfile
# 生产环境Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY requirements-prod.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements-prod.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["gunicorn", "run_server:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Docker Compose配置
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - DATABASE_URL=postgresql://user:${DB_PASSWORD}@db:5432/digital_employee
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    depends_on:
      - db
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - app
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: digital_employee
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    ports:
      - "5432:5432"
    command: >
      postgres
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: unless-stopped
    ports:
      - "6379:6379"

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge
```

---

## ☸️ Kubernetes部署规范

### Namespace配置
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: digital-employee
  labels:
    app.kubernetes.io/name: digital-employee
    app.kubernetes.io/version: "1.0.0"
```

### ConfigMap配置
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: digital-employee-config
  namespace: digital-employee
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  DB_HOST: "postgresql-service"
  DB_PORT: "5432"
  DB_NAME: "digital_employee"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  
  # AI服务配置
  AI_SERVICE_TIMEOUT: "30"
  AI_SERVICE_RETRY_COUNT: "3"
  AI_SERVICE_RETRY_DELAY: "2"
  
  # 监控配置
  PROMETHEUS_METRICS_PORT: "9000"
  HEALTH_CHECK_INTERVAL: "30"
```

### Secret配置
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: digital-employee-secrets
  namespace: digital-employee
type: Opaque
data:
  DB_PASSWORD: <base64-encoded-password>
  OPENAI_API_KEY: <base64-encoded-api-key>
  CLAUDE_API_KEY: <base64-encoded-api-key>
  JWT_SECRET_KEY: <base64-encoded-jwt-secret>
```

### Deployment配置
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-employee-app
  namespace: digital-employee
  labels:
    app: digital-employee
    version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: digital-employee
  template:
    metadata:
      labels:
        app: digital-employee
        version: "1.0.0"
    spec:
      containers:
      - name: app
        image: digital-employee:1.0.0
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9000
          name: metrics
        
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: digital-employee-secrets
              key: DB_PASSWORD
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: digital-employee-secrets
              key: OPENAI_API_KEY
        
        envFrom:
        - configMapRef:
            name: digital-employee-config
        
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 2Gi
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      
      terminationGracePeriodSeconds: 30
      
      # 反亲和性确保Pod分布在不同节点
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - digital-employee
              topologyKey: kubernetes.io/hostname
```

### Service配置
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: digital-employee-service
  namespace: digital-employee
  labels:
    app: digital-employee
spec:
  selector:
    app: digital-employee
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9000
    targetPort: 9000
  type: ClusterIP
```

### Ingress配置
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: digital-employee-ingress
  namespace: digital-employee
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.digital-employee.example.com
    secretName: digital-employee-tls
  rules:
  - host: api.digital-employee.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: digital-employee-service
            port:
              number: 80
```

---

## 📊 监控和可观测性

### Prometheus监控配置
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'digital-employee'
    static_configs:
      - targets: ['app:9000']
    metrics_path: /metrics
    scrape_interval: 30s
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis_exporter:9121']
    
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx_exporter:9113']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 告警规则配置
```yaml
# monitoring/alert_rules.yml
groups:
- name: digital_employee_alerts
  rules:
  
  # 服务可用性告警
  - alert: ServiceDown
    expr: up{job="digital-employee"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "数字员工服务宕机"
      description: "{{ $labels.instance }} 服务已宕机超过1分钟"
  
  # 响应时间告警
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 10
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "响应时间过高"
      description: "95%请求响应时间超过10秒，当前值: {{ $value }}秒"
  
  # AI服务错误率告警
  - alert: HighAIServiceErrorRate
    expr: rate(ai_requests_total{status="error"}[5m]) / rate(ai_requests_total[5m]) > 0.05
    for: 3m
    labels:
      severity: warning
    annotations:
      summary: "AI服务错误率过高"
      description: "AI服务错误率超过5%，当前值: {{ $value | humanizePercentage }}"
  
  # Token使用量告警
  - alert: HighTokenUsage
    expr: increase(ai_tokens_used_total[1h]) > 100000
    for: 0m
    labels:
      severity: warning
    annotations:
      summary: "Token使用量过高"
      description: "过去1小时Token使用量: {{ $value }}"
  
  # 数据库连接告警
  - alert: DatabaseConnectionsHigh
    expr: postgres_stat_database_numbackends > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "数据库连接数过高"
      description: "数据库连接数: {{ $value }}/100"
  
  # 内存使用告警
  - alert: HighMemoryUsage
    expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "内存使用率过高"
      description: "容器内存使用率: {{ $value | humanizePercentage }}"
```

### Grafana仪表板配置
```json
{
  "dashboard": {
    "id": null,
    "title": "数字员工系统监控",
    "tags": ["digital-employee"],
    "timezone": "browser",
    "panels": [
      {
        "title": "服务概览",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"digital-employee\"}",
            "legendFormat": "服务状态"
          }
        ]
      },
      {
        "title": "请求QPS",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "响应时间分布",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P99"
          }
        ]
      },
      {
        "title": "AI服务调用",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ai_requests_total[5m])",
            "legendFormat": "{{service}} {{status}}"
          }
        ]
      },
      {
        "title": "Token使用量",
        "type": "graph",
        "targets": [
          {
            "expr": "increase(ai_tokens_used_total[1h])",
            "legendFormat": "{{service}} {{model}}"
          }
        ]
      }
    ]
  }
}
```

---

## 🔐 安全配置规范

### SSL/TLS配置
```nginx
# nginx/ssl.conf
server {
    listen 443 ssl http2;
    server_name api.digital-employee.example.com;
    
    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # 代理配置
    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### 应用安全配置
```python
# config/security.py
from functools import wraps
import jwt
import time
from typing import Optional

class SecurityConfig:
    """安全配置类"""
    
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = "HS256"
        self.jwt_expiration = 3600  # 1小时
        self.rate_limit_requests = 100
        self.rate_limit_window = 60  # 1分钟
        
        # API密钥白名单
        self.api_key_whitelist = set(os.getenv("API_KEY_WHITELIST", "").split(","))
        
        # 敏感信息过滤
        self.sensitive_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # 信用卡号
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        ]

def require_api_key(f):
    """API密钥验证装饰器"""
    @wraps(f)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request') or args[0]
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key not in security_config.api_key_whitelist:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        return await f(*args, **kwargs)
    return wrapper

def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """频率限制装饰器"""
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request') or args[0]
            client_ip = request.client.host
            
            # 检查频率限制
            if not check_rate_limit(client_ip, max_requests, window_seconds):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            return await f(*args, **kwargs)
        return wrapper
    return decorator

def check_rate_limit(client_ip: str, max_requests: int, window_seconds: int) -> bool:
    """检查频率限制"""
    current_time = int(time.time())
    window_start = current_time - window_seconds
    
    # 使用Redis实现滑动窗口频率限制
    redis_key = f"rate_limit:{client_ip}"
    
    # 清理过期记录
    redis_client.zremrangebyscore(redis_key, 0, window_start)
    
    # 检查当前请求数
    current_requests = redis_client.zcard(redis_key)
    
    if current_requests >= max_requests:
        return False
    
    # 记录当前请求
    redis_client.zadd(redis_key, {str(current_time): current_time})
    redis_client.expire(redis_key, window_seconds)
    
    return True
```

---

## 🗄️ 数据备份和恢复

### 数据库备份策略
```bash
#!/bin/bash
# scripts/backup_database.sh

set -e

# 配置
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-digital_employee}
DB_USER=${DB_USER:-user}
BACKUP_DIR=${BACKUP_DIR:-/backups}
RETENTION_DAYS=${RETENTION_DAYS:-7}

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

echo "开始数据库备份: $BACKUP_FILE"

# 执行备份
PGPASSWORD=$DB_PASSWORD pg_dump \
  -h $DB_HOST \
  -p $DB_PORT \
  -U $DB_USER \
  -d $DB_NAME \
  --no-password \
  --format=custom \
  --compress=9 \
  --verbose \
  | gzip > $BACKUP_FILE

# 验证备份文件
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    echo "数据库备份成功: $BACKUP_FILE"
    
    # 记录备份日志
    echo "$(date): Database backup completed - $BACKUP_FILE" >> $BACKUP_DIR/backup.log
    
    # 清理过期备份
    find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "清理超过 $RETENTION_DAYS 天的旧备份"
    
else
    echo "数据库备份失败!"
    exit 1
fi

# 可选：上传到云存储
if [ -n "$AWS_S3_BUCKET" ]; then
    aws s3 cp $BACKUP_FILE s3://$AWS_S3_BUCKET/backups/database/
    echo "备份已上传到S3: s3://$AWS_S3_BUCKET/backups/database/"
fi
```

### 数据恢复脚本
```bash
#!/bin/bash
# scripts/restore_database.sh

set -e

BACKUP_FILE=$1
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-digital_employee}
DB_USER=${DB_USER:-user}

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file>"
    echo "可用备份文件:"
    ls -la /backups/db_backup_*.sql.gz
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "警告: 此操作将覆盖数据库 $DB_NAME 的所有数据!"
read -p "确认继续? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 1
fi

echo "开始数据库恢复: $BACKUP_FILE"

# 停止应用服务
echo "停止应用服务..."
docker-compose stop app

# 恢复数据库
echo "恢复数据库..."
gunzip -c $BACKUP_FILE | PGPASSWORD=$DB_PASSWORD psql \
  -h $DB_HOST \
  -p $DB_PORT \
  -U $DB_USER \
  -d $DB_NAME

echo "数据库恢复完成"

# 重启应用服务
echo "重启应用服务..."
docker-compose start app

echo "数据恢复完成: $BACKUP_FILE"
```

### 自动备份Cron任务
```bash
# crontab配置
# 每天凌晨2点执行数据库备份
0 2 * * * /opt/digital-employee/scripts/backup_database.sh >> /var/log/backup.log 2>&1

# 每周日凌晨1点执行完整系统备份
0 1 * * 0 /opt/digital-employee/scripts/full_system_backup.sh >> /var/log/backup.log 2>&1

# 每小时检查系统健康状态
0 * * * * /opt/digital-employee/scripts/health_check.sh >> /var/log/health.log 2>&1
```

---

## 🚀 自动化部署流程

### CI/CD Pipeline配置
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=digital_employee --cov-report=xml
    
    - name: Security scan
      run: |
        bandit -r digital_employee/
        safety check
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}:latest
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment..."
        # 这里添加staging部署逻辑
    
    - name: Run integration tests
      run: |
        echo "Running integration tests on staging..."
        # 这里添加集成测试逻辑
    
    - name: Deploy to production
      if: success()
      run: |
        echo "Deploying to production environment..."
        # 这里添加生产环境部署逻辑
```

### 蓝绿部署脚本
```bash
#!/bin/bash
# scripts/blue_green_deploy.sh

set -e

NEW_VERSION=$1
CURRENT_ENV=$(kubectl get service digital-employee-service -o jsonpath='{.spec.selector.version}')

if [ -z "$NEW_VERSION" ]; then
    echo "用法: $0 <new_version>"
    exit 1
fi

echo "当前版本: $CURRENT_ENV"
echo "新版本: $NEW_VERSION"

# 确定新环境颜色
if [ "$CURRENT_ENV" = "blue" ]; then
    NEW_ENV="green"
else
    NEW_ENV="blue"
fi

echo "部署到 $NEW_ENV 环境..."

# 更新部署配置
kubectl set image deployment/digital-employee-$NEW_ENV-deployment \
    app=digital-employee:$NEW_VERSION \
    --namespace=digital-employee

# 等待部署完成
kubectl rollout status deployment/digital-employee-$NEW_ENV-deployment \
    --namespace=digital-employee \
    --timeout=600s

# 健康检查
echo "执行健康检查..."
for i in {1..30}; do
    if kubectl exec -n digital-employee \
        deployment/digital-employee-$NEW_ENV-deployment \
        -- curl -f http://localhost:8000/health; then
        echo "健康检查通过"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "健康检查失败，回滚部署"
        kubectl rollout undo deployment/digital-employee-$NEW_ENV-deployment \
            --namespace=digital-employee
        exit 1
    fi
    
    echo "等待服务就绪... ($i/30)"
    sleep 10
done

# 执行烟雾测试
echo "执行烟雾测试..."
if ! ./scripts/smoke_test.sh $NEW_ENV; then
    echo "烟雾测试失败，回滚部署"
    kubectl rollout undo deployment/digital-employee-$NEW_ENV-deployment \
        --namespace=digital-employee
    exit 1
fi

# 切换流量
echo "切换流量到 $NEW_ENV 环境..."
kubectl patch service digital-employee-service \
    -p '{"spec":{"selector":{"version":"'$NEW_ENV'"}}}' \
    --namespace=digital-employee

echo "部署完成，流量已切换到版本 $NEW_VERSION ($NEW_ENV 环境)"

# 可选：保留旧版本一段时间后清理
echo "旧版本 ($CURRENT_ENV) 将保留24小时后自动清理"
```

---

## 🔧 运维工具和脚本

### 系统健康检查脚本
```python
#!/usr/bin/env python3
# scripts/health_check.py

import asyncio
import aiohttp
import psutil
import redis
import psycopg2
from datetime import datetime
import json
import logging

class SystemHealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.results = {}
        self.logger = logging.getLogger(__name__)
    
    async def check_all(self):
        """执行所有健康检查"""
        checks = [
            self.check_application_health(),
            self.check_database_health(),
            self.check_redis_health(),
            self.check_ai_service_health(),
            self.check_system_resources(),
            self.check_disk_space(),
        ]
        
        results = await asyncio.gather(*checks, return_exceptions=True)
        
        # 汇总结果
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        check_names = [
            "application", "database", "redis", 
            "ai_service", "system_resources", "disk_space"
        ]
        
        for i, result in enumerate(results):
            check_name = check_names[i]
            if isinstance(result, Exception):
                health_status["checks"][check_name] = {
                    "status": "error",
                    "error": str(result)
                }
                health_status["overall_status"] = "unhealthy"
            else:
                health_status["checks"][check_name] = result
                if not result.get("healthy", False):
                    health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def check_application_health(self):
        """检查应用程序健康状态"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/health', timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "healthy": True,
                            "response_time": resp.headers.get('X-Response-Time', 'unknown'),
                            "version": data.get('version', 'unknown')
                        }
                    else:
                        return {
                            "healthy": False,
                            "error": f"HTTP {resp.status}"
                        }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def check_database_health(self):
        """检查数据库健康状态"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="digital_employee",
                user="user",
                password=os.getenv("DB_PASSWORD")
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            active_connections = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return {
                "healthy": True,
                "active_connections": active_connections,
                "max_connections": 100  # 从配置获取
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def check_redis_health(self):
        """检查Redis健康状态"""
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            info = r.info()
            
            return {
                "healthy": True,
                "used_memory": info['used_memory_human'],
                "connected_clients": info['connected_clients'],
                "uptime": info['uptime_in_seconds']
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def check_ai_service_health(self):
        """检查AI服务健康状态"""
        try:
            # 这里可以添加对OpenAI API的简单测试
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                }
                
                # 发送简单的API请求测试连通性
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                }
                
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=10
                ) as resp:
                    if resp.status in [200, 429]:  # 429是频率限制，但说明服务可用
                        return {
                            "healthy": True,
                            "api_status": "available"
                        }
                    else:
                        return {
                            "healthy": False,
                            "error": f"API returned {resp.status}"
                        }
                        
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def check_system_resources(self):
        """检查系统资源使用情况"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            load_avg = psutil.getloadavg()
            
            # 健康阈值
            cpu_threshold = 80
            memory_threshold = 80
            
            is_healthy = (
                cpu_percent < cpu_threshold and 
                memory.percent < memory_threshold
            )
            
            return {
                "healthy": is_healthy,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "load_average": load_avg,
                "warnings": [
                    f"High CPU usage: {cpu_percent}%" if cpu_percent >= cpu_threshold else None,
                    f"High memory usage: {memory.percent}%" if memory.percent >= memory_threshold else None
                ]
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def check_disk_space(self):
        """检查磁盘空间"""
        try:
            disk_usage = psutil.disk_usage('/')
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            # 磁盘空间阈值
            disk_threshold = 85
            
            return {
                "healthy": used_percent < disk_threshold,
                "used_percent": used_percent,
                "free_space_gb": disk_usage.free / (1024**3),
                "total_space_gb": disk_usage.total / (1024**3)
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }

async def main():
    """主函数"""
    checker = SystemHealthChecker()
    health_status = await checker.check_all()
    
    # 输出结果
    print(json.dumps(health_status, indent=2))
    
    # 如果不健康，退出码为1
    if health_status["overall_status"] != "healthy":
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

### 日志分析脚本
```python
#!/usr/bin/env python3
# scripts/log_analyzer.py

import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import argparse

class LogAnalyzer:
    """日志分析工具"""
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.patterns = {
            'timestamp': r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
            'level': r'"level":\s*"(\w+)"',
            'message': r'"message":\s*"([^"]+)"',
            'response_time': r'"response_time":\s*([0-9.]+)',
            'status_code': r'"status_code":\s*(\d+)',
            'ai_tokens': r'"ai_tokens_used":\s*(\d+)',
            'error': r'"error":\s*"([^"]+)"'
        }
    
    def analyze_logs(self, hours=24):
        """分析日志文件"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        stats = {
            'total_requests': 0,
            'error_count': 0,
            'response_times': [],
            'status_codes': Counter(),
            'error_messages': Counter(),
            'ai_token_usage': 0,
            'hourly_distribution': defaultdict(int),
            'slow_requests': []
        }
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    # 解析时间戳
                    timestamp_match = re.search(self.patterns['timestamp'], line)
                    if not timestamp_match:
                        continue
                    
                    log_time = datetime.fromisoformat(timestamp_match.group(1))
                    if log_time < cutoff_time:
                        continue
                    
                    # 统计每小时分布
                    hour_key = log_time.strftime('%Y-%m-%d %H:00')
                    stats['hourly_distribution'][hour_key] += 1
                    
                    # 解析其他字段
                    level_match = re.search(self.patterns['level'], line)
                    if level_match and level_match.group(1) in ['INFO', 'ERROR', 'WARNING']:
                        stats['total_requests'] += 1
                        
                        # 错误统计
                        if level_match.group(1) == 'ERROR':
                            stats['error_count'] += 1
                            
                            error_match = re.search(self.patterns['error'], line)
                            if error_match:
                                stats['error_messages'][error_match.group(1)] += 1
                        
                        # 响应时间统计
                        response_time_match = re.search(self.patterns['response_time'], line)
                        if response_time_match:
                            response_time = float(response_time_match.group(1))
                            stats['response_times'].append(response_time)
                            
                            # 记录慢请求
                            if response_time > 5.0:
                                message_match = re.search(self.patterns['message'], line)
                                stats['slow_requests'].append({
                                    'timestamp': log_time.isoformat(),
                                    'response_time': response_time,
                                    'message': message_match.group(1) if message_match else 'unknown'
                                })
                        
                        # 状态码统计
                        status_match = re.search(self.patterns['status_code'], line)
                        if status_match:
                            stats['status_codes'][status_match.group(1)] += 1
                        
                        # AI Token使用统计
                        tokens_match = re.search(self.patterns['ai_tokens'], line)
                        if tokens_match:
                            stats['ai_token_usage'] += int(tokens_match.group(1))
                            
                except Exception as e:
                    print(f"解析日志行时出错: {e}")
                    continue
        
        return self.generate_report(stats)
    
    def generate_report(self, stats):
        """生成分析报告"""
        report = {
            'analysis_time': datetime.now().isoformat(),
            'summary': {
                'total_requests': stats['total_requests'],
                'error_rate': stats['error_count'] / max(stats['total_requests'], 1) * 100,
                'total_ai_tokens': stats['ai_token_usage']
            },
            'performance': {},
            'errors': {
                'count': stats['error_count'],
                'top_errors': dict(stats['error_messages'].most_common(10))
            },
            'traffic': {
                'hourly_distribution': dict(stats['hourly_distribution'])
            },
            'slow_requests': stats['slow_requests'][-10:]  # 最近10个慢请求
        }
        
        # 响应时间统计
        if stats['response_times']:
            response_times = sorted(stats['response_times'])
            count = len(response_times)
            
            report['performance'] = {
                'avg_response_time': sum(response_times) / count,
                'p50_response_time': response_times[int(count * 0.5)],
                'p95_response_time': response_times[int(count * 0.95)],
                'p99_response_time': response_times[int(count * 0.99)],
                'max_response_time': max(response_times)
            }
        
        return report

def main():
    parser = argparse.ArgumentParser(description='日志分析工具')
    parser.add_argument('--log-file', required=True, help='日志文件路径')
    parser.add_argument('--hours', type=int, default=24, help='分析最近N小时的日志')
    parser.add_argument('--output', help='输出文件路径')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.log_file)
    report = analyzer.analyze_logs(args.hours)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"分析报告已保存到: {args.output}")
    else:
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
```

---

## 📋 运维检查清单

### 部署前检查清单
- [ ] **代码质量**：通过所有测试，代码审查完成
- [ ] **安全检查**：通过安全扫描，无高危漏洞
- [ ] **配置验证**：环境变量和配置文件正确
- [ ] **数据库迁移**：数据库脚本测试通过
- [ ] **依赖检查**：所有外部服务可用
- [ ] **备份确认**：当前数据已备份
- [ ] **回滚方案**：回滚步骤明确，已测试
- [ ] **监控准备**：监控和告警配置就绪
- [ ] **文档更新**：部署文档和运维手册更新

### 日常运维检查清单
- [ ] **系统资源**：CPU、内存、磁盘使用正常
- [ ] **服务状态**：所有服务运行正常，无异常重启
- [ ] **响应时间**：API响应时间在正常范围内
- [ ] **错误率**：错误率低于告警阈值
- [ ] **AI服务**：AI API调用成功率正常
- [ ] **数据库**：数据库连接池正常，慢查询检查
- [ ] **备份状态**：自动备份执行成功
- [ ] **磁盘空间**：日志文件和数据库空间充足
- [ ] **安全日志**：检查异常访问和安全事件

### 故障响应检查清单
- [ ] **问题确认**：确认问题范围和影响程度
- [ ] **告警通知**：相关人员已收到通知
- [ ] **用户通信**：如需要，已通知用户
- [ ] **临时措施**：实施临时缓解措施
- [ ] **根因分析**：分析问题根本原因
- [ ] **修复方案**：制定并实施修复方案
- [ ] **验证恢复**：确认系统完全恢复
- [ ] **总结报告**：编写故障总结报告
- [ ] **预防措施**：制定预防类似问题的措施

---

*部署和运维规范文档版本：v1.0*  
*创建时间：2025-07-31*  
*维护者：数字员工系统运维团队*
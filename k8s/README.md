# 数字员工系统Kubernetes部署指南

## 概述

本目录包含数字员工系统的完整Kubernetes生产级部署配置，支持高可用、自动扩缩容、监控和日志系统。

## 系统架构

```
外部用户
    ↓
[Ingress Controller]
    ↓
[Nginx LoadBalancer] ←→ [Prometheus监控]
    ↓
[Digital Employee App] ←→ [Grafana仪表板]
    ↓        ↓
[PostgreSQL集群]  [Redis集群]
    ↓
[ELK日志系统]
```

## 部署组件

| 组件 | 文件 | 描述 |
|------|------|------|
| 命名空间 | `01-namespace.yaml` | 创建数字员工命名空间和资源配额 |
| 配置 | `02-configmap.yaml` | 应用配置、Nginx、Prometheus等配置 |
| 密钥 | `03-secrets.yaml` | 敏感信息如密码、API密钥 |
| 数据库 | `04-postgres.yaml` | PostgreSQL主从集群 |
| 缓存 | `05-redis.yaml` | Redis主从集群和Sentinel |
| 应用 | `06-digital-employee-app.yaml` | 核心应用程序 |
| 负载均衡 | `07-nginx.yaml` | Nginx负载均衡器 |
| 监控 | `08-monitoring.yaml` | Prometheus、Grafana、AlertManager |
| 日志 | `09-logging.yaml` | Elasticsearch、Logstash、Kibana |
| 入口 | `10-ingress.yaml` | HTTP/HTTPS外部访问 |
| 扩缩容 | `11-hpa.yaml` | 水平Pod自动扩缩容 |
| 网络安全 | `12-network-policy.yaml` | 网络策略和安全规则 |

## 系统要求

### Kubernetes集群要求
- Kubernetes版本: 1.25+
- 节点数量: 最少3个节点（生产环境推荐5+节点）
- 每个节点最少配置: 4 CPU, 8GB RAM, 100GB存储
- 网络插件: 支持NetworkPolicy（如Calico、Cilium）
- 存储类: 需要`fast-ssd`和`shared-storage`存储类

### 必需工具
- `kubectl` (1.25+)
- `docker` (20.10+)
- `helm` (3.0+, 可选)

### 集群组件依赖
- **Ingress Controller**: NGINX Ingress Controller
- **Metrics Server**: 用于HPA自动扩缩容
- **cert-manager**: 用于SSL证书管理（可选）
- **CSI驱动**: 用于持久化存储

## 快速部署

### 1. 准备环境

```bash
# 检查kubectl连接
kubectl cluster-info

# 检查存储类
kubectl get storageclass

# 安装NGINX Ingress Controller（如果未安装）
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 安装Metrics Server（如果未安装）
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 2. 配置密钥

**重要**: 在部署前必须更新密钥文件！

```bash
# 编辑密钥文件
vim 03-secrets.yaml

# 需要更新的密钥包括:
# - SECRET_KEY: 应用密钥
# - CLAUDE_API_KEY: Claude API密钥
# - POSTGRES_PASSWORD: 数据库密码
# - GRAFANA_PASSWORD: Grafana管理员密码
# - 其他相关密钥
```

### 3. 执行部署

```bash
# 给部署脚本执行权限
chmod +x deploy.sh

# 完整部署
./deploy.sh deploy

# 或者分步部署
./deploy.sh deploy namespace
./deploy.sh deploy config
./deploy.sh deploy storage
./deploy.sh deploy app
# ... 其他组件
```

### 4. 验证部署

```bash
# 验证所有组件状态
./deploy.sh verify

# 查看Pod状态
kubectl get pods -n digital-employee

# 查看服务状态
kubectl get services -n digital-employee
```

## 详细部署步骤

### 第一阶段：基础设施
```bash
# 1. 创建命名空间和资源配额
kubectl apply -f 01-namespace.yaml

# 2. 部署配置映射
kubectl apply -f 02-configmap.yaml

# 3. 部署密钥（请先更新密钥内容）
kubectl apply -f 03-secrets.yaml
```

### 第二阶段：存储层
```bash
# 4. 部署PostgreSQL集群
kubectl apply -f 04-postgres.yaml

# 等待PostgreSQL启动
kubectl wait --for=condition=Ready pod -l app=postgres,component=primary -n digital-employee --timeout=300s

# 5. 部署Redis集群
kubectl apply -f 05-redis.yaml

# 等待Redis启动
kubectl wait --for=condition=Ready pod -l app=redis,component=master -n digital-employee --timeout=300s
```

### 第三阶段：应用层
```bash
# 6. 部署数字员工应用
kubectl apply -f 06-digital-employee-app.yaml

# 等待应用启动
kubectl wait --for=condition=Ready pod -l app=digital-employee,component=app -n digital-employee --timeout=600s

# 7. 部署Nginx负载均衡器
kubectl apply -f 07-nginx.yaml

# 等待Nginx启动
kubectl wait --for=condition=Ready pod -l app=nginx,component=loadbalancer -n digital-employee --timeout=300s
```

### 第四阶段：监控和日志
```bash
# 8. 部署监控系统
kubectl apply -f 08-monitoring.yaml

# 9. 部署日志系统
kubectl apply -f 09-logging.yaml
```

### 第五阶段：网络和扩缩容
```bash
# 10. 配置外部访问
kubectl apply -f 10-ingress.yaml

# 11. 配置自动扩缩容
kubectl apply -f 11-hpa.yaml

# 12. 应用网络安全策略
kubectl apply -f 12-network-policy.yaml
```

## 配置定制

### 存储配置
修改存储类和存储大小：
```yaml
# 在相关文件中修改
spec:
  resources:
    requests:
      storage: 50Gi  # 根据需要调整
  storageClassName: your-storage-class
```

### 资源配置
根据集群规模调整resource requests和limits：
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### 副本数配置
调整各组件的副本数：
```yaml
spec:
  replicas: 3  # 根据需要调整
```

### 域名配置
在Ingress中配置自定义域名：
```yaml
rules:
- host: your-domain.com  # 替换为实际域名
```

## 访问系统

### 内部访问（集群内）
```bash
# 应用访问
curl http://digital-employee-app-svc.digital-employee.svc.cluster.local:8000

# 监控访问
curl http://prometheus-svc.digital-employee.svc.cluster.local:9090
curl http://grafana-svc.digital-employee.svc.cluster.local:3000
```

### 外部访问

#### 通过端口转发（开发环境）
```bash
# 主应用
kubectl port-forward -n digital-employee svc/nginx-svc 8080:80

# 监控系统
kubectl port-forward -n digital-employee svc/prometheus-svc 9090:9090
kubectl port-forward -n digital-employee svc/grafana-svc 3000:3000
kubectl port-forward -n digital-employee svc/kibana-svc 5601:5601
```

#### 通过LoadBalancer（生产环境）
```bash
# 获取外部IP
kubectl get service nginx-svc -n digital-employee

# 访问地址
# http://<external-ip>
# https://<external-ip>
```

#### 通过Ingress（推荐）
配置DNS记录指向Ingress Controller的外部IP：
- `digital-employee.your-domain.com` → 主应用
- `prometheus.your-domain.com` → Prometheus
- `grafana.your-domain.com` → Grafana
- `kibana.your-domain.com` → Kibana

## 监控和维护

### 监控指标
- **应用监控**: Prometheus + Grafana
- **日志监控**: ELK Stack
- **资源监控**: Kubernetes Dashboard
- **网络监控**: NetworkPolicy审计

### 关键指标监控
- CPU使用率 > 80%
- 内存使用率 > 85%
- 响应时间 > 2秒
- 错误率 > 5%
- 数据库连接数
- Redis内存使用

### 日常维护任务
```bash
# 检查Pod状态
kubectl get pods -n digital-employee

# 查看Pod日志
kubectl logs -f deployment/digital-employee-app -n digital-employee

# 检查资源使用
kubectl top pods -n digital-employee

# 检查HPA状态
kubectl get hpa -n digital-employee

# 检查存储使用
kubectl get pvc -n digital-employee
```

### 备份策略
```bash
# 数据库备份
kubectl exec -n digital-employee postgres-primary-0 -- pg_dump -U postgres digital_employee > backup.sql

# Redis备份
kubectl exec -n digital-employee redis-master-xxx -- redis-cli BGSAVE

# 配置备份
kubectl get all,configmap,secret -n digital-employee -o yaml > digital-employee-backup.yaml
```

## 故障排除

### 常见问题

#### Pod无法启动
```bash
# 查看Pod事件
kubectl describe pod <pod-name> -n digital-employee

# 查看Pod日志
kubectl logs <pod-name> -n digital-employee

# 检查资源限制
kubectl get limitrange -n digital-employee
```

#### 服务无法访问
```bash
# 检查Service
kubectl get svc -n digital-employee

# 检查Endpoints
kubectl get endpoints -n digital-employee

# 测试网络连通性
kubectl run test-pod --image=nicolaka/netshoot -n digital-employee -- sleep 3600
kubectl exec -it test-pod -n digital-employee -- nc -zv <service-name> <port>
```

#### 存储问题
```bash
# 检查PVC状态
kubectl get pvc -n digital-employee

# 查看存储类
kubectl get storageclass

# 检查磁盘空间
kubectl exec -it <pod-name> -n digital-employee -- df -h
```

#### 网络策略问题
```bash
# 检查NetworkPolicy
kubectl get networkpolicy -n digital-employee

# 测试网络连通性
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: network-test
  namespace: digital-employee
spec:
  containers:
  - name: test
    image: nicolaka/netshoot
    command: ["sleep", "3600"]
EOF

kubectl exec -it network-test -n digital-employee -- nc -zv <target-service> <port>
```

### 性能调优

#### 应用调优
- 调整副本数：根据负载调整`replicas`
- 资源限制：合理设置CPU和内存限制
- JVM参数：调整Java应用的JVM参数

#### 数据库调优
- 连接池：调整数据库连接池大小
- 索引优化：添加必要的数据库索引
- 查询优化：优化慢查询

#### 缓存调优
- Redis内存：调整Redis最大内存设置
- 缓存策略：选择合适的缓存淘汰策略
- 持久化：配置RDB和AOF持久化

## 安全考虑

### 网络安全
- 使用NetworkPolicy限制Pod间通信
- 配置Ingress的访问控制
- 启用TLS加密传输

### 容器安全
- 使用非root用户运行容器
- 配置Pod安全上下文
- 定期更新容器镜像

### 密钥管理
- 使用Kubernetes Secret存储敏感信息
- 考虑使用外部密钥管理系统（如HashiCorp Vault）
- 定期轮换密钥和证书

### 访问控制
- 配置RBAC权限
- 使用ServiceAccount限制Pod权限
- 启用审计日志

## 升级和回滚

### 滚动升级
```bash
# 更新应用镜像
kubectl set image deployment/digital-employee-app digital-employee=digital-employee:new-version -n digital-employee

# 查看升级状态
kubectl rollout status deployment/digital-employee-app -n digital-employee
```

### 回滚操作
```bash
# 查看升级历史
kubectl rollout history deployment/digital-employee-app -n digital-employee

# 回滚到上一版本
kubectl rollout undo deployment/digital-employee-app -n digital-employee

# 回滚到指定版本
kubectl rollout undo deployment/digital-employee-app --to-revision=2 -n digital-employee
```

## 清理和卸载

### 完全清理
```bash
# 使用脚本清理
./deploy.sh cleanup

# 手动清理
kubectl delete namespace digital-employee

# 清理集群级资源
kubectl delete clusterrole digital-employee-role
kubectl delete clusterrolebinding digital-employee-rolebinding
```

### 保留数据清理
```bash
# 只删除应用，保留数据
kubectl delete deployment,service,ingress -n digital-employee -l app!=postgres,app!=redis
```

## 支持和反馈

如有问题或建议，请通过以下方式联系：
- 项目仓库：提交Issue
- 邮箱：digital-employee-team@company.com
- 文档：查看项目Wiki

## 版本历史

- v2.0.0: 完整的Kubernetes生产级部署配置
- v1.5.0: 添加监控和日志系统
- v1.0.0: 基础部署配置

---

**注意**: 本部署配置适用于生产环境，部署前请确保充分测试并根据实际环境进行调整。
#!/bin/bash
# 数字员工系统Kubernetes部署脚本
# Digital Employee System Kubernetes Deployment Script

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必需的工具
check_prerequisites() {
    log_info "检查必需的工具..."
    
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl 未安装或不在PATH中"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        log_error "docker 未安装或不在PATH中"
        exit 1
    fi
    
    # 检查kubectl连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群"
        exit 1
    fi
    
    log_success "所有必需工具已就绪"
}

# 创建命名空间
create_namespace() {
    log_info "创建命名空间..."
    kubectl apply -f 01-namespace.yaml
    
    # 等待命名空间创建完成
    kubectl wait --for=condition=Active namespace/digital-employee --timeout=60s
    log_success "命名空间创建完成"
}

# 部署配置和密钥
deploy_configs() {
    log_info "部署配置和密钥..."
    
    # 提示用户更新密钥
    log_warning "请确保已更新 03-secrets.yaml 中的所有密钥和密码！"
    read -p "是否已更新所有密钥？ (y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        log_error "请先更新密钥文件后再继续部署"
        exit 1
    fi
    
    kubectl apply -f 02-configmap.yaml
    kubectl apply -f 03-secrets.yaml
    
    log_success "配置和密钥部署完成"
}

# 部署存储层
deploy_storage() {
    log_info "部署存储层 (PostgreSQL & Redis)..."
    
    # 部署PostgreSQL
    kubectl apply -f 04-postgres.yaml
    log_info "等待PostgreSQL启动..."
    kubectl wait --for=condition=Ready pod -l app=postgres,component=primary -n digital-employee --timeout=300s
    
    # 部署Redis
    kubectl apply -f 05-redis.yaml
    log_info "等待Redis启动..."
    kubectl wait --for=condition=Ready pod -l app=redis,component=master -n digital-employee --timeout=300s
    
    log_success "存储层部署完成"
}

# 部署应用层
deploy_application() {
    log_info "部署应用层 (Digital Employee App)..."
    
    kubectl apply -f 06-digital-employee-app.yaml
    
    # 等待应用启动
    log_info "等待应用启动..."
    kubectl wait --for=condition=Ready pod -l app=digital-employee,component=app -n digital-employee --timeout=600s
    
    log_success "应用层部署完成"
}

# 部署负载均衡器
deploy_loadbalancer() {
    log_info "部署负载均衡器 (Nginx)..."
    
    kubectl apply -f 07-nginx.yaml
    
    # 等待Nginx启动
    log_info "等待Nginx启动..."
    kubectl wait --for=condition=Ready pod -l app=nginx,component=loadbalancer -n digital-employee --timeout=300s
    
    log_success "负载均衡器部署完成"
}

# 部署监控系统
deploy_monitoring() {
    log_info "部署监控系统 (Prometheus & Grafana)..."
    
    kubectl apply -f 08-monitoring.yaml
    
    # 等待监控组件启动
    log_info "等待Prometheus启动..."
    kubectl wait --for=condition=Ready pod -l app=prometheus,component=server -n digital-employee --timeout=300s
    
    log_info "等待Grafana启动..."
    kubectl wait --for=condition=Ready pod -l app=grafana,component=server -n digital-employee --timeout=300s
    
    log_success "监控系统部署完成"
}

# 部署日志系统
deploy_logging() {
    log_info "部署日志系统 (ELK Stack)..."
    
    kubectl apply -f 09-logging.yaml
    
    # 等待Elasticsearch启动
    log_info "等待Elasticsearch启动..."
    kubectl wait --for=condition=Ready pod -l app=elasticsearch,component=server -n digital-employee --timeout=600s
    
    # 等待Kibana启动
    log_info "等待Kibana启动..."
    kubectl wait --for=condition=Ready pod -l app=kibana,component=server -n digital-employee --timeout=300s
    
    log_success "日志系统部署完成"
}

# 部署Ingress
deploy_ingress() {
    log_info "部署Ingress..."
    
    # 检查Ingress Controller是否存在
    if ! kubectl get ingressclass nginx &> /dev/null; then
        log_warning "未检测到NGINX Ingress Controller，请确保已安装"
        log_info "可以使用以下命令安装："
        log_info "kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml"
        read -p "是否继续部署Ingress配置？ (y/N): " confirm
        if [[ $confirm != [yY] ]]; then
            log_warning "跳过Ingress部署"
            return
        fi
    fi
    
    kubectl apply -f 10-ingress.yaml
    log_success "Ingress部署完成"
}

# 部署自动扩缩容
deploy_autoscaling() {
    log_info "部署自动扩缩容 (HPA)..."
    
    # 检查Metrics Server是否存在
    if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        log_warning "未检测到Metrics Server，HPA可能无法正常工作"
        log_info "可以使用以下命令安装："
        log_info "kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
    fi
    
    kubectl apply -f 11-hpa.yaml
    log_success "自动扩缩容部署完成"
}

# 部署网络策略
deploy_network_policies() {
    log_info "部署网络策略..."
    
    # 检查网络插件是否支持NetworkPolicy
    if ! kubectl get crd networkpolicies.networking.k8s.io &> /dev/null; then
        log_warning "当前网络插件可能不支持NetworkPolicy"
        read -p "是否继续部署网络策略？ (y/N): " confirm
        if [[ $confirm != [yY] ]]; then
            log_warning "跳过网络策略部署"
            return
        fi
    fi
    
    kubectl apply -f 12-network-policy.yaml
    log_success "网络策略部署完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    echo ""
    log_info "=== Pod状态 ==="
    kubectl get pods -n digital-employee -o wide
    
    echo ""
    log_info "=== 服务状态 ==="
    kubectl get services -n digital-employee
    
    echo ""
    log_info "=== Ingress状态 ==="
    kubectl get ingress -n digital-employee
    
    echo ""
    log_info "=== HPA状态 ==="
    kubectl get hpa -n digital-employee
    
    echo ""
    log_info "=== 存储状态 ==="
    kubectl get pvc -n digital-employee
    
    # 检查关键服务健康状态
    echo ""
    log_info "=== 健康检查 ==="
    
    # 检查应用健康状态
    if kubectl get pods -n digital-employee -l app=digital-employee,component=app | grep -q "Running"; then
        log_success "数字员工应用运行正常"
    else
        log_error "数字员工应用未正常运行"
    fi
    
    # 检查数据库状态
    if kubectl get pods -n digital-employee -l app=postgres,component=primary | grep -q "Running"; then
        log_success "PostgreSQL数据库运行正常"
    else
        log_error "PostgreSQL数据库未正常运行"
    fi
    
    # 检查Redis状态
    if kubectl get pods -n digital-employee -l app=redis,component=master | grep -q "Running"; then
        log_success "Redis缓存运行正常"
    else
        log_error "Redis缓存未正常运行"
    fi
    
    # 检查监控系统状态
    if kubectl get pods -n digital-employee -l app=prometheus,component=server | grep -q "Running"; then
        log_success "Prometheus监控运行正常"
    else
        log_warning "Prometheus监控未正常运行"
    fi
    
    if kubectl get pods -n digital-employee -l app=grafana,component=server | grep -q "Running"; then
        log_success "Grafana仪表板运行正常"
    else
        log_warning "Grafana仪表板未正常运行"
    fi
}

# 显示访问信息
show_access_info() {
    log_info "=== 访问信息 ==="
    
    # 获取LoadBalancer IP或NodePort
    local nginx_service=$(kubectl get service nginx-svc -n digital-employee -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    
    if [[ -n "$nginx_service" ]]; then
        echo ""
        log_success "系统已部署完成！"
        echo ""
        echo "外部访问地址："
        echo "  主应用: http://$nginx_service"
        echo "  HTTPS: https://$nginx_service"
    else
        local node_port=$(kubectl get service nginx-svc -n digital-employee -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null)
        if [[ -n "$node_port" ]]; then
            local node_ip=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
            if [[ -z "$node_ip" ]]; then
                node_ip=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
            fi
            echo ""
            log_success "系统已部署完成！"
            echo ""
            echo "外部访问地址（NodePort）："
            echo "  主应用: http://$node_ip:$node_port"
        else
            echo ""
            log_success "系统已部署完成！"
            echo ""
            echo "请配置Ingress或LoadBalancer以启用外部访问"
        fi
    fi
    
    echo ""
    echo "内部服务访问："
    echo "  Prometheus: http://prometheus-svc.digital-employee.svc.cluster.local:9090"
    echo "  Grafana: http://grafana-svc.digital-employee.svc.cluster.local:3000"
    echo "  Kibana: http://kibana-svc.digital-employee.svc.cluster.local:5601"
    
    echo ""
    echo "端口转发访问示例："
    echo "  kubectl port-forward -n digital-employee svc/prometheus-svc 9090:9090"
    echo "  kubectl port-forward -n digital-employee svc/grafana-svc 3000:3000"
    echo "  kubectl port-forward -n digital-employee svc/kibana-svc 5601:5601"
    
    echo ""
    log_info "默认登录凭据（请在生产环境中修改）："
    echo "  Grafana: admin / (见secrets中的GRAFANA_PASSWORD)"
    echo "  Kibana: 无认证（建议配置认证）"
}

# 清理函数
cleanup() {
    log_warning "收到中断信号，正在清理..."
    # 这里可以添加清理逻辑
    exit 1
}

# 主部署函数
deploy_all() {
    log_info "开始数字员工系统完整部署..."
    
    check_prerequisites
    create_namespace
    deploy_configs
    deploy_storage
    deploy_application
    deploy_loadbalancer
    deploy_monitoring
    deploy_logging
    deploy_ingress
    deploy_autoscaling
    deploy_network_policies
    
    # 等待所有Pod稳定
    log_info "等待所有服务稳定..."
    sleep 30
    
    verify_deployment
    show_access_info
    
    log_success "数字员工系统部署完成！"
}

# 单独部署函数
deploy_component() {
    case $1 in
        namespace)
            create_namespace
            ;;
        config)
            deploy_configs
            ;;
        storage)
            deploy_storage
            ;;
        app)
            deploy_application
            ;;
        nginx)
            deploy_loadbalancer
            ;;
        monitoring)
            deploy_monitoring
            ;;
        logging)
            deploy_logging
            ;;
        ingress)
            deploy_ingress
            ;;
        hpa)
            deploy_autoscaling
            ;;
        netpol)
            deploy_network_policies
            ;;
        verify)
            verify_deployment
            ;;
        *)
            log_error "未知组件: $1"
            show_help
            exit 1
            ;;
    esac
}

# 清理部署
cleanup_deployment() {
    log_warning "开始清理数字员工系统..."
    
    read -p "确定要删除整个数字员工系统吗？此操作不可逆！ (yes/NO): " confirm
    if [[ $confirm != "yes" ]]; then
        log_info "取消清理操作"
        exit 0
    fi
    
    log_info "删除所有资源..."
    
    # 按相反顺序删除
    kubectl delete -f 12-network-policy.yaml --ignore-not-found=true
    kubectl delete -f 11-hpa.yaml --ignore-not-found=true
    kubectl delete -f 10-ingress.yaml --ignore-not-found=true
    kubectl delete -f 09-logging.yaml --ignore-not-found=true
    kubectl delete -f 08-monitoring.yaml --ignore-not-found=true
    kubectl delete -f 07-nginx.yaml --ignore-not-found=true
    kubectl delete -f 06-digital-employee-app.yaml --ignore-not-found=true
    kubectl delete -f 05-redis.yaml --ignore-not-found=true
    kubectl delete -f 04-postgres.yaml --ignore-not-found=true
    kubectl delete -f 03-secrets.yaml --ignore-not-found=true
    kubectl delete -f 02-configmap.yaml --ignore-not-found=true
    kubectl delete -f 01-namespace.yaml --ignore-not-found=true
    
    log_success "清理完成"
}

# 显示帮助
show_help() {
    echo "数字员工系统Kubernetes部署脚本"
    echo ""
    echo "用法: $0 [命令] [组件]"
    echo ""
    echo "命令:"
    echo "  deploy [组件]    部署指定组件或完整系统"
    echo "  cleanup         清理整个系统"
    echo "  verify          验证部署状态"
    echo "  help            显示此帮助信息"
    echo ""
    echo "组件:"
    echo "  namespace       命名空间"
    echo "  config          配置和密钥"
    echo "  storage         存储层 (PostgreSQL & Redis)"
    echo "  app             应用层"
    echo "  nginx           负载均衡器"
    echo "  monitoring      监控系统"
    echo "  logging         日志系统"
    echo "  ingress         Ingress配置"
    echo "  hpa             自动扩缩容"
    echo "  netpol          网络策略"
    echo ""
    echo "示例:"
    echo "  $0 deploy                 # 部署完整系统"
    echo "  $0 deploy app             # 只部署应用层"
    echo "  $0 verify                 # 验证部署状态"
    echo "  $0 cleanup                # 清理整个系统"
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主程序
main() {
    case ${1:-deploy} in
        deploy)
            if [[ -n $2 ]]; then
                deploy_component $2
            else
                deploy_all
            fi
            ;;
        cleanup)
            cleanup_deployment
            ;;
        verify)
            verify_deployment
            show_access_info
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@"
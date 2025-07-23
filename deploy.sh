#!/bin/bash

# 数字员工系统部署脚本
# 支持Docker Compose和Kubernetes部署

set -e

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

# 显示帮助信息
show_help() {
    echo "数字员工系统部署脚本"
    echo ""
    echo "用法: $0 [选项] [命令]"
    echo ""
    echo "命令:"
    echo "  docker-dev      使用Docker Compose部署开发环境"
    echo "  docker-prod     使用Docker Compose部署生产环境"
    echo "  k8s-dev         部署到Kubernetes开发环境"
    echo "  k8s-prod        部署到Kubernetes生产环境"
    echo "  build           构建Docker镜像"
    echo "  test            运行测试"
    echo "  clean           清理环境"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示帮助信息"
    echo "  -v, --verbose   详细输出"
    echo "  --skip-build    跳过构建步骤"
    echo "  --tag TAG       指定镜像标签 (默认: latest)"
    echo ""
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    local deps=("docker" "docker-compose")
    
    if [[ "$1" == "k8s"* ]]; then
        deps+=("kubectl" "helm")
    fi
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "$dep 未安装或不在PATH中"
            exit 1
        fi
    done
    
    log_success "所有依赖检查通过"
}

# 检查环境变量
check_env_vars() {
    log_info "检查环境变量..."
    
    local required_vars=("OPENAI_API_KEY")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_warning "以下环境变量未设置: ${missing_vars[*]}"
        log_info "请在.env文件中设置这些变量或通过环境变量传入"
    fi
}

# 构建Docker镜像
build_image() {
    local tag="${IMAGE_TAG:-latest}"
    log_info "构建Docker镜像 (标签: $tag)..."
    
    docker build -t "digital-employee:$tag" .
    
    if [[ $? -eq 0 ]]; then
        log_success "镜像构建成功"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    # 启动测试环境
    docker-compose -f docker-compose.test.yml up -d
    
    # 等待服务启动
    sleep 10
    
    # 运行测试
    docker-compose -f docker-compose.test.yml exec -T api pytest tests/ -v --cov=./ --cov-report=html
    
    local test_result=$?
    
    # 清理测试环境
    docker-compose -f docker-compose.test.yml down
    
    if [[ $test_result -eq 0 ]]; then
        log_success "所有测试通过"
    else
        log_error "测试失败"
        exit 1
    fi
}

# Docker Compose部署
deploy_docker() {
    local env="$1"
    local compose_file="docker-compose.yml"
    
    if [[ "$env" == "prod" ]]; then
        compose_file="docker-compose.prod.yml"
    fi
    
    log_info "使用Docker Compose部署 ($env 环境)..."
    
    # 创建必要的目录
    mkdir -p logs config monitoring/prometheus monitoring/grafana nginx
    
    # 构建镜像 (如果没有跳过构建)
    if [[ "$SKIP_BUILD" != "true" ]]; then
        build_image
    fi
    
    # 启动服务
    docker-compose -f "$compose_file" up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 健康检查
    local api_url="http://localhost:8080/api/v1/health"
    local max_attempts=10
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f "$api_url" &> /dev/null; then
            log_success "数字员工系统部署成功!"
            log_info "API地址: http://localhost:8080"
            log_info "Grafana监控: http://localhost:3000 (admin/admin123)"
            log_info "Prometheus: http://localhost:9090"
            return 0
        fi
        
        log_info "等待服务启动... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    log_error "服务启动超时"
    docker-compose -f "$compose_file" logs
    exit 1
}

# Kubernetes部署
deploy_k8s() {
    local env="$1"
    local namespace="digital-employees"
    
    log_info "部署到Kubernetes ($env 环境)..."
    
    # 检查kubectl连接
    if ! kubectl cluster-info &> /dev/null; then
        log_error "无法连接到Kubernetes集群"
        exit 1
    fi
    
    # 构建并推送镜像
    if [[ "$SKIP_BUILD" != "true" ]]; then
        build_image
        
        # 如果是生产环境，推送到镜像仓库
        if [[ "$env" == "prod" ]]; then
            log_info "推送镜像到仓库..."
            docker tag "digital-employee:${IMAGE_TAG:-latest}" "${DOCKER_REGISTRY:-localhost:5000}/digital-employee:${IMAGE_TAG:-latest}"
            docker push "${DOCKER_REGISTRY:-localhost:5000}/digital-employee:${IMAGE_TAG:-latest}"
        fi
    fi
    
    # 应用Kubernetes配置
    kubectl apply -f k8s-deployment.yaml
    
    # 等待部署完成
    log_info "等待部署完成..."
    kubectl wait --for=condition=ready pod -l app=digital-employee-api -n "$namespace" --timeout=300s
    
    if [[ $? -eq 0 ]]; then
        log_success "Kubernetes部署成功!"
        
        # 显示服务信息
        kubectl get services -n "$namespace"
        kubectl get ingress -n "$namespace"
        
        # 获取访问地址
        local ingress_ip=$(kubectl get ingress digital-employee-ingress -n "$namespace" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        if [[ -n "$ingress_ip" ]]; then
            log_info "服务访问地址: http://$ingress_ip"
        fi
    else
        log_error "Kubernetes部署失败"
        kubectl logs -l app=digital-employee-api -n "$namespace" --tail=100
        exit 1
    fi
}

# 清理环境
clean_environment() {
    log_info "清理环境..."
    
    # 清理Docker环境
    if docker-compose ps &> /dev/null; then
        docker-compose down -v --remove-orphans
    fi
    
    # 清理Kubernetes环境
    if kubectl get namespace digital-employees &> /dev/null; then
        kubectl delete namespace digital-employees
    fi
    
    # 清理Docker镜像
    docker system prune -f
    
    log_success "环境清理完成"
}

# 监控部署状态
monitor_deployment() {
    log_info "监控部署状态..."
    
    while true; do
        echo "=== 系统状态 ==="
        date
        echo ""
        
        # Docker状态
        echo "Docker 服务状态:"
        docker-compose ps 2>/dev/null || echo "Docker Compose未运行"
        echo ""
        
        # Kubernetes状态
        echo "Kubernetes 服务状态:"
        kubectl get pods -n digital-employees 2>/dev/null || echo "Kubernetes未连接"
        echo ""
        
        # 系统资源
        echo "系统资源使用:"
        echo "内存: $(free -h | awk '/^Mem:/ {print $3"/"$2}')"
        echo "磁盘: $(df -h / | awk 'NR==2 {print $3"/"$2" ("$5")"}')"
        echo ""
        
        sleep 30
        clear
    done
}

# 主函数
main() {
    local command=""
    local env="dev"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                set -x
                shift
                ;;
            --skip-build)
                SKIP_BUILD="true"
                shift
                ;;
            --tag)
                IMAGE_TAG="$2"
                shift 2
                ;;
            docker-dev|docker-prod|k8s-dev|k8s-prod|build|test|clean|monitor)
                command="$1"
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 如果没有指定命令，显示帮助
    if [[ -z "$command" ]]; then
        show_help
        exit 0
    fi
    
    # 加载环境变量
    if [[ -f .env ]]; then
        source .env
        log_info "已加载.env文件"
    fi
    
    # 执行命令
    case "$command" in
        docker-dev)
            check_dependencies "docker"
            check_env_vars
            deploy_docker "dev"
            ;;
        docker-prod)
            check_dependencies "docker"
            check_env_vars
            deploy_docker "prod"
            ;;
        k8s-dev)
            check_dependencies "k8s"
            check_env_vars
            deploy_k8s "dev"
            ;;
        k8s-prod)
            check_dependencies "k8s"
            check_env_vars
            deploy_k8s "prod"
            ;;
        build)
            check_dependencies "docker"
            build_image
            ;;
        test)
            check_dependencies "docker"
            run_tests
            ;;
        clean)
            clean_environment
            ;;
        monitor)
            monitor_deployment
            ;;
    esac
}

# 执行主函数
main "$@"
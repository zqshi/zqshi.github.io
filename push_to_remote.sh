#!/bin/bash

# Digital Employee System - 推送到远程仓库脚本
# 用于将模块化架构改进推送到GitHub等远程仓库

echo "=========================================="
echo "数字员工系统 - Git推送脚本"
echo "=========================================="

# 检查当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

# 检查工作目录状态
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  工作目录不干净，请先提交或暂存更改"
    git status --short
    exit 1
fi

echo "✅ 工作目录干净"

# 显示要推送的提交
echo ""
echo "📋 准备推送的提交:"
git log --oneline -5

echo ""
echo "🔍 分支对比:"
git log --oneline main..HEAD

# 检查远程仓库配置
echo ""
echo "🌐 检查远程仓库配置:"
if git remote -v | grep -q origin; then
    echo "✅ 远程仓库已配置:"
    git remote -v
    
    echo ""
    echo "🚀 开始推送到远程仓库..."
    
    # 推送当前分支到远程
    if git push -u origin $CURRENT_BRANCH; then
        echo "✅ 分支推送成功: $CURRENT_BRANCH"
        
        # 显示远程分支信息
        echo ""
        echo "📊 远程分支状态:"
        git branch -va
        
        echo ""
        echo "🎯 后续操作建议:"
        echo "1. 在GitHub上创建Pull Request"
        echo "2. 进行代码审查"
        echo "3. 合并到主分支"
        echo "4. 部署到测试/生产环境"
        
        # 生成GitHub PR URL (如果是GitHub仓库)
        REMOTE_URL=$(git config --get remote.origin.url)
        if [[ $REMOTE_URL == *"github.com"* ]]; then
            # 提取仓库信息
            REPO_PATH=$(echo $REMOTE_URL | sed 's/.*github\.com[:/]\(.*\)\.git/\1/')
            PR_URL="https://github.com/${REPO_PATH}/compare/main...${CURRENT_BRANCH}?expand=1"
            echo ""
            echo "🔗 创建Pull Request:"
            echo "$PR_URL"
        fi
        
    else
        echo "❌ 推送失败，请检查网络连接和权限"
        exit 1
    fi
    
else
    echo "⚠️  未配置远程仓库"
    echo ""
    echo "🔧 配置远程仓库的方法:"
    echo "1. GitHub仓库:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/digital-employee-system.git"
    echo ""
    echo "2. GitLab仓库:"
    echo "   git remote add origin https://gitlab.com/YOUR_USERNAME/digital-employee-system.git"
    echo ""
    echo "3. 其他Git服务:"
    echo "   git remote add origin YOUR_REPOSITORY_URL"
    echo ""
    echo "配置完成后重新运行此脚本"
    exit 1
fi

echo ""
echo "=========================================="
echo "推送操作完成 ✨"
echo "=========================================="
# 本地Git版本管理策略

## 分支结构

### 主分支
- `main` - 主分支，保持稳定的代码状态
- `develop` - 开发分支，集成新功能

### 功能分支
- `feature/功能名称` - 新功能开发
- `bugfix/问题描述` - Bug修复
- `hotfix/紧急修复` - 生产环境紧急修复
- `experiment/实验名称` - 实验性功能

## 分支命名规范

```bash
# 功能开发
feature/prompt-manager-enhancement
feature/agent-system-upgrade

# Bug修复
bugfix/prompt-loading-error
bugfix/memory-leak-fix

# 紧急修复
hotfix/security-patch
hotfix/critical-bug-fix

# 实验功能
experiment/ai-model-integration
experiment/performance-optimization
```

## 常用Git命令

### 分支操作
```bash
# 创建并切换到新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main
git checkout develop

# 查看所有分支
git branch -a

# 删除本地分支
git branch -d feature/completed-feature
```

### 提交规范
```bash
# 提交格式：类型(范围): 描述
git commit -m "feat(prompt): 添加新的AI提示词管理功能"
git commit -m "fix(agent): 修复代理执行错误"
git commit -m "docs(readme): 更新部署文档"
git commit -m "refactor(core): 重构核心业务逻辑"
git commit -m "test(unit): 添加单元测试用例"
```

### 提交类型
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建、依赖等维护性工作

### 合并策略
```bash
# 切回主分支
git checkout main

# 合并功能分支（保留提交历史）
git merge feature/new-feature

# 合并功能分支（压缩提交）
git merge --squash feature/new-feature
git commit -m "feat: 完成新功能开发"

# 变基合并（线性历史）
git checkout feature/new-feature
git rebase main
git checkout main
git merge feature/new-feature
```

## 本地开发工作流

### 1. 开始新功能
```bash
git checkout main
git pull origin main  # 如果有远程仓库
git checkout -b feature/new-feature
```

### 2. 开发过程中
```bash
# 经常提交
git add .
git commit -m "feat(module): 实现基础功能"

# 定期同步主分支
git checkout main
git pull origin main
git checkout feature/new-feature
git rebase main
```

### 3. 完成功能
```bash
git checkout main
git merge feature/new-feature
git branch -d feature/new-feature
```

## 版本标签管理

### 语义化版本
```bash
# 主版本号.次版本号.修订号
v1.0.0  # 首次发布
v1.1.0  # 新增功能
v1.1.1  # Bug修复
v2.0.0  # 重大更新
```

### 标签操作
```bash
# 创建标签
git tag -a v1.0.0 -m "发布版本 1.0.0"

# 查看标签
git tag

# 查看标签详情
git show v1.0.0

# 删除标签
git tag -d v1.0.0
```

## 本地备份策略

### 1. 定期备份
```bash
# 创建备份分支
git checkout -b backup/$(date +%Y%m%d)

# 推送到备份目录
git bundle create ../backups/digital-employees-$(date +%Y%m%d).bundle --all
```

### 2. 重要里程碑备份
```bash
# 在重要功能完成后创建备份
git tag -a milestone/v1.0-complete -m "完成1.0版本所有功能"
git bundle create ../backups/milestone-v1.0.bundle --all
```

## 代码审查流程

### 自我审查清单
- [ ] 代码格式是否符合规范
- [ ] 是否有调试代码残留
- [ ] 提交信息是否清晰
- [ ] 是否更新了相关文档
- [ ] 是否添加了必要的测试

### 提交前检查
```bash
# 检查代码风格
python -m flake8 .

# 运行测试
python -m pytest

# 检查类型
python -m mypy .
```

## 项目维护

### 定期清理
```bash
# 清理已合并的分支
git branch --merged | grep -v main | xargs -n 1 git branch -d

# 清理不再跟踪的文件
git clean -fd

# 压缩Git历史（谨慎使用）
git gc --aggressive --prune=now
```

### 历史分析
```bash
# 查看提交统计
git log --oneline --graph --decorate

# 查看文件变更历史
git log --follow filename.py

# 查看贡献统计
git shortlog -sn
```

## 应急处理

### 撤销操作
```bash
# 撤销最后一次提交（保留文件修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃文件修改）
git reset --hard HEAD~1

# 撤销特定文件的修改
git checkout HEAD -- filename.py
```

### 恢复删除的分支
```bash
# 查看引用日志
git reflog

# 恢复分支
git checkout -b recovered-branch <commit-hash>
```

---

**注意**: 这个策略适用于本地开发和管理。如果后续需要与团队协作或使用远程仓库，请参考相应的协作工作流程。
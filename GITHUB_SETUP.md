# GitHub 仓库创建记录

## 📊 仓库信息

- **仓库名称**：talentflow
- **所有者**：vinson1101
- **仓库地址**：https://github.com/vinson1101/talentflow
- **创建时间**：2026年3月22日 15:58
- **可见性**：Public
- **默认分支**：main

## 🎯 初始提交

**Commit ID**: a3f1d1b

**提交信息**:
```
Initial commit: TalentFlow v0.1.0

- 招聘决策流水线系统
- 分层架构：configs/core/adapters/pipelines
- 支持飞书、本地文件适配
- 完整的数据存储、报告生成模块
```

**文件统计**:
- 28个文件
- 3105行代码

## 📁 目录结构

```
talentflow/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── configs/              # 配置文件
├── docs/                 # 文档
├── core/                 # 核心逻辑
├── adapters/             # 数据源适配器
├── pipelines/            # 处理流程
├── runs/                 # 运行记录
├── outputs/              # 最终输出
├── archive/              # 归档文件
└── skills/               # Skill化
```

## 🔐 认证方式

使用 GitHub Personal Access Token 认证：

```bash
# Token存储在 .env 文件
GH_TOKEN=ghp_**************** (已隐藏)

# 认证命令
echo "$GH_TOKEN" | gh auth login --with-token
```

## 📝 后续维护

### 提交新代码
```bash
cd talentflow
git add .
git commit -m "描述信息"
git push
```

### 查看仓库状态
```bash
gh repo view
gh repo view --web
```

### 创建 Release
```bash
gh release create v0.1.0 --title "TalentFlow v0.1.0" --notes "初始版本"
```

## ⭐ 核心特性

1. **分层架构**：清晰的职责分离
2. **多源适配**：支持飞书、本地文件
3. **完整流程**：解析 → 评估 → 存储 → 报告
4. **可扩展**：预留钉钉、Skill化接口

---

**创建者**: HuntMind (AI Agent)
**所有者**: Vinson Sun (vinson1101)
**创建日期**: 2026-03-22

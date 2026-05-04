# Claude 配置 — 工作流集成（精简版）

> 方案 D：按需加载技能  
> 常驻 Token：~500  
> 最后更新：2026-04-30

---

## 核心规则

### 1. Git 同步
```bash
git add . && git commit -m "auto: <描述>" && git push
```

### 2. 文件整理
- 删除重复文件（带 (1)(2) 版本号）
- 分类到：作业/比赛/知识库
- 清理空目录

### 3. Token 策略
- 单次读取 ≤200 行
- 大文件分段读取
- 按需加载 skills

---

## 工作流触发

**机制**：检测关键词 → 读取对应 skill → 执行

**核心 Skills**（9 个）：
1. `exam-prep-workflow` - 考试复习
2. `competition-prep-workflow` - 比赛备赛
3. `data-analysis-workflow` - 数据分析
4. `weekly-planning-workflow` - 周计划
5. `research-paper-workflow-isolated` - 论文写作（隔离）
6. `research-paper-workflow-with-kb` - 论文写作（知识库）
7. `literature-search-workflow` - 文献检索
8. `knowledge-manage-workflow` - 知识管理
9. `feature-design` - 需求设计

**完整列表**：`skills-index.md`

---

## 快捷命令

```bash
# 论文写作
./skills.sh paper <PDF/URL>        # 隔离模式
./skills.sh paper-kb <主题>        # 知识库模式

# 考试比赛
./skills.sh exam <科目> [日期]     # 考试复习
./skills.sh competition <比赛>     # 比赛备赛

# 数据分析
./skills.sh data <文件> [类型]     # 数据分析

# 日常管理
./skills.sh plan [日期]            # 周计划
./skills.sh kb <文件夹>            # 知识管理

# 工具
./skills.sh sync                   # Git 同步
./skills.sh compress <文件>        # 文档压缩
```

---

## 自动化规则

### 文件操作后自动同步 Git
每次创建/修改文件后：
```bash
git add . && git commit && git push
```

### 大文件自动压缩提醒
.md 文件 >500 行 → 提醒使用 `caveman-compress`

---

## 配置文件

| 文件 | 用途 |
|------|------|
| `skills-index.md` | 技能索引表 |
| `skills-trigger-map.md` | 关键词映射 |
| `skills-config.json` | 配置参数 |
| `MEMORY.md` | 用户偏好记忆 |

---

**完整文档**：见 `/workspace/方案 D_*.md`

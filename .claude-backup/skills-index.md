# Skills 索引表

> 版本：v1.0  
> 最后更新：2026-04-30  
> 说明：按需加载技能索引，常驻仅 ~500 tokens

---

## 使用说明

1. 检测用户输入中的关键词
2. 匹配对应的 skill
3. 读取完整 skill 文件
4. 执行工作流

---

## 技能列表

### 📚 学术写作类

| 技能名 | 关键词 | 触发示例 | 置信度 | 文件路径 |
|--------|--------|----------|--------|----------|
| research-paper-isolated | 写论文/写报告/论文写作 | "帮我写论文" | 高 | `skills/research-paper-workflow-isolated/SKILL.md` |
| research-paper-with-kb | 参考知识库/用知识库 | "参考知识库写论文" | 高 | `skills/research-paper-workflow-with-kb/SKILL.md` |
| literature-search | 查文献/找论文/引用格式 | "查找文献" | 高 | `skills/literature-search-workflow/SKILL.md` |

### 🏆 考试比赛类

| 技能名 | 关键词 | 触发示例 | 置信度 | 文件路径 |
|--------|--------|----------|--------|----------|
| exam-prep | 考试/复习/备考/背题 | "帮我复习" | 高 | `skills/exam-prep-workflow/SKILL.md` |
| competition-prep | 比赛/竞赛/学创杯/挑战杯 | "准备比赛" | 高 | `skills/competition-prep-workflow/SKILL.md` |

### 📊 数据分析类

| 技能名 | 关键词 | 触发示例 | 置信度 | 文件路径 |
|--------|--------|----------|--------|----------|
| data-analysis | 数据分析/处理 Excel/财务分析/图表 | "分析这个数据" | 高 | `skills/data-analysis-workflow/SKILL.md` |

### 📚 知识管理类

| 技能名 | 关键词 | 触发示例 | 置信度 | 文件路径 |
|--------|--------|----------|--------|----------|
| knowledge-manage | 整理资料/知识库/批量处理 | "整理这些文件" | 中 | `skills/knowledge-manage-workflow/SKILL.md` |

### 💼 项目管理类

| 技能名 | 关键词 | 触发示例 | 置信度 | 文件路径 |
|--------|--------|----------|--------|----------|
| feature-design | 需求分析/功能设计/写需求文档 | "设计一个功能" | 中 | `skills/feature-design/SKILL.md` |

### 📅 日常管理类

| 技能名 | 关键词 | 触发示例 | 置信度 | 文件路径 |
|--------|--------|----------|--------|----------|
| weekly-planning | 周计划/计划/日程安排/周回顾 | "制定计划" | 中 | `skills/weekly-planning-workflow/SKILL.md` |

### 🔧 工具类

| 技能名 | 关键词 | 触发示例 | 置信度 | 文件路径 |
|--------|--------|----------|--------|----------|
| git-sync | git/同步/commit/push | "提交代码" | 高 | `skills/git-sync.card` |
| file-organize | 整理文件/删除重复 | "整理工作区" | 中 | `skills/file-organize.card` |
| doc-compress | 压缩文档/节省 token | "压缩这个文件" | 高 | `skills/doc-compress.card` |

---

## 完整技能清单（88 个）

> 以下是完整列表，按需加载

### 核心技能（常驻卡片）
| 技能名 | 类别 | 文件路径 |
|--------|------|----------|
| exam-prep-workflow | 考试比赛 | `skills/exam-prep-workflow/SKILL.md` |
| competition-prep-workflow | 考试比赛 | `skills/competition-prep-workflow/SKILL.md` |
| data-analysis-workflow | 数据分析 | `skills/data-analysis-workflow/SKILL.md` |
| weekly-planning-workflow | 日常管理 | `skills/weekly-planning-workflow/SKILL.md` |
| research-paper-workflow-isolated | 学术写作 | `skills/research-paper-workflow-isolated/SKILL.md` |
| research-paper-workflow-with-kb | 学术写作 | `skills/research-paper-workflow-with-kb/SKILL.md` |
| literature-search-workflow | 学术写作 | `skills/literature-search-workflow/SKILL.md` |
| knowledge-manage-workflow | 知识管理 | `skills/knowledge-manage-workflow/SKILL.md` |
| feature-design | 项目管理 | `skills/feature-design/SKILL.md` |
| git-sync | 工具 | `skills/git-sync.card` |

### 工作流技能
| 技能名 | 文件路径 |
|--------|----------|
| feature-implementer | `skills/feature-implementer/SKILL.md` |
| software-dev-workflow | `skills/software-dev-workflow/SKILL.md` |
| debug-troubleshoot-workflow | `skills/debug-troubleshoot-workflow/SKILL.md` |
| content-publish-workflow | `skills/content-publish-workflow/SKILL.md` |

### 文档处理
| 技能名 | 文件路径 |
|--------|----------|
| pdf | `skills/pdf/SKILL.md` |
| docx | `skills/docx/SKILL.md` |
| xlsx | `skills/xlsx/SKILL.md` |
| pptx | `skills/pptx/SKILL.md` |
| doc-coauthoring | `skills/doc-coauthoring/SKILL.md` |

### 内容创作（Baoyu 系列）
| 技能名 | 文件路径 |
|--------|----------|
| baoyu-translate | `skills/baoyu-translate/SKILL.md` |
| baoyu-format-markdown | `skills/baoyu-format-markdown/SKILL.md` |
| baoyu-markdown-to-html | `skills/baoyu-markdown-to-html/SKILL.md` |
| baoyu-url-to-markdown | `skills/baoyu-url-to-markdown/SKILL.md` |
| baoyu-youtube-transcript | `skills/baoyu-youtube-transcript/SKILL.md` |
| baoyu-diagram | `skills/baoyu-diagram/SKILL.md` |
| baoyu-infographic | `skills/baoyu-infographic/SKILL.md` |
| baoyu-article-illustrator | `skills/baoyu-article-illustrator/SKILL.md` |
| baoyu-cover-image | `skills/baoyu-cover-image/SKILL.md` |
| baoyu-image-gen | `skills/baoyu-image-gen/SKILL.md` |
| baoyu-imagine | `skills/baoyu-imagine/SKILL.md` |
| baoyu-comic | `skills/baoyu-comic/SKILL.md` |
| baoyu-slide-deck | `skills/baoyu-slide-deck/SKILL.md` |
| baoyu-post-to-wechat | `skills/baoyu-post-to-wechat/SKILL.md` |
| baoyu-post-to-weibo | `skills/baoyu-post-to-weibo/SKILL.md` |
| baoyu-post-to-x | `skills/baoyu-post-to-x/SKILL.md` |

### 前端开发
| 技能名 | 文件路径 |
|--------|----------|
| frontend-design | `skills/frontend-design/SKILL.md` |
| frontend-project-creator | `skills/frontend-project-creator/SKILL.md` |
| ui-ux-pro-max | `skills/ui-ux-pro-max/SKILL.md` |
| design-system-patterns | `skills/design-system-patterns/SKILL.md` |
| tailwindcss-helper | `skills/tailwindcss-helper/SKILL.md` |
| shadcnui-helper | `skills/shadcnui-helper/SKILL.md` |
| mui-helper | `skills/mui-helper/SKILL.md` |
| deploy-website | `skills/deploy-website/SKILL.md` |
| react-code-fix-linter | `skills/react-code-fix-linter/SKILL.md` |
| react-native-ui-animation | `skills/react-native-ui-animation/SKILL.md` |

### 后端开发
| 技能名 | 文件路径 |
|--------|----------|
| golang-patterns | `skills/golang-patterns/SKILL.md` |
| golang-testing | `skills/golang-testing/SKILL.md` |
| golang-code-review | `skills/golang-code-review/SKILL.md` |

### 项目管理
| 技能名 | 文件路径 |
|--------|----------|
| implementation-planner | `skills/implementation-planner/SKILL.md` |
| executing-plans | `skills/executing-plans/SKILL.md` |
| finishing-a-development-branch | `skills/finishing-a-development-branch/SKILL.md` |
| project-wiki | `skills/project-wiki/SKILL.md` |

### 其他工具
| 技能名 | 文件路径 |
|--------|----------|
| brainstorming | `skills/brainstorming/SKILL.md` |
| skill-creator | `skills/skill-creator/SKILL.md` |
| mcp-builder | `skills/mcp-builder/SKILL.md` |
| dispatching-parallel-agents | `skills/dispatching-parallel-agents/SKILL.md` |
| subagent-driven-development | `skills/subagent-driven-development/SKILL.md` |
| systematic-debugging | `skills/systematic-debugging/SKILL.md` |
| security-review-audit | `skills/security-review-audit/SKILL.md` |
| test-driven-development | `skills/test-driven-development/SKILL.md` |
| verification-before-completion | `skills/verification-before-completion/SKILL.md` |
| requesting-code-review | `skills/requesting-code-review/SKILL.md` |
| receiving-code-review | `skills/receiving-code-review/SKILL.md` |

### Caveman 系列
| 技能名 | 文件路径 |
|--------|----------|
| caveman-commit | `skills/caveman-commit/SKILL.md` |
| caveman-compress | `skills/caveman-compress/SKILL.md` |
| caveman-review | `skills/caveman-review/SKILL.md` |
| caveman | `skills/caveman/SKILL.md` |

### 构建与检查
| 技能名 | 文件路径 |
|--------|----------|
| build | `skills/build/SKILL.md` |
| check | `skills/check/SKILL.md` |
| spec | `skills/spec/SKILL.md` |
| backprop | `skills/backprop/SKILL.md` |

### 写作技能
| 技能名 | 文件路径 |
|--------|----------|
| writing-skills | `skills/writing-skills/SKILL.md` |
| writing-plans | `skills/writing-plans/SKILL.md` |

### PUA 系列
| 技能名 | 文件路径 |
|--------|----------|
| pua | `skills/pua/SKILL.md` |

### 企业开发
| 技能名 | 文件路径 |
|--------|----------|
| corporate-website-dev | `skills/corporate-website-dev/SKILL.md` |

### 其他
| 技能名 | 文件路径 |
|--------|----------|
| bootstrap-helper | `skills/bootstrap-helper/SKILL.md` |
| web-artifacts-builder | `skills/web-artifacts-builder/SKILL.md` |
| webapp-testing | `skills/webapp-testing/SKILL.md` |
| web-component-design-architecture | `skills/web-component-design-architecture/SKILL.md` |
| visual-design-foundations | `skills/visual-design-foundations/SKILL.md` |
| using-superpowers | `skills/using-superpowers/SKILL.md` |
| using-git-worktrees | `skills/using-git-worktrees/SKILL.md` |
| verification-before-completion | `skills/verification-before-completion/SKILL.md` |

---

## 统计

- **技能总数**：88 个
- **常驻索引行数**：~200 行
- **预估 Token**：~500

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-04-30 | 初始版本，创建索引表 |

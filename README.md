# PBL项目实践报告

## 项目简介
本项目是基于PBL（Project-Based Learning）模式的实践报告，旨在通过实际项目开发提升学生的综合能力。

## 技术栈

### 后端
- 框架：Python Django
- 语言：Python

### 前端
- 框架：Vue3.js
- 语言：JavaScript/TypeScript

### 数据库
- MySQL

### 版本控制
- Git + GitHub

## 推荐项目类型

以下是推荐的项目类型，选择其中一种进行开发：

1. **学生成绩管理系统**
   - 核心表：users, admins, students, courses, grades
   - 功能：学生信息管理、课程管理、成绩录入与查询

2. **图书馆管理系统**
   - 核心表：users, admins, books, borrow_records, categories
   - 功能：图书管理、借阅记录管理、分类管理

3. **课程选课系统**
   - 核心表：users, admins, courses, course_selection, teachers
   - 功能：课程管理、选课管理、教师管理

4. **文章评论系统**
   - 核心表：users, admins, articles, comments, categories
   - 功能：文章管理、评论管理、分类管理

5. **项目任务管理系统**
   - 核心表：users, admins, projects, tasks, teams
   - 功能：项目管理、任务分配、团队管理

## 仓库文件结构

按照PBL项目实践报告要求，仓库文件结构如下：

```
├── database/           # 数据库相关文件
│   └── database.sql    # 数据库建表语句
├── docs/               # 项目文档
│   ├── README.md       # 项目说明文档
│   ├── 技术要求.md     # 技术要求文档
│   └── PBL项目实践报告评分标准.pdf # 评分标准
├── screenshots/        # 项目截图
├── src/                # 源代码
│   ├── backend/        # 后端代码（Django）
│   └── frontend/       # 前端代码（Vue）
└── README.md           # 项目根目录README
```

## 开发流程

1. 选择项目类型
2. 设计数据库结构
3. 实现后端API
4. 开发前端页面
5. 测试与优化
6. 提交代码与文档

## 评分标准

详见 `docs/PBL项目实践报告评分标准.pdf`

## 团队协作

- 使用GitHub进行版本控制
- 合理使用Issues管理任务
- 采用Pull Request进行代码审查
- 使用Project Board管理项目进度

## 注意事项

1. 代码规范遵循相关语言标准
2. 定期提交代码，保持良好的 commit 记录
3. 完善项目文档
4. 注重代码安全性和性能

## 联系方式

如有问题，请联系项目指导老师。
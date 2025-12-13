# 图书管理系统 Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- 实现完整的用户认证系统，包括注册、登录和权限管理
- 提供全面的图书管理功能，支持CRUD操作和高级搜索
- 建立高效的借阅管理系统，自动跟踪图书状态和借阅记录
- 实现管理员和普通用户的权限分离，确保数据安全
- 创建直观易用的用户界面，提升用户体验

### Background Context

当前许多小型图书馆和图书室仍在使用手动或Excel表格管理图书，导致管理效率低下、用户体验差、数据安全风险高等问题。本系统旨在通过现代化的Web技术栈（Vue3 + Flask + SQLite）提供一个完整的数字化图书管理解决方案，帮助图书馆实现数字化转型，提高管理效率和服务质量。

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-12-09 | 1.0 | Initial PRD creation | John (PM) |

## Requirements

### Functional

FR1: 用户可以通过用户名和邮箱进行注册，系统需要验证输入数据的唯一性和有效性
FR2: 用户可以使用用户名/邮箱和密码进行登录，系统生成JWT token用于会话管理
FR3: 系统支持管理员和普通用户两种角色，具有不同的操作权限
FR4: 管理员可以查看、创建、更新和删除所有用户信息
FR5: 普通用户只能查看和更新自己的个人信息
FR6: 管理员可以对图书进行完整的CRUD操作，包括添加、查询、更新和删除图书记录
FR7: 系统支持按书名、作者、分类和ISBN等多种条件搜索图书
FR8: 用户可以查看图书详情，包括基本信息、库存数量和当前借阅状态
FR9: 用户可以进行借书操作，系统自动更新图书可用数量和借阅记录
FR10: 用户可以进行还书操作，系统更新借阅记录状态并计算可能的罚金
FR11: 系统自动计算和管理逾期图书的罚金
FR12: 用户可以查看自己的借阅历史和当前借阅状态
FR13: 管理员可以查看所有用户的借阅记录和系统借阅统计
FR14: 系统支持图书分类管理，包括多级分类结构
FR15: 用户可以对已读图书进行评分和评论

### Non Functional

NFR1: 系统必须支持至少50个并发用户同时在线操作
NFR2: 所有API响应时间必须在500毫秒以内
NFR3: 页面加载时间必须控制在2秒以内
NFR4: 用户密码必须使用bcrypt加密存储，salt rounds不少于10
NFR5: JWT token必须在合理时间内自动过期
NFR6: 系统必须防止SQL注入、XSS等常见Web安全漏洞
NFR7: 数据库操作必须保证事务一致性，特别是在借阅操作中
NFR8: 系统界面必须响应式设计，支持主流浏览器和设备
NFR9: 系统必须提供完整的错误处理和用户友好的错误提示
NFR10: 数据库文件必须定期备份，确保数据安全

## User Interface Design Goals

### Overall UX Vision

创建一个现代化、直观且高效的图书管理界面，让用户能够快速找到所需功能，管理员能够高效完成日常工作。界面设计简洁明了，避免不必要的复杂性，同时保持专业性和易用性。

### Key Interaction Paradigms

- **仪表板驱动**: 登录后直接显示相关的核心功能和关键信息
- **快速搜索**: 顶部搜索栏提供即时搜索建议和筛选
- **表格视图**: 管理界面使用表格展示，支持排序、筛选和批量操作
- **模态对话框**: 增删改操作使用模态对话框，保持页面上下文
- **卡片布局**: 图书展示使用卡片布局，直观显示封面和基本信息

### Core Screens and Views

- **登录/注册页面**: 简洁的双栏布局，左侧系统介绍，右侧表单
- **管理员仪表板**: 系统概览、快速统计、待处理事项
- **用户仪表板**: 个人信息、当前借阅、借阅历史
- **图书管理页面**: 图书列表、搜索筛选、添加/编辑功能
- **用户管理页面**: 用户列表、角色管理、账户状态
- **借阅管理页面**: 当前借阅、借阅历史、逾期管理
- **图书详情页面**: 完整信息、借阅状态、用户评论

### Accessibility: WCAG AA

系统必须达到WCAG AA级别的可访问性标准，确保所有用户都能正常使用，包括：
- 适当的颜色对比度
- 键盘导航支持
- 屏幕阅读器兼容
- 语义化HTML结构

### Branding

采用现代化图书馆的视觉风格：
- 主色调：深蓝色（专业、可信）和米白色（温暖、友好）
- 辅助色：绿色（成功）、橙色（警告）、红色（错误）
- 字体：系统默认字体，确保跨平台一致性
- 图标：使用简洁的线性图标风格

### Target Device and Platforms: Web Responsive

系统采用响应式设计，支持：
- 桌面端：1920x1080及以上分辨率
- 平板端：768px-1024px分辨率
- 手机端：320px-768px分辨率
- 支持Chrome、Firefox、Safari、Edge等主流浏览器

## Technical Assumptions

### Repository Structure: Monorepo

采用单仓库结构，包含前端和后端代码：
```
library-management-system/
├── backend/          # Flask API
├── frontend/         # Vue3 前端
├── database/         # SQLite数据库文件
├── docs/            # 项目文档
└── tests/           # 测试文件
```

### Service Architecture

采用**前后端分离的单体架构**：
- 前端：Vue3 SPA，使用Composition API
- 后端：Flask RESTful API
- 数据库：SQLite，适合中小型应用
- 认证：JWT token认证机制

### Testing Requirements

采用**完整的测试金字塔**策略：
- 单元测试：Vue Test Utils（前端）+ pytest（后端）
- 集成测试：API端点测试，数据库操作测试
- E2E测试：关键用户流程测试
- 手动测试：提供测试用的便捷功能（如快速填充数据）

### Additional Technical Assumptions and Requests

- **前端技术栈**：Vue 3 + Vue Router + Pinia + Element Plus + Axios
- **后端技术栈**：Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-CORS
- **数据库设计**：5张核心表（Users、Books、Categories、BorrowRecords、Reviews）
- **开发环境**：支持热重载的开发服务器
- **生产部署**：Nginx + Gunicorn + Linux服务器
- **代码规范**：ESLint（前端）、Black（后端）
- **版本控制**：Git，采用GitFlow工作流

## Epic List

### Epic 1: Foundation & Core Infrastructure
建立项目基础架构、数据库设计和用户认证系统

### Epic 2: Core Business Entities
实现图书、分类和用户的核心管理功能

### Epic 3: Borrowing System
构建完整的借阅管理系统，包括借书、还书和逾期管理

### Epic 4: User Experience Enhancement
完善用户界面、搜索功能和系统优化

## Epic 1: Foundation & Core Infrastructure

**Epic Goal**: 建立项目的完整技术基础，包括前后端项目结构、数据库设计、用户认证系统和基础的API框架。这个史诗为整个应用奠定坚实的技术基础，确保后续功能的开发可以在稳固的基础上进行。

### Story 1.1 项目初始化和基础架构搭建

As a 开发团队,
I want 建立完整的项目结构和开发环境,
so that we can 开始高效的功能开发.

**Acceptance Criteria:**
1: 创建Monorepo结构的项目目录，包含backend、frontend、database、docs和tests文件夹
2: 初始化Vue3前端项目，配置Vue Router、Pinia和Element Plus
3: 初始化Flask后端项目，配置Flask-SQLAlchemy、Flask-JWT-Extended和Flask-CORS
4: 配置开发环境的热重载和调试功能
5: 设置ESLint、Black等代码规范工具
6: 创建基础的README.md和开发文档

### Story 1.2 数据库设计和模型创建

As a 开发团队,
I want 创建完整的数据库模型和迁移脚本,
so that we can 建立稳定的数据存储基础.

**Acceptance Criteria:**
1: 创建Users表模型，包含id、username、password、email、role、created_at、is_active字段
2: 创建Books表模型，包含id、isbn、title、author、publisher、publish_date、category_id、total_copies、available_copies、created_at字段
3: 创建Categories表模型，支持多级分类结构
4: 创建BorrowRecords表模型，包含完整的借阅信息字段
5: 创建Reviews表模型，支持用户评分和评论
6: 编写数据库初始化脚本和测试数据
7: 配置外键约束和数据验证规则

### Story 1.3 用户认证系统实现

As a 用户,
I want 能够注册、登录和管理我的账户,
so that I can 安全地使用系统功能.

**Acceptance Criteria:**
1: 实现用户注册API，包括输入验证和唯一性检查
2: 实现用户登录API，支持用户名/邮箱登录
3: 使用bcrypt加密存储用户密码
4: 实现JWT token生成和验证机制
5: 创建权限装饰器区分管理员和普通用户
6: 实现用户登出和token刷新功能
7: 创建登录和注册的前端页面和表单验证

### Story 1.4 API基础框架和权限控制

As a 开发团队,
I want 建立RESTful API框架和权限控制,
so that we can 安全地提供数据服务.

**Acceptance Criteria:**
1: 设计RESTful API的URL结构和响应格式
2: 实现统一的错误处理和响应格式
3: 创建API路由的前端拦截器，自动添加token
4: 实现基于角色的API访问控制
5: 创建API文档（使用Swagger或类似工具）
6: 实现CORS配置，支持跨域请求
7: 添加API请求日志记录

## Epic 2: Core Business Entities

**Epic Goal**: 实现系统的核心业务实体管理，包括图书管理、分类管理和用户管理功能。这个史诗让管理员能够有效地管理图书资源，用户能够浏览和搜索图书，为后续的借阅功能提供数据基础。

### Story 2.1 图书分类管理

As a 管理员,
I want 管理图书分类,
so that 我可以更好地组织和展示图书资源.

**Acceptance Criteria:**
1: 实现分类的CRUD API接口
2: 支持多级分类结构（父子分类关系）
3: 创建分类管理的前端页面
4: 实现分类的树形展示和编辑功能
5: 添加分类使用统计功能
6: 防止删除已有图书的分类
7: 支持分类的排序和搜索

### Story 2.2 图书信息管理

As a 管理员,
I want 管理图书的基本信息,
so that 我可以维护完整的图书库.

**Acceptance Criteria:**
1: 实现图书的CRUD API接口
2: 支持ISBN验证和重复检查
3: 创建图书管理页面，支持表格视图和卡片视图
4: 实现批量导入图书功能（Excel/CSV）
5: 添加图书封面图片上传和管理
6: 实现图书信息的批量编辑功能
7: 创建图书详情展示页面

### Story 2.3 图书搜索和筛选

As a 用户,
I want 搜索和筛选图书,
so that 我可以快速找到需要的图书.

**Acceptance Criteria:**
1: 实现多字段搜索（书名、作者、ISBN、分类）
2: 支持高级筛选条件（出版日期、可用性等）
3: 创建搜索历史和热门搜索功能
4: 实现搜索结果的排序和分页
5: 添加搜索建议和自动完成功能
6: 创建分类筛选和标签筛选
7: 保存用户的搜索偏好设置

### Story 2.4 用户账户管理

As a 管理员,
I want 管理用户账户,
so that 我可以维护系统的用户安全.

**Acceptance Criteria:**
1: 实现用户列表的查看、搜索和筛选
2: 支持用户信息的编辑和角色管理
3: 创建用户账户启用/禁用功能
4: 实现密码重置功能（管理员操作）
5: 添加用户操作日志记录
6: 创建用户统计和报表功能
7: 支持批量用户操作（导出、通知等）

## Epic 3: Borrowing System

**Epic Goal**: 构建完整的借阅管理系统，实现图书借阅、归还、续借和逾期管理的自动化。这个史诗是系统的核心功能，让用户能够方便地借阅图书，让管理员能够高效地管理借阅流程。

### Story 3.1 借书功能实现

As a 用户,
I want 借阅图书,
so that 我可以阅读和使用图书资源.

**Acceptance Criteria:**
1: 实现借书API，自动更新图书可用数量
2: 创建借书确认界面，显示借阅期限和规则
3: 检查用户借阅资格（借阅数量限制、信用状态等）
4: 生成借阅记录并发送确认通知
5: 更新图书状态为"已借出"
6: 记录借阅操作日志
7: 防止重复借阅同一本图书

### Story 3.2 还书功能实现

As a 用户,
I want 归还图书,
so that 我可以完成借阅周期并可能借阅其他图书.

**Acceptance Criteria:**
1: 实现还书API，更新图书可用数量
2: 创建还书确认界面，显示借阅详情
3: 自动计算逾期天数和罚金金额
4: 更新借阅记录状态为"已归还"
5: 发送还书成功通知
6: 记录还书操作和罚金信息
7: 支持批量还书操作

### Story 3.3 逾期管理和罚金计算

As a 管理员,
I want 管理逾期图书和罚金,
so that 我可以维护借阅秩序和及时归还.

**Acceptance Criteria:**
1: 实现逾期状态自动检测（定时任务）
2: 创建罚金计算规则和配置
3: 生成逾期通知和提醒邮件
4: 创建逾期图书管理页面
5: 支持罚金减免和特殊处理
6: 实现罚金缴纳记录功能
7: 生成逾期报告和统计

### Story 3.4 借阅历史和统计

As a 用户,
I want 查看我的借阅历史,
so that 我可以了解我的阅读习惯.

**Acceptance Criteria:**
1: 实现个人借阅历史查询
2: 显示当前借阅状态和应还日期
3: 创建借阅统计图表（月度、年度等）
4: 支持借阅记录的导出功能
5: 添加阅读推荐和评分提醒
6: 创建阅读成就和徽章系统
7: 实现借阅偏好的个性化推荐

### Story 3.5 管理员借阅管理

As a 管理员,
I want 管理所有用户的借阅记录,
so that 我可以进行系统管理和分析.

**Acceptance Criteria:**
1: 创建全系统借阅记录查看和搜索
2: 实现借阅统计和报表生成
3: 支持特殊情况的处理（挂失、损坏等）
4: 创建借阅规则配置界面
5: 实现批量借阅操作（班级借阅等）
6: 添加借阅高峰时段分析
7: 创建热门图书和借阅排行榜

## Epic 4: User Experience Enhancement

**Epic Goal**: 完善用户界面体验、高级搜索功能和系统性能优化，提供现代化的用户体验。这个史诗专注于提升系统的易用性、美观性和响应速度，确保用户获得最佳的使用体验。

### Story 4.1 用户界面优化和响应式设计

As a 用户,
I want 在各种设备上都有良好的使用体验,
so that 我可以随时随地访问系统.

**Acceptance Criteria:**
1: 优化所有页面的响应式布局
2: 实现移动端特有的交互设计（滑动、下拉刷新等）
3: 创建加载动画和骨架屏提升感知性能
4: 优化表单设计和错误提示
5: 实现主题切换（明暗主题）
6: 添加无障碍访问支持
7: 优化打印样式和导出功能

### Story 4.2 高级搜索和推荐系统

As a 用户,
I want 获得智能的搜索结果和推荐,
so that 我可以更快地找到感兴趣的图书.

**Acceptance Criteria:**
1: 实现全文搜索和模糊匹配
2: 添加基于用户行为的个性化推荐
3: 创建相似图书推荐功能
4: 实现基于借阅历史的阅读建议
5: 添加热门标签和趋势分析
6: 创建图书对比功能
7: 实现保存搜索条件和订阅功能

### Story 4.3 系统通知和消息中心

As a 用户,
I want 接收重要的系统通知,
so that 我可以及时了解我的借阅状态.

**Acceptance Criteria:**
1: 创建消息中心，显示各类通知
2: 实现借阅到期提醒通知
3: 添加新书上架通知功能
4: 创建预约图书可用通知
5: 实现邮件和站内信通知
6: 添加通知偏好设置
7: 创建系统公告发布功能

### Story 4.4 报表和数据分析

As a 管理员,
I want 查看详细的系统分析报表,
so that 我可以做出数据驱动的决策.

**Acceptance Criteria:**
1: 创建仪表板，显示关键指标
2: 实现图书流通分析报表
3: 添加用户行为分析功能
4: 创建借阅趋势预测
5: 实现自定义报表生成器
6: 添加数据可视化图表
7: 支持报表导出（PDF、Excel）

### Story 4.5 系统设置和配置

As a 管理员,
I want 配置系统的各项参数,
so that 我可以根据实际需求调整系统.

**Acceptance Criteria:**
1: 创建系统设置页面
2: 实现借阅规则配置（期限、数量限制等）
3: 添加罚金规则设置
4: 创建邮件模板配置
5: 实现系统参数管理
6: 添加备份和恢复功能
7: 创建系统日志查看功能

## Checklist Results Report

[待PM checklist执行后填充]

## Next Steps

### UX Expert Prompt

基于此PRD文档，请创建完整的UX/UI设计方案，包括：
1. 用户流程图和交互设计
2. 详细的页面线框图和原型
3. 设计系统和组件库规范
4. 可访问性合规方案
5. 移动端适配策略

### Architect Prompt

基于此PRD文档，请创建详细的系统架构设计，包括：
1. 数据库ER图和详细设计
2. API接口规范文档
3. 前后端技术架构方案
4. 部署和运维策略
5. 安全架构和合规方案
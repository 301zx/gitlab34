# Project Brief: 图书管理系统 (Vue3 + Flask + SQLite)

## Executive Summary

本项目旨在开发一个基于Web的现代化图书管理系统，采用Vue3前端框架、Flask后端API和SQLite数据库。系统将提供完整的用户管理、图书管理和借阅管理功能，实现管理员和普通用户的权限分离，确保数据安全性和系统易用性。

## Problem Statement

当前许多小型图书馆和图书室仍在使用手动或Excel表格管理图书，存在以下问题：

- **管理效率低下**：手动记录借阅信息，容易出错且耗时
- **用户体验差**：用户需要亲自到图书馆查询图书 availability
- **数据安全风险**：纸质记录容易丢失或损坏
- **统计困难**：难以生成借阅统计和图书流通分析报告
- **权限管理缺失**：缺乏有效的用户权限控制机制

## Proposed Solution

开发一个基于Web的图书管理系统，提供以下核心价值：

- **数字化管理**：完全数字化的图书和借阅记录管理
- **权限分离**：管理员和普通用户拥有不同的操作权限
- **用户友好界面**：基于Vue3的现代化响应式界面
- **实时数据同步**：即时更新图书状态和借阅信息
- **完整的数据操作**：所有数据表均支持完整的CRUD操作

## Target Users

### Primary User Segment: 系统管理员

- **Profile**: 图书管理员、系统管理员
- **职责**: 管理图书信息、用户账户、借阅记录
- **需求**: 高效的数据管理、统计报表、系统维护

### Secondary User Segment: 普通用户

- **Profile**: 读者、学生、研究人员
- **行为**: 查询图书、借阅图书、管理个人信息
- **目标**: 方便快捷地查找和借阅图书

## Technical Stack Requirements

### 前端技术栈
- **Vue 3**: 使用 Composition API 构建响应式界面
- **Vue Router**: 实现单页应用路由
- **Pinia**: 状态管理
- **Element Plus 或 Ant Design Vue**: UI组件库
- **Axios**: HTTP请求库

### 后端技术栈
- **Flask**: Web框架
- **Flask-SQLAlchemy**: ORM数据库操作
- **Flask-Login**: 用户认证
- **Flask-JWT-Extended**: JWT token认证
- **Flask-CORS**: 跨域请求支持

### 数据库
- **SQLite**: 轻量级关系型数据库
- **至少5张数据表**: 用户表、图书表、借阅记录表、分类表、评论表

## Database Schema Design

### 核心数据表

1. **Users (用户表)**
   - id (主键)
   - username (用户名)
   - password (密码)
   - email (邮箱)
   - role (角色: admin/user)
   - created_at (创建时间)
   - is_active (是否激活)

2. **Books (图书表)**
   - id (主键)
   - isbn (ISBN号)
   - title (书名)
   - author (作者)
   - publisher (出版社)
   - publish_date (出版日期)
   - category_id (分类ID, 外键)
   - total_copies (总册数)
   - available_copies (可借册数)
   - created_at (添加时间)

3. **Categories (分类表)**
   - id (主键)
   - name (分类名称)
   - description (分类描述)
   - parent_id (父分类ID, 支持多级分类)

4. **BorrowRecords (借阅记录表)**
   - id (主键)
   - user_id (用户ID, 外键)
   - book_id (图书ID, 外键)
   - borrow_date (借阅日期)
   - due_date (应还日期)
   - return_date (实际归还日期)
   - status (状态: borrowed/returned/overdue)
   - fine_amount (罚金金额)

5. **Reviews (评论表)**
   - id (主键)
   - user_id (用户ID, 外键)
   - book_id (图书ID, 外键)
   - rating (评分 1-5)
   - comment (评论内容)
   - created_at (评论时间)

## MVP Scope

### 核心功能 (必须实现)

1. **用户认证系统**
   - 用户注册：表单验证、重复用户名检查
   - 用户登录：JWT token认证、记住登录状态
   - 密码加密：使用bcrypt加密存储密码
   - 登出功能：清除token状态

2. **权限管理系统**
   - 管理员权限：管理所有用户、管理所有业务数据
   - 普通用户权限：只能查看和修改自己的数据
   - 路由守卫：根据用户角色控制页面访问
   - API权限：基于角色的API访问控制

3. **图书管理 (完整CRUD)**
   - 添加新书记录
   - 查询图书（按书名、作者、分类）
   - 更新图书信息
   - 删除图书记录
   - 图书状态管理

4. **借阅管理 (完整CRUD)**
   - 借书操作：更新图书可用数量
   - 还书操作：更新借阅记录状态
   - 查看借阅历史
   - 逾期管理和罚金计算
   - 当前借阅查询

5. **用户管理 (完整CRUD) - 仅管理员**
   - 查看所有用户列表
   - 更新用户信息
   - 禁用/启用用户账户
   - 用户角色管理

### Out of Scope for MVP

- 邮件通知功能
- 高级报表和数据分析
- 图书推荐系统
- 移动端适配
- 多语言支持

### MVP Success Criteria

- 所有5张数据表均实现完整的CRUD操作
- 用户注册和登录流程完全可用
- 权限分离正确实现，普通用户无法访问管理员功能
- 至少成功支持100个图书记录和20个用户并发操作

## Detailed Feature Specifications

### 用户注册功能
```
注册表单字段：
- 用户名（必填，3-20字符，唯一性检查）
- 邮箱（必填，格式验证，唯一性检查）
- 密码（必填，8-50字符，强度验证）
- 确认密码（必填，密码匹配验证）
- 用户角色（管理员可指定，默认为普通用户）

后端处理：
- 输入验证和清理
- 密码加密存储
- 返回JWT token
- 创建用户默认配置
```

### 用户登录功能
```
登录流程：
1. 输入用户名/邮箱和密码
2. 后端验证凭据
3. 生成JWT token（包含用户ID和角色）
4. 前端存储token
5. 根据角色跳转到对应页面

安全措施：
- 密码错误次数限制
- Token自动过期机制
- 刷新token机制
```

### 权限分离实现
```
前端权限控制：
- 路由守卫：检查meta.roles
- 组件内权限：v-if指令控制元素显示
- API请求：自动添加token

后端权限控制：
- 装饰器验证用户角色
- 数据访问权限检查
- 操作日志记录
```

## Implementation Plan

### Phase 1: 基础架构搭建 (1-2周)
1. 项目初始化和环境配置
2. 数据库设计和迁移脚本
3. 基础API框架搭建
4. Vue项目结构和路由配置

### Phase 2: 用户认证系统 (1周)
1. 用户注册API开发
2. 用户登录API开发
3. JWT认证中间件
4. 前端登录/注册页面开发

### Phase 3: 核心业务功能 (2-3周)
1. 图书管理CRUD API和页面
2. 借阅管理CRUD API和页面
3. 用户管理API（管理员）
4. 权限控制完善

### Phase 4: 测试和优化 (1周)
1. 单元测试编写
2. 集成测试
3. 性能优化
4. 部署准备

## Technical Considerations

### 安全性要求
- 密码使用bcrypt加密（至少10轮salt）
- JWT token设置合理过期时间
- API输入验证和SQL注入防护
- XSS攻击防护
- CORS配置

### 性能要求
- 页面加载时间 < 2秒
- API响应时间 < 500ms
- 支持50+并发用户
- 数据库查询优化

### 数据完整性
- 外键约束
- 数据验证规则
- 事务处理（借阅操作）
- 数据备份策略

## Testing Strategy

### 单元测试
- 前端组件测试（Vue Test Utils）
- 后端API测试（pytest）
- 数据库模型测试
- 工具函数测试

### 集成测试
- 用户注册登录流程
- 借阅还书流程
- 权限控制测试
- 数据CRUD操作测试

### 用户测试
- 管理员操作流程测试
- 普通用户操作流程测试
- 边界情况测试
- 错误处理测试

## Deployment Plan

### 开发环境
- Windows 10/11
- Python 3.8+
- Node.js 16+
- VS Code + Vue/Python插件

### 生产环境
- Linux服务器（推荐Ubuntu 20.04）
- Nginx反向代理
- Gunicorn WSGI服务器
- SQLite数据库文件定期备份

## Success Metrics

### 技术指标
- 代码覆盖率 > 80%
- API响应时间 < 500ms
- 页面加载时间 < 2秒
- 零严重安全漏洞

### 功能指标
- 所有CRUD操作正常工作
- 权限控制100%正确
- 用户认证成功率 > 99%
- 数据完整性100%

## Next Steps

### Immediate Actions

1. **环境准备**
   - 安装Python开发环境
   - 设置Node.js和npm
   - 配置VS Code开发环境
   - 创建Git仓库

2. **项目初始化**
   - 创建Flask项目结构
   - 初始化Vue3项目
   - 配置SQLite数据库
   - 设置开发工具

3. **数据库设计**
   - 编写SQLAlchemy模型
   - 创建数据库迁移脚本
   - 准备测试数据
   - 设计API接口规范

4. **开发计划**
   - 制定详细开发时间表
   - 设置代码规范
   - 配置自动化测试
   - 准备部署文档

### PM Handoff

This Project Brief provides the full context for 图书管理系统. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.

PRD should include:
- Detailed API specifications
- UI/UX mockups and wireframes
- Database schema diagrams
- Security implementation details
- Testing requirements and acceptance criteria
# 三、DEVELOPMENT_PLAN.md（中文完整版）

（结构清晰，逐 Issue 推进，包含验收标准与回退点）


# EbbVocab 开发计划

目标：构建可部署给朋友使用的多用户背单词系统。

## 执行进度

- [x] Issue 0：项目结构与文档初始化
- [x] Issue 1：后端基础结构（2026-03-01）
- [x] Issue 2：用户系统（2026-03-01）
- [x] Issue 3：Deck 与 Word CRUD（2026-03-01）
- [ ] Issue 4：复习调度系统
- [ ] Issue 5：统计接口
- [ ] Issue 6：前端登录与路由
- [ ] Issue 7：前端 CRUD 页面
- [ ] Issue 8：复习页面
- [ ] Issue 9：统计页面
- [ ] Issue 10：Docker 与部署

---

## Issue 0：项目结构与文档初始化

内容：
- 创建 frontend / backend 目录
- 编写三份中文文档

验收：
- 文档齐全

回退点：
- v0-docs

---

## Issue 1：后端基础结构

内容：
- FastAPI 初始化
- 环境变量管理
- 数据库连接
- Alembic 初始化
- /health 接口

验收：
- 服务可启动
- alembic 正常

回退点：
- v1-backend

---

## Issue 2：用户系统

内容：
- User 模型
- 注册
- 登录
- JWT 生成
- 鉴权依赖

验收：
- 可注册登录
- 密码错误拒绝
- 受保护接口必须带 token

回退点：
- v2-auth

---

## Issue 3：Deck 与 Word CRUD

内容：
- Deck 模型
- Word 模型
- 用户隔离校验
- 批量导入

验收：
- CRUD 正常
- 越权访问失败

回退点：
- v3-crud

---

## Issue 4：复习调度系统

内容：
- ReviewState
- ReviewLog
- 固定间隔算法实现
- 提交评分接口
- 获取到期队列接口

验收：
- 等级变化正确
- next_due_at 计算正确
- ReviewLog 正确记录

回退点：
- v4-review

---

## Issue 5：统计接口

内容：
- 今日到期数
- 今日复习数
- 连续打卡
- 最近 7 天统计

验收：
- 数据计算正确

回退点：
- v5-stats

---

## Issue 6：前端登录与路由

验收：
- 可注册登录
- token 管理正常

---

## Issue 7：前端 CRUD 页面

验收：
- Deck 与 Word 全流程可用

---

## Issue 8：复习页面

验收：
- 完整复习流程顺畅

---

## Issue 9：统计页面

验收：
- 数据正确显示

---

## Issue 10：Docker 与部署

验收：
- docker compose 可运行
- 部署文档可执行

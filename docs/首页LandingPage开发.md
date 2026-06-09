# 首页（Landing Page）开发文档

> 本文档记录为白泽项目新增公开首页（Landing Page）的设计方案与实现细节。

---

## 一、需求背景

项目上线后，访问 `wuyuxuan.xyz` 直接重定向到登录页，缺乏项目介绍入口。成熟的开源项目通常有一个公开首页，让访客了解项目用途后再进入系统。

**目标**：新增一个无需登录的 Landing Page，作为 `/` 的默认入口。

---

## 二、路由调整

| 路径 | 变更前 | 变更后 |
|------|--------|--------|
| `/` | RequireAuth → HomePage（知识库列表） | **LandingPage（公开首页）** |
| `/home` | 不存在 | **原 HomePage（知识库列表，需登录）** |
| `/login` | LoginPage（不变） | LoginPage（不变） |
| `/kb/:id` | 需登录 | 不变 |
| `/stats` | 需登录 | 不变 |

**已登录用户访问 `/`**：LandingPage 检测到 token 后自动重定向到 `/home`。

---

## 三、Landing Page 内容结构

| 区块 | 内容 |
|------|------|
| **Hero** | 大标题"白泽 BaiZe"、副标题、两个 CTA 按钮（开始使用 → 登录页，了解更多 → 锚点滚动） |
| **核心功能** | 三列卡片：文档管理、智能问答、安全可控 |
| **三步开始** | Steps 组件：创建知识库 → 上传文档 → 开始对话 |
| **技术栈** | 标签展示：FastAPI、React、Milvus、Ant Design、Celery、SQLite |
| **CTA** | 渐变背景 + "立即开始" 按钮 |
| **Footer** | 项目名称简介 |

**设计风格**：与登录页保持一致的紫蓝渐变主题，使用 Ant Design 组件，无额外 UI 库。

---

## 四、文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/pages/LandingPage.tsx` | **新增** | 公开首页组件 |
| `src/router.tsx` | **修改** | `/` 指向 LandingPage，`/home` 指向知识库管理 |
| `src/components/Layout.tsx` | **修改** | 侧边栏"知识库"菜单项路径改为 `/home` |
| `src/pages/LoginPage.tsx` | **修改** | 登录/注册成功后跳转 `/home` 而非 `/` |
| `src/index.css` | **修改** | 清理 Vite 脚手架残留样式 |
| `src/App.css` | **修改** | 清理 Vite 脚手架残留样式 |

---

## 五、部署步骤

```bash
# 重新构建前端
cd frontend && npm run build

# 部署到 Nginx 静态目录
rm -rf /var/www/rag-frontend/*
cp -r dist/* /var/www/rag-frontend/

# 重载 Nginx
systemctl reload nginx
```

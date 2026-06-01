# TypeScript 路径别名配置

## 问题现象

IDE 报错：`找不到模块"@/xxx"或其相应的类型声明。ts(2307)`，但 `vite build` 能通过。

## 根因

`@` 路径别名需要在**两处**同时配置：

| 工具 | 配置文件 | 作用 |
|------|----------|------|
| **Vite** | `vite.config.ts` → `resolve.alias` | 打包时解析路径 |
| **TypeScript** | `tsconfig.app.json` → `compilerOptions.paths` | 类型检查时解析路径 |

两者互不通信，缺一不可。

## 修复方法

### 1. `tsconfig.app.json`（告诉 TS 编译器 `@` 在哪）

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### 2. `vite.config.ts`（告诉 Vite 打包器 `@` 在哪）

```typescript
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
});
```

## 原理

```
前端代码: import { foo } from '@/api/client'
                │
       ┌────────┴────────┐
       ▼                 ▼
  npx tsc             vite build
  读 tsconfig         读 vite.config
  @ → src             @ → src
       │                 │
       └────────┬────────┘
                ▼
        都正确解析为 ./src/api/client
```

## 验证

```bash
cd frontend
npx tsc --noEmit    # 验证 TypeScript 类型检查通过
npx vite build      # 验证 Vite 打包通过
```

## 相关文件

- `frontend/tsconfig.app.json`
- `frontend/vite.config.ts`

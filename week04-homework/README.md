# 第四周作业 - 智能客服系统

## ✅ 作业完成情况

**所有三个阶段已完成并统一集成！**

### 系统特点

- 🎯 **统一架构**: 所有功能集成在一个程序中
- 🕒 **时间推理**: 自动识别"昨天"、"今天"、"3天前"等
- 🔧 **工具调用**: 6个工具（订单、退款、发票）
- 🔌 **插件系统**: 动态加载，自动集成
- 🚀 **生产就绪**: FastAPI + 热更新 + 健康检查
- ✅ **完整测试**: 25/25 测试通过

## 🚀 快速开始

```bash
# 安装依赖
uv sync

# 运行交互式客服（包含所有功能）
python -m smart_customer_service.main

# 运行生产服务器
python -m smart_customer_service.main --server

# 运行测试
python -m smart_customer_service.main --test

# 查看演示
python demo_unified_system.py
```

## 📋 作业要求对照

### ✅ 阶段一：基础对话系统搭建
- ✅ 使用 LangChain 构建 Prompt → LLM → OutputParser
- ✅ 时间推理："昨天" → 具体日期计算
- ✅ 代码位置: `smart_customer_service/agent.py` (calculate_relative_date)

### ✅ 阶段二：多轮对话与工具调用
- ✅ 使用 LangGraph 构建多轮流程
- ✅ 订单查询、退款申请工具
- ✅ 工具自动调用
- ✅ 代码位置: `smart_customer_service/agent.py` (create_agent)

### ✅ 阶段三：热更新与生产部署
- ✅ 模型热更新: `smart_customer_service/config.py`
- ✅ 插件热重载: `smart_customer_service/plugin_loader.py`
- ✅ `/health` 接口: `smart_customer_service/server.py`
- ✅ 自动化测试: `tests/` (25个测试)
- ✅ 发票插件测试: `tests/test_invoice_plugin.py`

## 💬 使用示例

```
用户: 我昨天下的订单
⏰ 时间解析：昨天=2025-11-29
客服: 找到 1 个订单...

用户: 帮我申请退款，订单 ORD003
客服: 退款申请已提交，退款单号：REF001...

用户: 查询发票 INV001
客服: 发票信息：金额 ¥8999.0...
```

## 📦 项目结构

```
smart_customer_service/
├── __init__.py
├── agent.py              # 统一代理（阶段1+2+3集成）
├── main.py               # 作业入口
├── config.py             # 配置管理（热更新）
├── plugin_loader.py      # 插件系统
├── server.py             # FastAPI 服务器
└── plugins/
    └── invoice_plugin.py # 发票插件示例

tests/                    # 25个自动化测试
├── test_invoice_plugin.py
├── test_plugin_loader.py
└── test_server.py

demo_unified_system.py    # 完整演示
README_UNIFIED.md         # 详细文档
```

## 🔧 可用工具

**基础工具（阶段2）:**
1. query_order - 订单查询
2. query_orders_by_date - 日期查询
3. process_refund - 退款处理
4. check_refund_status - 退款状态

**插件工具（阶段3）:**
5. query_invoice - 发票查询
6. request_invoice - 发票申请

## 🧪 测试结果

```bash
$ python -m smart_customer_service.main --test

===== 25 passed in 0.79s =====

✅ Invoice Plugin:  10/10
✅ Plugin Loader:    6/6
✅ Server API:       9/9
```

## 🌐 API 服务器

```bash
# 启动服务器
python -m smart_customer_service.main --server

# 访问 http://localhost:8000/docs
```

**API 端点:**
- `GET /health` - 健康检查
- `POST /chat` - 聊天接口
- `GET /plugins` - 插件列表
- `POST /reload` - 手动热更新

## 📚 详细文档

- `README_UNIFIED.md` - 统一系统完整文档
- `STAGE3_README.md` - Stage 3 详细说明
- `QUICKSTART.md` - 快速参考

## 🎯 技术亮点

1. **统一架构** - 三个阶段无缝集成
2. **自动化** - 插件自动加载，时间自动解析
3. **零配置** - 开箱即用
4. **生产级** - 完整的健康检查和热更新
5. **高测试覆盖** - 25个测试全部通过

---

## 原始作业要求

## 任务
构建一个小型多轮对话智能客服，支持工具调用以及模型与插件的热更新。

## 作业思路指导
### 阶段一：基础对话系统搭建
使用 LangChain 构建基础 Chain：Prompt → LLM → OutputParser
用户说"我昨天下的单"，系统能结合当前时间推断"昨天"的具体日期

### 阶段二：多轮对话与工具调用
实现"订单查询""退款申请"等多轮交互流程，支持工具自动调用。
使用 LangGraph 构建以下流程：
- 用户说"查订单" → 追问"请提供订单号"
- 收到订单号后 → 调用 query_order(order_id) 工具
- 返回订单状态与物流信息

### 阶段三：热更新与生产部署
实现模型与插件的热更新，完成系统部署与监控。
1. 模型热更新
2. 插件热重载
3. 暴露健康检查接口 /health
4. 编写自动化测试脚本
- 测试"发票开具"插件的功能正确性
- 验证热更新后旧会话不受影响

## 如何提交作业
请fork本仓库，然后在以下目录分别完成编码作业：
- [week04-homework/smart_customer_service](./smart_customer_service)

其中:
- main.py是作业的入口


完成作业后，请在【极客时间】上提交你的fork仓库链接，精确到本周的目录，例如：
```
https://github.com/your-username/ai-engineer-training/tree/main/week04-homework
```

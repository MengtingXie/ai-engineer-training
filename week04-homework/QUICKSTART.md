# Quick Start Guide

## Installation

```bash
# Install dependencies
uv sync
```

## Basic Usage

### 1. Interactive Chat (Stage 1 + 2)

```bash
python -m smart_customer_service.main
```

**Example conversation:**
```
用户: 查询订单 ORD001
客服: [Returns order details]

用户: 我昨天下的订单
⏰ 时间解析：昨天=2025-11-26
客服: [Finds orders from yesterday]

用户: 帮我申请退款，订单 ORD003，质量问题
客服: [Processes refund and returns refund ID]
```

### 2. Production Server (Stage 3)

```bash
# Start server
python -m smart_customer_service.main --server

# Access at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

**Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "查询订单 ORD001"}'
```

### 3. Feature Demo

```bash
python -m smart_customer_service.main --demo
```

### 4. Run Tests

```bash
python -m smart_customer_service.main --test
```

## Key Features

### Stage 1: Temporal Reasoning
- ✅ "昨天" → Actual date
- ✅ "3天前" → Calculated date
- ✅ Context-aware prompts

### Stage 2: Tool Calling
- ✅ Order queries
- ✅ Refund processing
- ✅ Multi-turn conversations

### Stage 3: Production Ready
- ✅ Hot reload (plugins & config)
- ✅ Health checks
- ✅ RESTful API
- ✅ Automated tests

## Testing Orders

Use these test order IDs:
- `ORD001` - iPhone 15 Pro (已发货)
- `ORD002` - MacBook Pro (处理中)
- `ORD003` - AirPods Pro (已完成, can refund)

## Creating New Plugins

1. Create `smart_customer_service/plugins/my_plugin.py`:

```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"

def get_tools():
    return [my_tool]
```

2. Plugin loads automatically (hot reload)!

## Troubleshooting

**Server won't start?**
- Check port 8000 is free
- Verify `.env` file exists

**Plugin not loading?**
- Check plugin syntax
- Look for errors in logs

**Tests failing?**
- Run `uv sync` to update deps
- Check Python version (requires 3.11+)

## Need Help?

- Full docs: `STAGE3_README.md`
- API docs: http://localhost:8000/docs (when server running)
- Tests: `pytest tests/ -v`

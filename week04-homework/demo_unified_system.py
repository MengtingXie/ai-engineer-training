"""
Demonstration of the unified system
Shows how all three stages work together in one program
"""

from smart_customer_service.agent import (
    calculate_relative_date,
    base_tools,
    load_plugins,
    preprocess_temporal_expressions
)
from datetime import datetime, timedelta


def demo_stage1_temporal():
    """Demo Stage 1: Temporal Reasoning"""
    print("=" * 70)
    print("STAGE 1: 时间推理演示")
    print("=" * 70)

    current_time = datetime.now()
    print(f"\n当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    test_cases = [
        "我昨天下的订单",
        "查询前天的订单",
        "3天前买的商品"
    ]

    for case in test_cases:
        result = calculate_relative_date(case, current_time)
        print(f"输入: {case}")
        print(f"解析: {result['processed_text']}")
        for date_info in result['parsed_dates']:
            print(f"  → {date_info['relative_term']} = {date_info['actual_date']}")
        print()


def demo_stage2_tools():
    """Demo Stage 2: Tool Calling"""
    print("\n" + "=" * 70)
    print("STAGE 2: 工具调用演示")
    print("=" * 70)

    print(f"\n基础工具数量: {len(base_tools)}")
    for i, tool in enumerate(base_tools, 1):
        print(f"{i}. {tool.name}")

    print("\n测试工具调用:\n")

    # Test order query
    print("1. 查询订单 ORD001:")
    result = base_tools[0].invoke({"order_id": "ORD001"})
    print(result)
    print()

    # Test date query
    print("2. 查询前天的订单:")
    yesterday = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    result = base_tools[1].invoke({"date_str": yesterday})
    print(result)
    print()

    # Test refund
    print("3. 提交退款申请:")
    result = base_tools[2].invoke({"order_id": "ORD003", "reason": "测试退款"})
    print(result)
    print()


def demo_stage3_plugins():
    """Demo Stage 3: Plugin System"""
    print("\n" + "=" * 70)
    print("STAGE 3: 插件系统演示")
    print("=" * 70)

    print("\n加载插件...")
    plugin_tools = load_plugins()

    print(f"插件工具数量: {len(plugin_tools)}")
    for i, tool in enumerate(plugin_tools, 1):
        print(f"{i}. {tool.name} - {tool.description}")

    if plugin_tools:
        print("\n测试插件工具:\n")

        # Test invoice query
        print("1. 查询发票 INV001:")
        result = plugin_tools[0].invoke({"invoice_id": "INV001"})
        print(result)
        print()

        # Test invoice request
        print("2. 申请发票:")
        result = plugin_tools[1].invoke({
            "order_id": "ORD001",
            "tax_id": "91110108MA01234567",
            "company_name": "测试公司"
        })
        print(result)
        print()


def demo_unified_system():
    """Demo all stages working together"""
    print("\n" + "=" * 70)
    print("统一系统: 三个阶段整合在一起")
    print("=" * 70)

    plugin_tools = load_plugins()
    total_tools = len(base_tools) + len(plugin_tools)

    print(f"\n总工具数: {total_tools}")
    print(f"  - 基础工具: {len(base_tools)}")
    print(f"  - 插件工具: {len(plugin_tools)}")

    print("\n所有可用工具:")
    all_tools = base_tools + plugin_tools
    for i, tool in enumerate(all_tools, 1):
        print(f"  {i}. {tool.name}")

    print("\n示例对话流程:")
    print("  用户: '我昨天下的订单'")
    print("  ↓ [Stage 1: 时间推理]")
    print("  系统: 昨天 = 2025-11-26")
    print("  ↓ [Stage 2: 工具调用]")
    print("  系统: 调用 query_orders_by_date('2025-11-26')")
    print("  ↓ [Stage 3: 包含插件工具]")
    print("  系统: 返回订单信息（可选：查询关联发票）")

    print("\n✅ 所有阶段无缝集成在同一程序中！")


def main():
    """Run all demonstrations"""
    print("\n")
    print("█" * 70)
    print("█  智能客服系统 - 统一演示")
    print("█  Stage 1 (时间推理) + Stage 2 (工具调用) + Stage 3 (插件系统)")
    print("█" * 70)
    print()

    # Demo each stage
    demo_stage1_temporal()
    demo_stage2_tools()
    demo_stage3_plugins()
    demo_unified_system()

    print("\n" + "=" * 70)
    print("运行交互式客服: python -m smart_customer_service.main")
    print("运行生产服务器: python -m smart_customer_service.main --server")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()

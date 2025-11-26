"""
Test script for the customer service agent
"""

from langchain_core.messages import HumanMessage
from smart_customer_service.agent import (
    create_agent,
    tools,
    preprocess_temporal_expressions,
    calculate_relative_date
)
from datetime import datetime, timedelta
from dotenv import load_dotenv


def test_temporal_preprocessing():
    """Test temporal expression preprocessing"""
    print("=== 测试时间表达式预处理 ===\n")

    test_cases = [
        "我昨天下的订单",
        "查询前天的订单",
        "今天有没有新订单",
        "3天前买的商品怎么样了"
    ]

    for case in test_cases:
        enhanced, context = preprocess_temporal_expressions(case)
        print(f"输入: {case}")
        print(f"增强: {enhanced}")
        if context['has_temporal_expressions']:
            for date_info in context['parsed_dates']:
                print(f"  → {date_info['relative_term']} = {date_info['actual_date']}")
        print()


def test_tools_directly():
    """Test individual tools directly"""
    print("\n=== 测试工具直接调用 ===\n")

    # Test query_order
    print("1. 测试订单查询:")
    result = tools[0].invoke({"order_id": "ORD001"})
    print(result)
    print()

    # Test query_orders_by_date
    print("2. 测试日期查询:")
    yesterday = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    result = tools[1].invoke({"date_str": yesterday})
    print(result)
    print()

    # Test process_refund
    print("3. 测试退款:")
    result = tools[2].invoke({"order_id": "ORD003", "reason": "商品质量问题"})
    print(result)
    print()

    # Test check_refund_status
    print("4. 测试退款状态查询:")
    result = tools[3].invoke({"refund_id": "REF001"})
    print(result)
    print()


def test_agent_conversation():
    """Test the agent with conversation scenarios"""
    print("\n=== 测试智能代理对话 ===\n")

    load_dotenv()

    try:
        agent = create_agent()
        print("✅ Agent 创建成功\n")
    except Exception as e:
        print(f"❌ Agent 创建失败: {e}")
        return

    # Test conversation scenarios
    test_cases = [
        "查询订单 ORD001",
        "我昨天下的订单",
        "前天的订单有哪些",
        "帮我对订单 ORD003 申请退款，原因是质量问题",
    ]

    state = {"messages": []}

    for i, test_input in enumerate(test_cases, 1):
        print(f"{'=' * 60}")
        print(f"测试 {i}: {test_input}")
        print(f"{'=' * 60}")

        # Show temporal preprocessing
        _, temp_context = preprocess_temporal_expressions(test_input)
        if temp_context['has_temporal_expressions']:
            print("⏰ 时间解析：", end="")
            for date_info in temp_context['parsed_dates']:
                print(f"{date_info['relative_term']}={date_info['actual_date']} ", end="")
            print()

        # Add user message
        state["messages"].append(HumanMessage(content=test_input))

        try:
            # Invoke agent
            result = agent.invoke(state)
            state = result

            # Print response
            last_message = result["messages"][-1]
            print(f"\n客服回复:\n{last_message.content}\n")

        except Exception as e:
            print(f"❌ 错误: {e}\n")
            import traceback
            traceback.print_exc()
            break


def main():
    """Run all tests"""
    print("开始测试智能客服系统...\n")

    # Test temporal preprocessing
    test_temporal_preprocessing()

    # Test tools
    test_tools_directly()

    # Test agent (requires API key)
    print("注意: 以下测试需要有效的 OpenAI API key\n")
    test_agent_conversation()

    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main()

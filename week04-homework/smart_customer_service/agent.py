"""
Smart Customer Service Agent: Combines temporal reasoning and tool calling
A complete customer service chatbot with intelligent time understanding and action capabilities
"""

import os
import re
from datetime import datetime, timedelta
from typing import TypedDict, Annotated, Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv


# ============================================================================
# Temporal Reasoning
# ============================================================================

def calculate_relative_date(text: str, current_time: datetime = None) -> Dict[str, Any]:
    """
    Calculate actual dates from relative time expressions like '昨天', '今天', '前天' etc.

    Args:
        text: Input text containing relative time expressions
        current_time: Current datetime, defaults to now()

    Returns:
        Dict containing parsed information and calculated dates
    """
    if current_time is None:
        current_time = datetime.now()

    # Patterns for relative date detection
    patterns = {
        r'今天': 0,
        r'昨天': -1,
        r'前天': -2,
        r'明天': 1,
        r'后天': 2,
        r'大前天': -3,
        r'大后天': 3,
        r'(\d+)天前': lambda match: -int(match.group(1)),
        r'(\d+)天后': lambda match: int(match.group(1)),
    }

    result = {
        'original_text': text,
        'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'parsed_dates': [],
        'processed_text': text
    }

    for pattern, offset in patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            if callable(offset):
                days_offset = offset(match)
            else:
                days_offset = offset

            target_date = current_time + timedelta(days=days_offset)
            date_info = {
                'relative_term': match.group(0),
                'actual_date': target_date.strftime('%Y-%m-%d'),
                'days_offset': days_offset
            }
            result['parsed_dates'].append(date_info)

            # Replace relative term with actual date in processed text
            result['processed_text'] = result['processed_text'].replace(
                match.group(0),
                f"{match.group(0)}({target_date.strftime('%Y-%m-%d')})"
            )

    return result


# ============================================================================
# Mock Database
# ============================================================================

MOCK_ORDERS = {
    "ORD001": {
        "order_id": "ORD001",
        "customer_name": "张三",
        "product": "iPhone 15 Pro",
        "price": 8999.0,
        "status": "已发货",
        "order_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "tracking_number": "SF1234567890"
    },
    "ORD002": {
        "order_id": "ORD002",
        "customer_name": "李四",
        "product": "MacBook Pro",
        "price": 15999.0,
        "status": "处理中",
        "order_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "tracking_number": None
    },
    "ORD003": {
        "order_id": "ORD003",
        "customer_name": "王五",
        "product": "AirPods Pro",
        "price": 1999.0,
        "status": "已完成",
        "order_date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "tracking_number": "SF0987654321"
    }
}

REFUND_RECORDS = {}


# ============================================================================
# Tools with Temporal Awareness
# ============================================================================

@tool
def query_order(order_id: str) -> str:
    """
    查询订单信息

    Args:
        order_id: 订单号，格式如 ORD001

    Returns:
        订单详细信息或错误消息
    """
    order = MOCK_ORDERS.get(order_id.upper())

    if not order:
        return f"未找到订单号 {order_id} 的信息。请检查订单号是否正确。"

    info = f"""订单信息：
- 订单号：{order['order_id']}
- 商品：{order['product']}
- 价格：¥{order['price']}
- 状态：{order['status']}
- 下单日期：{order['order_date']}"""

    if order['tracking_number']:
        info += f"\n- 物流单号：{order['tracking_number']}"

    return info.strip()


@tool
def query_orders_by_date(date_str: str) -> str:
    """
    根据日期查询订单。支持 YYYY-MM-DD 格式的日期

    Args:
        date_str: 日期字符串，格式 YYYY-MM-DD

    Returns:
        该日期的订单列表
    """
    matching_orders = [
        order for order in MOCK_ORDERS.values()
        if order['order_date'] == date_str
    ]

    if not matching_orders:
        return f"未找到 {date_str} 的订单记录。"

    result = f"找到 {len(matching_orders)} 个订单（{date_str}）：\n"
    for order in matching_orders:
        result += f"\n- 订单号：{order['order_id']}, 商品：{order['product']}, 状态：{order['status']}"

    return result


@tool
def process_refund(order_id: str, reason: str) -> str:
    """
    处理退款申请

    Args:
        order_id: 订单号
        reason: 退款原因

    Returns:
        退款处理结果
    """
    order = MOCK_ORDERS.get(order_id.upper())

    if not order:
        return f"未找到订单号 {order_id}，无法处理退款。"

    if order['status'] == "已完成":
        refund_id = f"REF{len(REFUND_RECORDS) + 1:03d}"
        REFUND_RECORDS[refund_id] = {
            "refund_id": refund_id,
            "order_id": order_id.upper(),
            "amount": order['price'],
            "reason": reason,
            "status": "审核中",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return f"""退款申请已提交：
- 退款单号：{refund_id}
- 订单号：{order_id.upper()}
- 退款金额：¥{order['price']}
- 退款原因：{reason}
- 状态：审核中

我们将在1-3个工作日内完成审核，审核通过后款项将原路退回。"""
    else:
        return f"订单 {order_id} 当前状态为 {order['status']}，暂时无法申请退款。只有已完成的订单才能申请退款。"


@tool
def check_refund_status(refund_id: str) -> str:
    """
    查询退款状态

    Args:
        refund_id: 退款单号

    Returns:
        退款状态信息
    """
    refund = REFUND_RECORDS.get(refund_id.upper())

    if not refund:
        return f"未找到退款单号 {refund_id} 的信息。"

    return f"""退款信息：
- 退款单号：{refund['refund_id']}
- 订单号：{refund['order_id']}
- 退款金额：¥{refund['amount']}
- 退款原因：{refund['reason']}
- 状态：{refund['status']}
- 申请时间：{refund['created_at']}"""


# ============================================================================
# Agent State and Configuration
# ============================================================================

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


tools = [query_order, query_orders_by_date, process_refund, check_refund_status]


def preprocess_temporal_expressions(text: str) -> tuple[str, dict]:
    """
    Preprocess user input to extract and calculate temporal expressions

    Returns:
        tuple: (enhanced_text, temporal_context)
    """
    current_time = datetime.now()
    temporal_info = calculate_relative_date(text, current_time)

    # Build enhanced context
    context = {
        'current_time': current_time,
        'parsed_dates': temporal_info['parsed_dates'],
        'has_temporal_expressions': len(temporal_info['parsed_dates']) > 0
    }

    # If temporal expressions found, enhance the text
    if context['has_temporal_expressions']:
        enhanced_text = text + "\n\n[时间上下文："
        for date_info in temporal_info['parsed_dates']:
            enhanced_text += f"{date_info['relative_term']}={date_info['actual_date']}, "
        enhanced_text = enhanced_text.rstrip(", ") + "]"
        return enhanced_text, context

    return text, context


def create_agent():
    """
    Create the customer service agent with temporal reasoning and tool calling
    """
    load_dotenv()

    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        temperature=0.7
    )

    llm_with_tools = llm.bind_tools(tools)

    def should_continue(state: AgentState):
        """Determine whether to continue or end"""
        messages = state["messages"]
        last_message = messages[-1]

        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        return "continue"

    def call_model(state: AgentState):
        """Call the model with temporal-aware processing"""
        messages = list(state["messages"])

        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            current_time = datetime.now()
            system_message = SystemMessage(content=f"""你是一个专业的智能客服助手，负责处理订单查询、退款申请等客户服务事务。

当前时间：{current_time.strftime('%Y年%m月%d日 %H:%M:%S')}

核心能力：
1. 时间理解：自动识别"昨天"、"今天"、"前天"、"3天前"等相对时间表达，并转换为具体日期
2. 订单查询：根据订单号或日期查询订单信息
3. 退款处理：处理退款申请和查询退款状态

可用工具：
- query_order(order_id): 根据订单号查询订单详情
- query_orders_by_date(date_str): 根据日期(YYYY-MM-DD格式)查询订单列表
- process_refund(order_id, reason): 处理退款申请
- check_refund_status(refund_id): 查询退款状态

工作准则：
- 友善、专业的语调
- 当用户提到相对时间时，优先使用 query_orders_by_date 工具，传入计算后的具体日期
- 如果需要更多信息，主动询问用户
- 准确传递参数给工具""")
            messages = [system_message] + messages

        # Process the latest user message for temporal expressions
        if messages and isinstance(messages[-1], HumanMessage):
            original_content = messages[-1].content

            # Check if already processed (has temporal context marker)
            if "[时间上下文：" not in original_content:
                enhanced_content, temporal_context = preprocess_temporal_expressions(original_content)
                messages[-1].content = enhanced_content

        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Build the graph
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )

    workflow.add_edge("tools", "agent")

    return workflow.compile()


# ============================================================================
# Interactive Chat Session
# ============================================================================

def chat_session():
    """
    Interactive chat session with temporal reasoning and tool calling
    """
    print("=== 智能客服系统 ===")
    print("✨ 时间推理 + 多轮对话 + 工具调用")
    print()
    print("功能列表：")
    print("  📅 智能时间理解（昨天、今天、前天、N天前等）")
    print("  📦 订单查询（按订单号或日期）")
    print("  💰 退款申请与状态查询")
    print("  💬 多轮对话上下文记忆")
    print()
    print("输入 'quit' 或 'exit' 退出\n")

    try:
        agent = create_agent()
        print("✅ 系统初始化成功")
        print("💡 测试订单号：ORD001, ORD002, ORD003")
        print("💡 示例：'查询订单 ORD001'，'我昨天下的订单'，'申请退款'\n")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("请检查 .env 文件配置")
        return

    # Initialize state
    state = {"messages": []}

    while True:
        try:
            user_input = input("用户: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出']:
                print("\n感谢使用智能客服系统！")
                break

            if not user_input:
                continue

            # Show temporal processing if detected
            _, temp_context = preprocess_temporal_expressions(user_input)
            if temp_context['has_temporal_expressions']:
                print(f"⏰ 时间解析：", end="")
                for date_info in temp_context['parsed_dates']:
                    print(f"{date_info['relative_term']}={date_info['actual_date']} ", end="")
                print()

            # Add user message
            state["messages"].append(HumanMessage(content=user_input))

            # Invoke agent
            result = agent.invoke(state)
            state = result

            # Display response
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                print(f"客服: {last_message.content}\n")

        except KeyboardInterrupt:
            print("\n\n感谢使用智能客服系统！")
            break
        except Exception as e:
            print(f"❌ 处理请求时出错: {e}\n")
            import traceback
            traceback.print_exc()


# ============================================================================
# Demonstration Functions
# ============================================================================

def demo_features():
    """Demonstrate the combined capabilities"""
    print("=== 功能演示：时间推理 + 工具调用 ===\n")

    current_time = datetime.now()
    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Demo 1: Temporal reasoning
    print("1️⃣  时间推理能力演示")
    print("-" * 50)
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

    # Demo 2: Tools
    print("\n2️⃣  工具调用能力演示")
    print("-" * 50)

    print("查询订单 ORD001:")
    print(tools[0].invoke({"order_id": "ORD001"}))
    print()

    print(f"查询昨天的订单:")
    yesterday = (current_time - timedelta(days=2)).strftime("%Y-%m-%d")
    print(tools[1].invoke({"date_str": yesterday}))
    print()

    print("提交退款:")
    print(tools[2].invoke({"order_id": "ORD003", "reason": "测试退款"}))
    print()

    print("\n✅ 演示完成！运行主程序体验完整功能。")

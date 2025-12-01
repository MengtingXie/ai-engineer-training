"""
Invoice plugin - demonstrates hot-reloadable plugin system
"""

from langchain_core.tools import tool
from datetime import datetime


# Mock invoice database
INVOICES = {
    "INV001": {
        "invoice_id": "INV001",
        "order_id": "ORD001",
        "amount": 8999.0,
        "status": "已开具",
        "issue_date": "2025-11-24",
        "tax_id": "91110108MA01234567"
    },
    "INV002": {
        "invoice_id": "INV002",
        "order_id": "ORD002",
        "amount": 15999.0,
        "status": "处理中",
        "issue_date": None,
        "tax_id": None
    }
}


@tool
def query_invoice(invoice_id: str) -> str:
    """
    查询发票信息

    Args:
        invoice_id: 发票号，格式如 INV001

    Returns:
        发票详细信息或错误消息
    """
    invoice = INVOICES.get(invoice_id.upper())

    if not invoice:
        return f"未找到发票号 {invoice_id} 的信息。"

    if invoice['status'] == "已开具":
        return f"""发票信息：
- 发票号：{invoice['invoice_id']}
- 订单号：{invoice['order_id']}
- 金额：¥{invoice['amount']}
- 状态：{invoice['status']}
- 开具日期：{invoice['issue_date']}
- 税号：{invoice['tax_id']}"""
    else:
        return f"""发票信息：
- 发票号：{invoice['invoice_id']}
- 订单号：{invoice['order_id']}
- 金额：¥{invoice['amount']}
- 状态：{invoice['status']}
发票正在处理中，预计1-3个工作日内开具。"""


@tool
def request_invoice(order_id: str, tax_id: str, company_name: str) -> str:
    """
    申请开具发票

    Args:
        order_id: 订单号
        tax_id: 纳税人识别号
        company_name: 公司名称

    Returns:
        申请结果
    """
    # Find invoice by order_id
    invoice = None
    for inv in INVOICES.values():
        if inv['order_id'] == order_id.upper():
            invoice = inv
            break

    if not invoice:
        # Create new invoice request
        invoice_id = f"INV{len(INVOICES) + 1:03d}"
        INVOICES[invoice_id] = {
            "invoice_id": invoice_id,
            "order_id": order_id.upper(),
            "amount": 0,  # Would be fetched from order
            "status": "处理中",
            "issue_date": None,
            "tax_id": tax_id,
            "company_name": company_name
        }

        return f"""发票申请已提交：
- 发票号：{invoice_id}
- 订单号：{order_id.upper()}
- 公司名称：{company_name}
- 税号：{tax_id}
- 状态：处理中

我们将在1-3个工作日内开具发票并发送至您的邮箱。"""
    else:
        if invoice['status'] == "已开具":
            return f"订单 {order_id} 的发票已开具（发票号：{invoice['invoice_id']}）。"
        else:
            return f"订单 {order_id} 的发票正在处理中（发票号：{invoice['invoice_id']}）。"


def get_tools():
    """Return all tools provided by this plugin"""
    return [query_invoice, request_invoice]

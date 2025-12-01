"""
Automated tests for invoice plugin
Tests the hot-reloadable plugin system
"""

import pytest
from smart_customer_service.plugins.invoice_plugin import (
    query_invoice,
    request_invoice,
    get_tools,
    INVOICES
)


class TestInvoicePlugin:
    """Test suite for invoice plugin"""

    def test_get_tools(self):
        """Test that plugin exports tools correctly"""
        tools = get_tools()
        assert len(tools) == 2
        assert query_invoice in tools
        assert request_invoice in tools

    def test_query_invoice_exists(self):
        """Test querying an existing invoice"""
        result = query_invoice.invoke({"invoice_id": "INV001"})
        assert "INV001" in result
        assert "8999.0" in result
        assert "已开具" in result
        assert "税号" in result

    def test_query_invoice_not_found(self):
        """Test querying a non-existent invoice"""
        result = query_invoice.invoke({"invoice_id": "INV999"})
        assert "未找到" in result

    def test_query_invoice_pending(self):
        """Test querying a pending invoice"""
        result = query_invoice.invoke({"invoice_id": "INV002"})
        assert "INV002" in result
        assert "处理中" in result
        assert "1-3个工作日" in result

    def test_request_invoice_new(self):
        """Test requesting a new invoice"""
        result = request_invoice.invoke({
            "order_id": "ORD999",
            "tax_id": "91110108MA99999999",
            "company_name": "测试公司"
        })
        assert "发票申请已提交" in result
        assert "ORD999" in result
        assert "测试公司" in result
        assert "91110108MA99999999" in result

    def test_request_invoice_existing(self):
        """Test requesting invoice for existing order"""
        result = request_invoice.invoke({
            "order_id": "ORD001",
            "tax_id": "91110108MA01234567",
            "company_name": "已有公司"
        })
        assert "已开具" in result or "处理中" in result

    def test_invoice_case_insensitive(self):
        """Test that invoice IDs are case insensitive"""
        result1 = query_invoice.invoke({"invoice_id": "inv001"})
        result2 = query_invoice.invoke({"invoice_id": "INV001"})
        assert "INV001" in result1
        assert "INV001" in result2


class TestPluginIntegration:
    """Test plugin integration with the system"""

    def test_tools_have_names(self):
        """Test that all tools have proper names"""
        tools = get_tools()
        for tool in tools:
            assert hasattr(tool, 'name')
            assert len(tool.name) > 0

    def test_tools_have_descriptions(self):
        """Test that all tools have descriptions"""
        tools = get_tools()
        for tool in tools:
            assert hasattr(tool, 'description')
            assert len(tool.description) > 0

    def test_tools_are_callable(self):
        """Test that all tools can be invoked"""
        tools = get_tools()
        for tool in tools:
            assert callable(tool.invoke)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

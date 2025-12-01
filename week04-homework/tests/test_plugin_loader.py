"""
Tests for plugin loader system
"""

import pytest
from pathlib import Path
from smart_customer_service.plugin_loader import PluginLoader


class TestPluginLoader:
    """Test plugin loading system"""

    def test_plugin_loader_init(self):
        """Test plugin loader initialization"""
        loader = PluginLoader()
        assert loader.plugins_dir.exists()

    def test_discover_plugins(self):
        """Test plugin discovery"""
        loader = PluginLoader()
        plugins = loader.discover_plugins()
        assert isinstance(plugins, list)
        # Should find at least the invoice plugin
        assert len(plugins) >= 1

    def test_load_all_plugins(self):
        """Test loading all plugins"""
        loader = PluginLoader()
        tools = loader.load_all_plugins()
        assert isinstance(tools, list)
        # Invoice plugin should provide 2 tools
        assert len(tools) >= 2

    def test_plugin_status(self):
        """Test getting plugin status"""
        loader = PluginLoader()
        loader.load_all_plugins()
        status = loader.get_plugin_status()

        assert "total_plugins" in status
        assert "plugins" in status
        assert status["total_plugins"] >= 1

    def test_loaded_plugins_have_tools(self):
        """Test that loaded plugins have tools"""
        loader = PluginLoader()
        loader.load_all_plugins()

        for plugin_name, plugin_info in loader.loaded_plugins.items():
            assert "tools" in plugin_info
            assert len(plugin_info["tools"]) > 0

    def test_reload_if_changed(self):
        """Test reload detection"""
        loader = PluginLoader()
        loader.load_all_plugins()

        # First call should return False (nothing changed)
        changed, tools = loader.reload_if_changed()
        assert isinstance(changed, bool)
        assert isinstance(tools, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

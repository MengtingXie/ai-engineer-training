"""
Plugin system for dynamically loading tools
Supports hot reload of plugins without restarting the server
"""

import os
import importlib
import importlib.util
from typing import List, Dict, Any
from pathlib import Path
from langchain_core.tools import BaseTool
import logging

logger = logging.getLogger(__name__)


class PluginLoader:
    """Load and manage plugins dynamically"""

    def __init__(self, plugins_dir: str = None):
        if plugins_dir is None:
            plugins_dir = Path(__file__).parent / "plugins"
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        self.loaded_plugins: Dict[str, Any] = {}

    def discover_plugins(self) -> List[Path]:
        """Discover all Python files in plugins directory"""
        if not self.plugins_dir.exists():
            return []

        return [
            f for f in self.plugins_dir.glob("*.py")
            if not f.name.startswith("_")
        ]

    def load_plugin(self, plugin_path: Path) -> List[BaseTool]:
        """Load a single plugin and return its tools"""
        try:
            module_name = plugin_path.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)

            if spec is None or spec.loader is None:
                logger.error(f"Failed to load spec for {plugin_path}")
                return []

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Look for tools in the module
            tools = []
            if hasattr(module, 'get_tools'):
                tools = module.get_tools()
            elif hasattr(module, 'tools'):
                tools = module.tools

            self.loaded_plugins[module_name] = {
                'path': plugin_path,
                'module': module,
                'tools': tools,
                'mtime': plugin_path.stat().st_mtime
            }

            logger.info(f"Loaded plugin: {module_name} with {len(tools)} tools")
            return tools

        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            return []

    def load_all_plugins(self) -> List[BaseTool]:
        """Load all plugins and return combined list of tools"""
        all_tools = []
        plugin_files = self.discover_plugins()

        for plugin_file in plugin_files:
            tools = self.load_plugin(plugin_file)
            all_tools.extend(tools)

        return all_tools

    def reload_if_changed(self) -> tuple[bool, List[BaseTool]]:
        """
        Check if any plugins have changed and reload if necessary

        Returns:
            tuple: (changed: bool, tools: List[BaseTool])
        """
        changed = False
        plugin_files = self.discover_plugins()

        # Check for new or modified plugins
        current_plugins = {p.stem for p in plugin_files}
        loaded_plugins = set(self.loaded_plugins.keys())

        # New plugins
        new_plugins = current_plugins - loaded_plugins
        if new_plugins:
            changed = True
            logger.info(f"New plugins detected: {new_plugins}")

        # Removed plugins
        removed_plugins = loaded_plugins - current_plugins
        if removed_plugins:
            changed = True
            for plugin_name in removed_plugins:
                del self.loaded_plugins[plugin_name]
            logger.info(f"Plugins removed: {removed_plugins}")

        # Modified plugins
        for plugin_file in plugin_files:
            plugin_name = plugin_file.stem
            if plugin_name in self.loaded_plugins:
                old_mtime = self.loaded_plugins[plugin_name]['mtime']
                new_mtime = plugin_file.stat().st_mtime
                if new_mtime > old_mtime:
                    changed = True
                    logger.info(f"Plugin modified: {plugin_name}")

        if changed:
            # Reload all plugins
            all_tools = self.load_all_plugins()
            return True, all_tools

        # Return existing tools
        all_tools = []
        for plugin_info in self.loaded_plugins.values():
            all_tools.extend(plugin_info['tools'])

        return False, all_tools

    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status of all loaded plugins"""
        return {
            'total_plugins': len(self.loaded_plugins),
            'plugins': {
                name: {
                    'path': str(info['path']),
                    'tool_count': len(info['tools']),
                    'tools': [tool.name for tool in info['tools']]
                }
                for name, info in self.loaded_plugins.items()
            }
        }

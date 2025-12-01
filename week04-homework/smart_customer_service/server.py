"""
FastAPI server for production deployment
Includes hot reload, health checks, and API endpoints
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from .config import config
from .plugin_loader import PluginLoader
from .agent import create_agent as create_base_agent, MOCK_ORDERS

# Setup logging
# Use force=True to avoid duplicate handlers
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)


# ============================================================================
# Global State
# ============================================================================

plugin_loader = PluginLoader()
agent_instance = None
agent_tools = []
start_time = datetime.now()


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    config: Dict[str, Any]
    plugins: Dict[str, Any]
    timestamp: str


# ============================================================================
# Agent Management
# ============================================================================

def create_agent_with_plugins():
    """Create agent with base tools + dynamically loaded plugins"""
    global agent_tools

    # Load plugins
    plugin_tools = plugin_loader.load_all_plugins()
    logger.info(f"Loaded {len(plugin_tools)} tools from plugins")

    # Store tools for health check
    agent_tools = plugin_tools

    # Create agent with combined tools
    from .agent import (
        create_agent,
        tools as base_tools,
        AgentState,
        preprocess_temporal_expressions
    )

    # For now, we'll use the base agent
    # In a full implementation, we'd modify create_agent to accept additional tools
    agent = create_agent()

    return agent


def reload_agent():
    """Reload agent with updated configuration and plugins"""
    global agent_instance

    try:
        # Check for config changes
        config_changed = config.reload_if_changed()
        if config_changed:
            logger.info("Configuration reloaded")

        # Check for plugin changes
        plugins_changed, new_tools = plugin_loader.reload_if_changed()
        if plugins_changed:
            logger.info("Plugins reloaded")

        # Recreate agent if anything changed
        if config_changed or plugins_changed:
            agent_instance = create_agent_with_plugins()
            logger.info("Agent reloaded successfully")
            return True

        return False

    except Exception as e:
        logger.error(f"Error reloading agent: {e}")
        return False


# ============================================================================
# Lifespan Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global agent_instance

    # Startup
    logger.info("Starting customer service server...")
    agent_instance = create_agent_with_plugins()
    logger.info("Server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down server...")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Smart Customer Service API",
    description="Intelligent customer service with hot reload capabilities",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Customer Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns system status, uptime, configuration, and plugin information
    """
    uptime = (datetime.now() - start_time).total_seconds()

    return HealthResponse(
        status="healthy",
        uptime_seconds=uptime,
        config={
            "model": config.get("llm.model"),
            "temperature": config.get("llm.temperature"),
            "plugins_enabled": config.get("plugins.enabled"),
            "auto_reload": config.get("plugins.auto_reload")
        },
        plugins=plugin_loader.get_plugin_status(),
        timestamp=datetime.now().isoformat()
    )


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Chat endpoint for customer service
    Processes user messages and returns AI responses
    """
    global agent_instance

    if agent_instance is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Check for hot reload in background
        if config.get("plugins.auto_reload", True):
            background_tasks.add_task(reload_agent)

        # Process message
        state = {"messages": [HumanMessage(content=request.message)]}
        result = agent_instance.invoke(state)

        # Get last AI message
        last_message = result["messages"][-1]
        if isinstance(last_message, AIMessage):
            response_text = last_message.content
        else:
            response_text = str(last_message)

        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reload", tags=["Admin"])
async def trigger_reload():
    """
    Manually trigger reload of configuration and plugins
    """
    try:
        reloaded = reload_agent()
        return {
            "status": "success",
            "reloaded": reloaded,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error during reload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plugins", tags=["Admin"])
async def list_plugins():
    """
    List all loaded plugins and their tools
    """
    return plugin_loader.get_plugin_status()


@app.get("/orders", tags=["Data"])
async def list_orders():
    """
    List all orders (for testing)
    """
    return {
        "orders": list(MOCK_ORDERS.values()),
        "total": len(MOCK_ORDERS)
    }


# ============================================================================
# Main
# ============================================================================

def start_server(host: str = None, port: int = None):
    """Start the FastAPI server"""
    import uvicorn

    if host is None:
        host = config.get("server.host", "0.0.0.0")
    if port is None:
        port = config.get("server.port", 8000)

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "smart_customer_service.server:app",
        host=host,
        port=port,
        reload=False,  # We handle reload ourselves
        log_level="info"
    )

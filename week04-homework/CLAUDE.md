# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a homework assignment for building a smart customer service chatbot system with three progressive stages:

1. **Stage 1**: Basic conversation system using LangChain (Prompt → LLM → OutputParser)
2. **Stage 2**: Multi-turn dialogue with tool calling using LangGraph (order queries, refunds, etc.)
3. **Stage 3**: Hot updates and production deployment (model/plugin hot reload, health checks, automated tests)

## Development Commands

### Package Management
```bash
# Install dependencies (uses Tsinghua PyPI mirror)
uv sync

# Add new dependencies to pyproject.toml then run:
uv sync
```

### Running the Application
```bash
# Run the main application
python -m smart_customer_service.main

# Or directly
python smart_customer_service/main.py
```

## Architecture

### Entry Point
- `smart_customer_service/main.py`: Main application entry point where all functionality should be implemented or orchestrated

### Key Requirements by Stage
- **Stage 1**: Implement temporal reasoning (e.g., "yesterday" → actual date calculation)
- **Stage 2**: Multi-turn flows with tool calling for order management
- **Stage 3**: Hot reload capabilities, `/health` endpoint, automated testing for invoice plugins

### Dependencies
- Uses `python-dotenv` for environment configuration
- Requires Python >=3.11
- Add LangChain/LangGraph dependencies as needed for chatbot functionality

## Development Notes

The project uses uv for dependency management with a Tsinghua University PyPI mirror for faster package installation in China. The main implementation should extend from the basic `main()` function while maintaining the entry point structure.
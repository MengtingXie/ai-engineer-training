

def main():
    """
    智能客服系统入口
    整合了 Stage 1（时间推理）、Stage 2（工具调用）、Stage 3（插件系统）
    在根目录可以通过 python -m smart_customer_service.main 运行
    """
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--server":
            # Production server mode
            from .server import start_server
            print("=== 智能客服系统 - 生产服务器 ===")
            print("启动 FastAPI 服务器...")
            print("功能：REST API + 热更新 + 健康检查 + 插件系统")
            print()
            start_server()
        elif sys.argv[1] == "--test":
            # Run automated tests
            import pytest
            print("=== 运行自动化测试 ===")
            pytest.main(["-v", "tests/"])
        else:
            print("用法:")
            print("  python -m smart_customer_service.main         # 交互式客服（默认）")
            print("  python -m smart_customer_service.main --server # 启动生产服务器")
            print("  python -m smart_customer_service.main --test   # 运行测试")
    else:
        # Default: Interactive chat with all features integrated
        from .agent import chat_session
        chat_session()


if __name__ == "__main__":
    main()
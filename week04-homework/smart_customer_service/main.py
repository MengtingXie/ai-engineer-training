

def main():
    """
    作业的入口写在这里。你可以就写这个文件，或者扩展多个文件，但是执行入口留在这里。
    在根目录可以通过python -m smart_customer_service.main 运行
    """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Demo mode: show all features
        from .agent import demo_features
        demo_features()
    else:
        # Default: Run complete system
        from .agent import chat_session
        chat_session()


if __name__ == "__main__":
    main()
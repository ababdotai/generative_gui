import os

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def disable_langsmith() -> None:
    """Disable LangSmith for tests."""
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ.pop("LANGSMITH_API_KEY", None)

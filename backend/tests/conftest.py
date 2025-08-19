"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def mock_azure_request():
    """Create a mock Azure Functions HTTP request"""
    import azure.functions as func
    
    request = Mock(spec=func.HttpRequest)
    return request


@pytest.fixture
def mock_tokenizer():
    """Create a mock tokenizer with standard responses"""
    tokenizer = Mock()
    tokenizer.tokenize.return_value = ["Hello", ",", " world", "!"]
    tokenizer.encode.return_value = [15496, 11, 995, 0]
    tokenizer.decode.return_value = "Hello, world!"
    tokenizer.vocab_size = 50257
    tokenizer.pad_token = "<|endoftext|>"
    tokenizer.unk_token = "<|endoftext|>"
    tokenizer.cls_token = None
    tokenizer.sep_token = None
    tokenizer.mask_token = None
    return tokenizer


@pytest.fixture
def clean_environment():
    """Provide a clean environment for testing"""
    # Store original environment
    original_env = os.environ.copy()
    
    # Clear environment for test
    os.environ.clear()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'DEFAULT_MODEL': 'gpt2',
        'HUGGINGFACE_TOKEN': 'test_token'
    }):
        yield


@pytest.fixture(scope="session")
def clear_tokenizer_cache():
    """Clear tokenizer cache before running tests"""
    # Import here to avoid circular imports
    try:
        from TokenizerFunction import _tokenizer_cache
        _tokenizer_cache.clear()
    except ImportError:
        pass
    
    yield
    
    # Clear again after tests
    try:
        from TokenizerFunction import _tokenizer_cache
        _tokenizer_cache.clear()
    except ImportError:
        pass


@pytest.fixture
def sample_tokenize_response():
    """Sample successful tokenization response"""
    return {
        "success": True,
        "model": "gpt2",
        "text": "Hello, world!",
        "tokens": ["Hello", ",", " world", "!"],
        "token_ids": [15496, 11, 995, 0],
        "token_count": 4,
        "vocab_size": 50257,
        "special_tokens": {
            "pad_token": "<|endoftext|>",
            "unk_token": "<|endoftext|>",
            "cls_token": None,
            "sep_token": None,
            "mask_token": None
        }
    }


@pytest.fixture
def sample_error_response():
    """Sample error response"""
    return {
        "success": False,
        "error": "Model loading failed",
        "model": "invalid-model",
        "text": "test text"
    }


# Configure logging for tests
@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logging for tests"""
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)  # Suppress logs during tests


# Performance monitoring fixture
@pytest.fixture
def performance_monitor():
    """Monitor performance of tests"""
    import time
    
    start_time = time.time()
    
    yield
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Log slow tests (> 1 second)
    if duration > 1.0:
        print(f"\n⚠️ Slow test detected: {duration:.2f}s")
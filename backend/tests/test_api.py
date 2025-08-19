"""
Unit tests for Azure Function API endpoints
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Azure Functions
import azure.functions as func

# Import the main function
from TokenizerFunction import main


class TestMainFunction:
    """Test the main Azure Function entry point"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Mock environment variable
        self.default_model_patcher = patch.dict(os.environ, {'DEFAULT_MODEL': 'gpt2'})
        self.default_model_patcher.start()
    
    def teardown_method(self):
        """Clean up after tests"""
        self.default_model_patcher.stop()
    
    def test_get_request_success(self):
        """Test successful GET request"""
        # Create mock request
        req = Mock(spec=func.HttpRequest)
        req.method = "GET"
        
        # Call the function
        response = main(req)
        
        # Assert response
        assert isinstance(response, func.HttpResponse)
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        # Parse and check response body
        response_data = json.loads(response.get_body().decode())
        assert response_data["message"] == "Tokenizer API is running"
        assert response_data["default_model"] == "gpt2"
        assert "GET" in response_data["supported_methods"]
        assert "POST" in response_data["supported_methods"]
    
    def test_post_request_success(self):
        """Test successful POST request with tokenization"""
        # Create mock request
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = {
            "text": "Hello world",
            "model": "gpt2"
        }
        
        # Mock the tokenize_text function
        mock_tokenize_result = {
            "success": True,
            "model": "gpt2",
            "text": "Hello world",
            "tokens": ["Hello", " world"],
            "token_ids": [15496, 995],
            "token_count": 2,
            "vocab_size": 50257,
            "special_tokens": {"pad_token": "<|endoftext|>"}
        }
        
        with patch('TokenizerFunction.tokenize_text', return_value=mock_tokenize_result):
            response = main(req)
        
        # Assert response
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["success"] is True
        assert response_data["model"] == "gpt2"
        assert response_data["text"] == "Hello world"
        assert response_data["token_count"] == 2
    
    def test_post_request_missing_text(self):
        """Test POST request with missing text parameter"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = {"model": "gpt2"}  # Missing 'text'
        
        response = main(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Text parameter is required"
    
    def test_post_request_empty_text(self):
        """Test POST request with empty text"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = {"text": ""}  # Empty text
        
        response = main(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Text parameter is required"
    
    def test_post_request_no_json_body(self):
        """Test POST request with no JSON body"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = None
        
        response = main(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Request body must be JSON"
    
    def test_post_request_invalid_json(self):
        """Test POST request with invalid JSON"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.side_effect = ValueError("Invalid JSON")
        
        response = main(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Invalid JSON in request body"
    
    def test_post_request_default_model(self):
        """Test POST request using default model"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = {"text": "Hello world"}  # No model specified
        
        mock_tokenize_result = {
            "success": True,
            "model": "gpt2",
            "text": "Hello world",
            "tokens": ["Hello", " world"],
            "token_ids": [15496, 995],
            "token_count": 2,
            "vocab_size": 50257,
            "special_tokens": {"pad_token": "<|endoftext|>"}
        }
        
        with patch('TokenizerFunction.tokenize_text', return_value=mock_tokenize_result) as mock_tokenize:
            response = main(req)
            
            # Verify that tokenize_text was called with the default model
            mock_tokenize.assert_called_once_with("Hello world", "gpt2", {})
        
        assert response.status_code == 200
    
    def test_post_request_with_options(self):
        """Test POST request with custom options"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = {
            "text": "Hello world",
            "model": "gpt2",
            "options": {
                "add_special_tokens": False,
                "include_decoded": True
            }
        }
        
        mock_tokenize_result = {
            "success": True,
            "model": "gpt2",
            "text": "Hello world"
        }
        
        with patch('TokenizerFunction.tokenize_text', return_value=mock_tokenize_result) as mock_tokenize:
            main(req)
            
            # Verify options were passed correctly
            expected_options = {
                "add_special_tokens": False,
                "include_decoded": True
            }
            mock_tokenize.assert_called_once_with("Hello world", "gpt2", expected_options)
    
    def test_post_request_tokenization_error(self):
        """Test POST request when tokenization fails"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = {"text": "Hello world"}
        
        mock_tokenize_result = {
            "success": False,
            "error": "Model loading failed"
        }
        
        with patch('TokenizerFunction.tokenize_text', return_value=mock_tokenize_result):
            response = main(req)
        
        assert response.status_code == 500
        response_data = json.loads(response.get_body().decode())
        assert response_data["success"] is False
        assert response_data["error"] == "Model loading failed"
    
    def test_unsupported_method(self):
        """Test unsupported HTTP method"""
        req = Mock(spec=func.HttpRequest)
        req.method = "PUT"
        
        response = main(req)
        
        assert response.status_code == 405
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Method PUT not allowed"
    
    def test_function_exception(self):
        """Test unexpected exception in function"""
        req = Mock(spec=func.HttpRequest)
        req.method = "GET"
        
        # Mock an unexpected exception
        with patch('json.dumps', side_effect=Exception("Unexpected error")):
            response = main(req)
        
        assert response.status_code == 500
        response_data = json.loads(response.get_body().decode())
        assert "Function execution failed" in response_data["error"]
    
    def test_environment_variable_fallback(self):
        """Test fallback when DEFAULT_MODEL environment variable is not set"""
        with patch.dict(os.environ, {}, clear=True):
            req = Mock(spec=func.HttpRequest)
            req.method = "GET"
            
            response = main(req)
            
            response_data = json.loads(response.get_body().decode())
            assert response_data["default_model"] == "openai/gpt-oss-120b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
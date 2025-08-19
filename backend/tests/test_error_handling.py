"""
Unit tests for error handling scenarios
"""
import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import azure.functions as func
from TokenizerFunction import main, get_tokenizer, tokenize_text


class TestErrorHandling:
    """Test comprehensive error handling scenarios"""
    
    def test_tokenizer_network_error(self):
        """Test handling of network errors when loading tokenizer"""
        import requests
        with patch('TokenizerFunction.AutoTokenizer') as mock_auto_tokenizer:
            mock_auto_tokenizer.from_pretrained.side_effect = requests.exceptions.ConnectionError("Network error")
            
            with pytest.raises(requests.exceptions.ConnectionError):
                get_tokenizer("gpt2")
    
    def test_tokenizer_auth_error(self):
        """Test handling of authentication errors"""
        from transformers import RepositoryNotFoundError
        
        with patch('TokenizerFunction.AutoTokenizer') as mock_auto_tokenizer:
            mock_auto_tokenizer.from_pretrained.side_effect = RepositoryNotFoundError("Repository not found")
            
            with pytest.raises(RepositoryNotFoundError):
                get_tokenizer("private/model")
    
    def test_tokenize_text_memory_error(self):
        """Test handling of memory errors during tokenization"""
        mock_tokenizer = Mock()
        mock_tokenizer.tokenize.side_effect = MemoryError("Out of memory")
        
        with patch('TokenizerFunction.get_tokenizer', return_value=mock_tokenizer):
            result = tokenize_text("Very long text" * 1000, "gpt2")
            
            assert result["success"] is False
            assert "Out of memory" in result["error"]
    
    def test_tokenize_text_encoding_error(self):
        """Test handling of encoding errors"""
        mock_tokenizer = Mock()
        mock_tokenizer.encode.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "invalid character")
        
        with patch('TokenizerFunction.get_tokenizer', return_value=mock_tokenizer):
            result = tokenize_text("Text with special characters: 🌟", "gpt2")
            
            assert result["success"] is False
            assert "error" in result
    
    def test_api_malformed_json_request(self):
        """Test API handling of malformed JSON"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        
        response = main(req)
        
        assert response.status_code == 400
        response_data = json.loads(response.get_body().decode())
        assert response_data["error"] == "Invalid JSON in request body"
    
    def test_api_large_payload(self):
        """Test API handling of extremely large payloads"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        # Simulate a very large text payload
        large_text = "A" * 1000000  # 1MB of text
        req.get_json.return_value = {"text": large_text}
        
        mock_tokenize_result = {
            "success": False,
            "error": "Text too large to process"
        }
        
        with patch('TokenizerFunction.tokenize_text', return_value=mock_tokenize_result):
            response = main(req)
        
        assert response.status_code == 500
    
    def test_api_timeout_simulation(self):
        """Test API behavior during timeout scenarios"""
        req = Mock(spec=func.HttpRequest)
        req.method = "POST"
        req.get_json.return_value = {"text": "Hello world"}
        
        # Simulate a timeout error
        with patch('TokenizerFunction.tokenize_text', side_effect=TimeoutError("Request timed out")):
            response = main(req)
        
        assert response.status_code == 500
        response_data = json.loads(response.get_body().decode())
        assert "Request timed out" in response_data["error"]
    
    def test_missing_environment_variables(self):
        """Test behavior when environment variables are missing"""
        with patch.dict(os.environ, {}, clear=True):
            req = Mock(spec=func.HttpRequest)
            req.method = "GET"
            
            response = main(req)
            
            # Should fall back to default
            assert response.status_code == 200
            response_data = json.loads(response.get_body().decode())
            assert response_data["default_model"] == "openai/gpt-oss-120b"
    
    def test_tokenizer_attribute_error(self):
        """Test handling of missing tokenizer attributes"""
        mock_tokenizer = Mock()
        mock_tokenizer.tokenize.return_value = ["test"]
        mock_tokenizer.encode.return_value = [123]
        mock_tokenizer.vocab_size = 50257
        
        # Remove some attributes to test getattr fallback
        del mock_tokenizer.pad_token
        del mock_tokenizer.cls_token
        
        with patch('TokenizerFunction.get_tokenizer', return_value=mock_tokenizer):
            result = tokenize_text("test", "gpt2")
            
            assert result["success"] is True
            assert result["special_tokens"]["pad_token"] is None
            assert result["special_tokens"]["cls_token"] is None
    
    def test_concurrent_requests_race_condition(self):
        """Test handling of race conditions in tokenizer caching"""
        import threading
        import time
        
        # Clear the cache
        if hasattr(tokenize_text, '_tokenizer_cache'):
            tokenize_text._tokenizer_cache.clear()
        
        results = []
        errors = []
        
        def make_request():
            try:
                with patch('TokenizerFunction.AutoTokenizer') as mock_auto_tokenizer:
                    mock_tokenizer = Mock()
                    mock_tokenizer.tokenize.return_value = ["test"]
                    mock_tokenizer.encode.return_value = [123]
                    mock_tokenizer.vocab_size = 50257
                    
                    # Add a small delay to simulate loading time
                    def slow_load(*args, **kwargs):
                        time.sleep(0.1)
                        return mock_tokenizer
                    
                    mock_auto_tokenizer.from_pretrained.side_effect = slow_load
                    result = get_tokenizer("gpt2")
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = [threading.Thread(target=make_request) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All requests should succeed, no race condition errors
        assert len(errors) == 0
        assert len(results) == 3
    
    def test_invalid_model_name_formats(self):
        """Test various invalid model name formats"""
        invalid_names = [
            "",
            None,
            "model with spaces",
            "model/with/too/many/slashes",
            "model@invalid",
            "model#invalid"
        ]
        
        for invalid_name in invalid_names:
            if invalid_name is None:
                continue
                
            with patch('TokenizerFunction.AutoTokenizer') as mock_auto_tokenizer:
                mock_auto_tokenizer.from_pretrained.side_effect = ValueError(f"Invalid model name: {invalid_name}")
                
                result = tokenize_text("test", invalid_name)
                assert result["success"] is False
                assert "error" in result
    
    def test_tokenizer_decode_error(self):
        """Test error handling in decode operation"""
        mock_tokenizer = Mock()
        mock_tokenizer.tokenize.return_value = ["test"]
        mock_tokenizer.encode.return_value = [123]
        mock_tokenizer.decode.side_effect = Exception("Decode failed")
        mock_tokenizer.vocab_size = 50257
        
        with patch('TokenizerFunction.get_tokenizer', return_value=mock_tokenizer):
            result = tokenize_text("test", "gpt2", {"include_decoded": True})
            
            # Should handle decode error gracefully
            assert result["success"] is False
            assert "Decode failed" in result["error"]


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_token_list(self):
        """Test handling of empty token lists"""
        mock_tokenizer = Mock()
        mock_tokenizer.tokenize.return_value = []
        mock_tokenizer.encode.return_value = []
        mock_tokenizer.vocab_size = 50257
        
        with patch('TokenizerFunction.get_tokenizer', return_value=mock_tokenizer):
            result = tokenize_text("", "gpt2")
            
            assert result["success"] is True
            assert result["tokens"] == []
            assert result["token_count"] == 0
    
    def test_special_characters_text(self):
        """Test tokenization of special characters and unicode"""
        special_texts = [
            "🌟⭐✨",  # Emojis
            "café naïve résumé",  # Accented characters
            "こんにちは世界",  # Japanese
            "مرحبا بالعالم",  # Arabic
            "\n\t\r",  # Whitespace characters
            "\\n\\t\\r",  # Escaped characters
        ]
        
        mock_tokenizer = Mock()
        mock_tokenizer.vocab_size = 50257
        
        for text in special_texts:
            mock_tokenizer.tokenize.return_value = [text]
            mock_tokenizer.encode.return_value = [123]
            
            with patch('TokenizerFunction.get_tokenizer', return_value=mock_tokenizer):
                result = tokenize_text(text, "gpt2")
                
                assert result["success"] is True
                assert result["text"] == text
    
    def test_very_long_text(self):
        """Test handling of very long text inputs"""
        long_text = "This is a test sentence. " * 10000  # ~250k characters
        
        mock_tokenizer = Mock()
        mock_tokenizer.tokenize.return_value = ["test"] * 10000
        mock_tokenizer.encode.return_value = list(range(10000))
        mock_tokenizer.vocab_size = 50257
        
        with patch('TokenizerFunction.get_tokenizer', return_value=mock_tokenizer):
            result = tokenize_text(long_text, "gpt2")
            
            assert result["success"] is True
            assert result["token_count"] == 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Unit tests for tokenizer functionality
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to sys.path to import the function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the functions we want to test
from TokenizerFunction import get_tokenizer, tokenize_text


class TestGetTokenizer:
    """Test the get_tokenizer function"""
    
    def test_get_tokenizer_caching(self):
        """Test that tokenizers are cached properly"""
        with patch('TokenizerFunction.AutoTokenizer') as mock_auto_tokenizer:
            mock_tokenizer = Mock()
            mock_auto_tokenizer.from_pretrained.return_value = mock_tokenizer
            
            # First call should load the tokenizer
            result1 = get_tokenizer("gpt2")
            assert result1 == mock_tokenizer
            mock_auto_tokenizer.from_pretrained.assert_called_once_with("gpt2")
            
            # Second call should use cached version
            result2 = get_tokenizer("gpt2")
            assert result2 == mock_tokenizer
            # Should still only be called once (cached)
            mock_auto_tokenizer.from_pretrained.assert_called_once()
    
    def test_get_tokenizer_different_models(self):
        """Test that different models are cached separately"""
        with patch('TokenizerFunction.AutoTokenizer') as mock_auto_tokenizer:
            mock_tokenizer1 = Mock()
            mock_tokenizer2 = Mock()
            mock_auto_tokenizer.from_pretrained.side_effect = [mock_tokenizer1, mock_tokenizer2]
            
            result1 = get_tokenizer("gpt2")
            result2 = get_tokenizer("bert-base-uncased")
            
            assert result1 == mock_tokenizer1
            assert result2 == mock_tokenizer2
            assert mock_auto_tokenizer.from_pretrained.call_count == 2
    
    def test_get_tokenizer_error_handling(self):
        """Test error handling when tokenizer loading fails"""
        with patch('TokenizerFunction.AutoTokenizer') as mock_auto_tokenizer:
            mock_auto_tokenizer.from_pretrained.side_effect = Exception("Model not found")
            
            with pytest.raises(Exception, match="Model not found"):
                get_tokenizer("invalid-model")


class TestTokenizeText:
    """Test the tokenize_text function"""
    
    def setup_method(self):
        """Set up mock tokenizer for each test"""
        self.mock_tokenizer = Mock()
        self.mock_tokenizer.tokenize.return_value = ["Hello", ",", "▁world", "!"]
        self.mock_tokenizer.encode.return_value = [15496, 11, 995, 0]
        self.mock_tokenizer.vocab_size = 50257
        self.mock_tokenizer.pad_token = "<|endoftext|>"
        self.mock_tokenizer.unk_token = "<|endoftext|>"
        self.mock_tokenizer.cls_token = None
        self.mock_tokenizer.sep_token = None
        self.mock_tokenizer.mask_token = None
    
    def test_tokenize_text_basic(self):
        """Test basic tokenization functionality"""
        with patch('TokenizerFunction.get_tokenizer', return_value=self.mock_tokenizer):
            result = tokenize_text("Hello, world!", "gpt2")
            
            assert result["success"] is True
            assert result["model"] == "gpt2"
            assert result["text"] == "Hello, world!"
            assert result["tokens"] == ["Hello", ",", "▁world", "!"]
            assert result["token_ids"] == [15496, 11, 995, 0]
            assert result["token_count"] == 4
            assert result["vocab_size"] == 50257
    
    def test_tokenize_text_with_options(self):
        """Test tokenization with custom options"""
        with patch('TokenizerFunction.get_tokenizer', return_value=self.mock_tokenizer):
            options = {
                "add_special_tokens": False,
                "include_decoded": True
            }
            self.mock_tokenizer.decode.return_value = "Hello, world!"
            
            result = tokenize_text("Hello, world!", "gpt2", options)
            
            assert result["success"] is True
            assert "decoded_text" in result
            assert result["decoded_text"] == "Hello, world!"
            
            # Verify encode was called with correct options
            self.mock_tokenizer.encode.assert_called_with("Hello, world!", add_special_tokens=False)
    
    def test_tokenize_text_default_options(self):
        """Test tokenization with default options"""
        with patch('TokenizerFunction.get_tokenizer', return_value=self.mock_tokenizer):
            result = tokenize_text("Hello, world!", "gpt2")
            
            # Verify encode was called with default options
            self.mock_tokenizer.encode.assert_called_with("Hello, world!", add_special_tokens=True)
    
    def test_tokenize_text_special_tokens(self):
        """Test that special tokens are properly extracted"""
        with patch('TokenizerFunction.get_tokenizer', return_value=self.mock_tokenizer):
            result = tokenize_text("Hello, world!", "gpt2")
            
            expected_special_tokens = {
                "pad_token": "<|endoftext|>",
                "unk_token": "<|endoftext|>",
                "cls_token": None,
                "sep_token": None,
                "mask_token": None
            }
            assert result["special_tokens"] == expected_special_tokens
    
    def test_tokenize_text_error_handling(self):
        """Test error handling in tokenization"""
        with patch('TokenizerFunction.get_tokenizer') as mock_get_tokenizer:
            mock_get_tokenizer.side_effect = Exception("Tokenizer loading failed")
            
            result = tokenize_text("Hello, world!", "invalid-model")
            
            assert result["success"] is False
            assert "error" in result
            assert result["error"] == "Tokenizer loading failed"
            assert result["model"] == "invalid-model"
            assert result["text"] == "Hello, world!"
    
    def test_tokenize_text_tokenizer_error(self):
        """Test error handling when tokenizer methods fail"""
        with patch('TokenizerFunction.get_tokenizer', return_value=self.mock_tokenizer):
            self.mock_tokenizer.tokenize.side_effect = Exception("Tokenization failed")
            
            result = tokenize_text("Hello, world!", "gpt2")
            
            assert result["success"] is False
            assert "error" in result
            assert "Tokenization failed" in result["error"]
    
    def test_tokenize_text_empty_string(self):
        """Test tokenization with empty string"""
        self.mock_tokenizer.tokenize.return_value = []
        self.mock_tokenizer.encode.return_value = []
        
        with patch('TokenizerFunction.get_tokenizer', return_value=self.mock_tokenizer):
            result = tokenize_text("", "gpt2")
            
            assert result["success"] is True
            assert result["tokens"] == []
            assert result["token_ids"] == []
            assert result["token_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
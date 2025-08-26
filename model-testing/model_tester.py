#!/usr/bin/env python3
"""
Multi-Model Testing Framework for Azure ML
Works with existing conda environment
"""

import time
import psutil
import json
from datetime import datetime
from typing import Dict, List, Any
import gc
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class ModelTester:
    """Test multiple language models and compare performance"""
    
    def __init__(self):
        self.results = []
        self.models_to_test = {
            # Start with smaller models first
            "gpt2": "gpt2",
            "gpt2-medium": "gpt2-medium", 
            "gpt2-large": "gpt2-large",
            
            # 7B models
            "llama2-7b": "meta-llama/Llama-2-7b-hf",
            "mistral-7b": "mistralai/Mistral-7B-v0.1",
            
            # 20B models (test if RAM allows)
            "gpt-neox-20b": "EleutherAI/gpt-neox-20b",
            "falcon-20b": "tiiuae/falcon-20b"
        }
    
    def get_system_info(self) -> Dict:
        """Get current system resource usage"""
        memory = psutil.virtual_memory()
        return {
            "ram_total_gb": memory.total // (1024**3),
            "ram_available_gb": memory.available // (1024**3),
            "ram_used_percent": memory.percent,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_model(self, model_name: str, model_id: str, test_prompt: str) -> Dict:
        """Test a single model and return performance metrics"""
        
        print(f"\n🧪 Testing {model_name} ({model_id})")
        print("-" * 50)
        
        start_time = time.time()
        
        try:
            # Record initial system state
            initial_memory = self.get_system_info()
            
            # Load tokenizer
            print("📝 Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load model
            print("🤖 Loading model...")
            model_load_start = time.time()
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,  # Save memory
                device_map="auto",
                low_cpu_mem_usage=True
            )
            model_load_time = time.time() - model_load_start
            
            # Record memory after loading
            after_load_memory = self.get_system_info()
            
            # Test inference
            print("⚡ Running inference...")
            inputs = tokenizer(test_prompt, return_tensors="pt", truncation=True, max_length=512)
            
            inference_start = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            inference_time = time.time() - inference_start
            
            # Decode output
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = generated_text[len(test_prompt):].strip()
            
            # Record final memory state
            final_memory = self.get_system_info()
            
            result = {
                "model_name": model_name,
                "model_id": model_id,
                "success": True,
                "model_load_time_seconds": round(model_load_time, 2),
                "inference_time_seconds": round(inference_time, 2),
                "total_time_seconds": round(time.time() - start_time, 2),
                "memory_initial": initial_memory,
                "memory_after_load": after_load_memory,
                "memory_final": final_memory,
                "response": response[:200] + "..." if len(response) > 200 else response,
                "response_length": len(response),
                "test_prompt": test_prompt
            }
            
            print(f"✅ Success! Load: {model_load_time:.1f}s, Inference: {inference_time:.1f}s")
            print(f"📝 Response preview: {response[:100]}...")
            
        except Exception as e:
            result = {
                "model_name": model_name,
                "model_id": model_id,
                "success": False,
                "error": str(e),
                "total_time_seconds": round(time.time() - start_time, 2),
                "memory_initial": self.get_system_info()
            }
            print(f"❌ Error: {str(e)}")
        
        # Cleanup
        try:
            del model
            del tokenizer
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        except:
            pass
        
        return result
    
    def run_tests(self, test_prompt: str = None) -> List[Dict]:
        """Run tests on all models"""
        
        if test_prompt is None:
            test_prompt = """Write a professional grant application response for the following:

Organization: Tech for Education Initiative
Project: AI-powered learning platform for underserved communities
Funding Request: $150,000
Question: Describe how your organization's mission aligns with this funding opportunity.

Response:"""
        
        print("🚀 Starting Multi-Model Testing")
        print(f"💾 System: {self.get_system_info()}")
        print(f"📝 Test prompt: {test_prompt[:100]}...")
        print("=" * 60)
        
        for model_name, model_id in self.models_to_test.items():
            # Check memory before each test
            memory = psutil.virtual_memory()
            if memory.available < 10 * (1024**3):  # Less than 10GB available
                print(f"⚠️  Skipping {model_name} - insufficient memory ({memory.available//1024**3}GB available)")
                continue
            
            result = self.test_model(model_name, model_id, test_prompt)
            self.results.append(result)
            
            # Save results after each test
            self.save_results()
            
            print(f"💾 Memory after test: {psutil.virtual_memory().available//1024**3}GB available")
        
        return self.results
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"model_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"💾 Results saved to: {filename}")
    
    def print_summary(self):
        """Print summary of all test results"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = [r for r in self.results if r.get('success', False)]
        failed_tests = [r for r in self.results if not r.get('success', False)]
        
        print(f"✅ Successful tests: {len(successful_tests)}")
        print(f"❌ Failed tests: {len(failed_tests)}")
        
        if successful_tests:
            print("\n🏆 Performance Ranking:")
            sorted_results = sorted(successful_tests, key=lambda x: x['inference_time_seconds'])
            
            for i, result in enumerate(sorted_results, 1):
                print(f"{i}. {result['model_name']}")
                print(f"   ⚡ Inference: {result['inference_time_seconds']}s")
                print(f"   🔄 Load time: {result['model_load_time_seconds']}s") 
                print(f"   💾 Memory usage: {result['memory_after_load']['ram_used_percent']:.1f}%")
                print()

if __name__ == "__main__":
    tester = ModelTester()
    tester.run_tests()
    tester.print_summary()
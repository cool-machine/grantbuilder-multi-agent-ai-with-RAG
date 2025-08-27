# Multi-Tier Web Search Unit Tests

## Overview
Comprehensive unit tests for the multi-tier web search system that validates the cascading fallback mechanism: **Google → Bing → Brave → Intelligent Analysis**

## Test Coverage

### ✅ **Core Functionality Tests**

1. **`test_google_search_success`**
   - Tests successful Google Custom Search API response
   - Validates proper result parsing and formatting
   - Confirms Google API is tried first

2. **`test_google_quota_exhausted_fallback_to_bing`**
   - Mocks Google API quota exceeded (403 error)
   - Verifies automatic fallback to Bing Search API
   - Validates Bing result parsing

3. **`test_google_bing_exhausted_fallback_to_brave`**
   - Mocks both Google and Bing quota exhausted
   - Verifies fallback to Brave Search API
   - Validates Brave result parsing

4. **`test_all_apis_exhausted_fallback_to_intelligence`**
   - Mocks all three APIs as quota exhausted
   - Verifies fallback to intelligent analysis system
   - Validates query-specific knowledge synthesis

### ✅ **Intelligent Analysis Tests**

5. **`test_google_search_different_query_types`**
   - Tests intelligent fallback for different query categories:
     - **Salary queries**: Provides market salary data
     - **Funding queries**: Offers foundation funding landscape
     - **Organization queries**: Delivers competitive landscape analysis
     - **Budget queries**: Supplies budget allocation best practices

### ✅ **Error Handling Tests**

6. **`test_api_credentials_missing`**
   - Tests behavior when API credentials are not configured
   - Ensures graceful fallback to intelligent analysis

7. **`test_google_api_invalid_credentials`**
   - Tests handling of invalid API keys (400/401 errors)
   - Validates error handling and fallback mechanisms

8. **`test_network_timeout_handling`**
   - Tests timeout exception handling
   - Ensures system continues to function during network issues

### ✅ **System Behavior Tests**

9. **`test_search_tier_priority`**
   - **CRITICAL TEST**: Validates correct API priority order
   - Tracks actual API call sequence: Google → Bing → Brave
   - Ensures no APIs are skipped inappropriately

10. **`test_empty_search_results`**
    - Tests handling of APIs that return empty results
    - Validates graceful handling of malformed responses

11. **`test_sync_search_wrapper`**
    - Tests async function compatibility with sync contexts
    - Validates proper event loop handling

## Test Scenarios Validated

### 🎯 **Quota Exhaustion Cascade**
```
Google (403) → Bing (success) ✅
Google (403) → Bing (403) → Brave (success) ✅  
Google (403) → Bing (403) → Brave (403) → Intelligence ✅
```

### 🎯 **API Error Handling**
```
Invalid Credentials (400/401) → Fallback ✅
Network Timeout → Fallback ✅
Empty Results → Graceful Handling ✅
Missing Credentials → Fallback ✅
```

### 🎯 **Query Intelligence**
```
"salary research" → 💰 SALARY RESEARCH ✅
"grant funding" → 📊 FUNDING LANDSCAPE ANALYSIS ✅
"nonprofit organization" → 🏢 COMPETITIVE LANDSCAPE ✅
"budget allocation" → 💼 BUDGET BEST PRACTICES ✅
```

## Mock Strategy

- **Requests Library**: Mocked using `unittest.mock.patch`
- **Environment Variables**: Controlled using `patch.dict(os.environ)`
- **Response Simulation**: Realistic API response structures for each provider
- **Error Simulation**: HTTP status codes (403, 400, 500, timeout exceptions)

## Key Assertions

1. **Correct API Selection**: Validates Google is tried first, then Bing, then Brave
2. **Proper Fallback Logic**: Ensures quota exhaustion triggers next tier
3. **Result Format Validation**: Confirms proper parsing of each API's response format
4. **Intelligent Analysis**: Validates context-aware fallback research
5. **Error Resilience**: Confirms system continues functioning despite API failures

## Test Execution

```bash
# Run all tests
python -m pytest tests/test_web_search.py -v

# Run specific test
python -m pytest tests/test_web_search.py::TestMultiTierWebSearch::test_search_tier_priority -v

# Run with coverage
python -m pytest tests/test_web_search.py --cov=MultiAgentFramework --cov-report=html
```

## Expected Results

- **11/11 tests passing** ✅
- **100% coverage** of multi-tier search functionality
- **Validation** of complete quota exhaustion handling
- **Confirmation** of intelligent fallback system

## Integration Notes

These tests validate the core multi-tier search logic that powers the **Multi-Agent Grant Writing Framework**. The search system is used by:
- **Research Agent**: Competitive intelligence and funding patterns
- **Budget Agent**: Salary data and cost benchmarking  
- **All Agents**: Market research and industry analysis

The multi-tier approach ensures **maximum uptime** and **cost optimization** by leveraging free tiers across multiple providers before falling back to intelligent synthesis.
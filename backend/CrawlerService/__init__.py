import json
import asyncio
import logging
import azure.functions as func
from typing import Dict, Any
from .crawler_manager import CrawlerManager
from .database import FundingDatabase
from .config import CrawlerConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function for handling crawler operations
    
    Endpoints:
    - POST /api/CrawlerService?action=start&mode=mock|real - Start crawling
    - GET /api/CrawlerService?action=status - Get crawler status  
    - GET /api/CrawlerService?action=results - Get crawling results
    - POST /api/CrawlerService?action=config - Update crawler configuration
    - POST /api/CrawlerService?action=toggle_mode - Toggle between mock/real mode
    """
    
    logger.info('CrawlerService function processed a request.')
    
    try:
        # Get action parameter
        action = req.params.get('action', 'status').lower()
        
        # Enable CORS
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        # Handle OPTIONS request for CORS
        if req.method == 'OPTIONS':
            return func.HttpResponse('', status_code=200, headers=headers)
        
        # Route to appropriate handler
        if action == 'start':
            result = await handle_start_crawling(req)
        elif action == 'status':
            result = await handle_get_status(req)
        elif action == 'results':
            result = await handle_get_results(req)
        elif action == 'config':
            result = await handle_update_config(req)
        elif action == 'toggle_mode':
            result = await handle_toggle_mode(req)
        else:
            result = {
                'success': False,
                'error': f'Unknown action: {action}',
                'available_actions': ['start', 'status', 'results', 'config', 'toggle_mode']
            }
        
        return func.HttpResponse(
            json.dumps(result, indent=2),
            status_code=200 if result.get('success', False) else 400,
            headers=headers
        )
    
    except Exception as e:
        logger.error(f'Error in CrawlerService: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Internal server error in crawler service'
            }),
            status_code=500,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )

async def handle_start_crawling(req: func.HttpRequest) -> Dict[str, Any]:
    """Start the crawling process"""
    try:
        # Parse request parameters and body
        mode = req.params.get('mode', 'mock').lower()
        use_mock = mode == 'mock'
        
        request_body = req.get_json() if req.get_json() else {}
        
        logger.info(f'Starting crawler in {mode} mode')
        
        # Initialize crawler manager
        crawler_manager = CrawlerManager(use_mock=use_mock)
        
        # Start crawling
        result = await crawler_manager.start_crawl(request_body)
        
        return {
            'success': result.success,
            'message': f'Crawling completed successfully in {result.mode} mode' if result.success else 'Crawling failed',
            'mode': result.mode,
            'results': {
                'total_found': result.total_found,
                'saved_to_database': result.saved_count,
                'duration_seconds': result.duration_seconds,
                'errors': result.errors
            },
            'opportunities': result.opportunities[:10] if result.opportunities else []  # Preview first 10
        }
    
    except Exception as e:
        logger.error(f'Error starting crawler: {str(e)}')
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to start crawler'
        }

async def handle_get_status(req: func.HttpRequest) -> Dict[str, Any]:
    """Get crawler status and database statistics"""
    try:
        # Default to mock mode, but can be overridden
        mode = req.params.get('mode', 'mock').lower()
        use_mock = mode == 'mock'
        
        crawler_manager = CrawlerManager(use_mock=use_mock)
        status = crawler_manager.get_status()
        
        return {
            'success': True,
            'status': status
        }
    
    except Exception as e:
        logger.error(f'Error getting status: {str(e)}')
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to get crawler status'
        }

async def handle_get_results(req: func.HttpRequest) -> Dict[str, Any]:
    """Get crawling results from database"""
    try:
        # Parse query parameters
        limit = int(req.params.get('limit', '50'))
        source = req.params.get('source')
        query = req.params.get('query')
        
        # Use mock mode as default, but doesn't matter for results retrieval
        crawler_manager = CrawlerManager(use_mock=True)
        results = crawler_manager.get_results(limit=limit, source=source, query=query)
        
        return results
    
    except Exception as e:
        logger.error(f'Error getting results: {str(e)}')
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to get crawler results'
        }

async def handle_update_config(req: func.HttpRequest) -> Dict[str, Any]:
    """Update crawler configuration"""
    try:
        request_body = req.get_json()
        if not request_body:
            return {
                'success': False,
                'error': 'No configuration data provided',
                'message': 'Please provide configuration in request body'
            }
        
        # Validate the configuration
        config = CrawlerConfig(
            request_delay=request_body.get('request_delay', 2.0),
            max_concurrent_requests=request_body.get('max_concurrent_requests', 5),
            respect_robots_txt=request_body.get('respect_robots_txt', True)
        )
        
        return {
            'success': True,
            'message': 'Configuration validated successfully',
            'config': {
                'request_delay': config.request_delay,
                'max_concurrent_requests': config.max_concurrent_requests,
                'respect_robots_txt': config.respect_robots_txt
            }
        }
    
    except Exception as e:
        logger.error(f'Error updating config: {str(e)}')
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to update configuration'
        }

async def handle_toggle_mode(req: func.HttpRequest) -> Dict[str, Any]:
    """Toggle between mock and real crawling modes"""
    try:
        request_body = req.get_json() if req.get_json() else {}
        current_mode = request_body.get('current_mode', 'mock')
        
        # Toggle the mode
        new_mode = 'real' if current_mode == 'mock' else 'mock'
        use_mock = new_mode == 'mock'
        
        crawler_manager = CrawlerManager(use_mock=use_mock)
        status = crawler_manager.get_status()
        
        return {
            'success': True,
            'message': f'Switched to {new_mode} crawling mode',
            'previous_mode': current_mode,
            'current_mode': new_mode,
            'status': status
        }
    
    except Exception as e:
        logger.error(f'Error toggling mode: {str(e)}')
        return {
            'success': False,
            'error': str(e),
            'message': 'Failed to toggle crawler mode'
        }
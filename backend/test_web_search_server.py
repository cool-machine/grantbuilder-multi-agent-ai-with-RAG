#!/usr/bin/env python3
"""
Standalone Web Search Test Server
Test the Google Custom Search + Brave Search functionality without Azure Functions
"""

import asyncio
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import logging

# Add current directory to path to import our module
sys.path.append(os.path.dirname(__file__))

# Set up logging
logging.basicConfig(level=logging.INFO)

class WebSearchHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests - show status and simple form"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Simple HTML form to test web search
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Web Search Test</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .result { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                    .error { background: #ffe6e6; color: #d00; }
                    .success { background: #e6ffe6; color: #060; }
                    input[type="text"] { width: 300px; padding: 8px; }
                    button { padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; }
                    button:hover { background: #005a87; }
                </style>
            </head>
            <body>
                <h1>🔍 Web Search Test</h1>
                <p>Test the Google Custom Search (primary) + Brave Search (fallback) system</p>
                
                <form onsubmit="testSearch(event)">
                    <input type="text" id="query" placeholder="Enter search query" value="climate change grants" />
                    <button type="submit">Search</button>
                </form>
                
                <div id="results"></div>
                
                <script>
                async function testSearch(event) {
                    event.preventDefault();
                    const query = document.getElementById('query').value;
                    const resultsDiv = document.getElementById('results');
                    
                    resultsDiv.innerHTML = '<div class="result">🔍 Searching...</div>';
                    
                    try {
                        const response = await fetch('/search', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({query: query})
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            let html = `<div class="result success">
                                <h3>✅ Search Successful</h3>
                                <p><strong>Source:</strong> ${data.source_used}</p>
                                <p><strong>Results:</strong> ${data.total_results}</p>
                                <p><strong>Time:</strong> ${data.search_time}s</p>
                                <p><strong>Quota:</strong> ${data.quota_usage}</p>
                            </div>`;
                            
                            data.results.forEach((result, i) => {
                                html += `<div class="result">
                                    <h4>${i+1}. ${result.title}</h4>
                                    <p>${result.content}</p>
                                    <p><a href="${result.url}" target="_blank">${result.url}</a></p>
                                    <p><em>Source: ${result.source}</em></p>
                                </div>`;
                            });
                            
                            resultsDiv.innerHTML = html;
                        } else {
                            resultsDiv.innerHTML = `<div class="result error">
                                <h3>❌ Search Failed</h3>
                                <p><strong>Error:</strong> ${data.error_message}</p>
                                <p><strong>Quota:</strong> ${data.quota_usage || 'Unknown'}</p>
                            </div>`;
                        }
                    } catch (error) {
                        resultsDiv.innerHTML = `<div class="result error">
                            <h3>❌ Connection Error</h3>
                            <p>${error.message}</p>
                        </div>`;
                    }
                }
                </script>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            
        elif self.path == '/status':
            # Status endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            status = {
                "server": "Web Search Test Server",
                "google_api_configured": bool(os.getenv('GOOGLE_CUSTOM_SEARCH_KEY')),
                "google_cx_configured": bool(os.getenv('GOOGLE_CUSTOM_SEARCH_CX')),
                "brave_api_configured": bool(os.getenv('BRAVE_SEARCH_API_KEY')),
                "google_key_preview": os.getenv('GOOGLE_CUSTOM_SEARCH_KEY', '')[:20] + '...' if os.getenv('GOOGLE_CUSTOM_SEARCH_KEY') else None,
                "brave_key_preview": os.getenv('BRAVE_SEARCH_API_KEY', '')[:20] + '...' if os.getenv('BRAVE_SEARCH_API_KEY') else None,
            }
            
            self.wfile.write(json.dumps(status, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        """Handle POST requests - perform web search"""
        if self.path == '/search':
            try:
                # Read POST data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())
                query = data.get('query', 'test')
                
                # Import and run web search
                from reliable_web_search import reliable_web_search
                
                # Perform async search
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(reliable_web_search.web_search(query, count=3))
                loop.close()
                
                # Format response
                response_data = {
                    "success": result.success,
                    "query": query,
                    "source_used": result.source_used,
                    "total_results": result.total_results,
                    "search_time": result.search_time,
                    "results": [
                        {
                            "title": r.title,
                            "content": r.content[:300] + "..." if len(r.content) > 300 else r.content,
                            "url": r.url,
                            "source": r.source
                        } for r in result.results
                    ],
                    "error_message": result.error_message,
                    "quota_usage": result.quota_usage,
                    "requests_made": result.requests_made
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, indent=2).encode())
                
            except Exception as e:
                logging.error(f"Search error: {e}")
                error_response = {
                    "success": False,
                    "error_message": f"Search failed: {str(e)}",
                    "error_type": type(e).__name__
                }
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Override to use Python logging"""
        logging.info(f"{self.address_string()} - {format % args}")

if __name__ == '__main__':
    # Set environment variables
    os.environ['GOOGLE_CUSTOM_SEARCH_KEY'] = 'AIzaSyCucwfX-aRIQouwBT3L5FsytCwa8Xnhmkw'
    os.environ['GOOGLE_CUSTOM_SEARCH_CX'] = '21c7d5c3c29c245e5'
    os.environ['BRAVE_SEARCH_API_KEY'] = 'BSAnw95GF_t0f55nid0AluGgwvOxXwA'
    
    # Start server
    PORT = 8000
    server = HTTPServer(('localhost', PORT), WebSearchHandler)
    
    print("🔍 Web Search Test Server Starting...")
    print(f"🌐 Server running at: http://localhost:{PORT}")
    print(f"📊 Status endpoint: http://localhost:{PORT}/status")
    print("🔍 Open the URL in your browser to test web search")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()
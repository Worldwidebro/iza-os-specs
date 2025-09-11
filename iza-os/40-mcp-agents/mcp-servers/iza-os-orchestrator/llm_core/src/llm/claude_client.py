"""
Production-ready Claude client for Iza OS
"""

import os
import anthropic
from typing import Dict, Any, Optional
# from ...utils.rate_limiter import RateLimiter # Commented out for now, will create later
# from ...utils.logger import get_logger # Commented out for now, will create later

# logger = get_logger(__name__)

class ClaudeClient:
    """A production-ready client for the Claude API with rate limiting and error handling."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        # self.rate_limiter = RateLimiter(requests_per_minute=50)  # Respect rate limits
    
    # @rate_limiter.apply_limit
    def create_completion(self, prompt: str, model: str = "claude-3-sonnet-20240229", **kwargs) -> Dict[str, Any]:
        """Generate a completion using Claude with robust error handling."""
        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return {
                "success": True,
                "content": message.content,
                "model": model,
                "usage": message.usage
            }
        except anthropic.APIConnectionError as e:
            # logger.error(f"Connection error: {e}")
            return {"success": False, "error": f"Connection failed: {e}"}
        except anthropic.RateLimitError as e:
            # logger.error(f"Rate limit exceeded: {e}")
            return {"success": False, "error": "Rate limit exceeded. Please try again later."}
        except Exception as e:
            # logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": f"An unexpected error occurred: {e}"}

# Example of how an MCP server would use this
if __name__ == "__main__":
    # This part is for local testing and requires ANTHROPIC_API_KEY to be set in environment
    # client = ClaudeClient()
    # response = client.create_completion("Hello, Claude!")
    # if response['success']:
    #     print(response['content'])
    # else:
    #     print(f"Error: {response['error']}")
    print("ClaudeClient module created. Run tests or integrate into orchestrator.")

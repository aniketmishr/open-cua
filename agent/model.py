"""
The Model used in agent, litellm implementation for model agnosticisim, instructor for structured output
https://docs.litellm.ai/docs/#litellm-python-sdk
"""
import asyncio
import instructor
import litellm 
from typing import List, Dict, Any
from .schema import AgentStep
from dotenv import load_dotenv

load_dotenv()

client = instructor.from_litellm(litellm.acompletion)

async def get_agent_next_step(model: str = "openai/gpt-5-mini", messages : List[Dict] = list()) -> AgentStep:
    try: 
        return await client.chat.completions.create(
            model=model,
            response_model=AgentStep,
            messages = messages,
            max_retries=3,
            )
    except litellm.AuthenticationError as e: 
        # thrown when the api key is invalid
        print(f"Authentication failed: {e}")
    except litellm.RateLimitError as e: 
        # thrown when you've exceeded your rate limit
        print(f"Rate limited: {e}")
    except litellm.APIError as e: 
        # thrown for general API errors
        print(f"API error: {e}")

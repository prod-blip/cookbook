import asyncio
import os
from dotenv import load_dotenv
from agents import Runner
from agents_mcp import Agent, RunnerContext
from openai import OpenAI
from agents import set_tracing_export_api_key


load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")
set_tracing_export_api_key(api_key=api_key)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


mcp_config_path = "mcp_agent.config.yaml"

context = RunnerContext(
        mcp_config_path=mcp_config_path,  # Use default discovery
        
    )

    # Create agent with proper configuration
agent = Agent(
        name="LinkedInProfileAgent",
        instructions="You are an assistant that helps find information about LinkedIn profiles. Use the linkedin_profile_scraper tool to fetch profile details for the given username.",
        mcp_servers=["linkedin_profile_scraper"],  # Ensure this matches your MCP configuration
        mcp_server_registry=None
    )

prompt = f"Please fetch and analyze the LinkedIn profile for the username: 'atulpandey-iift'"

result = Runner.run_sync(agent, input=prompt, context=context)

print("LinkedIn Profile Analysis:")
print(result.final_output)
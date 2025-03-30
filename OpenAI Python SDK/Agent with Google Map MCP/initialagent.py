import asyncio
import os
from dotenv import load_dotenv
from agents import Runner,handoff
from agents_mcp import Agent, RunnerContext
from openai import OpenAI
from pydantic import BaseModel
from agents import set_tracing_export_api_key, RunContextWrapper
load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")
set_tracing_export_api_key(api_key=api_key)
   

itineraryagent = Agent(
        name="CityInfoAgent",
        instructions="Basis the input given please elaborate the itinerary"
    )


async def main():
    
    travel_info = {
        "destination": input("Where would you like to travel? "),
        "duration": input("How long would you like to stay? "),
        "month": input("What month are you travelling in? "),
        "experience": input("What kind of experience are you looking for? "),
        "travellers": input("Who are you travelling with? "),
        "priority": input("Are there some must see places that you want to go to? ")
    }

    raw_info = "\n".join(f"{k}: {v}" for k, v in travel_info.items())

    first_result = await Runner.run(
        itineraryagent,raw_info
    )

    print(first_result.final_output)
    
    



if __name__ == "__main__":
    asyncio.run(main())

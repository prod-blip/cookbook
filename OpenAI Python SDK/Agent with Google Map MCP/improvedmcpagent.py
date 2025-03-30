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

mcp_config_path = "mcp_agent.config.yaml"
context = RunnerContext(mcp_config_path=mcp_config_path)

class CityData(BaseModel):
   places: str
   
async def process_citydata(ctx: RunContextWrapper, input_data: CityData):
   print(f"citydata: {input_data.places}")
   

itineraryagent = Agent(
        name="CityInfoAgent",
        instructions="Basis the input given and considering all factors given by the user, please give the names of the places that can be visited. Do not elaborate the itinerary"
    )

locationagent = Agent(
        name='Location Agent',
        instructions="Give the distance between the places suggested. For example, if the place auggested are A, B, C, then give the distance of B from A and then C from B",
        # handoffs=[handoff(agent=cityagent, on_handoff=process_citydata, input_type=CityData)]
    )

synthesizer_agent = Agent(
    name="synthesizer_agent",
    instructions="You take the input and then build the complete itinerary around it",
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

    # print(first_result.final_output)
    
    second_result = await Runner.run(
        locationagent, first_result.final_output, context=context
    )

    # print(second_result.final_output)

    third_result = await Runner.run(
        synthesizer_agent, second_result.final_output
    )

    print(third_result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

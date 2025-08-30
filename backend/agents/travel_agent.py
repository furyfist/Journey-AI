# backend/agents/travel_agent.py

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

# Import all the tools we created in tools.py
from .tools import (
    search_the_web,
    find_flights,
    find_hotels,
    find_place_details,
    find_youtube_videos,
    add_trip_to_calendar
)

# Load environment variables
load_dotenv()

def create_travel_agent():
    """
    Assembles and returns the main travel agent executor.
    """
    # 1. --- DEFINE THE AGENT'S PERSONA AND INSTRUCTIONS (THE PROMPT) ---
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an expert travel AI assistant named Journey. Your primary goal is to create a personalized, detailed, and visually rich travel itinerary based on a user's request.

        **Your Process:**
        1.  **Deconstruct the Request**: Identify the destination, dates, traveler count, and any specific user interests (e.g., "foodie," "history lover," "adventurous").
        2.  **Gather Information**: Use your available tools sequentially to find flights, hotels, and points of interest. You MUST use your tools to get up-to-date information.
        3.  **Enrich the Itinerary**: For each major location or activity, use your tools to find and include:
            - A direct Google Maps link.
            - Relevant YouTube vlogs or Shorts, complete with thumbnails.
        4.  **Synthesize and Format**: Assemble all the gathered information into a single, cohesive, day-by-day itinerary. The final output MUST be well-formatted in Markdown. It should be engaging, easy to read, and visually appealing.
        5.  **Final Action (If Requested)**: If the user asks to schedule the trip, use the calendar tool as the very last step.

        **Important Rules:**
        - Be efficient and direct. Go straight to using the tools to build the plan.
        - Always use the `find_place_details` tool to get Google Maps links for locations.
        - Always use the `find_youtube_videos` tool to add visual flair to the itinerary.
        """),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 2. --- INITIALIZE THE LLM ---
    # We use a powerful model capable of tool calling
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 3. --- GATHER ALL THE TOOLS ---
    tools = [
        search_the_web,
        find_flights,
        find_hotels,
        find_place_details,
        find_youtube_videos,
        add_trip_to_calendar
    ]

    # 4. --- CREATE THE AGENT ---
    # This binds the LLM, the prompt, and the tools together
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 5. --- CREATE THE AGENT EXECUTOR ---
    # This is the final, runnable object that powers the agent's logic loop
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True  # Set to True to see the agent's thought process in the terminal
    )

    return agent_executor

# Create a single, reusable instance of the agent
travel_agent_executor = create_travel_agent()
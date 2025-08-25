# backend/services/calendar_service.py
from core.config import emailer_agent # We use the emailer_agent as it has tools enabled

async def add_event_to_calendar(title: str, start_time: str, end_time: str, description: str, attendees: list[str]) -> dict:
    """
    Uses the Portia agent's Google Calendar tool to create a new event.
    """
    if not emailer_agent:
        raise Exception("Tool-enabled Agent (emailer_agent) not initialized.")

    # The prompt must be extremely precise, instructing the agent on exactly which tool to use
    # and how to map our variables to the tool's required arguments.
    agent_prompt = (
        f"Your task is to create a Google Calendar event. Use the 'portia:google:gcalendar:create_event' tool. "
        f"Set the 'event_title' to '{title}'. "
        f"Set the 'start_time' to '{start_time}'. "
        f"Set the 'end_time' to '{end_time}'. "
        f"Set the 'event_description' to '{description}'. "
        f"Set the 'attendees' to the following list: {attendees}."
    )

    print(f"Calendar Service: Instructing agent to create event...")
    try:
        # We use the agent that was initialized with the PortiaToolRegistry
        result = await emailer_agent.arun(agent_prompt)
        print("Calendar Service: Agent task completed.")
        return result.model_dump()
    except Exception as e:
        print(f"Calendar Service Error: {e}")
        return {"status": "error", "message": "Failed to create calendar event."}
from core.config import portia_agent
import json

async def add_itinerary_to_calendar(itinerary: list[dict]) -> str:
    """
    Uses the Portia agent's Google Calendar tools to check availability and add itinerary events to the user's calendar.
    
    Args:
        itinerary: A list of dictionaries containing event details with keys 'event_title', 
                  'start_time', 'end_time', and 'event_description'. 
                  Example: [{'event_title': 'Visit Louvre', 'start_time': '2024-09-20T10:00:00', 
                             'end_time': '2024-09-20T12:00:00', 'event_description': 'Tour the Louvre Museum'}]

    Returns:
        A string summarizing the result of the calendar event creation process.
    """
    if not portia_agent:
        raise Exception("Research Agent not initialized.")

    results = []
    
    for event in itinerary:
        # Validate required fields
        required_fields = ['event_title', 'start_time', 'end_time', 'event_description']
        if not all(field in event for field in required_fields):
            results.append(f"Failed to add event '{event.get('event_title', 'Unknown')}' to calendar: Missing required fields.")
            continue

        # Step 1: Check availability using the check_availability tool
        availability_data = {
            "start_time": event['start_time'],
            "end_time": event['end_time']
        }
        
        availability_prompt = (
            f"Your task is to check Google Calendar availability using the 'portia:google:gcalendar:check_availability' tool. "
            f"Use the following data: {json.dumps(availability_data)}. "
            f"Return only the raw output from the tool."
        )
        
        print(f"  - Calendar Service: Checking availability for event '{event['event_title']}'...")
        
        try:
            # Check availability
            availability_result = await portia_agent.arun(availability_prompt)
            await portia_agent.wait_for_ready()  # Handle OAuth clarification if raised
            availability_output = availability_result.outputs.final_output
            
            # Check if the time slot is available (assuming non-empty list means available)
            if not isinstance(availability_output, list) or not availability_output:
                print(f"  - Calendar Service: Time slot not available for '{event['event_title']}'.")
                results.append(f"Failed to add event '{event['event_title']}' to calendar: Time slot not available.")
                continue
        except Exception as e:
            print(f"  - Calendar Service Error checking availability for '{event['event_title']}': {e}")
            results.append(f"Failed to add event '{event['event_title']}' to calendar: Availability check failed - {str(e)}")
            continue

        # Step 2: Create event if slot is available
        event_data = {
            "event_title": event['event_title'],
            "start_time": event['start_time'],
            "end_time": event['end_time'],
            "event_description": event['event_description'],
            "attendees": []  # Assuming no attendees for travel itinerary events
        }
        
        event_prompt = (
            f"Your task is to create a Google Calendar event using the 'portia:google:gcalendar:create_event' tool. "
            f"Use the following event data: {json.dumps(event_data)}. "
            f"Return only the raw output from the tool."
        )
        
        print(f"  - Calendar Service: Instructing agent to create event '{event['event_title']}'...")
        
        try:
            # Create the event
            event_result = await portia_agent.arun(event_prompt)
            await portia_agent.wait_for_ready()  # Handle OAuth clarification if raised
            event_output = str(event_result.outputs.final_output)
            print(f"  - Calendar Service: Successfully created event '{event['event_title']}'.")
            results.append(f"Successfully added event '{event['event_title']}' to calendar: {event_output}")
        except Exception as e:
            print(f"  - Calendar Service Error creating event '{event['event_title']}': {e}")
            results.append(f"Failed to add event '{event['event_title']}' to calendar: {str(e)}")

    return "\n".join(results)
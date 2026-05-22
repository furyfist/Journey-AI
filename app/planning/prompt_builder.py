import json

from app.planning.schemas import ItinerarySchema, ResearchBundle


def researcher_system_prompt() -> str:
    return (
        "You are a travel research assistant. Gather real data about the destination using the tools provided.\n\n"
        "Step 1: Call get_weather with the city name to fetch weather AND get the city's lat/lon coordinates.\n"
        "Step 2: Use those lat/lon coordinates to call search_places for at least two categories "
        "(e.g. 'attractions' and 'food'). You may call search_places up to 4 times for different categories.\n\n"
        "Do NOT invent place names — only use data from tool results. "
        "After all tool calls are done, write a one-paragraph summary of what you found."
    )


def researcher_user_message(
    prompt: str,
    destination: str,
    total_days: int,
    start_date: str | None,
    budget: str | None,
) -> str:
    parts = [f"Research a {total_days}-day trip to {destination}."]
    if start_date:
        parts.append(f"Trip starts on {start_date}.")
    if budget:
        parts.append(f"Budget level: {budget}.")
    parts.append(f"Original request: {prompt}")
    parts.append("Use your tools to gather weather data and places in multiple categories.")
    return " ".join(parts)


def planner_system_prompt() -> str:
    return (
        "You are a travel planning strategist. Analyze the research data and build a logical day-by-day structure.\n\n"
        "Tasks:\n"
        "1. Detect the traveler's persona from the original request. Choose exactly ONE from:\n"
        "   Budget Backpacker, Luxury Explorer, Culture Seeker, Foodie, Adventure Junkie, "
        "Family Traveler, Digital Nomad.\n"
        "2. Build a day-by-day schedule using real place names from the research data.\n"
        "   Consider: timing (morning/afternoon/evening), weather conditions, and the traveler's persona.\n"
        "3. For each day write a short reasoning explaining the structure.\n\n"
        "Output ONLY a JSON object with this exact shape:\n"
        '{"persona": "string", "days": [{"day_number": 1, "date": null, "title": "Creative Title", '
        '"morning": ["place_name"], "afternoon": ["place_name"], "evening": ["place_name"], '
        '"reasoning": "Why this structure suits the traveler"}]}'
    )


def planner_user_message(prompt: str, research: ResearchBundle) -> str:
    return (
        f"Plan a {research.total_days}-day trip to {research.destination}.\n\n"
        f"Original request: {prompt}\n\n"
        f"Weather data:\n{json.dumps(research.weather, default=str)}\n\n"
        f"Available places by category:\n{json.dumps(research.places, default=str)}\n\n"
        "Build the day-by-day plan using real place names from the research above. "
        "Return only the JSON object."
    )


def synthesizer_system_prompt() -> str:
    schema = ItinerarySchema.model_json_schema()
    return (
        "You are a precise JSON generator. Convert the rough trip plan into the exact itinerary schema.\n\n"
        f"Required schema:\n{json.dumps(schema, indent=2)}\n\n"
        "Rules:\n"
        "- All required fields must be present and non-null.\n"
        "- Each time block must have 1–4 activities.\n"
        "- tips must have exactly 3–5 items.\n"
        "- Use real place names from the research data wherever possible.\n"
        "- Output ONLY the JSON object — no markdown, no explanation."
    )


def synthesizer_user_message(
    prompt: str, research: ResearchBundle, rough_plan: dict
) -> str:
    return (
        f"Convert this trip plan for {research.destination} into the required JSON schema.\n\n"
        f"Original request: {prompt}\n"
        f"Total days: {research.total_days}\n"
        f"Budget: {research.budget or 'mid-range'}\n\n"
        f"Weather data:\n{json.dumps(research.weather, default=str)}\n\n"
        f"Available places:\n{json.dumps(research.places, default=str)}\n\n"
        f"Rough plan to convert:\n{json.dumps(rough_plan, indent=2)}\n\n"
        "Generate the complete itinerary JSON now."
    )

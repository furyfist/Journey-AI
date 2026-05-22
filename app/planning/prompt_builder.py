import json

from app.planning.schemas import Conflict, ItinerarySchema, ResearchBundle


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


# ---------------------------------------------------------------------------
# Regeneration prompts
# ---------------------------------------------------------------------------

def regen_full_user_message(prompt: str, research: ResearchBundle, constraint: str | None) -> str:
    parts = [f"Replan a {research.total_days}-day trip to {research.destination}."]
    if constraint:
        parts.append(f"Constraint for this replan: {constraint}.")
    parts.append(f"Original request: {prompt}")
    parts.append(f"Weather data:\n{json.dumps(research.weather, default=str)}")
    parts.append(f"Available places:\n{json.dumps(research.places, default=str)}")
    parts.append("Build the day-by-day plan. Return only the JSON object.")
    return "\n\n".join(parts)


def regen_day_system_prompt() -> str:
    from app.planning.schemas import DayPlan
    schema = DayPlan.model_json_schema()
    return (
        "You are a travel day planner. Regenerate a single day's plan.\n\n"
        f"Required DayPlan schema:\n{json.dumps(schema, indent=2)}\n\n"
        "Rules:\n"
        "- Keep the same day_number and date.\n"
        "- Each time block must have 1–4 activities.\n"
        "- Use real place names from the research data.\n"
        "- Apply the constraint exactly.\n"
        "- Output ONLY the DayPlan JSON object — no markdown, no explanation."
    )


def regen_day_user_message(
    day_number: int,
    itinerary: "ItinerarySchema",
    research: ResearchBundle,
    constraint: str | None,
) -> str:
    existing_day = next((d for d in itinerary.days if d.day_number == day_number), None)
    weather_snap = existing_day.weather if existing_day else None
    parts = [
        f"Regenerate day {day_number} of a {itinerary.total_days}-day trip to {itinerary.destination}.",
        f"Traveler persona: {itinerary.persona}",
        f"Budget level: {itinerary.budget_level}",
    ]
    if constraint:
        parts.append(f"Constraint: {constraint}")
    parts.append(f"Weather for this day:\n{json.dumps(weather_snap, default=str)}")
    parts.append(f"Available places:\n{json.dumps(research.places, default=str)}")
    parts.append("Return only the DayPlan JSON.")
    return "\n\n".join(parts)


def regen_block_system_prompt() -> str:
    from app.planning.schemas import TimeBlock
    schema = TimeBlock.model_json_schema()
    return (
        "You are a travel block planner. Regenerate a single time block.\n\n"
        f"Required TimeBlock schema:\n{json.dumps(schema, indent=2)}\n\n"
        "Rules:\n"
        "- Keep the same label, start_time, and end_time as the original block.\n"
        "- 1–4 activities.\n"
        "- Use real place names from the research data.\n"
        "- Apply the constraint exactly.\n"
        "- Output ONLY the TimeBlock JSON object — no markdown, no explanation."
    )


def regen_block_user_message(
    day_number: int,
    block_label: str,
    itinerary: "ItinerarySchema",
    research: ResearchBundle,
    constraint: str | None,
) -> str:
    day = next((d for d in itinerary.days if d.day_number == day_number), None)
    existing_block = getattr(day, block_label, None) if day else None
    parts = [
        f"Regenerate the {block_label} block for day {day_number} of a trip to {itinerary.destination}.",
        f"Traveler persona: {itinerary.persona}",
        f"Budget level: {itinerary.budget_level}",
    ]
    if constraint:
        parts.append(f"Constraint: {constraint}")
    parts.append(
        f"Current block (for reference):\n"
        f"{json.dumps(existing_block.model_dump() if existing_block else {}, default=str)}"
    )
    parts.append(f"Available places:\n{json.dumps(research.places, default=str)}")
    parts.append("Return only the TimeBlock JSON.")
    return "\n\n".join(parts)


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


def critic_system_prompt() -> str:
    conflict_schema = Conflict.model_json_schema()
    return (
        "You are a travel itinerary critic. Review the trip plan and identify any quality issues "
        "the traveler would notice on the ground.\n\n"
        "Check for:\n"
        "1. Weather mismatches — outdoor activities on a stormy or snowy day.\n"
        "2. Distance conflicts — consecutive activities that are unrealistically far apart.\n"
        "3. Timing feasibility — activities that leave no time for travel or meals.\n"
        "4. Budget conflicts — expensive venues that contradict the stated budget level.\n"
        "5. Persona mismatches — e.g. nightclubs for Family Traveler, budget hostels for Luxury Explorer.\n\n"
        "For each genuine problem, output a Conflict object. "
        "If the plan looks sound, output an empty array.\n\n"
        f"Conflict schema:\n{json.dumps(conflict_schema, indent=2)}\n\n"
        "Output ONLY a JSON object with a single key 'conflicts' containing a list of Conflict objects. "
        "Example: {\"conflicts\": []}"
    )


def critic_user_message(
    itinerary: ItinerarySchema,
    pre_conflicts: list[Conflict],
    research: ResearchBundle,
) -> str:
    return (
        f"Review this {itinerary.total_days}-day itinerary for {itinerary.destination}.\n\n"
        f"Traveler persona: {itinerary.persona}\n"
        f"Budget level: {itinerary.budget_level}\n\n"
        f"Itinerary:\n{json.dumps(itinerary.model_dump(), default=str)}\n\n"
        f"Weather data:\n{json.dumps(research.weather, default=str)}\n\n"
        f"Pre-computed structural conflicts (for context — do not duplicate these):\n"
        f"{json.dumps([c.model_dump() for c in pre_conflicts], default=str)}\n\n"
        "Identify any additional quality issues. Return only the JSON object."
    )

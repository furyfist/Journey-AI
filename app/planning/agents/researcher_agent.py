import httpx

from app.common.logger import get_logger
from app.planning.agents.base_agent import BaseAgent
from app.planning.prompt_builder import researcher_system_prompt, researcher_user_message
from app.planning.schemas import ResearchBundle
from app.planning.tools import places_tool, weather_tool
from app.planning.tools.tool_registry import RESEARCHER_TOOLS

logger = get_logger(__name__)


class ResearcherAgent(BaseAgent):
    name = "researcher"
    tools = RESEARCHER_TOOLS

    def __init__(self, http: httpx.AsyncClient):
        super().__init__(http)
        self._weather: dict | None = None
        self._places: dict[str, list[dict]] = {}

    async def _execute_tool(self, tool_name: str, args: dict) -> dict:
        if tool_name == weather_tool.TOOL_NAME:
            result = await weather_tool.execute(self._http, args)
            self._weather = result
            return result
        if tool_name == places_tool.TOOL_NAME:
            result = await places_tool.execute(self._http, args)
            category = args.get("category", "places")
            self._places.setdefault(category, [])
            self._places[category].extend(result.get("places", []))
            return result
        return {"error": f"Unknown tool: {tool_name}"}

    async def run_research(
        self,
        prompt: str,
        destination: str,
        total_days: int,
        start_date: str | None = None,
        budget: str | None = None,
    ) -> ResearchBundle:
        user_msg = researcher_user_message(prompt, destination, total_days, start_date, budget)
        try:
            await self.run(
                user_message=user_msg,
                system_prompt=researcher_system_prompt(),
            )
        except Exception as exc:
            # Tool data already collected even if LLM summary step failed
            logger.warning("researcher LLM step failed (%s) — using collected tool data", exc)

        return ResearchBundle(
            destination=destination,
            prompt=prompt,
            total_days=total_days,
            weather=self._weather,
            places=self._places,
            budget=budget,
            start_date=start_date,
        )

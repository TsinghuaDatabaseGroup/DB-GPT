from __future__ import annotations

from typing import TYPE_CHECKING, List
from . import decision_maker_registry
from .base import BaseDecisionMaker
from multiagents.message import Message
if TYPE_CHECKING:
    from multiagents.agents.base import BaseAgent
    from multiagents.message import CriticMessage


@decision_maker_registry.register("brainstorming")
class BrainstormingDecisionMaker(BaseDecisionMaker):
    """
    Much like the horizontal decision maker, but with some twists:
    (1) Solver acts as a summarizer, summarizing the discussion of this turn
    (2) After summarizing, all the agents' memory are cleared, and replaced with
    the summary (to avoid exceeding maximum context length of the model too fast)
    """

    name: str = "brainstorming"

    async def astep(
        self,
        agents: List[BaseAgent],
        task_description: str,
        previous_plan: str = "No solution yet.",
        advice: str = "No advice yet.",
        *args,
        **kwargs,
    ) -> List[str]:
        if advice != "No advice yet.":
            self.broadcast_messages(
                agents, [Message(content=advice, sender="Evaluator")]
            )
        for agent in agents[1:]:
            review: CriticMessage = await agent.astep(
                previous_plan, advice, task_description
            )
            if review.content != "":
                self.broadcast_messages(agents, [review])

        result = agents[0].step(previous_plan, advice, task_description)
        for agent in agents:
            agent.memory.reset()
        self.broadcast_messages(
            agents,
            [
                Message(
                    content=result.content, sender="Summary From Previous Discussion"
                )
            ],
        )
        return [result]

from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, List
from . import decision_maker_registry
from .base import BaseDecisionMaker
from multiagents.message import Message
if TYPE_CHECKING:
    from multiagents.agents import BaseAgent
    from multiagents.message import CriticMessage, SolverMessage


@decision_maker_registry.register("vertical-solver-first")
class VerticalSolverFirstDecisionMaker(BaseDecisionMaker):
    """
    Discuss in a vertical manner.
    """

    name: str = "vertical"
    max_inner_turns: int = 3

    async def astep(
        self,
        agents: List[BaseAgent],
        task_description: str,
        previous_plan: str = "No solution yet.",
        advice: str = "No advice yet.",
        *args,
        **kwargs,
    ) -> List[SolverMessage]:
        # Here we assume that the first agent is the solver.
        # The rest of the agents are the reviewers.
        if advice != "No advice yet.":
            self.broadcast_messages(
                agents, [Message(content=advice, sender="Evaluator")]
            )
        previous_plan = agents[0].step(previous_plan, advice, task_description)
        self.broadcast_messages(agents, [previous_plan])
        
        for i in range(self.max_inner_turns):
            reviews: List[CriticMessage] = await asyncio.gather(
                *[
                    agent.astep(previous_plan, advice, task_description)
                    for agent in agents[1:]
                ]
            )

            nonempty_reviews = []
            for review in reviews:
                if not review.is_agree and review.content != "":
                    nonempty_reviews.append(review)

            self.broadcast_messages(agents, nonempty_reviews)
            previous_plan = agents[0].step(previous_plan, advice, task_description)

            self.broadcast_messages(agents, [previous_plan])
        result = previous_plan
        return [result]

    def broadcast_messages(self, agents, messages) -> None:
        for agent in agents:
            agent.add_message_to_memory(messages)

    def p2p_messages(self, agents, messages) -> None:
        agents[0].add_message_to_memory(messages)
        for message in messages:
            for agent in agents[1:]:
                if agent.name == message.sender:
                    agent.add_message_to_memory(messages)
                    break

    def reset(self):
        pass

from __future__ import annotations

from typing import TYPE_CHECKING, List
import json

from . import role_assigner_registry
from .base import BaseRoleAssigner

if TYPE_CHECKING:
    from multiagents.message import RoleAssignerMessage
    from multiagents.agents import CriticAgent, RoleAssignerAgent


@role_assigner_registry.register("role_description")
class DescriptionAssigner(BaseRoleAssigner):
    """
    Generates descriptions for each agent.
    """

    cnt_agents: int = 0

    def step(
        self,
        role_assigner: RoleAssignerAgent,
        group_members: List[CriticAgent],
        advice: str = "No advice yet.",
        task_description: str = "",
        *args,
        **kwargs,
    ) -> List[CriticAgent]:


        selected_group_members = []

        # task_description is the list of the names of group_members
        expert_names = [member.name for member in group_members]


        # read the alert info from file
        with open("latest_alert_info.txt", "r") as f:
            alert_info = f.read()
            alert_info = alert_info.replace("\'", '\"')
            alert_info = alert_info.replace("'", '"')
            
            # todo: link relevant alerts to the agents
            alert_str = alert_info

        roles = role_assigner.step(advice, expert_names, alert_str)

        for role in roles:
            role = role.lower()
            for member in group_members:
                if member.name.lower() in role:
                    selected_group_members.append(member)
                    break

        return selected_group_members

    def reset(self):
        pass

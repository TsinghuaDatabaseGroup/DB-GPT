from __future__ import annotations

from typing import TYPE_CHECKING, List

from . import role_assigner_registry
from .base import BaseRoleAssigner


if TYPE_CHECKING:
    from multiagents.message import RoleAssignerMessage
    from multiagents.agents import CriticAgent, RoleAssignerAgent


@role_assigner_registry.register("role_description")
class DescriptionAssigner(BaseRoleAssigner):
    class Config:
        arbitrary_types_allowed = True

    """
    Generates descriptions for each agent.
    """

    alert_str: str = ""
    alert_dict: List[dict] = []
    
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

        roles = role_assigner.step(advice, expert_names, self.alert_str)

        for role in roles:
            role = role.lower()
            for member in group_members:
                if member.name.lower() in role:
                    selected_group_members.append(member)
                    break

        return selected_group_members

    def reset(self):
        pass

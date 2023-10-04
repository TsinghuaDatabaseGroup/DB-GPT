from __future__ import annotations

from typing import TYPE_CHECKING, List
import json
import re
from dateutil import parser, tz
from datetime import datetime, timedelta

from . import role_assigner_registry
from .base import BaseRoleAssigner


if TYPE_CHECKING:
    from multiagents.message import RoleAssignerMessage
    from multiagents.agents import CriticAgent, RoleAssignerAgent

def extract_alert_info():

    with open("latest_alert_info.txt", "r") as f:
        alert_info = f.read()
        alert_info = alert_info.replace("\'", '\"')
        alert_dict = alert_info.replace("'", '"')
    
    alert_dict = re.sub(r'"groupKey": ".*?",', '', alert_dict)
    alert_dict = json.loads(alert_dict)

    alert_status = alert_dict['status']
    alert_status = alert_status.strip()

    # identify the first alert 
    alert_desc = alert_dict['alerts'][0]['annotations']['description']
    alert_desc = alert_desc.strip()

    alert_exporter = alert_dict['alerts'][0]['labels']['instance']
    alert_exporter = alert_exporter.strip()

    # Critical High Warning Info
    alert_level = alert_dict['alerts'][0]['labels']['severity']
    alert_level = alert_level.strip()

    starts_at = parser.parse(alert_dict['alerts'][0]['startsAt'])
    ends_at = parser.parse(alert_dict['alerts'][0]['endsAt'])

    if ends_at.year == 1:
        ends_at = starts_at + timedelta(minutes=2)

    # Convert the start and end times to seconds since the Unix epoch
    epoch = datetime(1970, 1, 1, tzinfo=tz.tzutc())  # set timezone to UTC
    starts_at_seconds = (starts_at - epoch).total_seconds()
    ends_at_seconds = (ends_at - epoch).total_seconds()

    starts_at_seconds = str(int(starts_at_seconds))
    ends_at_seconds = str(int(ends_at_seconds))

    alert_info = f"Alert Status: {alert_status}\nAlert Description: {alert_desc}\nAlert Level: {alert_level}\nAlert Starts At: {starts_at_seconds}\nAlert Ends At: {ends_at_seconds}"

    alert_dict = {  "alert_status": alert_status,
                    "alert_level": alert_level, 
                    "alert_desc": alert_desc, 
                    "alert_exporter": alert_exporter, 
                    "start_time": starts_at_seconds,
                    "end_time": ends_at_seconds}

    return alert_info, alert_dict


@role_assigner_registry.register("role_description")
class DescriptionAssigner(BaseRoleAssigner):
    class Config:
        arbitrary_types_allowed = True

    """
    Generates descriptions for each agent.
    """

    alert_str: str = ""
    alert_dict: str  = ""
    alert_str, alert_dict = extract_alert_info()

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

from __future__ import annotations

import os
from typing import Dict, List, TYPE_CHECKING

import yaml

from multiagents.llms import llm_registry
from multiagents.agents import agent_registry
from multiagents.environments.base import BaseEnvironment
from multiagents.environments import env_registry
from multiagents.memory import memory_registry
from multiagents.custom_parser import output_parser_registry
from multiagents.tools.api_retrieval import APICaller, register_functions_from_module

import multiagents.tools.metric_monitor.api as metric_monitor
import multiagents.tools.query_advisor.api as query_advisor
import multiagents.tools.index_advisor.api as index_advisor

import importlib

if TYPE_CHECKING:
    from agents import BaseAgent


def load_llm(llm_config: Dict):
    llm_type = llm_config.pop("llm_type", "xxxx")

    return llm_registry.build(llm_type, **llm_config)


def load_memory(memory_config: Dict):
    memory_type = memory_config.pop("memory_type", "chat_history")
    return memory_registry.build(memory_type, **memory_config)


def load_tools(tool_config: List[Dict], max_api_num, agent_name):
    
    if len(tool_config) == 0:
        return []
    
    caller = APICaller()

    for tool in tool_config:

        api_module = importlib.import_module(f"""multiagents.tools.{tool["tool_name"]}.api""")
        register_functions_from_module(api_module, caller, max_api_num, agent_name)
    
    return caller


def load_environment(env_config: Dict) -> BaseEnvironment:
    
    env_type = env_config.pop("env_type", "basic")
    return env_registry.build(env_type, **env_config)


def load_agent(agent_config: Dict) -> BaseAgent:
    
    agent_type = agent_config.pop("agent_type", "conversation")
    agent = agent_registry.build(agent_type, **agent_config)

    return agent


def prepare_task_config(task, args):
    """Read the yaml config of the given task in `tasks` directory."""
    
    task_path = os.path.join(os.path.dirname(__file__), task)
    config_path = os.path.join(task_path, "config.yaml")
    
    if not os.path.exists(task_path):
        raise ValueError(f"Config {task} not found.")
    if not os.path.exists(config_path):
        raise ValueError(
            "You should include the config.yaml file in the task directory"
        )
    
    task_config = yaml.safe_load(open(config_path))

    # Build the output parser
    parser = output_parser_registry.build(task)
    task_config["output_parser"] = parser

    for i, agent_configs in enumerate(task_config["agents"]):

        agent_configs["memory"] = load_memory(agent_configs.get("memory", {}))
        if agent_configs.get("tool_memory", None) is not None:
            agent_configs["tool_memory"] = load_memory(agent_configs["tool_memory"])
        llm = load_llm(agent_configs.get("llm", "xxxx"))
        agent_configs["llm"] = llm
        
        agent_configs["tools"] = load_tools(agent_configs.get("tools", []), args.max_api_num, agent_configs['name'])

        agent_configs["name"] = agent_configs['name']

        agent_configs["output_parser"] = task_config["output_parser"]

    return task_config

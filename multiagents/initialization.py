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

import importlib

if TYPE_CHECKING:
    from agents import BaseAgent

LANGUAGE = "en"

def load_llm(llm_config: Dict):
    llm_type = llm_config.pop("llm_type", "xxxx")

    return llm_registry.build(llm_type, **llm_config)


def load_memory(memory_config: Dict):
    memory_type = memory_config.pop("memory_type", "chat_history")
    return memory_registry.build(memory_type, **memory_config)


def load_tools(tool_config: List[Dict], agent_name):

    if len(tool_config) == 0:
        return []

    caller = APICaller() # adopt tool matching model

    # register all the apis from required tools
    for tool in tool_config:
        api_module = importlib.import_module(f"""multiagents.tools.{tool["tool_name"]}.api""")
        register_functions_from_module(api_module, caller, agent_name)

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
    config_path = os.path.join(task_path, args.config_file)

    if not os.path.exists(task_path):
        raise ValueError(f"Config {task} not found.")
    if not os.path.exists(config_path):
        raise ValueError(
            "You should include the config.yaml file in the task directory"
        )

    task_config = yaml.safe_load(open(config_path, encoding='utf8'))
    global LANGUAGE
    LANGUAGE = task_config.get("language", LANGUAGE)

    # Build the output parser
    parser = output_parser_registry.build(task)
    task_config["output_parser"] = parser

    for i, agent_configs in enumerate(task_config["agents"]):

        agent_configs["memory"] = load_memory(agent_configs.get("memory", {}))
        if agent_configs.get("tool_memory", None) is not None:
            agent_configs["tool_memory"] = load_memory(agent_configs["tool_memory"])
        llm = load_llm(agent_configs.get("llm", "xxxx"))

        agent_configs["llm"] = llm
        agent_configs["tools"] = load_tools(agent_configs.get("tools", []), agent_configs['name'])
        agent_configs["name"] = agent_configs['name']
        
        # 临时给qwen写了个output parser, 不会影响之前的（主要是role assigner的config里有个dict）
        if isinstance(agent_configs.get("output_parser", None), str):
            agent_configs["output_parser"] = output_parser_registry.build(agent_configs["output_parser"])
        else:
            agent_configs["output_parser"] = task_config["output_parser"]

        agent_configs["language"] = task_config.get("language", "en")

    return task_config

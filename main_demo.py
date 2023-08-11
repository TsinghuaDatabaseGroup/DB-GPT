from agentverse.demo import UI
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--task", type=str, default="db_diag")
args = parser.parse_args()

ui = UI(args.task)
ui.launch()

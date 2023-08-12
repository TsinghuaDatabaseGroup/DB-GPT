import bmtools
import os

def run_tool_server():

    def load_database_tool():
        server.load_tool("database")

    def load_db_diag_tool():
        server.load_tool("db_diag")


    server = bmtools.ToolServer()
    # print(server.list_tools())

    # tool_choice = input("Enter 'ALL' to load all tools, or enter the specific tools you want to load (comma-separated): ")
    
    load_database_tool()
    load_db_diag_tool()

    server.serve()

if __name__ == "__main__":
    run_tool_server()

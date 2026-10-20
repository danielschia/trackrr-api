import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server

from database.base import db
from model.user import User
from model.dashboard import Dashboard
from model.list import List
from model.task import Task

from app import app as flask_app

server = Server("tracker-mcp")

from mcp_handlers import register_dashboard_tools
# from mcp_handlers.tools.tasks import register_task_tools
# from mcp_handlers.resources.dashboards import register_dashboard_resources

register_dashboard_tools(server)
# register_task_tools(server)
# register_dashboard_resources(server)

async def main():
    with flask_app.app_context():
        db.create_all()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

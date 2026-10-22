import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from app import app as flask_app
from database.base import db
from mcp_handlers.tools.dashboards import list_dashboards
from mcp_handlers.tools.lists import list_lists
from mcp_handlers.tools.tasks import create_task, list_tasks

server = Server("tracker-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_dashboards",
            description="Lista todos os dashboards de um usuário",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID do usuário"}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="create_task",
            description="Cria uma nova task em uma lista de um dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID do usuário"},
                    "title": {"type": "string", "minLength": 1, "description": "Título da task"},
                    "description": {"type": "string", "description": "Descrição opcional"},
                    "list_id": {"type": "integer", "description": "ID da lista onde a task entra"},
                    "dashboard_id": {"type": "integer", "description": "ID do dashboard"}
                },
                "required": ["user_id", "title", "list_id", "dashboard_id"]
            }
        ),
        Tool(
            name="list_tasks",
            description="Lista todas as tasks de uma lista",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID do usuário"},
                    "list_id": {"type": "integer", "description": "ID da lista"}
                },
                "required": ["user_id", "list_id"]
            }
        ),
        Tool(
            name="list_lists",
            description="Lista todas as listas de um dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID do usuário"},
                    "dashboard_id": {"type": "integer", "description": "ID do dashboard"}
                },
                "required": ["user_id", "dashboard_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_dashboards":
            result = await list_dashboards(user_id=arguments["user_id"])
        
        elif name == "create_task":
            result = await create_task(
                user_id=arguments["user_id"],
                title=arguments["title"],
                description=arguments.get("description", ""),
                list_id=arguments["list_id"],
                dashboard_id=arguments["dashboard_id"]
            )
        
        elif name == "list_tasks":
            result = await list_tasks(
                user_id=arguments["user_id"],
                list_id=arguments["list_id"]
            )
        
        elif name == "list_lists":
            result = await list_lists(
                user_id=arguments["user_id"],
                dashboard_id=arguments["dashboard_id"]
            )
        
        else:
            raise ValueError(f"Tool desconhecida: {name}")
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    
    except ValueError as e:
        return [TextContent(type="text", text=f"Erro: {e}")]


async def main():
    with flask_app.app_context():
        db.create_all()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

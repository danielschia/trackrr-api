from mcp.server import Server
from mcp.types import Tool, TextContent

from app import app as flask_app
from model.dashboard import Dashboard

def register_dashboard_tools(server: Server):
    
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
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "list_dashboards":
            user_id = arguments["user_id"]
            
            # SQLAlchemy precisa do contexto de app
            with flask_app.app_context():
                dashboards = Dashboard.query.filter_by(user_id=user_id).all()
                result = [d.lightweight_dict() for d in dashboards]
            
            import json
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        raise ValueError(f"Tool desconhecida: {name}")
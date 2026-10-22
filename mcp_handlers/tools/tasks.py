
from mcp.server import Server
from mcp.types import TextContent, Tool


def register_tasks_tools(server: Server):

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return[
            Tool(
                name="create_task",
                description="Cria uma nova task em uma lista de um dashboard",
                inputSchema={
                    "type":"object",
                    "properties":{
                        "user_id": {"type": "integer", "description": "ID do usuário"},
                        "title": {"type": "string", "minLength": 1, "description": "Título da task"},
                        "description": {"type": "string", "description": "Descrição opcional"},
                        "list_id": {"type": "integer", "description": "ID da lista onde a task entra"},
                        "dashboard_id": {"type": "integer", "description": "ID do dashboard (deve ser o mesmo da lista)"}
                    },
                    "required": ["user_id", "title", "list_id", "dashboard_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name:str, arguments:dict) -> list[TextContent]:
        if name == "create_task":
             # TODO: extrair user_id, title, description, list_id, dashboard_id de arguments
            
            # TODO: title = title.strip(); se vazio, retornar erro
            
            # TODO: description default "" se None
            
            # TODO: validar Dashboard existe e pertence ao user_id
            
            # TODO: validar List existe, pertence ao user_id, e ao dashboard_id
            
            # TODO: query tasks_in_list da lista (order_by position, id)
            
            # TODO: target_position = len(tasks_in_list) + 1
            
            # TODO: criar Task com position=target_position
            
            # TODO: tasks_in_list.append(new_task), _reindex_task_positions(tasks_in_list)
            
            # TODO: db.session.add(new_task), db.session.commit()
            
            # TODO: retornar json.dumps(new_task.to_dict(), indent=2, ensure_ascii=False)
            
            pass
        
        raise ValueError(f"Tool desconhecida: {name}")

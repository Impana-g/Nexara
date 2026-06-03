from django.urls import path
from mcp import server
from django.http import JsonResponse

def mcp_index(request):
    return JsonResponse({
        "status": "ok",
        "endpoints": [
            "/mcp/list_nodes/",
            "/mcp/execute_node/",
            "/mcp/get_workflow_status/",
            "/mcp/submit_human_decision/",
        ]
    })

urlpatterns = [
    path('',                       mcp_index,                    name='mcp_index'),
    path('execute_node/',          server.execute_node,          name='mcp_execute_node'),
    path('submit_human_decision/', server.submit_human_decision, name='mcp_submit_human_decision'),
    path('get_workflow_status/',   server.get_workflow_status,   name='mcp_get_workflow_status'),
    path('list_nodes/',            server.list_nodes,            name='mcp_list_nodes'),
]
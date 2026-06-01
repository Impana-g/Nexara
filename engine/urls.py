# engine/urls.py

from django.urls import path
from engine import views

urlpatterns = [
    # Agent trigger
    path('api/engine/agents/<str:agent_code>/trigger/',
         views.trigger_agent, name='agent-trigger'),

    # Workflow runs
    path('api/engine/runs/',
         views.list_workflow_runs, name='workflow-run-list'),

    path('api/engine/runs/<uuid:run_id>/',
         views.workflow_run_status, name='workflow-run-detail'),

    # HITL
    path('api/engine/runs/<uuid:run_id>/hitl/submit/',
         views.submit_human_decision, name='hitl-submit'),

    # SSE real-time stream
    path('api/engine/runs/<uuid:run_id>/stream/',
         views.workflow_run_stream, name='workflow-run-stream'),

    # Internal (LangGraph → Django)
    path('api/internal/nodes/<str:node_code>/execute/',
         views.internal_node_execute, name='internal-node-execute'),
]
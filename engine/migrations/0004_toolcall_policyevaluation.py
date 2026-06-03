import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0003_alter_agent_code_alter_agent_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolCall',
            fields=[
                ('id',             models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('node_run',       models.ForeignKey('engine.NodeRun', on_delete=django.db.models.deletion.CASCADE, related_name='tool_calls')),
                ('tool_name',      models.CharField(max_length=100)),
                ('tool_version',   models.CharField(max_length=50, blank=True)),
                ('input_payload',  models.JSONField(default=dict)),
                ('output_payload', models.JSONField(default=dict)),
                ('status',         models.CharField(max_length=20, choices=[('success','Success'),('error','Error'),('timeout','Timeout')], default='success')),
                ('error_message',  models.TextField(blank=True)),
                ('duration_ms',    models.IntegerField(null=True, blank=True)),
                ('called_at',      models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'tool_calls', 'ordering': ['called_at']},
        ),
        migrations.CreateModel(
            name='PolicyEvaluation',
            fields=[
                ('id',             models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('workflow_run',   models.ForeignKey('engine.WorkflowRun', on_delete=django.db.models.deletion.CASCADE, related_name='policy_evaluations')),
                ('node_code',      models.CharField(max_length=100)),
                ('policy_code',    models.CharField(max_length=100)),
                ('policy_version', models.CharField(max_length=20, default='1.0')),
                ('outcome',        models.CharField(max_length=20, choices=[('pass','Pass'),('fail','Fail'),('warn','Warn'),('skip','Skip')])),
                ('evidence',       models.JSONField(default=dict)),
                ('rationale',      models.TextField(blank=True)),
                ('evaluated_at',   models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'policy_evaluations', 'ordering': ['evaluated_at']},
        ),
    ]
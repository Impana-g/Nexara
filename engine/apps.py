# engine/apps.py

from django.apps import AppConfig


class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'

    def ready(self):
        # Import all node modules here so @register_node decorators fire at startup
        import engine.nodes.common      # noqa: F401
        # Later: import engine.nodes.finance, engine.nodes.it, etc.
        import engine.nodes.finance   # noqa: F401  ← add this line
      
       
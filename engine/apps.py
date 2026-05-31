# engine/apps.py

from django.apps import AppConfig


class EngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'engine'

    def ready(self):
        import engine.nodes.common         # noqa: F401
        import engine.nodes.finance        # noqa: F401
        import engine.nodes.it             # noqa: F401
        import engine.nodes.hr             # noqa: F401
        import engine.nodes.legal          # noqa: F401
        import engine.nodes.healthcare     # noqa: F401
        import engine.nodes.insurance      # noqa: F401
        import engine.nodes.education      # noqa: F401
        import engine.nodes.government     # noqa: F401
        import engine.nodes.energy         # noqa: F401
        import engine.nodes.telecom        # noqa: F401
        import engine.nodes.manufacturing  # noqa: F401
        import engine.nodes.logistics      # noqa: F401
        import engine.nodes.retail         # noqa: F401
        import engine.nodes.cybersecurity  # noqa: F401
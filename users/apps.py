from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # This 'ready' method is a standard Django hook.
    # It runs exactly once when the application starts.
    def ready(self):
        # We import the signals file here.
        # By simply importing it, the @receiver decorators inside it get registered.
        import users.signals

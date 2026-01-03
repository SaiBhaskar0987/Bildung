from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "Safely apply migrations"

    def handle(self, *args, **kwargs):

        self.stdout.write("\n🔧 Creating migrations...")
        call_command("makemigrations")

        connection = connections["default"]
        executor = MigrationExecutor(connection)

        self.stdout.write("\n🔍 Checking migration state...")
        executor.loader.build_graph()

        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

        if not plan:
            self.stdout.write("✅ No migrations needed.")
            return

        existing_tables = set(connection.introspection.table_names())

        fake_migrations = []
        real_migrations = []

        for migration, _ in plan:
            needs_fake = False

            for op in migration.operations:
                if hasattr(op, "name"):
                    table_name = op.name.lower()
                    if table_name in existing_tables:
                        needs_fake = True

            if needs_fake:
                fake_migrations.append(migration)
            else:
                real_migrations.append(migration)

        for migration in fake_migrations:
            self.stdout.write(
                f"🧩 Faking migration: {migration.app_label}.{migration.name}"
            )
            call_command(
                "migrate",
                migration.app_label,
                migration.name,
                fake=True,
            )

        if real_migrations:
            self.stdout.write("🚀 Applying schema changes...")
            call_command("migrate")

        self.stdout.write(
            self.style.SUCCESS("\n✅ Migrations completed safely.\n")
        )

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "Safely apply migrations (fake initial only when required)"

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

        fake_required = False
        real_required = False

        for migration, _ in plan:
            if migration.initial:
                for op in migration.operations:
                    if hasattr(op, "name") and op.name.lower() in existing_tables:
                        fake_required = True
            else:
                real_required = True

        if fake_required:
            self.stdout.write("🧩 Faking initial migrations (tables already exist)...")
            call_command("migrate", fake_initial=True)

        if real_required:
            self.stdout.write("🚀 Applying schema changes...")
            call_command("migrate")

        self.stdout.write(
            self.style.SUCCESS("\n✅ Migrations completed safely.\n")
        )

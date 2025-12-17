import MySQLdb
from django.conf import settings

db_settings = settings.DATABASES['default']

def create_database():
    try:
        # Connect to MySQL server without selecting DB
        connection = MySQLdb.connect(
            host=db_settings['HOST'],
            user=db_settings['USER'],
            passwd=db_settings['PASSWORD']
        )

        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_settings['NAME']}`")
        print(f"Database `{db_settings['NAME']}` checked/created successfully!")
        cursor.close()
        connection.close()
    except Exception as e:
        print("Database creation failed:", e)

# Run creation if DB missing
create_database()
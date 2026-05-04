import sqlite3
import os

db_path = 'monitoring.db'

if not os.path.exists(db_path):
    print("Database file not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Count characters
    cursor.execute("SELECT count(*) FROM chat_service_characters")
    char_count = cursor.fetchone()[0]
    print(f"Total ChatServiceCharacters: {char_count}")

    # Count by service
    cursor.execute("SELECT service, count(*) FROM chat_service_characters GROUP BY service")
    rows = cursor.fetchall()
    print("Characters by Service:")
    for service, count in rows:
        print(f"  {service}: {count}")
    
    # Count new chat services
    cursor.execute("SELECT count(*) FROM new_chat_services")
    service_count = cursor.fetchone()[0]
    print(f"Total NewChatServices: {service_count}")

except sqlite3.OperationalError as e:
    print(f"Error querying database: {e}")

conn.close()

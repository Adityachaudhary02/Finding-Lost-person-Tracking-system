import mysql.connector

conn = mysql.connector.connect(host='localhost', user='root', password='Adi@808389', database='findthem_db', port=3306)
cursor = conn.cursor(dictionary=True)

print("Cases table columns:")
cursor.execute('DESCRIBE cases')
for col in cursor.fetchall():
    print(f"  {col['Field']}: {col['Type']}")

print("\nTesting INSERT:")
query = "INSERT INTO cases (name, status, description, contact, image_path, embedding, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
params = ('Test', 'missing', 'Test description', 'test@test.com', 'test.jpg', '[]', '2026-01-22 12:00:00')
try:
    cursor.execute(query, params)
    conn.commit()
    print(f"Insert successful! Last ID: {cursor.lastrowid}")
except Exception as e:
    print(f"Insert failed: {e}")
    conn.rollback()

cursor.close()
conn.close()

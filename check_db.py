import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Adi@808389'
    )
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute('SHOW DATABASES LIKE "findthem_db"')
    db_exists = len(cursor.fetchall()) > 0
    print(f"Database exists: {db_exists}")
    
    if db_exists:
        # Check tables and data
        cursor.execute('USE findthem_db')
        cursor.execute('SELECT COUNT(*) FROM cases')
        case_count = cursor.fetchone()[0]
        print(f"Total cases in database: {case_count}")
        
        cursor.execute('SELECT id, name, status, created_at FROM cases LIMIT 5')
        cases = cursor.fetchall()
        print(f"\nFirst few cases:")
        for case in cases:
            print(f"  ID: {case[0]}, Name: {case[1]}, Status: {case[2]}, Created: {case[3]}")
    
    cursor.close()
    conn.close()
    print("\nConnection successful!")
    
except Exception as e:
    print(f"Error: {e}")

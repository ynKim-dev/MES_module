import mariadb
import json


# 메인 파일에서 설정한 conn을 받아옴
def set_connection(connection):
    global conn
    conn = connection

def insert_budding(name, age):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sowing (name, age, ) VALUES (?, ?)", (name, age))
        conn.commit()
        print("User inserted successfully")
        return True
    except mariadb.Error as e:
        print(f"Error inserting user: {e}")
        return False

def get_budding(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dailymission WHERE (ProcessFlow = '발아')")  
        rows = cursor.fetchall()

        processed_rows = []
        for row in rows:
            
            completion_status = "미완료" if row[4] == 0 else "완료"

            json_data = json.loads(row[3])

            processed_row = {

                'Column1': row[0],
                'Column2': row[1],
                'Column3': row[2],
                'Column4': completion_status,
                'Column5': row[5],
                'Column6': row[6],
                'Column7': row[3]
            }

            processed_rows.append(processed_row)
            print(processed_rows)
        print("TEST Method")
        return processed_rows
    except mariadb.Error as e:
        print(f"Error getting budding: {e}")
        return None

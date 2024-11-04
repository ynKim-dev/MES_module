import mariadb
import json


# 메인 파일에서 설정한 conn을 받아옴
def set_connection(connection):
    global conn
    conn = connection

def insert_sub(name, age):
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sowing (name, age, ) VALUES (?, ?)", (name, age))
        conn.commit()
        print("User inserted successfully")
        return True
    except mariadb.Error as e:
        print(f"Error inserting user: {e}")
        return False

def get_store(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pstore ")  
        rows = cursor.fetchall()

        processed_rows = []
        for row in rows:
        
            processed_row = {

                'Column1': row[0],
                'Column2': row[1]
            }

            processed_rows.append(processed_row)
            print(processed_rows)
        print("TEST Method")
        return processed_rows
    except mariadb.Error as e:
        print(f"Error getting storeList: {e}")
        return None


def get_detail_store(conn, store):
    try:

        print(f"Executing query for StoreId: {store}")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM detailpstore WHERE StoreId = ?", (store,))
        rows = cursor.fetchall()

        processed_rows = []
        for row in rows:
            processed_row = {
                'Row': row[1],
                'Column': row[2],
                'KindLocal': row[4],
                'State': row[7]
            }
            processed_rows.append(processed_row)
        print(processed_rows)
        return processed_rows
    except mariadb.Error as e:
        print(f"Error getting storeList: {e}")
        return None
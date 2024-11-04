import mariadb
import json
import datetime


# 메인 파일에서 설정한 conn을 받아옴
def set_connection(connection):
    global conn
    conn = connection

def insert_sowing(conn, seedValue, trayStandardValue, trayQuantityValue, soilValue, soilQunatityValue, otherMaterial1Value, otherMaterialQunatity1Value, otherMaterial2Value, otherMaterialQuantity2Value, noteValue, missionNumber):
    try:
     
        completeDate = datetime.datetime.now().strftime("%Y-%m-%d")
        data = {
            "seedValue": seedValue,
            "trayStandardValue": trayStandardValue,
            "trayQuantityValue": trayQuantityValue,
            "soilValue": soilValue,
            "soilQunatityValue": soilQunatityValue,
            "otherMaterial1Value": otherMaterial1Value,
            "otherMaterialQunatity1Value": otherMaterialQunatity1Value,
            "otherMaterial2Value": otherMaterial2Value,
            "otherMaterialQuantity2Value": otherMaterialQuantity2Value
        }

        jsonData = json.dumps(data)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO sowing (Dataset, Note, CompleteDate, DailyMissionId) VALUES (?, ?, ?, ?)", (jsonData, noteValue, completeDate, str(missionNumber)))
        conn.commit()
        
        return True
    except mariadb.Error as e:
        print(f"Error inserting user: {e}")
        return False

def get_sowing(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dailymission WHERE (ProcessFlow = '파종대기' || ProcessFlow = '파종')")  
        rows = cursor.fetchall()

        processed_rows = []
        for row in rows:

            json_data = json.loads(row[3])

            processed_row = {

                'Column1': row[0],
                'Column2': json_data.get('Seed', ''),
                'Column3': row[2],
                'Column4': row[5],
                'Column5': row[6],
                'Column6': row[7],
                'Column7': row[3]
            }

            processed_rows.append(processed_row)
            print(processed_rows)
        print("TEST Method")
        return processed_rows
    except mariadb.Error as e:
        print(f"Error getting sowing: {e}")
        return None

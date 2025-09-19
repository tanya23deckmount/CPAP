from flask import Flask, jsonify, send_file, request
import sqlite3
import json
import os
from datetime import datetime
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Absolute path for JSON file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "view_user.json")

# Initialize database
def init_db():
    try:
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                string_serial_number TEXT,
                report_uniq_id_uid TEXT,
                device_user_id TEXT,
                device_reading TEXT,
                start_date TEXT,
                end_date TEXT,
                mask TEXT,
                mask_type TEXT,
                start_hour_min TEXT,
                end_hour_min TEXT,
                timedifferenceinMinute TEXT,
                reading_dev_mode TEXT,
                mode_name TEXT,
                device_name TEXT,
                csa_count TEXT,
                osa_count TEXT,
                hsa_count TEXT,
                a_flex TEXT,
                a_flex_level TEXT,
                a_flex_value TEXT,
                leak TEXT,
                max_pressure TEXT,
                min_pressure TEXT,
                pressurechangecount TEXT,
                ratechangeFactor TEXT,
                final_date TEXT,
                date_time TEXT,
                old_or_new TEXT
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Database and users table initialized")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        raise

# Function to update the JSON file
def update_json_file():
    try:
        logger.debug("Starting update_json_file")
        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, string_serial_number, report_uniq_id_uid, device_user_id, device_reading,
                   start_date, end_date, mask, mask_type, start_hour_min, end_hour_min,
                   timedifferenceinMinute, reading_dev_mode, mode_name, device_name,
                   csa_count, osa_count, hsa_count, a_flex, a_flex_level, a_flex_value,
                   leak, max_pressure, min_pressure, pressurechangecount, ratechangeFactor,
                   final_date, date_time, old_or_new
            FROM users
        """)
        rows = cursor.fetchall()
        
        users = {}
        for row in rows:
            users[str(row[0])] = {
                "string_serial_number": row[1] if row[1] is not None else "",
                "report_uniq_id_uid": row[2] if row[2] is not None else "",
                "device_user_id": row[3] if row[3] is not None else "",
                "device_reading": row[4] if row[4] is not None else "",
                "start_date": row[5] if row[5] is not None else "",
                "end_date": row[6] if row[6] is not None else "",
                "mask": row[7] if row[7] is not None else "",
                "mask_type": row[8] if row[8] is not None else "",
                "start_hour_min": row[9] if row[9] is not None else "",
                "end_hour_min": row[10] if row[10] is not None else "",
                "timedifferenceinMinute": row[11] if row[11] is not None else "",
                "reading_dev_mode": row[12] if row[12] is not None else "",
                "mode_name": row[13] if row[13] is not None else "",
                "device_name": row[14] if row[14] is not None else "",
                "csa_count": row[15] if row[15] is not None else "",
                "osa_count": row[16] if row[16] is not None else "",
                "hsa_count": row[17] if row[17] is not None else "",
                "a_flex": row[18] if row[18] is not None else "",
                "a_flex_level": row[19] if row[19] is not None else "",
                "a_flex_value": row[20] if row[20] is not None else "",
                "leak": row[21] if row[21] is not None else "",
                "max_pressure": row[22] if row[22] is not None else "",
                "min_pressure": row[23] if row[23] is not None else "",
                "pressurechangecount": row[24] if row[24] is not None else "",
                "ratechangeFactor": row[25] if row[25] is not None else "",
                "final_date": row[26] if row[26] is not None else "",
                "date_time": row[27] if row[27] is not None else "",
                "old_or_new": row[28] if row[28] is not None else ""
            }
        
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(JSON_FILE, "w", encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        
        conn.close()
        logger.info(f"JSON file updated with {len(users)} records at {JSON_FILE}")
        return len(users)
    except sqlite3.Error as e:
        logger.error(f"Database error in update_json_file: {e}")
        return 0
    except IOError as e:
        logger.error(f"File error when writing to {JSON_FILE}: {e}")
        return 0
    except Exception as e:
        logger.error(f"General error in update_json_file: {e}")
        return 0

# Helper endpoint to manually trigger JSON update
@app.route('/api/update_json', methods=['GET'])
def manual_update_json():
    try:
        count = update_json_file()
        logger.debug(f"Manually triggered JSON update, {count} records written")
        return jsonify({
            "status": "success",
            "message": f"JSON file updated with {count} records",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in manual_update_json: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Default home route
@app.route('/')
def home():
    return "Welcome! Use /api/users to fetch data, /api/send to forward JSON, /api/users (POST) to add data, /api/users/<id> (PUT) to update data, or /api/update_json to manually update JSON."

# API endpoint to get user data
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        count = update_json_file()
        with open(JSON_FILE, "r", encoding='utf-8') as f:
            users = json.load(f)
        
        logger.debug(f"Serving {count} users from JSON")
        return jsonify({
            "status": "success",
            "count": count,
            "data": users,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_users: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API endpoint to directly serve the JSON file
@app.route('/api/users/json', methods=['GET'])
def get_users_json():
    try:
        update_json_file()
        logger.debug(f"Serving JSON file from {JSON_FILE}")
        return send_file(JSON_FILE, mimetype='application/json')
    except Exception as e:
        logger.error(f"Error in get_users_json: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API endpoint to get user count
@app.route('/api/users/count', methods=['GET'])
def get_user_count():
    try:
        count = update_json_file()
        logger.debug(f"User count: {count}")
        return jsonify({
            "status": "success",
            "count": count,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in get_user_count: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API endpoint to get single user by ID
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        update_json_file()
        with open(JSON_FILE, "r", encoding='utf-8') as f:
            users = json.load(f)
        
        user = users.get(str(user_id))
        if user:
            logger.debug(f"Found user {user_id}")
            return jsonify({"status": "success", "user_id": user_id, "data": user})
        else:
            logger.warning(f"User {user_id} not found")
            return jsonify({"status": "error", "message": f"User {user_id} not found"}), 404
    except Exception as e:
        logger.error(f"Error in get_user_by_id: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to add a new user
@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        # Check Content-Type
        if not request.content_type or request.content_type != 'application/json':
            logger.warning(f"Invalid or missing Content-Type: {request.content_type}")
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        data = request.get_json()
        if not data:
            logger.warning("No input data provided or invalid JSON")
            return jsonify({"status": "error", "message": "No input data provided or invalid JSON"}), 400

        required_fields = ['start_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return jsonify({"status": "error", "message": f"Missing required fields: {missing_fields}"}), 400

        # Validate data types
        try:
            for field in ['timedifferenceinMinute', 'csa_count', 'osa_count', 'hsa_count', 'a_flex_level', 
                         'a_flex_value', 'leak', 'max_pressure', 'min_pressure', 'pressurechangecount', 
                         'ratechangeFactor']:
                if field in data and data[field] and not isinstance(data[field], (str, int, float)):
                    raise ValueError(f"{field} must be a string or number")
            for field in ['string_serial_number', 'report_uniq_id_uid', 'device_user_id', 'device_reading',
                         'start_date', 'end_date', 'mask', 'mask_type', 'start_hour_min', 'end_hour_min',
                         'reading_dev_mode', 'mode_name', 'device_name', 'a_flex', 'final_date', 'date_time',
                         'old_or_new']:
                if field in data and data[field] and not isinstance(data[field], str):
                    raise ValueError(f"{field} must be a string")
        except ValueError as e:
            logger.warning(f"Invalid data type: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 400

        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (
                    string_serial_number, report_uniq_id_uid, device_user_id, device_reading,
                    start_date, end_date, mask, mask_type, start_hour_min, end_hour_min,
                    timedifferenceinMinute, reading_dev_mode, mode_name, device_name,
                    csa_count, osa_count, hsa_count, a_flex, a_flex_level, a_flex_value,
                    leak, max_pressure, min_pressure, pressurechangecount, ratechangeFactor,
                    final_date, date_time, old_or_new
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('string_serial_number', ''),
                data.get('report_uniq_id_uid', ''),
                data.get('device_user_id', ''),
                data.get('device_reading', ''),
                data.get('start_date', ''),
                data.get('end_date', ''),
                data.get('mask', ''),
                data.get('mask_type', ''),
                data.get('start_hour_min', ''),
                data.get('end_hour_min', ''),
                data.get('timedifferenceinMinute', ''),
                data.get('reading_dev_mode', ''),
                data.get('mode_name', ''),
                data.get('device_name', ''),
                data.get('csa_count', ''),
                data.get('osa_count', ''),
                data.get('hsa_count', ''),
                data.get('a_flex', ''),
                data.get('a_flex_level', ''),
                data.get('a_flex_value', ''),
                data.get('leak', ''),
                data.get('max_pressure', ''),
                data.get('min_pressure', ''),
                data.get('pressurechangecount', ''),
                data.get('ratechangeFactor', ''),
                data.get('final_date', ''),
                data.get('date_time', ''),
                data.get('old_or_new', '')
            ))
            conn.commit()
        except sqlite3.Error as e:
            conn.close()
            logger.error(f"Database error during insertion: {e}")
            return jsonify({"status": "error", "message": f"Database error: {e}"}), 500
        finally:
            conn.close()

        user_id = cursor.lastrowid
        logger.debug(f"Added user {user_id} to database")

        count = update_json_file()
        logger.debug(f"JSON updated after adding user {user_id} with {count} records")
        return jsonify({
            "status": "success",
            "message": f"User {user_id} added successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        logger.error(f"Unexpected error in add_user: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to update an existing user
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        # Check Content-Type
        if not request.content_type or request.content_type != 'application/json':
            logger.warning(f"Invalid or missing Content-Type: {request.content_type}")
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        data = request.get_json()
        if not data:
            logger.warning("No input data provided or invalid JSON")
            return jsonify({"status": "error", "message": "No input data provided or invalid JSON"}), 400

        required_fields = ['start_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            return jsonify({"status": "error", "message": f"Missing required fields: {missing_fields}"}), 400

        # Validate data types
        try:
            for field in ['timedifferenceinMinute', 'csa_count', 'osa_count', 'hsa_count', 'a_flex_level', 
                         'a_flex_value', 'leak', 'max_pressure', 'min_pressure', 'pressurechangecount', 
                         'ratechangeFactor']:
                if field in data and data[field] and not isinstance(data[field], (str, int, float)):
                    raise ValueError(f"{field} must be a string or number")
            for field in ['string_serial_number', 'report_uniq_id_uid', 'device_user_id', 'device_reading',
                         'start_date', 'end_date', 'mask', 'mask_type', 'start_hour_min', 'end_hour_min',
                         'reading_dev_mode', 'mode_name', 'device_name', 'a_flex', 'final_date', 'date_time',
                         'old_or_new']:
                if field in data and data[field] and not isinstance(data[field], str):
                    raise ValueError(f"{field} must be a string")
        except ValueError as e:
            logger.warning(f"Invalid data type: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 400

        conn = sqlite3.connect("user_data.db")
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                conn.close()
                logger.warning(f"User {user_id} not found")
                return jsonify({"status": "error", "message": f"User {user_id} not found"}), 404

            cursor.execute("""
                UPDATE users
                SET string_serial_number = ?, report_uniq_id_uid = ?, device_user_id = ?,
                    device_reading = ?, start_date = ?, end_date = ?, mask = ?, mask_type = ?,
                    start_hour_min = ?, end_hour_min = ?, timedifferenceinMinute = ?,
                    reading_dev_mode = ?, mode_name = ?, device_name = ?, csa_count = ?,
                    osa_count = ?, hsa_count = ?, a_flex = ?, a_flex_level = ?, a_flex_value = ?,
                    leak = ?, max_pressure = ?, min_pressure = ?, pressurechangecount = ?,
                    ratechangeFactor = ?, final_date = ?, date_time = ?, old_or_new = ?
                WHERE id = ?
            """, (
                data.get('string_serial_number', ''),
                data.get('report_uniq_id_uid', ''),
                data.get('device_user_id', ''),
                data.get('device_reading', ''),
                data.get('start_date', ''),
                data.get('end_date', ''),
                data.get('mask', ''),
                data.get('mask_type', ''),
                data.get('start_hour_min', ''),
                data.get('end_hour_min', ''),
                data.get('timedifferenceinMinute', ''),
                data.get('reading_dev_mode', ''),
                data.get('mode_name', ''),
                data.get('device_name', ''),
                data.get('csa_count', ''),
                data.get('osa_count', ''),
                data.get('hsa_count', ''),
                data.get('a_flex', ''),
                data.get('a_flex_level', ''),
                data.get('a_flex_value', ''),
                data.get('leak', ''),
                data.get('max_pressure', ''),
                data.get('min_pressure', ''),
                data.get('pressurechangecount', ''),
                data.get('ratechangeFactor', ''),
                data.get('final_date', ''),
                data.get('date_time', ''),
                data.get('old_or_new', ''),
                user_id
            ))
            conn.commit()
        except sqlite3.Error as e:
            conn.close()
            logger.error(f"Database error during update: {e}")
            return jsonify({"status": "error", "message": f"Database error: {e}"}), 500
        finally:
            conn.close()

        logger.debug(f"Updated user {user_id} in database")
        
        update_json_file()
        logger.debug(f"JSON updated after updating user {user_id}")
        return jsonify({
            "status": "success",
            "message": f"User {user_id} updated successfully",
            "user_id": user_id
        })

    except Exception as e:
        logger.error(f"Unexpected error in update_user: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# API endpoint to send JSON to external API
@app.route('/api/send', methods=['GET', 'POST'])
def send_data_to_external():
    try:
        with open(JSON_FILE, "r", encoding='utf-8') as f:
            payload = json.load(f)

        logger.debug("Payload BEFORE sending:")
        logger.debug(json.dumps(payload, indent=4))

        url = "https://deckmount.in/api/web/tanya.php?user_id=1"
        response = requests.post(url, data={"data": json.dumps(payload)})

        logger.debug(f"External API status code: {response.status_code}")
        logger.debug("External API raw response:")
        logger.debug(response.text)

        try:
            external_json = response.json()
        except Exception:
            external_json = {"raw": response.text}

        return jsonify({
            "status": "success",
            "external_status": response.status_code,
            "external_response": external_json,
            "records_sent": len(payload)
        })

    except Exception as e:
        logger.error(f"Error in send_data_to_external: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500  

# creating own API to fetch data for a specific user from the database

def get_user_data(user_id):
    """Fetch data for a specific user from the database."""
    try:
        conn = sqlite3.connect("user_data.db")  # use your DB path
        conn.row_factory = sqlite3.Row  # dict-like rows
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))  # your DB column is `id`, not `user_id`
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        else:
            return None
    except Exception as e:
        print(f"DB Error: {str(e)}")
        return None



# API Endpoint
@app.route('/api/users/<username>/<int:user_id>', methods=['GET'])
def get_user(username, user_id):
    user_data = get_user_data(user_id)
    if user_data and user_data.get("username") == username:
        return jsonify({"status": "success", "data": user_data})
    else:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    
    
if __name__ == '__main__':
    init_db()  # Initialize database
    try:
        update_json_file()
        logger.info(f"✅ JSON file created/updated on startup at {JSON_FILE}")
    except Exception as e:
        logger.error(f"Failed to create/update JSON on startup: {str(e)}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
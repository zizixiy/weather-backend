import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'weather.db')

def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建天气记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            city TEXT,
            district TEXT,
            latitude REAL,
            longitude REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            realtime_weather TEXT,
            hourly_forecast TEXT,
            daily_forecast TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_weather_record(data: Dict[str, Any]) -> int:
    """保存天气记录到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    location = data.get('location', {})
    realtime_weather = data.get('realtime_weather', {})
    hourly_forecast = data.get('hourly_forecast', {})
    daily_forecast = data.get('daily_forecast', {})
    
    cursor.execute('''
        INSERT INTO weather_records 
        (ip_address, city, district, latitude, longitude, realtime_weather, hourly_forecast, daily_forecast)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('ip'),
        location.get('city'),
        location.get('district'),
        float(location.get('latitude', 0)),
        float(location.get('longitude', 0)),
        json.dumps(realtime_weather, ensure_ascii=False),
        json.dumps(hourly_forecast, ensure_ascii=False),
        json.dumps(daily_forecast, ensure_ascii=False)
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id

def get_latest_weather_record(city: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """获取最新的天气记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if city:
        cursor.execute('''
            SELECT * FROM weather_records 
            WHERE city = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (city,))
    else:
        cursor.execute('''
            SELECT * FROM weather_records 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'ip_address': row[1],
            'city': row[2],
            'district': row[3],
            'latitude': row[4],
            'longitude': row[5],
            'timestamp': row[6],
            'realtime_weather': json.loads(row[7]),
            'hourly_forecast': json.loads(row[8]),
            'daily_forecast': json.loads(row[9])
        }
    return None

def get_weather_history(city: Optional[str] = None, limit: int = 10) -> list:
    """获取天气历史记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if city:
        cursor.execute('''
            SELECT * FROM weather_records 
            WHERE city = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (city, limit))
    else:
        cursor.execute('''
            SELECT * FROM weather_records 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    records = []
    for row in rows:
        records.append({
            'id': row[0],
            'ip_address': row[1],
            'city': row[2],
            'district': row[3],
            'latitude': row[4],
            'longitude': row[5],
            'timestamp': row[6],
            'realtime_weather': json.loads(row[7]),
            'hourly_forecast': json.loads(row[8]),
            'daily_forecast': json.loads(row[9])
        })
    
    return records

# 初始化数据库
init_database()

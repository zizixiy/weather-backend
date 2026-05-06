from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from utils import get_client_ip
from services.location_service import get_location_by_ip, get_location_by_coordinates
from services.weather_service import get_weather_by_location, get_hourly_forecast, get_daily_forecast, get_comprehensive_weather
from services.database_service import save_weather_record, get_latest_weather_record, get_weather_history

# 创建FastAPI应用
app = FastAPI(
    title="雾霾探测系统API",
    description="通过IP地址获取地理位置和天气信息，包括实况数据、逐小时预报和生活指数",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/weather")
async def get_weather(request: Request):
    """通过IP地址获取天气信息（基础版）"""
    # 获取客户端IP地址
    client_ip = await get_client_ip(request)
    
    # 通过IP地址获取地理位置
    location = await get_location_by_ip(client_ip)
    
    # 通过地理位置获取天气信息
    weather = await get_weather_by_location(
        location.get('longitude'),
        location.get('latitude')
    )
    
    # 返回综合信息
    return {
        'ip': client_ip,
        'location': location,
        'weather': weather
    }

@app.get("/weather/comprehensive")
async def get_comprehensive_weather_endpoint(request: Request):
    """通过IP地址获取综合天气信息（完整版）"""
    # 获取客户端IP地址
    client_ip = await get_client_ip(request)
    
    # 通过IP地址获取地理位置
    location = await get_location_by_ip(client_ip)
    
    # 使用综合接口获取所有天气数据
    comprehensive_weather_data = await get_comprehensive_weather(
        location.get('longitude'),
        location.get('latitude'),
        dailysteps=3,  # 未来三天逐天预报
        hourlysteps=48  # 未来两天逐小时预报
    )
    
    # 构建综合数据，确保返回的JSON结构符合要求
    comprehensive_data = {
        'ip': client_ip,
        'location': {
            'city': location.get('city'),
            'district': location.get('district'),
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'address': location.get('address')
        },
        'realtime_weather': {
            'temperature': comprehensive_weather_data['realtime'].get('temperature'),
            'humidity': comprehensive_weather_data['realtime'].get('humidity'),
            'weather_condition': comprehensive_weather_data['realtime'].get('sky_condition'),
            'wind_direction': comprehensive_weather_data['realtime'].get('wind_direction'),
            'wind_speed': comprehensive_weather_data['realtime'].get('wind_speed'),
            'pressure': comprehensive_weather_data['realtime'].get('pressure'),
            'visibility': comprehensive_weather_data['realtime'].get('visibility'),
            'cloud_rate': comprehensive_weather_data['realtime'].get('cloud_rate'),
            'apparent_temperature': comprehensive_weather_data['realtime'].get('apparent_temperature'),
            'precipitation': comprehensive_weather_data['realtime'].get('precipitation')
        },
        'air_quality': comprehensive_weather_data['realtime'].get('air_quality', {
            'aqi': None,
            'pm25': None,
            'pm10': None,
            'o3': None,
            'so2': None,
            'no2': None,
            'co': None,
            'description': None
        }),
        'life_index': comprehensive_weather_data['realtime'].get('life_index', {}),
        'hourly_forecast': {
            'temperature': comprehensive_weather_data['hourly'].get('temperature', []),
            'precipitation': comprehensive_weather_data['hourly'].get('precipitation', []),
            'humidity': comprehensive_weather_data['hourly'].get('humidity', []),
            'wind': comprehensive_weather_data['hourly'].get('wind', []),
            'cloudrate': comprehensive_weather_data['hourly'].get('cloudrate', []),
            'skycon': comprehensive_weather_data['hourly'].get('skycon', []),
            'pressure': comprehensive_weather_data['hourly'].get('pressure', []),
            'visibility': comprehensive_weather_data['hourly'].get('visibility', []),
            'dswrf': comprehensive_weather_data['hourly'].get('dswrf', []),
            'air_quality': comprehensive_weather_data['hourly'].get('air_quality', {})
        },
        'daily_forecast': {
            'temperature': comprehensive_weather_data['daily'].get('temperature', []),
            'precipitation': comprehensive_weather_data['daily'].get('precipitation', []),
            'humidity': comprehensive_weather_data['daily'].get('humidity', []),
            'wind': comprehensive_weather_data['daily'].get('wind', []),
            'cloudrate': comprehensive_weather_data['daily'].get('cloudrate', []),
            'pressure': comprehensive_weather_data['daily'].get('pressure', []),
            'visibility': comprehensive_weather_data['daily'].get('visibility', []),
            'dswrf': comprehensive_weather_data['daily'].get('dswrf', []),
            'skycon': comprehensive_weather_data['daily'].get('skycon', []),
            'air_quality': comprehensive_weather_data['daily'].get('air_quality', {}),
            'life_index': comprehensive_weather_data['daily'].get('life_index', {}),
            'astro': comprehensive_weather_data['daily'].get('astro', [])
        },
        'forecast_keypoint': comprehensive_weather_data.get('forecast_keypoint', '')
    }
    
    # 保存到数据库
    try:
        record_id = save_weather_record(comprehensive_data)
        comprehensive_data['record_id'] = record_id
    except Exception as e:
        # 数据库保存失败不影响返回数据
        comprehensive_data['database_error'] = str(e)
    
    # 返回综合信息
    return comprehensive_data

@app.get("/weather/latest")
async def get_latest_weather(city: str = None):
    """获取最新的天气记录"""
    record = get_latest_weather_record(city)
    if record:
        return record
    else:
        return {"message": "没有找到天气记录"}

@app.get("/weather/history")
async def get_history(city: str = None, limit: int = 10):
    """获取天气历史记录"""
    records = get_weather_history(city, limit)
    return {"records": records, "count": len(records)}


@app.get("/weather/by-location")
async def get_weather_by_coordinates(longitude: str, latitude: str):
    """通过经纬度直接获取综合天气信息"""
    # 通过经纬度获取地理位置
    location = await get_location_by_coordinates(longitude, latitude)
    
    # 使用综合接口获取所有天气数据
    comprehensive_weather_data = await get_comprehensive_weather(
        longitude,
        latitude,
        dailysteps=3,  # 未来三天逐天预报
        hourlysteps=48  # 未来两天逐小时预报
    )
    
    # 构建综合数据，确保返回的JSON结构符合要求
    comprehensive_data = {
        'location': {
            'latitude': latitude,
            'longitude': longitude,
            'city': location.get('city'),
            'district': location.get('district'),
            'street': location.get('street'),
            'address': location.get('address')
        },
        'realtime_weather': {
            'temperature': comprehensive_weather_data['realtime'].get('temperature'),
            'humidity': comprehensive_weather_data['realtime'].get('humidity'),
            'weather_condition': comprehensive_weather_data['realtime'].get('sky_condition'),
            'wind_direction': comprehensive_weather_data['realtime'].get('wind_direction'),
            'wind_speed': comprehensive_weather_data['realtime'].get('wind_speed'),
            'pressure': comprehensive_weather_data['realtime'].get('pressure'),
            'visibility': comprehensive_weather_data['realtime'].get('visibility'),
            'cloud_rate': comprehensive_weather_data['realtime'].get('cloud_rate'),
            'apparent_temperature': comprehensive_weather_data['realtime'].get('apparent_temperature'),
            'precipitation': comprehensive_weather_data['realtime'].get('precipitation')
        },
        'air_quality': comprehensive_weather_data['realtime'].get('air_quality', {
            'aqi': None,
            'pm25': None,
            'pm10': None,
            'o3': None,
            'so2': None,
            'no2': None,
            'co': None,
            'description': None
        }),
        'life_index': comprehensive_weather_data['realtime'].get('life_index', {}),
        'hourly_forecast': {
            'temperature': comprehensive_weather_data['hourly'].get('temperature', []),
            'precipitation': comprehensive_weather_data['hourly'].get('precipitation', []),
            'humidity': comprehensive_weather_data['hourly'].get('humidity', []),
            'wind': comprehensive_weather_data['hourly'].get('wind', []),
            'cloudrate': comprehensive_weather_data['hourly'].get('cloudrate', []),
            'skycon': comprehensive_weather_data['hourly'].get('skycon', []),
            'pressure': comprehensive_weather_data['hourly'].get('pressure', []),
            'visibility': comprehensive_weather_data['hourly'].get('visibility', []),
            'dswrf': comprehensive_weather_data['hourly'].get('dswrf', []),
            'air_quality': comprehensive_weather_data['hourly'].get('air_quality', {})
        },
        'daily_forecast': {
            'temperature': comprehensive_weather_data['daily'].get('temperature', []),
            'precipitation': comprehensive_weather_data['daily'].get('precipitation', []),
            'humidity': comprehensive_weather_data['daily'].get('humidity', []),
            'wind': comprehensive_weather_data['daily'].get('wind', []),
            'cloudrate': comprehensive_weather_data['daily'].get('cloudrate', []),
            'pressure': comprehensive_weather_data['daily'].get('pressure', []),
            'visibility': comprehensive_weather_data['daily'].get('visibility', []),
            'dswrf': comprehensive_weather_data['daily'].get('dswrf', []),
            'skycon': comprehensive_weather_data['daily'].get('skycon', []),
            'air_quality': comprehensive_weather_data['daily'].get('air_quality', {}),
            'life_index': comprehensive_weather_data['daily'].get('life_index', {}),
            'astro': comprehensive_weather_data['daily'].get('astro', [])
        },
        'forecast_keypoint': comprehensive_weather_data.get('forecast_keypoint', '')
    }
    
    # 保存到数据库
    try:
        record_id = save_weather_record(comprehensive_data)
        comprehensive_data['record_id'] = record_id
    except Exception as e:
        # 数据库保存失败不影响返回数据
        comprehensive_data['database_error'] = str(e)
    
    # 返回综合信息
    return comprehensive_data


@app.get("/weather/by-coordinates")
async def get_weather_by_coordinates_json(
    longitude: str = Body(..., embed=True),
    latitude: str = Body(..., embed=True)
):
    """通过JSON请求体提交经纬度直接查询综合天气信息"""
    # 使用综合接口获取所有天气数据
    comprehensive_weather_data = await get_comprehensive_weather(
        longitude,
        latitude,
        dailysteps=3,  # 未来三天逐天预报
        hourlysteps=48  # 未来两天逐小时预报
    )
    
    # 构建综合数据，确保返回的JSON结构符合要求
    comprehensive_data = {
        'location': {
            'latitude': latitude,
            'longitude': longitude
        },
        'realtime_weather': {
            'temperature': comprehensive_weather_data['realtime'].get('temperature'),
            'humidity': comprehensive_weather_data['realtime'].get('humidity'),
            'weather_condition': comprehensive_weather_data['realtime'].get('sky_condition'),
            'wind_direction': comprehensive_weather_data['realtime'].get('wind_direction'),
            'wind_speed': comprehensive_weather_data['realtime'].get('wind_speed'),
            'pressure': comprehensive_weather_data['realtime'].get('pressure'),
            'visibility': comprehensive_weather_data['realtime'].get('visibility'),
            'cloud_rate': comprehensive_weather_data['realtime'].get('cloud_rate'),
            'apparent_temperature': comprehensive_weather_data['realtime'].get('apparent_temperature'),
            'precipitation': comprehensive_weather_data['realtime'].get('precipitation')
        },
        'air_quality': comprehensive_weather_data['realtime'].get('air_quality', {
            'aqi': None,
            'pm25': None,
            'pm10': None,
            'o3': None,
            'so2': None,
            'no2': None,
            'co': None,
            'description': None
        }),
        'life_index': comprehensive_weather_data['realtime'].get('life_index', {}),
        'hourly_forecast': {
            'temperature': comprehensive_weather_data['hourly'].get('temperature', []),
            'precipitation': comprehensive_weather_data['hourly'].get('precipitation', []),
            'humidity': comprehensive_weather_data['hourly'].get('humidity', []),
            'wind': comprehensive_weather_data['hourly'].get('wind', []),
            'cloudrate': comprehensive_weather_data['hourly'].get('cloudrate', []),
            'skycon': comprehensive_weather_data['hourly'].get('skycon', []),
            'pressure': comprehensive_weather_data['hourly'].get('pressure', []),
            'visibility': comprehensive_weather_data['hourly'].get('visibility', []),
            'dswrf': comprehensive_weather_data['hourly'].get('dswrf', []),
            'air_quality': comprehensive_weather_data['hourly'].get('air_quality', {})
        },
        'daily_forecast': {
            'temperature': comprehensive_weather_data['daily'].get('temperature', []),
            'precipitation': comprehensive_weather_data['daily'].get('precipitation', []),
            'humidity': comprehensive_weather_data['daily'].get('humidity', []),
            'wind': comprehensive_weather_data['daily'].get('wind', []),
            'cloudrate': comprehensive_weather_data['daily'].get('cloudrate', []),
            'pressure': comprehensive_weather_data['daily'].get('pressure', []),
            'visibility': comprehensive_weather_data['daily'].get('visibility', []),
            'dswrf': comprehensive_weather_data['daily'].get('dswrf', []),
            'skycon': comprehensive_weather_data['daily'].get('skycon', []),
            'air_quality': comprehensive_weather_data['daily'].get('air_quality', {}),
            'life_index': comprehensive_weather_data['daily'].get('life_index', {}),
            'astro': comprehensive_weather_data['daily'].get('astro', [])
        },
        'forecast_keypoint': comprehensive_weather_data.get('forecast_keypoint', '')
    }
    
    # 保存到数据库
    try:
        record_id = save_weather_record(comprehensive_data)
        comprehensive_data['record_id'] = record_id
    except Exception as e:
        # 数据库保存失败不影响返回数据
        comprehensive_data['database_error'] = str(e)
    
    # 返回综合信息
    return comprehensive_data


@app.get("/location/by-coordinates")
async def get_location_only(longitude: str, latitude: str):
    """通过经纬度仅获取地理位置信息（不含天气）"""
    # 通过经纬度获取地理位置
    location = await get_location_by_coordinates(longitude, latitude)
    return location


@app.get("/")
async def root():
    """根路径"""
    return {"message": "雾霾探测系统API服务运行中"}

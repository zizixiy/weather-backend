import httpx
import time
from config import CAIYUN_WEATHER_URL

# 缓存字典，用于存储API响应
cache = {
    'realtime': {'data': None, 'timestamp': 0},
    'hourly': {'data': None, 'timestamp': 0},
    'daily': {'data': None, 'timestamp': 0},
    'comprehensive': {'data': None, 'timestamp': 0}
}

# 缓存有效期（秒）
CACHE_EXPIRY = 3600  # 1小时

async def get_weather_by_location(longitude: str, latitude: str) -> dict:
    """通过经纬度获取天气实况数据"""
    cache_key = f"realtime_{longitude}_{latitude}"
    
    # 检查缓存
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_EXPIRY:
        return cache[cache_key]['data']
    
    url = f"{CAIYUN_WEATHER_URL}/{longitude},{latitude}/realtime"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # 提取天气信息
            if data.get('status') == 'ok':
                weather = data.get('result', {}).get('realtime', {})
                result = {
                    'temperature': weather.get('temperature'),
                    'humidity': weather.get('humidity'),
                    'wind_speed': weather.get('wind', {}).get('speed'),
                    'wind_direction': weather.get('wind', {}).get('direction'),
                    'pressure': weather.get('pressure'),
                    'sky_condition': weather.get('skycon'),
                    'visibility': weather.get('visibility'),
                    'cloud_rate': weather.get('cloudrate'),
                    'apparent_temperature': weather.get('apparent_temperature'),
                    'precipitation': weather.get('precipitation'),
                    # 空气质量指数
                    'air_quality': {
                        'aqi': weather.get('air_quality', {}).get('aqi'),
                        'pm25': weather.get('air_quality', {}).get('pm25'),
                        'pm10': weather.get('air_quality', {}).get('pm10'),
                        'o3': weather.get('air_quality', {}).get('o3'),
                        'so2': weather.get('air_quality', {}).get('so2'),
                        'no2': weather.get('air_quality', {}).get('no2'),
                        'co': weather.get('air_quality', {}).get('co'),
                        'description': weather.get('air_quality', {}).get('description')
                    },
                    # 生活指数
                    'life_index': weather.get('life_index', {})
                }
                # 更新缓存
                cache[cache_key] = {'data': result, 'timestamp': time.time()}
                return result
            else:
                raise Exception(f"彩云天气API错误: {data.get('error', '未知错误')}")
    except Exception as e:
        print(f"获取实况天气数据失败: {str(e)}")
        # 返回默认结构，确保客户端能收到完整的数据
        return {
            'temperature': None,
            'humidity': None,
            'wind_speed': None,
            'wind_direction': None,
            'pressure': None,
            'sky_condition': None,
            'visibility': None,
            'cloud_rate': None,
            'apparent_temperature': None,
            'precipitation': None,
            'air_quality': {
                'aqi': None,
                'pm25': None,
                'pm10': None,
                'o3': None,
                'so2': None,
                'no2': None,
                'co': None,
                'description': None
            },
            'life_index': {}
        }

async def get_hourly_forecast(longitude: str, latitude: str, hourlysteps: int = 48) -> dict:
    """获取未来2天逐小时预报"""
    cache_key = f"hourly_{longitude}_{latitude}_{hourlysteps}"
    
    # 检查缓存
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_EXPIRY:
        return cache[cache_key]['data']
    
    url = f"{CAIYUN_WEATHER_URL}/{longitude},{latitude}/hourly"
    params = {'hourlysteps': hourlysteps}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                hourly = data.get('result', {}).get('hourly', {})
                # 提取温度数据用于折线图
                temperature_data = []
                if 'temperature' in hourly:
                    for item in hourly['temperature']:
                        temperature_data.append({
                            'datetime': item.get('datetime'),
                            'value': item.get('value')
                        })
                
                result = {
                    'temperature': temperature_data,
                    'precipitation': hourly.get('precipitation', []),
                    'humidity': hourly.get('humidity', []),
                    'wind_speed': hourly.get('wind_speed', []),
                    'sky_condition': hourly.get('sky_condition', []),
                    'visibility': hourly.get('visibility', []),
                    'cloud_rate': hourly.get('cloud_rate', [])
                }
                # 更新缓存
                cache[cache_key] = {'data': result, 'timestamp': time.time()}
                return result
            else:
                raise Exception(f"彩云天气API错误: {data.get('error', '未知错误')}")
    except Exception as e:
        print(f"获取逐小时预报数据失败: {str(e)}")
        # 返回默认结构，确保客户端能收到完整的数据
        return {
            'temperature': [],
            'precipitation': [],
            'humidity': [],
            'wind_speed': [],
            'sky_condition': [],
            'visibility': [],
            'cloud_rate': []
        }

async def get_daily_forecast(longitude: str, latitude: str, dailysteps: int = 3) -> dict:
    """获取4项生活指数"""
    cache_key = f"daily_{longitude}_{latitude}_{dailysteps}"
    
    # 检查缓存
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_EXPIRY:
        return cache[cache_key]['data']
    
    url = f"{CAIYUN_WEATHER_URL}/{longitude},{latitude}/daily"
    params = {'dailysteps': dailysteps}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                daily = data.get('result', {}).get('daily', {})
                result = {
                    'temperature': daily.get('temperature', []),
                    'humidity': daily.get('humidity', []),
                    'wind_speed': daily.get('wind_speed', []),
                    'sky_condition': daily.get('sky_condition', []),
                    'visibility': daily.get('visibility', []),
                    'cloud_rate': daily.get('cloud_rate', []),
                    'life_index': daily.get('life_index', {})
                }
                # 更新缓存
                cache[cache_key] = {'data': result, 'timestamp': time.time()}
                return result
            else:
                raise Exception(f"彩云天气API错误: {data.get('error', '未知错误')}")
    except Exception as e:
        print(f"获取生活指数数据失败: {str(e)}")
        # 返回默认结构，确保客户端能收到完整的数据
        return {
            'temperature': [],
            'humidity': [],
            'wind_speed': [],
            'sky_condition': [],
            'visibility': [],
            'cloud_rate': [],
            'life_index': {}
        }

async def get_comprehensive_weather(longitude: str, latitude: str, dailysteps: int = 3, hourlysteps: int = 48) -> dict:
    """通过综合接口获取实况数据、未来两天逐小时预报、未来三天逐天预报"""
    cache_key = f"comprehensive_{longitude}_{latitude}_{dailysteps}_{hourlysteps}"
    
    # 检查缓存
    if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_EXPIRY:
        return cache[cache_key]['data']
    
    url = f"{CAIYUN_WEATHER_URL}/{longitude},{latitude}/weather"
    params = {'dailysteps': dailysteps, 'hourlysteps': hourlysteps}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                result = data.get('result', {})
                
                # 提取实况数据
                realtime = result.get('realtime', {})
                realtime_data = {
                    'temperature': realtime.get('temperature'),
                    'humidity': realtime.get('humidity'),
                    'wind_speed': realtime.get('wind', {}).get('speed'),
                    'wind_direction': realtime.get('wind', {}).get('direction'),
                    'pressure': realtime.get('pressure'),
                    'sky_condition': realtime.get('skycon'),
                    'visibility': realtime.get('visibility'),
                    'cloud_rate': realtime.get('cloudrate'),
                    'apparent_temperature': realtime.get('apparent_temperature'),
                    'precipitation': realtime.get('precipitation'),
                    'air_quality': realtime.get('air_quality', {}),
                    'life_index': realtime.get('life_index', {})
                }
                
                # 提取逐小时预报数据
                hourly = result.get('hourly', {})
                hourly_data = {
                    'temperature': hourly.get('temperature', []),
                    'precipitation': hourly.get('precipitation', []),
                    'humidity': hourly.get('humidity', []),
                    'wind': hourly.get('wind', []),
                    'cloudrate': hourly.get('cloudrate', []),
                    'skycon': hourly.get('skycon', []),
                    'pressure': hourly.get('pressure', []),
                    'visibility': hourly.get('visibility', []),
                    'dswrf': hourly.get('dswrf', []),
                    'air_quality': hourly.get('air_quality', {})
                }
                
                # 提取逐天预报数据
                daily = result.get('daily', {})
                daily_data = {
                    'temperature': daily.get('temperature', []),
                    'precipitation': daily.get('precipitation', []),
                    'humidity': daily.get('humidity', []),
                    'wind': daily.get('wind', []),
                    'cloudrate': daily.get('cloudrate', []),
                    'pressure': daily.get('pressure', []),
                    'visibility': daily.get('visibility', []),
                    'dswrf': daily.get('dswrf', []),
                    'skycon': daily.get('skycon', []),
                    'air_quality': daily.get('air_quality', {}),
                    'life_index': daily.get('life_index', {}),
                    'astro': daily.get('astro', [])
                }
                
                # 组装完整结果
                comprehensive_result = {
                    'realtime': realtime_data,
                    'hourly': hourly_data,
                    'daily': daily_data,
                    'forecast_keypoint': result.get('forecast_keypoint', '')
                }
                
                # 更新缓存
                cache[cache_key] = {'data': comprehensive_result, 'timestamp': time.time()}
                return comprehensive_result
            else:
                raise Exception(f"彩云天气API错误: {data.get('error', '未知错误')}")
    except Exception as e:
        print(f"获取综合天气数据失败: {str(e)}")
        # 返回默认结构，确保客户端能收到完整的数据
        return {
            'realtime': {
                'temperature': None,
                'humidity': None,
                'wind_speed': None,
                'wind_direction': None,
                'pressure': None,
                'sky_condition': None,
                'visibility': None,
                'cloud_rate': None,
                'apparent_temperature': None,
                'precipitation': None,
                'air_quality': {},
                'life_index': {}
            },
            'hourly': {
                'temperature': [],
                'precipitation': [],
                'humidity': [],
                'wind': [],
                'cloudrate': [],
                'skycon': [],
                'pressure': [],
                'visibility': [],
                'dswrf': [],
                'air_quality': {}
            },
            'daily': {
                'temperature': [],
                'precipitation': [],
                'humidity': [],
                'wind': [],
                'cloudrate': [],
                'pressure': [],
                'visibility': [],
                'dswrf': [],
                'skycon': [],
                'air_quality': {},
                'life_index': {},
                'astro': []
            },
            'forecast_keypoint': ''
        }

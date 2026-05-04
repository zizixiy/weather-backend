import httpx
from config import BAIDU_MAP_AK, BAIDU_MAP_COOR, BAIDU_MAP_IP_URL, BAIDU_MAP_REVERSE_GEO_URL

async def get_location_by_ip(ip: str) -> dict:
    """通过IP地址获取地理位置信息"""
    # 处理本地IP地址
    if ip in ['127.0.0.1', 'localhost', '::1']:
        # 使用默认IP地址（北京市）
        return {
            'latitude': '39.9042',
            'longitude': '116.4074',
            'city': '北京市',
            'district': '东城区',
            'street': '',
            'address': '北京市东城区'
        }
    
    params = {
        'ip': ip,
        'coor': BAIDU_MAP_COOR,
        'ak': BAIDU_MAP_AK
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(BAIDU_MAP_IP_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 提取地理位置信息
        if data.get('status') == 0:
            content = data.get('content', {})
            point = content.get('point', {})
            location = {
                'latitude': point.get('y'),
                'longitude': point.get('x'),
                'city': content.get('address_detail', {}).get('city'),
                'district': content.get('address_detail', {}).get('district'),
                'street': content.get('address_detail', {}).get('street'),
                'address': content.get('address')
            }
            return location
        else:
            # 如果API调用失败，使用默认位置
            return {
                'latitude': '39.9042',
                'longitude': '116.4074',
                'city': '北京市',
                'district': '东城区',
                'street': '',
                'address': '北京市东城区'
            }


async def get_location_by_coordinates(longitude: str, latitude: str) -> dict:
    """通过经纬度获取地理位置信息（逆地理编码）"""
    params = {
        'ak': BAIDU_MAP_AK,
        'output': 'json',
        'coordtype': 'wgs84ll',
        'location': f'{latitude},{longitude}'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(BAIDU_MAP_REVERSE_GEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 0:
            result = data.get('result', {})
            address_component = result.get('addressComponent', {})
            location = {
                'latitude': latitude,
                'longitude': longitude,
                'city': address_component.get('city'),
                'district': address_component.get('district'),
                'street': address_component.get('street'),
                'address': result.get('formatted_address')
            }
            return location
        else:
            # 如果API调用失败，返回包含经纬度的基本信息
            return {
                'latitude': latitude,
                'longitude': longitude,
                'city': None,
                'district': None,
                'street': None,
                'address': None,
                'error': '无法获取地理位置信息'
            }

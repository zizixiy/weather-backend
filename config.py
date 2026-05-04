from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 百度地图API配置
BAIDU_MAP_AK = os.getenv('BAIDU_MAP_AK')
BAIDU_MAP_COOR = os.getenv('BAIDU_MAP_COOR')
BAIDU_MAP_IP_URL = os.getenv('BAIDU_MAP_IP_URL')
BAIDU_MAP_REVERSE_GEO_URL = os.getenv('BAIDU_MAP_REVERSE_GEO_URL', 'https://api.map.baidu.com/reverse_geocoding/v3/')

# 彩云天气API配置
CAIYUN_WEATHER_URL = os.getenv('CAIYUN_WEATHER_URL')

# 雾霾探测系统 API

基于 FastAPI 的天气信息获取服务，通过 IP 地址自动获取地理位置和天气数据。

## 功能

- IP 地址自动定位
- 实时天气查询
- 空气质量指数（AQI）
- 逐小时/逐天预报
- 生活指数

## 快速开始

```bash
# 安装依赖
uv install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件填写 API 密钥

# 启动服务
uv run main.py
```

访问 API 文档：http://localhost:8002/docs

## API 接口

| 接口 | 说明 |
|------|------|
| GET /weather | 通过 IP 获取天气 |
| GET /weather/comprehensive | 综合天气信息 |
| GET /weather/by-location?longitude=&latitude= | 经纬度查询 |
| GET /weather/latest | 最新记录 |
| GET /weather/history | 历史记录 |

## 技术栈

- FastAPI 0.135+
- Python 3.13+
- SQLite
- httpx


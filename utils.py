from fastapi import Request

async def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    # 优先从X-Forwarded-For头获取
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # X-Forwarded-For格式: client, proxy1, proxy2
        return x_forwarded_for.split(',')[0].strip()
    
    # 从Remote-Addr获取
    remote_addr = request.client.host if request.client else None
    if remote_addr:
        return remote_addr
    
    # 默认返回本地IP
    return '127.0.0.1'

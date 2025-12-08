from socketio import AsyncServer

from logging import getLogger, Logger

logger: Logger = getLogger(f"streamstorm.{__name__}")

sio: AsyncServer = AsyncServer(
    async_mode='asgi', 
    cors_allowed_origins='*'
)

@sio.on('connect')
async def handle_connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    
    await sio.enter_room(sid, "streamstorm")
    
@sio.on('disconnect')
async def handle_disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    await sio.leave_room(sid, "streamstorm")

@sio.on('ping')
async def darkglance(sid, data):
    return {
        'success': True,
        'message': 'pong',
        'data': data,
        'sid': sid
    }
    
    
__all__: list[str] = ['sio']
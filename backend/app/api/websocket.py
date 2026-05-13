import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.database import SessionLocal
from app.models.vm import VirtualMachine

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/status/{user_id}")
async def websocket_status(websocket: WebSocket, user_id: int):
    await websocket.accept()

    try:
        while True:
            db = SessionLocal()
            try:
                vm = db.query(VirtualMachine).filter(
                    VirtualMachine.current_user_id == user_id,
                    VirtualMachine.is_active == True,
                ).first()

                if vm:
                    payload = {
                        "status": "connected",
                        "host": vm.host,
                        "port": vm.port,
                        "protocol": vm.protocol,
                    }
                else:
                    payload = {"status": "disconnected"}
            finally:
                db.close()

            await websocket.send_json(payload)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
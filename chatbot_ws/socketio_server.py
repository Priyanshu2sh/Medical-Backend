# chatbot_ws/socketio_server.py
import os
import django
import socketio
import asyncio
import json
import traceback

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_books.settings")
django.setup()

sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode="asgi",
    ping_interval=25,
    ping_timeout=60,
    logger=True,
    engineio_logger=True,
)
app = socketio.ASGIApp(sio, socketio_path="/socket.io")

# Map sid -> {'pc': RTCPeerConnection, 'datachannel': RTCDataChannel}
peer_map = {}


def create_pc_for_sid(sid):
    pc = RTCPeerConnection()
    peer_map[sid] = {"pc": pc, "datachannel": None}
    print(f"[server] Created RTCPeerConnection for {sid}")

    # when aiortc gathers a local ice candidate, forward to browser
    @pc.on("icecandidate")
    def _on_icecandidate(candidate):
        try:
            if candidate is None:
                return
            payload = {
                "candidate": {
                    "candidate": getattr(candidate, "candidate", str(candidate)),
                    "sdpMid": getattr(candidate, "sdpMid", None),
                    "sdpMLineIndex": getattr(candidate, "sdpMLineIndex", None),
                }
            }
            asyncio.create_task(sio.emit("ice-candidate", payload, to=sid))
            print(f"[server] Emitted ICE candidate to {sid}")
        except Exception:
            traceback.print_exc()

    # Browser created datachannel -> aiortc triggers on datachannel
    @pc.on("datachannel")
    def _on_datachannel(channel):
        print(f"[server] Data channel opened from browser for sid={sid} label={channel.label}")
        peer_map[sid]["datachannel"] = channel

        @channel.on("message")
        def _on_message(message):
            try:
                print(f"[server] Received message from {sid} via datachannel:", message)
                data = None
                if isinstance(message, (bytes, bytearray)):
                    try:
                        data = json.loads(message.decode("utf-8"))
                    except Exception:
                        data = {"raw": str(message)}
                else:
                    try:
                        data = json.loads(message)
                    except Exception:
                        data = {"text": message}

                # Echo back in unified format
                if isinstance(data, dict):
                    user_text = data.get("text", "")
                    user_voice = data.get("voice")

                    bot_reply = {
                        "usertext": user_text,
                        "bottext": user_text,
                        "botvoice": user_voice  # echo voice back if present
                    }
                    channel.send(json.dumps(bot_reply))
                    print(f"[server] Sent echo reply to {sid}: {bot_reply}")
                else:
                    channel.send(json.dumps({"error": "Invalid format"}))
            except Exception:
                traceback.print_exc()

    @pc.on("track")
    def _on_track(track):
        print(f"[server] Track received from {sid}: kind={track.kind}")
        @track.on("ended")
        async def _on_ended():
            print(f"[server] Track ended for {sid}: kind={track.kind}")

    return pc


@sio.event
async def connect(sid, environ):
    print(f"🔌 Client connected: {sid}")
    create_pc_for_sid(sid)
    await sio.emit("server_message", {"message": "Connected to Socket.IO server"}, to=sid)


@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")
    info = peer_map.pop(sid, None)
    if info:
        pc = info.get("pc")
        try:
            await pc.close()
            print(f"[server] Closed pc for sid={sid}")
        except Exception:
            traceback.print_exc()


@sio.event
async def message(sid, data):
    print(f"💬 Message from {sid}: {data}")
    await sio.emit("message", data, to=sid)


@sio.event
async def offer(sid, offer):
    """
    Browser sends: offer = { type: 'offer', sdp: 'v=0...' }
    """
    print(f"📨 offer received from {sid}")
    try:
        info = peer_map.get(sid)
        if not info:
            pc = create_pc_for_sid(sid)
        else:
            pc = info["pc"]

        desc = RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
        await pc.setRemoteDescription(desc)
        print(f"[server] setRemoteDescription OK for {sid}")

        # create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        print(f"[server] Created local description (answer) for {sid}")

        payload = {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        await sio.emit("answer", payload, to=sid)
        print(f"[server] Sent answer to {sid}")
    except Exception:
        print(f"[server] ERROR handling offer from {sid}")
        traceback.print_exc()


@sio.event
async def answer(sid, data):
    print(f"📨 answer event from {sid}: {data}")
    target = data.get("to")
    if target:
        await sio.emit("answer", data["answer"], to=target)


@sio.event
async def ice_candidate(sid, data):
    """
    Expecting { candidate: { candidate: 'candidate:...', sdpMid: '0', sdpMLineIndex: 0 } }
    """
    print(f"🔸 ice_candidate from {sid}: {bool(data)}")
    try:
        info = peer_map.get(sid)
        if not info:
            print(f"[server] No PeerConnection exists for {sid} to add ICE candidate to")
            return
        pc = info["pc"]
        cand = data.get("candidate") if isinstance(data, dict) else None
        if not cand:
            print("[server] No candidate payload")
            return

        try:
            rtc_cand = RTCIceCandidate(
                sdpMid=cand.get("sdpMid"),
                sdpMLineIndex=cand.get("sdpMLineIndex"),
                candidate=cand.get("candidate"),
            )
            await pc.addIceCandidate(rtc_cand)
            print(f"[server] Added ICE candidate for {sid}")
        except Exception:
            try:
                await pc.addIceCandidate(cand)
                print(f"[server] Added ICE candidate (fallback) for {sid}")
            except Exception:
                traceback.print_exc()
    except Exception:
        traceback.print_exc()


@sio.event
async def list_clients(sid):
    await sio.emit("clients", list(peer_map.keys()), to=sid)

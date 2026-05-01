"""
    Zombie using aiohttp
"""

from aiohttp import web
import asyncio
from inspect import cleandoc
import queue
import socket
from threading import Thread

import janus


async def ws_handler(request, application_class):
    """Upgrade this connection to a websocket then create a message socket
    and a handler thread and instantiate the `application_class` in the thread
    passing in the socket."""

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    send_queue = janus.Queue()
    application = application_class(send_queue.sync_q)

    async def ws_recv():
        async for msg in ws:
            print(f"RECV {msg}")
            await application.recv(msg)
        send_queue.async_q.shutdown()

    async def ws_send():
        try:
            while True:
                msg = await send_queue.async_q.get()
                print(f"SEND {msg}")
                await ws.send_str(msg)
        except janus.QueueShutDown:
            pass

    async def run_application():
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, application.run)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_application())
        tg.create_task(ws_recv())
        tg.create_task(ws_send())

    send_queue.aclose()


def root_handler(request):
    """Handler returns a little loader stub which establishes a websocket,
    then evals messages as it receives them, passing the evaluated code a
    single parameter which is a function it can use to send further messages."""
    # it's missing a disconnect handler which knows how to reconnect to
    # the session, and there's no session secret which could be used to do
    # this anyway.  
    return web.Response(text=cleandoc("""
        <!DOCTYPE html><html>
            <head><script>
                window.addEventListener('load', function () {
                    console.log("LOAD")
                    var ws = new WebSocket("ws://" + window.location.host + "/ws");
                    function Z(msg) {
                        console.log("SEND " + msg);
                        ws.send(msg);
                    }
                    ws.addEventListener('message', function(msg) {
                        console.log("RECV " + msg.data);
                        (new Function('Z', msg.data))(Z);
                    });
                    ws.addEventListener('error', function(msg) { console.log("ERROR " + msg); });
                });
            </script></head>
            <body><noscript>This zombie site requires Javascript</noscript></body>
        </html>
    """), content_type="text/html")

def serve(application_class, host='localhost', port=8888):
    webapp = web.Application()
    webapp.add_routes([
        web.get("/", root_handler),
        web.get("/ws", lambda request: ws_handler(request, application_class)),
    ])
    web.run_app(webapp, host=host, port=port)

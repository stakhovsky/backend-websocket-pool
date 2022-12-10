import asyncio
import signal


def stop_marker() -> asyncio.Future:
    loop = asyncio.get_event_loop()
    result = loop.create_future()

    loop.add_signal_handler(signal.SIGINT, result.set_result, None)
    loop.add_signal_handler(signal.SIGTERM, result.set_result, None)

    return result

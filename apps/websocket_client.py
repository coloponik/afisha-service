import asyncio

import websockets


async def main() -> None:
    async with websockets.connect(
        "ws://localhost:8001/ws/payments"
    ) as ws:
        async for message in ws:
            print("Received:", message, end="\n\n")


if __name__ == "__main__":
    asyncio.run(main())

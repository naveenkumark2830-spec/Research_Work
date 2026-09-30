import asyncio
import os

from dotenv import load_dotenv

from app.jarvis.provider import create_teddy_orchestrator
from app.jarvis.schemas import TeddyRequest


load_dotenv()


async def main():

    teddy = create_teddy_orchestrator()

    request = TeddyRequest(
        session_id="demo-session",
        user_id="demo-user",
        message="Create a 1 GB file using 128 MB blocks with replication factor 3 and show me how HDFS stores it."
    )

    response = await teddy.process(request)

    print("\n" + "=" * 70)
    print("TEDDY RESPONSE")
    print("=" * 70)

    print("\nINTENT:")
    print(response.plan.intent)

    print("\nANSWER:")
    print(response.plan.answer.encode("ascii", "replace").decode("ascii"))

    print("\nVOICE:")
    print(response.plan.voice_text.encode("ascii", "replace").decode("ascii"))

    print("\nSIMULATION REQUIRED:")
    print(response.plan.simulation_required)

    print("\nSIMULATION ACTION:")
    print(response.plan.simulation_action)

    print("\nVISUALIZATION:")
    for step in response.plan.visualization:
        print(
            f"- {step.type}: "
            f"{step.title} | "
            f"{step.description}"
        )

    print("\nSOURCES:")
    for source in response.plan.sources:
        print("-", source)

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from model import decide_tool


async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("\nConnected to MCP Server")

            tools = await session.list_tools()
            print("\nAvailable tools:")
            print([t.name for t in tools.tools])

            while True:

                user_query = input("\nUser: ").strip()

                if user_query.lower() == "exit":
                    break

                if not user_query:
                    continue

                tool = decide_tool(user_query)

                # CALCULATOR TOOL
                if tool == "calculate":

                    nums = [int(x) for x in re.findall(r'\d+', user_query)]

                    if len(nums) < 2:
                        print("AI: Please provide two numbers.")
                        continue

                    # detect operation
                    if "add" in user_query or "+" in user_query:
                        operation = "add"

                    elif "multiply" in user_query or "*" in user_query:
                        operation = "multiply"

                    else:
                        operation = "add"

                    result = await session.call_tool(
                        "calculate",
                        {
                            "a": nums[0],
                            "b": nums[1],
                            "operation": operation
                        }
                    )

                    print("\nAI Response:")
                    print(result.content[0].text)

                # TEMPERATURE CONVERTER TOOL
                elif tool == "convert_temperature":

                    nums = [int(x) for x in re.findall(r'\d+', user_query)]

                    if not nums:
                        print("AI: Please provide a number to convert.")
                        continue

                    unit_match = re.findall(r'\b[cCfF]\b', user_query)

                    if not unit_match:
                        print("AI: specify C or F")
                        continue

                    unit = unit_match[0].lower()

                    result = await session.call_tool(
                        "convert_temperature",
                        {
                            "value": nums[0],
                            "unit": unit
                        }
                    )

                    print("\nAI Response:")
                    print(result.content[0].text)

                else:
                    print("AI: I cannot determine which tool to use.")


asyncio.run(main())
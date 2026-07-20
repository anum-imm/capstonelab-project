from mcp.server.fastmcp import FastMCP
from tools import calculator_tool, temperature_converter
from schemas import CalculatorInput, TempInput

mcp = FastMCP("UtilityServer")


@mcp.tool()
def calculate(a: float, b: float, operation: str):

    data = CalculatorInput(a=a, b=b, operation=operation)
    result = calculator_tool(data)

    return result.dict()


@mcp.tool()
def convert_temperature(value: float, unit: str):

    data = TempInput(value=value, unit=unit)
    result = temperature_converter(data)

    return result.dict()


if __name__ == "__main__":
    mcp.run()
from schemas import CalculatorInput, CalculatorOutput, TempInput, TempOutput


def calculator_tool(data: CalculatorInput) -> CalculatorOutput:

    if data.operation == "add":
        result = data.a + data.b

    elif data.operation == "multiply":
        result = data.a * data.b

    else:
        result = 0

    return CalculatorOutput(result=result)


def temperature_converter(data: TempInput) -> TempOutput:

    if data.unit.lower() == "c":
        converted = (data.value * 9/5) + 32
        unit = "F"

    elif data.unit.lower() == "f":
        converted = (data.value - 32) * 5/9
        unit = "C"

    else:
        converted = data.value
        unit = data.unit

    return TempOutput(
        converted_value=converted,
        unit=unit
    )
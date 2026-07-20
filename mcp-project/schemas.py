from pydantic import BaseModel


class CalculatorInput(BaseModel):
    a: float
    b: float
    operation: str


class CalculatorOutput(BaseModel):
    result: float


class TempInput(BaseModel):
    value: float
    unit: str


class TempOutput(BaseModel):
    converted_value: float
    unit: str
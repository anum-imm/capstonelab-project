def decide_tool(user_query: str):

    user_query = user_query.lower()

    # temperature converter
    if "convert" in user_query or "celsius" in user_query or "fahrenheit" in user_query:
        return "convert_temperature"

    # calculator
    if "multiply" in user_query or "*" in user_query:
        return "calculate"

    if "add" in user_query or "+" in user_query:
        return "calculate"

    return None
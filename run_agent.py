from graph import app
from langchain_core.messages import HumanMessage

# Use the specific ID format if possible, or let the tool handle it
initial_state = {"messages": [HumanMessage(content="Can I get refund for order 1001?")]}

print("--- STARTING GRAPH ---")
final_message = ""

for step in app.stream(initial_state, stream_mode="values"):
    # Using 'values' mode lets you see the full history update at each step
    last_msg = step["messages"][-1]
    last_msg.pretty_print()
    final_message = last_msg.content

print("\n=== FINAL ANSWER ===")
print(final_message)
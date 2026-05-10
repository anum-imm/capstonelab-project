# Improvement Demo

## Identified Issue
Based on our feedback monitoring, a common point of friction occurred when users asked about their order or shipment without providing an order ID (e.g., "Where is my order?"). The `order_agent` would sometimes fail tool calls due to the missing required `order_id` argument or return unhelpful mechanical responses.

## Fix Applied (Prompt Engineering)
To resolve this, we updated the system prompt for `order_agent` in both `graph.py` and `secured_graph.py` to explicitly instruct the LLM to handle missing order IDs conversationally.

**Before:**
> "You are an order management assistant. Use tools for order and shipping queries. Never guess."

**After:**
> "You are an order management assistant. Use tools for order and shipping queries. Never guess. If the user does not provide an order ID, politely ask them to provide it before proceeding."

## Before vs. After Results

### Before
**User:** "I want to track my shipment"
**Agent:** "I cannot check without an order ID." (or a tool failure message if it hallucinated an ID)
**Feedback:** 👎 Bad

### After
**User:** "I want to track my shipment"
**Agent:** "I would be happy to help you track your shipment! Could you please provide your order ID?"
**Feedback:** 👍 Good

The conversational recovery prevents user frustration and improves the overall success rate of shipping inquiries.

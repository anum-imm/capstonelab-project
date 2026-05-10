import json
import os
from collections import Counter

def analyze_feedback(log_file="feedback_log.json"):
    if not os.path.exists(log_file):
        print("No feedback log found.")
        return

    with open(log_file, "r") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON format in log file.")
            return

    total_responses = len(logs)
    negative_feedback = sum(1 for log in logs if log.get("feedback") == "bad")

    failed_queries = [log.get("user_input") for log in logs if log.get("feedback") == "bad"]
    failed_counts = Counter(failed_queries)
    top_failed = failed_counts.most_common(3)

    print(f"Total Responses: {total_responses}")
    print(f"Negative Feedback Count: {negative_feedback}")
    print("Top 3 Failed Queries:")
    for query, count in top_failed:
        print(f" - '{query}' ({count} times)")

if __name__ == "__main__":
    analyze_feedback()

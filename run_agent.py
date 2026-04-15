import argparse

from agent_runner import run_cli
from graph import app
from secured_graph import secured_app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run support agent.")
    parser.add_argument(
        "--secured",
        action="store_true",
        help="Run the secured graph with guardrails enabled.",
    )
    args = parser.parse_args()

    if args.secured:
        run_cli(
            secured_app,
            thread_id="secure_session_1",
            banner="Secured AI Support Agent Started (type 'exit' to quit)",
        )
    else:
        run_cli(app, thread_id="session_1", banner="AI Support Agent Started")
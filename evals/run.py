import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CASES_PATH = Path(__file__).with_name("cases.jsonl")
RESULTS_PATH = Path(__file__).with_name("last_run.json")
RUN_AGENT = None


def get_run_agent():
    global RUN_AGENT

    if RUN_AGENT is None:
        from app.agent.loop import run_agent

        RUN_AGENT = run_agent

    return RUN_AGENT


def load_cases(path: Path) -> list[dict]:
    cases = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                cases.append(json.loads(line))

            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc

    return cases


def values_match(actual, expected) -> bool:
    if isinstance(expected, bool):
        return actual is expected

    if isinstance(expected, (int, float)):
        try:
            return abs(float(actual) - float(expected)) < 0.01
        except (TypeError, ValueError):
            return False

    return actual == expected


def find_tool_call(tool_calls: list[dict], expected_tool: str) -> dict | None:
    for tool_call in tool_calls:
        if tool_call.get("name") == expected_tool:
            return tool_call

    return None


def has_proposal_tool(tool_calls: list[dict]) -> bool:
    return any(call.get("name", "").startswith("propose_") for call in tool_calls)


def check_expected_args(arguments: dict, expected_args: dict) -> list[str]:
    failures = []

    for key, expected_value in expected_args.items():
        actual_value = arguments.get(key)

        if not values_match(actual_value, expected_value):
            failures.append(
                f"{key} expected {expected_value!r}, got {actual_value!r}"
            )

    return failures


def check_arg_contains(arguments: dict, expected_contains: dict) -> list[str]:
    failures = []

    for key, expected_words in expected_contains.items():
        actual_text = str(arguments.get(key, "")).lower()

        if not any(word.lower() in actual_text for word in expected_words):
            failures.append(
                f"{key} expected to contain one of {expected_words!r}, got {actual_text!r}"
            )

    return failures


def check_tool_case(case: dict, result: dict) -> tuple[bool, list[str]]:
    expected_tool = case["expected_tool"]
    tool_call = find_tool_call(result["tool_calls"], expected_tool)

    if not tool_call:
        seen_tools = [call.get("name") for call in result["tool_calls"]]
        return False, [f"expected tool {expected_tool!r}, saw {seen_tools!r}"]

    arguments = tool_call.get("arguments") or {}
    failures = []
    failures.extend(check_expected_args(arguments, case.get("expected_args", {})))
    failures.extend(check_arg_contains(arguments, case.get("arg_contains", {})))

    return not failures, failures


def check_behavior_case(case: dict, result: dict) -> tuple[bool, list[str]]:
    behavior = case["expected_behavior"]
    reply = result["reply"].lower()
    keywords = [keyword.lower() for keyword in case.get("reply_keywords", [])]
    failures = []

    if behavior == "clarify":
        if has_proposal_tool(result["tool_calls"]):
            failures.append("expected clarification, but a propose_* tool was called")

        if keywords and not any(keyword in reply for keyword in keywords):
            failures.append(f"reply did not contain any expected keyword: {keywords!r}")

    elif behavior == "refuse":
        if result["tool_calls"]:
            failures.append("expected refusal with no tool calls")

        if keywords and not any(keyword in reply for keyword in keywords):
            failures.append(f"reply did not contain any expected keyword: {keywords!r}")

    else:
        failures.append(f"unknown expected_behavior {behavior!r}")

    return not failures, failures


def check_case(case: dict, result: dict) -> tuple[bool, list[str]]:
    if "expected_tool" in case:
        return check_tool_case(case, result)

    return check_behavior_case(case, result)


def run_case(case: dict) -> dict:
    try:
        run_agent = get_run_agent()
        result = run_agent(case["input"], history=None)
        passed, failures = check_case(case, result)

        return {
            "id": case["id"],
            "category": case["category"],
            "input": case["input"],
            "passed": passed,
            "failures": failures,
            "reply": result["reply"],
            "tool_calls": result["tool_calls"],
        }

    except Exception as exc:
        return {
            "id": case["id"],
            "category": case["category"],
            "input": case["input"],
            "passed": False,
            "failures": [f"{type(exc).__name__}: {exc}"],
            "reply": "",
            "tool_calls": [],
        }


def summarize(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    by_category = defaultdict(Counter)

    for result in results:
        category = result["category"]
        by_category[category]["total"] += 1

        if result["passed"]:
            by_category[category]["passed"] += 1

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round((passed / total) * 100, 1) if total else 0.0,
        "by_category": {
            category: {
                "passed": counts["passed"],
                "total": counts["total"],
                "pass_rate": round((counts["passed"] / counts["total"]) * 100, 1),
            }
            for category, counts in sorted(by_category.items())
        },
    }


def print_scoreboard(summary: dict, results: list[dict]) -> None:
    print("\n=== Eval Scoreboard ===")
    print(
        f"Overall: {summary['passed']}/{summary['total']} "
        f"({summary['pass_rate']}%)"
    )

    print("\nBy category:")
    for category, stats in summary["by_category"].items():
        print(
            f"- {category}: {stats['passed']}/{stats['total']} "
            f"({stats['pass_rate']}%)"
        )

    failures = [result for result in results if not result["passed"]]

    if failures:
        print("\nFailures:")
        for result in failures:
            print(f"- {result['id']}: {'; '.join(result['failures'])}")


def main() -> int:
    cases = load_cases(CASES_PATH)
    results = []

    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] {case['id']}...", flush=True)
        results.append(run_case(case))

    summary = summarize(results)
    output = {
        "ran_at": datetime.now(ZoneInfo("Asia/Karachi")).isoformat(),
        "cases_path": str(CASES_PATH),
        "summary": summary,
        "results": results,
    }

    RESULTS_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print_scoreboard(summary, results)
    print(f"\nSaved results to {RESULTS_PATH}")

    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

import subprocess
import sys
import tempfile
import os

import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from theme import inject_theme, page_header, section_title, empty_state

st.set_page_config(page_title="Coding - TalentForge AI", page_icon="💻", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header(
    "💻", "Coding Practice",
    "Write a Python function and run it against test cases. Code executes in an "
    "isolated subprocess with a strict timeout — this is a practice sandbox, "
    "not a production judge.",
)

PROBLEMS = {
    "Two Sum": {
        "prompt": (
            "Write a function `solve(nums, target)` that returns the indices of the two "
            "numbers in `nums` that add up to `target`, as a list `[i, j]` with i < j."
        ),
        "starter": "def solve(nums, target):\n    # your code here\n    pass\n",
        "tests": [
            (([2, 7, 11, 15], 9), [0, 1]),
            (([3, 2, 4], 6), [1, 2]),
            (([3, 3], 6), [0, 1]),
        ],
    },
    "Reverse String": {
        "prompt": "Write a function `solve(s)` that returns the string `s` reversed.",
        "starter": "def solve(s):\n    # your code here\n    pass\n",
        "tests": [
            (("hello",), "olleh"),
            (("",), ""),
            (("a",), "a"),
        ],
    },
    "FizzBuzz Count": {
        "prompt": (
            "Write a function `solve(n)` that returns how many numbers from 1 to n "
            "(inclusive) are divisible by 3 or 5."
        ),
        "starter": "def solve(n):\n    # your code here\n    pass\n",
        "tests": [
            ((15,), 8),
            ((1,), 0),
            ((30,), 15),
        ],
    },
}

problem_name = st.selectbox("Choose a problem", list(PROBLEMS.keys()))
problem = PROBLEMS[problem_name]

st.markdown(
    f"""<div class="tf-card"><div class="tf-history-sub">Prompt</div>
    <div class="tf-history-main" style="font-weight:500;">{problem['prompt']}</div></div>""",
    unsafe_allow_html=True,
)

code = st.text_area("Your solution", value=problem["starter"], height=220, key=f"code_{problem_name}")

TIMEOUT_SECONDS = 5


def run_against_tests(user_code: str, tests: list) -> tuple[bool, str]:
    harness = f"""
{user_code}

import json
_tests = {tests!r}
_results = []
for args, expected in _tests:
    try:
        actual = solve(*args)
        _results.append({{"args": args, "expected": expected, "actual": actual, "passed": actual == expected}})
    except Exception as e:
        _results.append({{"args": args, "expected": expected, "actual": f"ERROR: {{e}}", "passed": False}})
print(json.dumps(_results))
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(harness)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (possible infinite loop)."
    finally:
        os.remove(tmp_path)

    if proc.returncode != 0:
        return False, f"Error:\n{proc.stderr[-1000:]}"

    return True, proc.stdout.strip()


if st.button("▶️ Run tests", type="primary", use_container_width=True):
    with st.spinner("Running..."):
        ok, output = run_against_tests(code, problem["tests"])

    if not ok:
        st.error(output)
        db.save_coding_submission(user["id"], problem_name, code, False, output)
    else:
        import json
        results = json.loads(output)
        all_passed = all(r["passed"] for r in results)

        for r in results:
            icon = "✅" if r["passed"] else "❌"
            st.write(f"{icon} solve{r['args']} → got `{r['actual']}`, expected `{r['expected']}`")

        if all_passed:
            st.success("All tests passed! 🎉")
        else:
            st.warning("Some tests failed — keep iterating.")

        db.save_coding_submission(user["id"], problem_name, code, all_passed, output)

st.markdown("---")
section_title("Submission history")
history = db.get_coding_history(user["id"])
if history:
    for h in history[:10]:
        status = "✅ Passed" if h["passed"] else "❌ Failed"
        st.markdown(
            f"""
            <div class="tf-history-row">
                <div>
                    <div class="tf-history-main">{h['problem_title']}</div>
                    <div class="tf-history-sub">{h['created_at'][:19]}</div>
                </div>
                <div class="tf-history-score">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    empty_state("No submissions yet.", "💻")

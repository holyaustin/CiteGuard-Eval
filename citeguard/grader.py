"""Deterministic grader for CiteGuard-Eval model outputs."""
from __future__ import annotations
import json, re
from pathlib import Path

VALID_VERDICTS = {"VERIFIED","INCORRECT","UNVERIFIABLE","SUPPORTED","NOT_SUPPORTED","PARTIALLY_SUPPORTED"}

def normalize(s):
    return re.sub(r"\s+", " ", str(s or "").strip()).casefold()

def grade_one(task, answer):
    """Score only explicit structured fields; no LLM judge is used."""
    gold = task["gold"]
    score, maximum, details = 0.0, 0.0, []
    if not answer or answer.get("error"):
        expected_max = 7
        if "field_status" in gold:
            expected_max += len(gold["field_status"])
        if "support" in gold:
            expected_max += 2
        return {"task_id": task["id"], "score": 0.0, "max_score": float(expected_max),
                "percent": 0.0, "passed": False,
                "details": [{"criterion": "response_present", "expected": "valid structured answer",
                             "actual": "missing or failed", "passed": False, "weight": expected_max}]}

    def check(label, got, expected, weight):
        nonlocal score, maximum
        maximum += weight
        ok = normalize(got) == normalize(expected)
        if ok: score += weight
        details.append({"criterion": label, "expected": expected, "actual": got, "passed": ok, "weight": weight})

    check("verdict", answer.get("verdict"), gold["verdict"], 4)
    got_issues = sorted(set(answer.get("issues") or []))
    expected_issues = sorted(set(gold.get("issues") or []))
    # Exact issue-set match; partial credit by per-label precision/recall is avoided.
    check("issue_codes", got_issues, expected_issues, 3)

    if "field_status" in gold:
        expected_fields = gold["field_status"]
        got_fields = answer.get("field_status") or {}
        for field, expected in expected_fields.items():
            check(f"field:{field}", got_fields.get(field), expected, 1)
    if "support" in gold:
        check("claim_support", answer.get("support"), gold["support"], 2)
    return {"task_id":task["id"],"score":score,"max_score":maximum,
            "percent":round(100*score/maximum,2) if maximum else 0,
            "passed":score == maximum,"details":details}

def grade_dataset(tasks, answers):
    by_id = {a.get("task_id"):a for a in answers}
    results=[]
    for task in tasks:
        answer=by_id.get(task["id"], {})
        results.append(grade_one(task, answer))
    total=sum(x["score"] for x in results); maximum=sum(x["max_score"] for x in results)
    return {"benchmark":"CiteGuard-Eval","tasks":results,"score":round(total,2),
            "max_score":round(maximum,2),"accuracy_percent":round(100*total/maximum,2) if maximum else 0,
            "tasks_submitted":len(answers),"tasks_expected":len(tasks)}

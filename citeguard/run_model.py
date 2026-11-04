"""Run a model through an OpenAI-compatible chat-completions API."""
import argparse, json, os, time
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parent
SYSTEM_PROMPT="""You are completing a research-reference verification benchmark.
Use only the evidence supplied in each task. Do not use outside knowledge or invent metadata.
Return exactly one JSON object, no markdown, with these keys:
task_id, verdict, issues, field_status, support, rationale.
Allowed verdicts: VERIFIED, INCORRECT, UNVERIFIABLE, SUPPORTED, NOT_SUPPORTED, PARTIALLY_SUPPORTED.
Allowed field_status values: match, mismatch, missing, unverifiable.
Allowed support values: supported, not_supported, partial, contradicted, unknown.
Use issue codes where applicable:
AUTHOR_ORDER_MISMATCH, AUTHOR_MISMATCH, YEAR_MISMATCH, TITLE_MISMATCH,
VENUE_MISMATCH, DOI_MISMATCH, DOI_MISSING, EFFECT_SIZE_CONTRADICTED,
CAUSALITY_NOT_ESTABLISHED, IMPACT_CLAIM_UNSUPPORTED, CLAIM_NOT_EVIDENCED.
For metadata-only tasks use an empty support string. For claim-only tasks use an empty field_status object.
Be conservative: absent evidence is not proof of correctness."""
def call_api(base_url, api_key, model, task):
    payload={"model":model,"temperature":0,"messages":[
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":json.dumps(task,ensure_ascii=False)}
    ]}
    req=urllib.request.Request(base_url.rstrip("/")+"/chat/completions",
        data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+api_key,
        "Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=120) as r: data=json.loads(r.read())
    content=data["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content=content.split("\n",1)[1].rsplit("```",1)[0].strip()
    answer=json.loads(content)
    answer.setdefault("task_id",task["id"])
    return answer

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--model",default=os.getenv("OPENAI_MODEL",""))
    p.add_argument("--base-url",default=os.getenv("OPENAI_BASE_URL","https://openrouter.ai/api/v1"))
    p.add_argument("--api-key",default=os.getenv("OPENAI_API_KEY",""))
    p.add_argument("--input",default=str(ROOT/"data/tasks.json"))
    p.add_argument("--output",default=str(ROOT/"results/model_answers.json"))
    p.add_argument("--limit",type=int,default=0)
    args=p.parse_args()
    if not args.model or not args.api_key: p.error("Set OPENAI_MODEL and OPENAI_API_KEY, or pass --model and --api-key.")
    tasks=json.loads(Path(args.input).read_text())
    if args.limit: tasks=tasks[:args.limit]
    answers=[]
    for i,task in enumerate(tasks,1):
        print(f"[{i}/{len(tasks)}] {task['id']}",flush=True)
        try: answers.append(call_api(args.base_url,args.api_key,args.model,task))
        except Exception as e:
            print(f"ERROR {task['id']}: {e}",flush=True)
            answers.append({"task_id":task["id"],"error":str(e)})
        time.sleep(.2)
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(answers,indent=2,ensure_ascii=False))
    print(f"Saved {len(answers)} answers to {out}")
if __name__=="__main__": main()

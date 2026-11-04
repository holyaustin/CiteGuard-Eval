"""Grade saved model answers."""
import argparse,json
from pathlib import Path
from grader import grade_dataset
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument("--answers",default=str(ROOT/"results/model_answers.json"))
p.add_argument("--tasks",default=str(ROOT/"data/tasks.json"))
p.add_argument("--output",default=str(ROOT/"results/graded_results.json"))
a=p.parse_args()
tasks=json.loads(Path(a.tasks).read_text()); answers=json.loads(Path(a.answers).read_text())
report=grade_dataset(tasks,answers)
out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!="tasks"},indent=2))

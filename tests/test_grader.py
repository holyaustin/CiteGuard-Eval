import json, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"citeguard"))
from grader import grade_one, grade_dataset
TASKS=json.loads((Path(__file__).resolve().parents[1]/"citeguard/data/tasks.json").read_text())

class GraderTests(unittest.TestCase):
    def test_perfect_answer_scores_full(self):
        t=TASKS[0]
        a={"verdict":"VERIFIED","issues":[],"field_status":t["gold"]["field_status"]}
        r=grade_one(t,a)
        self.assertEqual(r["percent"],100)
    def test_wrong_doi_is_not_verified(self):
        t=TASKS[1]
        a={"verdict":"INCORRECT","issues":["DOI_MISMATCH"],"field_status":t["gold"]["field_status"]}
        self.assertEqual(grade_one(t,a)["percent"],100)
    def test_missing_answer_is_zero(self):
        r=grade_dataset(TASKS,[])
        self.assertEqual(r["score"],0)
    def test_partial_claim_is_distinct(self):
        t=TASKS[8]
        a={"verdict":"PARTIALLY_SUPPORTED","issues":["IMPACT_CLAIM_UNSUPPORTED"],"support":"partial"}
        self.assertEqual(grade_one(t,a)["percent"],100)
    def test_dataset_has_recommended_task_count(self):
        self.assertGreaterEqual(len(TASKS),5)
        self.assertLessEqual(len(TASKS),10)

if __name__=="__main__": unittest.main()

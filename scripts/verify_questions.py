import json
import duckdb

con = duckdb.connect("data/github.duckdb", read_only=True)
failed = 0
for line in open("eval/github_dev_questions.jsonl"):
    q = json.loads(line)
    try:
        rows = con.execute(q["reference_sql"]).fetchall()
        status = "OK" if len(rows) > 0 else "EMPTY"
        if not rows:
            failed += 1
        print(f"{q['id']}: {status} ({len(rows)} rows)")
    except Exception as e:
        failed += 1
        print(f"{q['id']}: ERROR -> {str(e)[:120]}")
print(f"\n{15 - failed}/15 passed")

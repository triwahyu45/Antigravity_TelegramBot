import json

TRANSCRIPT = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\.system_generated\logs\transcript.jsonl"

def check():
    lines = open(TRANSCRIPT, encoding="utf-8", errors="ignore").readlines()
    print("Total Lines in Transcript:", len(lines))

    planner_done_count = 0
    for raw in lines:
        raw = raw.strip()
        if not raw: continue
        try:
            d = json.loads(raw)
            typ = d.get("type", "")
            status = d.get("status", "")
            content = (d.get("content") or "").strip()
            if typ == "PLANNER_RESPONSE" and status == "DONE" and content:
                planner_done_count += 1
                step = d.get("step_index")
                print(f"Done Planner Response #{planner_done_count} | Step: {step} | Content Len: {len(content)}")
        except Exception as e:
            print("ERR:", e)

if __name__ == "__main__":
    check()

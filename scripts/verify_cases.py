"""Check eval cases against the source PDF pages, one by one.

Run: uv run python scripts/verify_cases.py [start_id] [end_id]
Keys: y = expected answer is correct, n = wrong (marks NEEDS FIX), s = skip, q = quit.
Progress is saved after every answer.
"""
import json
import sys

from pypdf import PdfReader

from fin_reg_copilot import config

CASES = config.ROOT / "tests" / "eval_cases.jsonl"
_readers = {}


def page_text(file, page):
    if file not in _readers:
        _readers[file] = PdfReader(config.RAW_DIR / file)
    return _readers[file].pages[page - 1].extract_text() or ""


def save(cases):
    CASES.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases))


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
    cases = [json.loads(line) for line in CASES.read_text().splitlines() if line.strip()]

    for c in cases:
        if not (start <= c["id"] <= end) or c["verified"] or "NEEDS FIX" in c["note"]:
            continue
        print("\n" + "=" * 80)
        print(f"#{c['id']} [{c['type']}] {c['question']}")
        print(f"EXPECTED: {c['expected']}")
        if c["note"]:
            print(f"NOTE: {c['note']}")
        if not c["sources"]:
            print("\n(negative case: confirm this answer is NOT in any of the PDFs)")
        for s in c["sources"]:
            print(f"\n--- {s['file']} p.{s['page']} ---\n{page_text(s['file'], s['page'])}")

        ans = input("\n[y] correct  [n] wrong  [s] skip  [q] quit > ").strip().lower()
        if ans == "q":
            break
        if ans == "y":
            c["verified"] = True
        elif ans == "n":
            c["note"] = f"{c['note']} | NEEDS FIX" if c["note"] else "NEEDS FIX"
        save(cases)

    done = sum(c["verified"] for c in cases)
    fix = sum("NEEDS FIX" in c["note"] for c in cases)
    print(f"\nVerified: {done}/{len(cases)}  |  Needs fix: {fix}")


if __name__ == "__main__":
    main()
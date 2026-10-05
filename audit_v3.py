"""Read-only audit of v3 predictions; writes diagnostics under reports/v3_audit.

Run from the repository root with Python 3.10+. No model or third-party packages.
Diagnostic equivalence is deliberately separate from official Program Accuracy.
"""
import ast
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

from vinumqa.utils.dsl_parser import parse_program, validate_program, programs_equivalent

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "reports" / "v3_audit"
MATH = {"add", "subtract", "multiply", "divide", "greater", "exp"}
LOOKUP = {"chart_at", "chart_max", "chart_min", "chart_sum", "chart_average", "chart_total",
          "table_max", "table_min", "table_sum", "table_average"}


def number(s):
    # Canonical DSL decimal only. Do not guess whether 1.234 means 1234.
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", s):
        return Fraction(s)
    return None


def diagnose(program, sample):
    steps = parse_program(program)
    issues = []
    depth = 0
    for ch in program:
        depth += (ch == "(") - (ch == ")")
        if depth < 0:
            issues.append("unbalanced_parentheses")
            break
    if depth:
        issues.append("unbalanced_parentheses")
    if not steps:
        issues.append("empty")
    for i, step in enumerate(steps):
        op, args = step.operator, step.args
        if op not in MATH | LOOKUP:
            issues.append(f"unknown_operator@{i}:{op}")
        expected = 2 if op in MATH else 4
        if len(args) != expected:
            issues.append(f"arity@{i}:{len(args)}!={expected}")
        for arg in args:
            if arg.startswith("#"):
                if not re.fullmatch(r"#\d+", arg) or int(arg[1:]) >= i:
                    issues.append(f"reference@{i}:{arg}")
            elif op in MATH and number(arg) is None:
                issues.append(f"math_type@{i}:{arg}")
        if op in LOOKUP and args:
            expected_prefix = "Image " if op.startswith("chart_") else "Table "
            if not re.fullmatch(expected_prefix + r"\d+", args[0]):
                issues.append(f"source_type@{i}:{args[0]}")
            elif args[0] not in sample.get("images" if op.startswith("chart_") else "tables", {}):
                issues.append(f"source_missing@{i}:{args[0]}")
        if op == "divide" and len(args) == 2 and number(args[1]) == 0:
            issues.append(f"division_zero@{i}")
    return steps, list(dict.fromkeys(issues))


def tree(steps):
    """Final expression retaining lookups, argument order and duplicate multiplicity."""
    nodes = []
    for i, s in enumerate(steps):
        args = []
        for a in s.args:
            if re.fullmatch(r"#\d+", a):
                j = int(a[1:])
                if j >= i:
                    raise ValueError("invalid reference")
                args.append(nodes[j])
            else:
                n = number(a) if s.operator in MATH else None
                args.append(("num", str(n)) if n is not None else ("str", a))
        if s.operator in {"add", "multiply"}:
            args.sort(key=repr)
        nodes.append((s.operator, tuple(args)))
    return nodes[-1] if nodes else None


def math_value(steps):
    values = []
    for s in steps:
        if s.operator not in MATH:
            return None
        args = [values[int(a[1:])] if re.fullmatch(r"#\d+", a) else number(a) for a in s.args]
        if len(args) != 2 or None in args:
            return None
        a, b = args
        op = s.operator
        if op == "add": v = a + b
        elif op == "subtract": v = a - b
        elif op == "multiply": v = a * b
        elif op == "divide": v = a / b
        elif op == "greater": v = Fraction(int(a > b))
        elif op == "exp" and b.denominator == 1 and abs(b) <= 100: v = a ** int(b)
        else: return None
        values.append(v)
    return values[-1] if values else None


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    with (ROOT / "evaluation_report_v3.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    public = load("data/public_test/public_test.json")
    by_id = {s["qid"]: s for s in public}
    assert len(by_id) == len(public)
    assert len({r["QID"] for r in rows}) == len(rows)
    assert set(by_id) == {r["QID"] for r in rows}
    submission_path = ROOT / "content.json"
    if submission_path.exists():
        submission = {s["qid"]: s["program"] for s in load("content.json")}
        assert all(submission[r["QID"]].strip() == r["Model_Predict"].strip() for r in rows)
    counts = Counter()
    details = []
    op_counts = {"gold": Counter(), "pred": Counter()}
    groups = {}
    for row_no, r in enumerate(rows, 2):
        sample = by_id[r["QID"]]
        g, p = r["Ground_Truth"].strip(), r["Model_Predict"].strip()
        assert g == sample["qa"]["program"].strip(), r["QID"]
        gs, gi = diagnose(g, sample)
        ps, pi = diagnose(p, sample)
        go, po = [s.operator for s in gs], [s.operator for s in ps]
        op_counts["gold"].update(go)
        op_counts["pred"].update(po)
        gm, pm = all(o in MATH for o in go), bool(ps) and all(o in MATH for o in po)
        category = "math_only" if gm else "mixed_lookup" if any(o.startswith("chart_") for o in go) and any(o.startswith("table_") for o in go) else "chart" if any(o.startswith("chart_") for o in go) else "table"
        group = groups.setdefault(category, Counter())
        group["total"] += 1
        flags = []
        if p == g:
            flags.append("exact")
            group["exact"] += 1
        else:
            flags.append("non_exact")
        if programs_equivalent(p, g): flags.append("repo_equivalent")
        if pm: flags.append("pred_math_only")
        if pm and not gm: flags.append("lookup_omitted_math_only")
        if pm and gm: flags.append("both_math_only")
        if gm and any(o in LOOKUP for o in po): flags.append("lookup_added_to_math_gold")
        if pi: flags.append("strict_invalid")
        if not validate_program(p)[0]: flags.append("repo_invalid")
        if go != po: flags.append("operator_sequence_diff")
        if len(gs) != len(ps): flags.append("step_count_diff")
        if len(ps) < len(gs): flags.append("fewer_steps")
        if go == po and p != g: flags.append("same_ops_argument_diff")
        if "exact" not in flags and not gi and not pi:
            if tree(gs) == tree(ps): flags.append("expression_tree_equivalent_non_exact")
        try:
            gv, pv = math_value(gs), math_value(ps)
            if gv is not None and pv is not None and gv == pv and p != g:
                flags.append("same_math_value_non_exact")
        except (ValueError, IndexError, ZeroDivisionError, OverflowError):
            pass
        if any(x.startswith("reference@") for x in pi): flags.append("invalid_reference")
        if any(x.startswith("arity@") for x in pi): flags.append("invalid_arity")
        if any(x.startswith("math_type@") for x in pi): flags.append("invalid_math_argument")
        if any(x.startswith("source_type@") for x in pi): flags.append("invalid_source_type")
        if any(x.startswith("source_missing@") for x in pi): flags.append("missing_source_id")
        differences = []
        for i in range(max(len(gs), len(ps))):
            if i >= len(gs): differences.append(f"#{i}: extra predicted step {ps[i]}")
            elif i >= len(ps): differences.append(f"#{i}: missing gold step {gs[i]}")
            else:
                a, b = gs[i], ps[i]
                if a.operator != b.operator: differences.append(f"#{i}: operator {a.operator} -> {b.operator}")
                for j in range(max(len(a.args), len(b.args))):
                    ga = a.args[j] if j < len(a.args) else "<absent>"
                    pa = b.args[j] if j < len(b.args) else "<absent>"
                    if ga != pa: differences.append(f"#{i} arg{j}: {ga!r} -> {pa!r}")
                if a.operator == b.operator and a.operator in {"subtract", "divide", "greater", "exp"} and a.args != b.args and a.args == b.args[::-1]:
                    flags.append("aligned_noncommutative_swap")
        counts.update(set(flags))
        details.append(dict(csv_row=row_no, qid=r["QID"], question=sample["qa"]["question"],
                            gold=g, pred=p, flags=sorted(set(flags)), gold_issues=gi, pred_issues=pi,
                            differences=differences))
    syntax = []
    for path in sorted((ROOT / "vinumqa").rglob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"))
            status = "OK"
        except SyntaxError as e:
            status = f"{type(e).__name__}: {e.msg}, line {e.lineno}"
        syntax.append({"file": path.relative_to(ROOT).as_posix(), "status": status})
    train = load("data/train/train.json")
    datasets = {}
    for filename in ["train_formatted.json", "public_test_formatted.json"]:
        data = load("vinumqa/data/" + filename)
        datasets[filename] = dict(samples=len(data), instructions=Counter(s["instruction"] for s in data),
            cv_error_samples=sum("Model chưa được load" in s["input"] or "| Lỗi |" in s["input"] for s in data),
            chart_placeholder_samples=sum("extracted by CV Module" in s["input"] for s in data),
            image_header_samples=sum("**Image " in s["input"] for s in data),
            max_output_chars=max(len(s["output"]) for s in data))
    def fingerprint(s):
        return hashlib.sha256(json.dumps({k:s.get(k) for k in ["text", "tables", "images"]},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    train_docs = {fingerprint(s) for s in train}
    train_stats = dict(samples=len(train), math_only=sum(all(x.operator in MATH for x in parse_program(s["qa"]["program"])) for s in train),
                       public_same_context=sum(fingerprint(s) in train_docs for s in public))
    summary = dict(total=len(rows), counts=counts, groups=groups, operators=op_counts, syntax=syntax,
                   formatted=datasets, train=train_stats, gold_issue_rows=sum(bool(d["gold_issues"]) for d in details))
    summary["source_sha256"] = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [ROOT / "page.html", ROOT / "evaluation_report_v3.csv",
                                         *sorted((ROOT / "vinumqa").rglob("*.py"))]}
    assert counts["exact"] + counts["non_exact"] == len(rows)
    assert counts["pred_math_only"] == counts["both_math_only"] + counts["lookup_omitted_math_only"]
    assert all("strict_invalid" in d["flags"] for d in details if "repo_invalid" in d["flags"])
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "rows.json").write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Đối chiếu toàn bộ 459 câu của evaluation_report_v3.csv", "",
          "Các cờ là chẩn đoán tự động, có thể chồng lấp; không phải điểm chính thức. Số thứ tự dòng CSV tính header là dòng 1.",
          "`lookup_omitted_math_only` chỉ xác nhận bỏ lookup so với gold, không khẳng định kết quả số đúng.",
          "`same_math_value_non_exact` chỉ là trùng kết quả của các hằng số, không chứng minh quy trình tương đương.", ""]
    for d in details:
        md += [f"## Dòng {d['csv_row']} — {d['qid']}", "", d["question"], "",
               f"- Nhãn: {', '.join(d['flags'])}", f"- Ground truth: `{d['gold']}`", f"- Model: `{d['pred']}`"]
        if d["pred_issues"]: md.append("- Vi phạm kiểm tra: " + "; ".join(d["pred_issues"]))
        if d["gold_issues"]: md.append("- Cần rà soát gold: " + "; ".join(d["gold_issues"]))
        md += ["- " + x for x in d["differences"]]
        md.append("")
    (OUT / "row_review.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "formatted"},ensure_ascii=False,indent=2))
    print("FORMATTED", json.dumps({k:{a:b for a,b in v.items() if a != "instructions"} for k,v in datasets.items()},ensure_ascii=False))


if __name__ == "__main__":
    main()

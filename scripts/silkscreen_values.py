#!/usr/bin/env python3
"""Plan and audit value labels from normalized, verified EDA inventory.

This tool never edits EDA and never certifies geometry or manufacturing output.
"""

import argparse
import json
import re
import sys
from pathlib import Path


KINDS = {"R", "C", "L", "FB", "Y", "U", "Q", "D", "LED", "J", "SW", "F", "BT", "OTHER", "MECHANICAL"}
SYMBOLS = str.maketrans({"µ": "u", "μ": "u", "Ω": "Ohm", "Ω": "Ohm"})


def text(value):
    """Preserve case, decimals and unit prefixes; only normalize glyphs/spacing."""
    return " ".join(value.translate(SYMBOLS).split())


def load(path):
    with Path(path).open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def require_string(obj, key, allow_empty=False):
    value = obj.get(key)
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{key} must be a nonempty string" if not allow_empty else f"{key} must be a string")
    return value.strip()


def plan(data):
    if not isinstance(data, dict) or not isinstance(data.get("components"), list):
        raise ValueError("inventory must be an object with a components array")
    labels, skipped, issues, warnings = [], [], [], []
    ids, designators = set(), set()
    for index, comp in enumerate(data["components"]):
        name = f"components[{index}]"
        try:
            if not isinstance(comp, dict):
                raise ValueError("component must be an object")
            cid = require_string(comp, "id")
            des = require_string(comp, "designator")
            name = des
            if cid in ids or des in designators:
                raise ValueError("duplicate component id or designator")
            ids.add(cid)
            designators.add(des)
            kind = require_string(comp, "kind")
            if kind not in KINDS:
                raise ValueError("unsupported kind; normalize using silkscreen-data.md")
            if kind == "MECHANICAL":
                if re.match(r"^(?:R|C|L|FB|Y)\d", des, re.I):
                    raise ValueError("passive designator cannot be silently excluded as mechanical")
                skipped.append({"component_id": cid, "designator": des, "reason": "mechanical"})
                continue
            if comp.get("side") not in ("top", "bottom"):
                raise ValueError("side must be top or bottom")
            if type(comp.get("populated")) is not bool:
                raise ValueError("populated must be a JSON boolean from the selected variant")
            source = require_string(comp, "value_source")
            raw = require_string(comp, "value", allow_empty=True)
            unit = comp.get("unit", "")
            if not isinstance(unit, str):
                raise ValueError("unit must be a string")
            raw_display = text(raw)
            if not raw_display and comp["populated"]:
                raise ValueError("missing verified value/model/function")
            if raw_display.lower() in {"?", "unknown", "tbd", "n/a", "dnp", "nc"}:
                raise ValueError("placeholder is not a verified value; use empty value for unknown DNP")
            if kind in {"R", "C", "L", "FB", "Y", "F"} and raw_display:
                if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", raw_display) and not unit.strip():
                    raise ValueError("bare numeric passive value requires an explicit unit")
            display = raw_display + text(unit) if raw_display else ""
            if not comp["populated"]:
                if not display:
                    warnings.append({"component": des, "reason": "DNP nominal value unknown; not inferred"})
                display = (display + " DNP").strip()
            label = f"{des} {display}"
            labels.append({
                "component_id": cid, "designator": des, "raw_value": raw,
                "unit": unit, "value_source": source, "text": label,
                "layer": f"{comp['side']}_silkscreen", "visible": True,
            })
        except ValueError as exc:
            issues.append({"component": name, "reason": str(exc)})
    status = "failed" if issues else ("planned" if labels else "not_applicable")
    return {"status": status, "labels": labels, "skipped": skipped, "issues": issues,
            "warnings": warnings, "scope": "text plan only; EDA not modified"}


def audit(data, actual):
    expected = plan(data)
    if not isinstance(actual, dict) or not isinstance(actual.get("labels"), list):
        raise ValueError("readback must be an object with a labels array")
    wanted = {label["component_id"]: label for label in expected["labels"]}
    issues = list(expected["issues"])
    found = {}
    primitive_ids = set()
    for index, label in enumerate(actual["labels"]):
        name = f"labels[{index}]"
        try:
            if not isinstance(label, dict):
                raise ValueError("label must be an object")
            cid = require_string(label, "component_id")
            name = cid
            if cid not in wanted:
                raise ValueError("orphaned or out-of-scope value label; inspect before deleting")
            found.setdefault(cid, []).append(label)
            target = wanted[cid]
            if require_string(label, "designator") != target["designator"]:
                issues.append({"component": name, "reason": "stale or incorrect designator"})
            if text(require_string(label, "text")) != target["text"]:
                issues.append({"component": name, "reason": f"value text mismatch; expected {target['text']!r}"})
            if label.get("visible") is not True:
                issues.append({"component": name, "reason": "label is hidden or visibility was not read back"})
            if label.get("layer") != target["layer"]:
                issues.append({"component": name, "reason": f"wrong layer; expected {target['layer']}"})
            tids = label.get("text_ids")
            if not isinstance(tids, list) or not tids or any(not isinstance(t, str) or not t.strip() for t in tids):
                raise ValueError("text_ids must list actual EDA attribute/text primitive ids")
            if len(set(tids)) != len(tids) or any(t in primitive_ids for t in tids):
                raise ValueError("text primitive id repeated or shared by labels")
            primitive_ids.update(tids)
        except ValueError as exc:
            issues.append({"component": name, "reason": str(exc)})
    for cid, label in wanted.items():
        count = len(found.get(cid, []))
        if count != 1:
            issues.append({"component": label["designator"], "reason": f"expected one logical label, found {count}"})
    status = "failed" if issues else ("passed" if wanted else "not_applicable")
    return {"status": status, "expected": len(wanted), "observed_records": len(actual["labels"]),
            "issues": issues, "warnings": expected["warnings"],
            "scope": "normalized text/layer/visibility coverage only; geometry and Gerber not checked"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "audit"):
        child = sub.add_parser(command)
        child.add_argument("inventory", type=Path)
        if command == "audit":
            child.add_argument("readback", type=Path)
        child.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        result = plan(load(args.inventory)) if args.command == "plan" else audit(load(args.inventory), load(args.readback))
        output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 1 if result["status"] == "failed" else 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

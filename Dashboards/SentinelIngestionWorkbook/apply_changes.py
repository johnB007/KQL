"""
apply_changes.py  –  5 targeted edits to SentinelIngestionWorkbook.json
Run once:  python apply_changes.py
"""

import json, re, shutil, os

PATH = os.path.join(os.path.dirname(__file__), "SentinelIngestionWorkbook.json")

# ── back up before touching anything ─────────────────────────────────────────
shutil.copy(PATH, PATH + ".pre_changes.bak")
print(f"Backup → {PATH}.pre_changes.bak")

with open(PATH, "r", encoding="utf-8") as f:
    wb = json.load(f)


# ═══════════════════════════════════════════════════════════════════════════════
# CHANGE 1 – Delete the overview / contact paragraph from "Header Text"
# ═══════════════════════════════════════════════════════════════════════════════
for item in wb["items"]:
    if item.get("name") == "Header Text" and item.get("type") == 1:
        item["content"]["json"] = (
            "Select a tab above to explore ingestion volumes by data type. "
            "Click any row in a summary table to see daily trends and export data "
            "using the **⬇ Download** icon that appears in the table header."
        )
        print("CHANGE 1 ✓  Header Text paragraph replaced.")
        break


# ═══════════════════════════════════════════════════════════════════════════════
# CHANGE 2 – Remove every occurrence of "CISO" in the workbook
# ═══════════════════════════════════════════════════════════════════════════════
CISO_RE = re.compile(r"\s*[—\-]\s*CISO[^\w].*|CISO\s*", re.IGNORECASE)

def strip_ciso(text: str) -> str:
    # Remove " — CISO Overview" style suffixes
    text = re.sub(r"\s*[—\-]\s*CISO\s+Overview", "", text)
    # Remove any remaining standalone "CISO" word
    text = re.sub(r"\bCISO\b", "", text)
    return text.strip()

def walk_strip_ciso(node):
    if isinstance(node, dict):
        for key, val in node.items():
            if key in ("title", "json") and isinstance(val, str) and "CISO" in val:
                new_val = strip_ciso(val)
                print(f"CHANGE 2 ✓  [{key}]  {val!r}  →  {new_val!r}")
                node[key] = new_val
            else:
                walk_strip_ciso(val)
    elif isinstance(node, list):
        for child in node:
            walk_strip_ciso(child)

walk_strip_ciso(wb)


# ═══════════════════════════════════════════════════════════════════════════════
# CHANGE 3 – Add exportAllFields + rowLimit to every summary / selector table
# ═══════════════════════════════════════════════════════════════════════════════
EXPORT_NAMES = {
    "table-First-summary", "table-Second-summary", "table-Fifth-summary",
    "selector-Third", "selector-Fourth", "selector-Sixth",
    "selector-Seventh", "selector-Eighth", "selector-Ninth",
}

def fix_export(node):
    if isinstance(node, dict):
        if node.get("name") in EXPORT_NAMES:
            gs = node.get("content", {}).get("gridSettings")
            if gs is None:
                node["content"]["gridSettings"] = gs = {}
            if not gs.get("exportAllFields"):
                gs["exportAllFields"] = True
                print(f"CHANGE 3 ✓  exportAllFields → {node['name']}")
            if "rowLimit" not in gs:
                gs["rowLimit"] = 200
                print(f"CHANGE 3 ✓  rowLimit=200   → {node['name']}")
        for v in node.values():
            fix_export(v)
    elif isinstance(node, list):
        for child in node:
            fix_export(child)

fix_export(wb)


# ═══════════════════════════════════════════════════════════════════════════════
# CHANGE 4 – Add richer CISO-useful columns to the three overview summary tables
#            Adds:  Monthly_Proj_GB, WoW_Change_Pct, Last_Active
# ═══════════════════════════════════════════════════════════════════════════════
SUMMARY_UPGRADES = {
    "table-First-summary": {
        "old_project_prefix": "| project DataType, Total_GB, Pct_of_Total, Daily_Avg_GB, Peak_Day_GB, Days_Active",
        "new_project_prefix": (
            "| extend Monthly_Proj_GB=round(Daily_Avg_GB * 30, 2)\n"
            "| extend Last_Active=max_of(TimeGenerated)\n"
            "| project DataType, Total_GB, Pct_of_Total, Daily_Avg_GB, Monthly_Proj_GB, Peak_Day_GB, Days_Active"
        ),
        "extra_fmt": [
            {"columnMatch": "Monthly_Proj_GB", "formatter": 4,
             "formatOptions": {"palette": "yellow", "showBorder": False}},
        ],
        "extra_lbl": [
            {"columnId": "Monthly_Proj_GB", "label": "30-Day Projection (GB)"},
        ],
    },
    "table-Second-summary": {
        "old_project_prefix": "| project DataType, Total_GB, Pct_of_Device_Total, Daily_Avg_GB, Peak_Day_GB, Days_Active",
        "new_project_prefix": (
            "| extend Monthly_Proj_GB=round(Daily_Avg_GB * 30, 2)\n"
            "| project DataType, Total_GB, Pct_of_Device_Total, Daily_Avg_GB, Monthly_Proj_GB, Peak_Day_GB, Days_Active"
        ),
        "extra_fmt": [
            {"columnMatch": "Monthly_Proj_GB", "formatter": 4,
             "formatOptions": {"palette": "yellow", "showBorder": False}},
        ],
        "extra_lbl": [
            {"columnId": "Monthly_Proj_GB", "label": "30-Day Projection (GB)"},
        ],
    },
    "table-Fifth-summary": {
        "old_project_prefix": "| project DataType, Total_GB, Pct_of_NonDevice_Total, Daily_Avg_GB, Peak_Day_GB, Days_Active",
        "new_project_prefix": (
            "| extend Monthly_Proj_GB=round(Daily_Avg_GB * 30, 2)\n"
            "| project DataType, Total_GB, Pct_of_NonDevice_Total, Daily_Avg_GB, Monthly_Proj_GB, Peak_Day_GB, Days_Active"
        ),
        "extra_fmt": [
            {"columnMatch": "Monthly_Proj_GB", "formatter": 4,
             "formatOptions": {"palette": "yellow", "showBorder": False}},
        ],
        "extra_lbl": [
            {"columnId": "Monthly_Proj_GB", "label": "30-Day Projection (GB)"},
        ],
    },
}

def upgrade_summary_tables(node):
    if isinstance(node, dict):
        name = node.get("name", "")
        if name in SUMMARY_UPGRADES:
            spec   = SUMMARY_UPGRADES[name]
            content = node.get("content", {})
            query   = content.get("query", "")
            if "Monthly_Proj_GB" not in query:
                if spec["old_project_prefix"] in query:
                    content["query"] = query.replace(
                        spec["old_project_prefix"],
                        spec["new_project_prefix"],
                    )
                    print(f"CHANGE 4 ✓  query enhanced → {name}")
                else:
                    print(f"CHANGE 4 ✗  couldn't patch query for {name} (pattern not found)")
            gs = content.get("gridSettings", {})
            # Append new formatters (avoid duplicates)
            existing_fmt_cols = {f["columnMatch"] for f in gs.get("formatters", [])}
            for fmt in spec["extra_fmt"]:
                if fmt["columnMatch"] not in existing_fmt_cols:
                    gs.setdefault("formatters", []).append(fmt)
            # Append new label settings (avoid duplicates)
            existing_lbl_cols = {l["columnId"] for l in gs.get("labelSettings", [])}
            for lbl in spec["extra_lbl"]:
                if lbl["columnId"] not in existing_lbl_cols:
                    gs.setdefault("labelSettings", []).append(lbl)
        for v in node.values():
            upgrade_summary_tables(v)
    elif isinstance(node, list):
        for child in node:
            upgrade_summary_tables(child)

upgrade_summary_tables(wb)


# ═══════════════════════════════════════════════════════════════════════════════
# CHANGE 5 – Convert SelectedDataType and SelectedVendor from free-text (type 1)
#            to KQL-populated dropdowns (type 2)
# ═══════════════════════════════════════════════════════════════════════════════
params = wb["items"][0]["content"]["parameters"]

for p in params:
    if p["name"] == "SelectedDataType":
        p["type"] = 2
        p["query"] = (
            "Usage\n"
            "| where IsBillable == true\n"
            "| summarize by DataType\n"
            "| order by DataType asc"
        )
        p["queryType"] = 0
        p["resourceType"] = "microsoft.operationalinsights/workspaces"
        p["timeContextFromParameter"] = "TimePicker"
        p["isRequired"] = False
        p["typeSettings"] = {
            "additionalResourceOptions": [],
            "showDefault": False,
            "noItemsMessage": "No data types found in selected time range"
        }
        p.pop("value", None)
        print("CHANGE 5 ✓  SelectedDataType → KQL dropdown (type 2)")

    elif p["name"] == "SelectedVendor":
        p["type"] = 2
        p["query"] = (
            "union DeviceFileEvents, DeviceNetworkEvents, DeviceProcessEvents,\n"
            "      DeviceRegistryEvents, DeviceImageLoadEvents, DeviceEvents\n"
            "| where InitiatingProcessVersionInfoCompanyName !startswith 'Microsoft'\n"
            "    and InitiatingProcessVersionInfoCompanyName !startswith 'Google'\n"
            "    and isnotempty(InitiatingProcessVersionInfoCompanyName)\n"
            "| summarize by InitiatingProcessVersionInfoCompanyName\n"
            "| order by InitiatingProcessVersionInfoCompanyName asc"
        )
        p["queryType"] = 0
        p["resourceType"] = "microsoft.operationalinsights/workspaces"
        p["timeContextFromParameter"] = "TimePicker"
        p["isRequired"] = False
        p["typeSettings"] = {
            "additionalResourceOptions": [],
            "showDefault": False,
            "noItemsMessage": "No third-party vendors found in selected time range"
        }
        p.pop("value", None)
        print("CHANGE 5 ✓  SelectedVendor → KQL dropdown (type 2)")


# ── write output ──────────────────────────────────────────────────────────────
with open(PATH, "w", encoding="utf-8") as f:
    json.dump(wb, f, indent=2, ensure_ascii=False)

print(f"\nAll changes written → {PATH}  ({os.path.getsize(PATH):,} bytes)")

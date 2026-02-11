### Collecting ASR Telemetry for Analysis
Run the following KQL to analyze ASR Telemetry    

This KQL script collects and summarizes 30 days of Attack Surface Reduction (ASR) telemetry from the DeviceEvents table in Microsoft Defender for Endpoint to help analysts evaluate ASR rule impact before moving from Audit to Block mode. It extracts key ASR metadata such as rule GUIDs, audit versus block actions, initiating processes, and the exact file path that triggered each event, then aggregates these hits into a clean, export‑ready dataset. The goal is to give SOC teams and endpoint engineers a reliable way to identify noisy applications, understand which files or processes are repeatedly triggering ASR rules, and determine where tightly scoped exclusions may be required in Intune without weakening protection. This query is designed for large‑scale review during ASR tuning cycles, helping teams make data‑driven decisions on whether events represent legitimate application behavior or true risk requiring enforcement.

```
//30 day ASR Rule Telemetry Collection
let TimeRange = 30d;
DeviceEvents
| where Timestamp > ago(TimeRange)
| where ActionType startswith "Asr"
| extend AF = parse_json(tostring(AdditionalFields))
| extend IsAudit = tostring(AF.IsAudit)
| extend RuleGUID = tostring(AF.RuleId)
| extend Mode = case(
    ActionType endswith "Blocked" or IsAudit == "false", "Block",
    ActionType endswith "Audited" or IsAudit == "true", "Audit",
    "Unknown"
)
| extend ChildFullPath = iif(isnotempty(FolderPath) and isnotempty(FileName), strcat(FolderPath, "\\", FileName), FolderPath)
| extend AF_Path = coalesce(tostring(AF.Path), tostring(AF.TargetFilePath), tostring(AF.TargetPath), tostring(AF.FilePath))
| extend FileThatTriggeredASR = coalesce(ChildFullPath, AF_Path, "N/A")
| summarize
    EventCount = count(),
    arg_max(Timestamp, InitiatingProcessFileName, InitiatingProcessFolderPath, InitiatingProcessCommandLine, ProcessCommandLine, FileName, FolderPath
)
  by DeviceName, Mode, ActionType, RuleGUID, FileThatTriggeredASR
| project LastSeen = Timestamp, EventCount, DeviceName, Mode, ActionType, RuleGUID, FileThatTriggeredASR, FileName, FolderPath, InitiatingProcessFileName,
InitiatingProcessFolderPath, InitiatingProcessCommandLine, ProcessCommandLine
| top 30000 by EventCount desc
```

<img width="3024" height="1543" alt="image" src="https://github.com/user-attachments/assets/34354ae4-be1b-4c51-8160-c51207feefca" />

In this example, the query shows three ASR Audit events (EventCount = 3) last seen on Jan 30, 2026 5:31:36 PM, where the ASR action type was AsrAbusedSystemToolAudited.  The initiating process was cmd.exe from C:\Windows\System32, and the command line indicates it ran cmd /c to execute vulkaninfo.exe.  The file that triggered the ASR event was C:\Program Files\Google\Play Games\current\service\vulkaninfo.exe, derived from FolderPath + FileName, which in the DeviceEvents schema represents the file the recorded action was applied to.  This is exactly the kind of execution chain ASR telemetry helps you validate during tuning, because ASR rules are designed to flag behaviors commonly abused by threats such as using system tools to launch other executables, and Audit mode lets you measure impact before enforcing Block.

<img width="3068" height="1625" alt="image" src="https://github.com/user-attachments/assets/ca4fad5b-b852-4950-bf16-b67682081c6a" />



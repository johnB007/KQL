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

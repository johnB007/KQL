### Getting Exclusions from KQL for Intune for ASR

This KQL  analyzes Attack Surface Reduction activity on a "specific" device and shows which files triggered the ASR events, how often they occurred, 
and which ASR rules were involved. It identifies the exact file path that caused the rule to fire and determines the best exclusion path to consider if the file is legitimate.
It also applies a risk label so analysts can easily understand whether an exclusion would be safe or potentially harmful. A SOC team can use the output to decide which
ASR events are false positives during audit or testing, and then use the identified exclusion paths to create precise and minimal ASR exclusions in Intune so that
business required applications continue functioning without weakening security.

```
//Get exclusion paths
let TargetDevice = "defcon30"; //Insert DeviceName Here
let TimeRange = 90d;
DeviceEvents
| where Timestamp > ago(TimeRange)
| where DeviceName == TargetDevice
| where ActionType startswith "Asr"
| extend AF = tostring(AdditionalFields)
| extend RuleGUID = coalesce(
    extract(@'"RuleId"\s*:\s*"([0-9A-Fa-f-]{36})"', 1, AF),
    extract(@'"ruleId"\s*:\s*"([0-9A-Fa-f-]{36})"', 1, AF),
    extract(@'"RuleID"\s*:\s*"([0-9A-Fa-f-]{36})"', 1, AF),
    extract(@'"ruleID"\s*:\s*"([0-9A-Fa-f-]{36})"', 1, AF)
)
| extend EvaluatedPath = coalesce(
    extract(@'"Path"\s*:\s*"([^"]+)"', 1, AF),
    extract(@'"path"\s*:\s*"([^"]+)"', 1, AF)
)
| extend ChildFullPath = iif(isnotempty(FolderPath) and isnotempty(FileName), strcat(FolderPath, "\\", FileName), FolderPath)
| extend PreferredExclusionPath = coalesce(EvaluatedPath, ChildFullPath)
| extend FileThatTriggeredASR = coalesce(ChildFullPath, FolderPath)
// Risk classification for exclusion candidates
| extend P = tolower(PreferredExclusionPath)
| extend RiskFlag = case(
    isempty(PreferredExclusionPath), "UNKNOWN - No path captured",
    P startswith "c:\\windows\\system32\\" or P startswith "c:\\windows\\syswow64\\", "HIGH - Windows system binary (avoid excluding)",
    P has "\\program files\\" and P has "\\microsoft office\\", "MED - Microsoft Office binary (avoid unless confirmed needed)",
    P has "\\program files\\", "MED - Program Files binary (validate signer/publisher)",
    P startswith "c:\\programdata\\", "MED - ProgramData (shared, validate ownership)",
    P has "\\users\\" and (P has "\\appdata\\" or P has "\\inetcache\\" or P has "\\temp\\"), "HIGH - User-writable temp/cache (risky exclusion)",
    P has "\\onedrive", "MED/HIGH - OneDrive user content (risky, scope narrowly)",
    P startswith "c:\\users\\", "MED/HIGH - User profile path (scope narrowly)",
    "UNKNOWN - Review required"
)
| summarize EventCount = count(), arg_max(Timestamp, InitiatingProcessFolderPath, InitiatingProcessCommandLine, FolderPath, ChildFullPath, ProcessCommandLine, AdditionalFields, FileThatTriggeredASR) by DeviceName, ActionType, RuleGUID, InitiatingProcessFileName, FileName, PreferredExclusionPath, RiskFlag
| project Timestamp, DeviceName, ActionType, RuleGUID, RiskFlag, EventCount, InitiatingProcessFileName, InitiatingProcessFolderPath, InitiatingProcessCommandLine, FileName, FolderPath, ChildFullPath, FileThatTriggeredASR, ProcessCommandLine, PreferredExclusionPath, AdditionalFields
| order by EventCount desc, Timestamp desc
```
### The story behind this event

What we’re looking at is a normal Office workflow that Defender’s Attack Surface Reduction rules are designed to watch closely, because attackers often use Office as the 
first step to run code. In this record, the initiating process is powerpnt.exe, meaning PowerPoint is the application that started the chain of activity. The initiating process
path shows it’s the standard Microsoft Office install location, which tells us the parent process itself is legitimate Office. In other words, the user opened something in 
PowerPoint, and PowerPoint then attempted an action that matched an ASR rule’s “blocked behavior.” ASR rules are built to stop behaviors that are commonly abused by
malware, especially when Office tries to create or run executable content or trigger suspicious execution patterns.

Now look at the “file that got blocked” side of the record. The output shows FolderPath as C:\Program Files (x86)\Microsoft Office\Office15 and the file name is a DLL called 
AntiMalware.Utils.RemoteAPI.Interop-...dll, which the query builds into the full file path in ChildFullPath and also surfaces as FileThatTriggeredASR. That means the 
ASR event was applied to that specific DLL at that specific path. In the Defender hunting schema, FileName is the name of the file the action was applied to, and FolderPath
is the folder containing that file, so that combination is the authoritative “target file” for this event.

<img width="3063" height="1711" alt="image" src="https://github.com/user-attachments/assets/58bc6411-a7e4-4f65-ab0c-8677043589e6" />

### Exclusions
If you 100% needed this excluded, this is what you would do. 
- Do not exclude the entire folder    
- Do not exclude PowerPoint (powerpnt.exe)     
- Do not use wildcards (*.dll or Office15* directories)

      
  C:\Program Files (x86)\Microsoft Office\Office15\AntiMalware.Utils.RemoteAPI.Interop-{GUID}.dll

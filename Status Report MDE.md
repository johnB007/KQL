## KQL
```Kusto
DeviceTvmInfoGathering
| extend AvModeRaw = tostring(AdditionalFields.AvMode)
| where isnotnull(AvModeRaw)
| distinct DeviceId, AvModeRaw
| extend AvMode = case(
    AvModeRaw == "0", "Active",
    AvModeRaw == "1", "Passive",
    AvModeRaw == "2", "Disabled",
    AvModeRaw == "4", "EDR Blocked",
    AvModeRaw == "5", "PassiveAudit",
    "Unknown"
)
| summarize DeviceCount = count() by AvMode
| order by DeviceCount desc
```

## Picture of output
<img width="716" height="482" alt="image" src="https://github.com/user-attachments/assets/12c7dae6-c6e2-4bf8-8404-766bee1a9680" />



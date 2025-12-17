
# Microsoft Defender Advanced Hunting - ActionType Reference

This document lists **ActionType** values for `DeviceEvents` and `MiscEvents` tables in Microsoft Defender Advanced Hunting.

---

## **MiscEvents - ActionType Values**

- `PnpDeviceConnected`
- `OpenProcessApiCall`
- `NtAllocateVirtualMemoryRemoteApiCall`
- `NtMapViewOfSectionRemoteApiCall`
- `PowerShellCommand`
- `AsrLsassCredentialTheftBlocked`
- `ProcessPrimaryTokenModified`
- `CreateRemoteThreadApiCall`
- `AntivirusReport`
- `ExploitGuardAcgEnforced`
- `ExploitGuardNonMicrosoftSignedBlocked`
- `ReadProcessMemoryApiCall`
- `FirewallInboundConnectionBlocked`
- `NtAllocateVirtualMemoryApiCall`
- `ScheduledTaskDeleted`
- `ScheduledTaskCreated`
- `BrowserLaunchedToOpenUrl`
- `ScreenshotTaken`
- `ExploitGuardAcgAudited`
- `GetClipboardData`
- `AmsiScriptDetection`
- `ExploitGuardWin32SystemCallBlocked`
- `WriteProcessMemoryApiCall`
- `AntivirusDetection`
- `AntivirusScanCompleted`
- `QueueUserApcRemoteApiCall`
- `ControlledFolderAccessViolationAudited`
- `AppControlCodeIntegrityPolicyAudited`
- `ExploitGuardNonMicrosoftSignedAudited`
- `AsrLsassCredentialTheftAudited`
- `SmartScreenAppWarning`
- `SmartScreenUserOverride`
- `AsrUntrustedExecutableAudited`
- `AppControlExecutableAudited`
- `ExploitGuardChildProcessAudited`
- `AsrOfficeChildProcessBlocked`
- `AntivirusScanCancelled`
- `UserAccountCreated`
- `LdapSearch`
- `AppControlCodeIntegrityPolicyBlocked`
- `GetAsyncKeyStateApiCall`
- `SetThreadContextRemoteApiCall`
- `OtherAlertRelatedActivity`
- `ExploitGuardNetworkProtectionBlocked`
- `SmartScreenUrlWarning`
- `ControlledFolderAccessViolationBlocked`
- `AsrOfficeChildProcessAudited`
- `AsrOfficeProcessInjectionAudited`
- `AppControlExecutableBlocked`
- `RemoteWmiOperation`

---

### **Usage Example in Advanced Hunting**

```kusto
DeviceEvents
| where ActionType in (
    "PnpDeviceConnected",
    "OpenProcessApiCall",
    "PowerShellCommand",
    "AntivirusDetection"
)
```

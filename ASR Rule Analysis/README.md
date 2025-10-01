ASR rules do not work in passive mode (block), since not all of the RTP and BM functionalities are enabled, since the customer is choosing to run the 3rd party AV as their primary.

1. The ASR Audit events do not generate toast notifications. However, since the LSASS ASR rule produces large volume of audit events and almost all of which are safe to ignore when the rule is enabled in Block mode, customers can choose to skip the Audit mode evaluation and jump to the Block mode deployment starting with the small set of devices and gradually moving to cover the rest.
2. The rule is designed to suppress the block reports/toasts for the friendly processes. It is also designed to drop the reports for duplicate blocks. As such, the rule is perfectly fine to be enabled in Block mode irrespective of the state of the Toast Notifications (enabled or disabled). 
3. MDAV has to be in active mode for ASR rules to work, period. It is a hard requirement. If an ASR rule blocked/audited something it will be in the Defender operational log in the event viewer on the device under applications and services. You can first validate that there is no block event there.

Show reports dashboard and walk through, configs, etc,  Run the top machines ASR query and then pivot to the device, and then  Show machine timeline and then filter by ASR events to show timeline.

----- ALL ASR and GUIDs---
[
"Block abuse of exploited vulnerable signed drivers","56a863a9-875e-4185-98a7-b882c64b5ce5",
"Block Adobe Reader from creating child processes","7674ba52-37eb-4a4f-a9a1-f0f9a1619a2c",
"Block all Office applications from creating child processes","d4f940ab-401b-4efc-aadc-ad5f3c50688a",
"Block credential stealing from the Windows local security authority subsystem (lsass.exe)","9e6c4e1f-7d60-472f-ba1a-a39ef669e4b2",
"Block executable content from email client and webmail","be9ba2d9-53ea-4cdc-84e5-9b1eeee46550",
"Block executable files from running unless they meet a prevalence, age, or trusted list criterion","01443614-cd74-433a-b99e-2ecdc07bfc25",
"Block execution of potentially obfuscated scripts","5beb7efe-fd9a-4556-801d-275e5ffc04cc",
"Block JavaScript or VBScript from launching downloaded executable content","d3e037e1-3eb8-44c8-a917-57927947596d",
"Block Office applications from creating executable content","3b576869-a4ec-4529-8536-b80a7769e899",
"Block Office applications from injecting code into other processes","75668c1f-73b5-4cf0-bb93-3ecf5cb7cc84",
"Block Office communication application from creating child processes","26190899-1602-49e8-8b27-eb1d0a1ce869",
"Block persistence through WMI event subscription ","e6db77e5-3df2-4cf1-b95a-636979351e5b",
"Block process creations originating from PSExec and WMI commands","d1e49aac-8f56-4280-b9ba-993a6d77406c",
"Block rebooting machine in Safe Mode (preview)","33ddedf1-c6e0-47cb-833e-de6133960387",
"Block untrusted and unsigned processes that run from USB","b2b3f03d-6a65-4f7b-a9c7-1c7ef74a9ba4",
"Block use of copied or impersonated system tools (preview)","c0033c00-d16d-4114-a5a0-dc9b3a7d2ceb",
"Block Webshell creation for Servers","a8f5898e-1dc8-49a9-9878-85004b8a61e6",
"Block Win32 API calls from Office macro","92e97fa1-2edf-4476-bdd6-9dd0b4dddc7b",
"Use advanced protection against ransomware","c1db55ab-c21a-4637-bb3f-a12568109d35",
];

// uncomment one line at a time to look at hits within a specific category
DeviceEvents
//| where ActionType =~ "AsrAdobeReaderChildProcessAudited"
//| where ActionType =~ "AsrExecutableEmailContentAudited"
//| where ActionType =~ "AsrExecutableOfficeContentAudited"
//| where ActionType =~ "AsrLsassCredentialTheftAudited"
//| where ActionType =~ "AsrObfuscatedScriptAudited"
//| where ActionType =~ "AsrOfficeChildProcessAudited"
//| where ActionType =~ "AsrOfficeCommAppChildProcessAudited"
//| where ActionType =~ "AsrOfficeMacroWin32ApiCallsAudited"
//| where ActionType =~ "AsrOfficeProcessInjectionAudited"
//| where ActionType =~ "AsrPersistenceThroughWmiAudited"
//| where ActionType =~ "AsrPsexecWmiChildProcessAudited"
//| where ActionType =~ "AsrRansomwareAudited"
//| where ActionType =~ "AsrScriptExecutableDownloadAudited"
//| where ActionType =~ "AsrUntrustedExecutableAudited"
//| where ActionType =~ "AsrUntrustedUsbProcessAudited"
//| where ActionType =~ "AsrVulnerableSignedDriverAudited"
//| where ActionType =~ "ControlledFolderAccessViolationAudited"
| project DeviceName, FileName, FolderPath, InitiatingProcessFileName, InitiatingProcessFolderPath, ProcessCommandLine

Event Viewer Logs | ASR logged event IDs : Log Name: Microsoft-Windows-Windows Defender/Operational
Event ID	Description
5007	Event when settings are changed
1121	Event when an attack surface reduction rule fires in block mode
1122	Event when an attack surface reduction rule fires in audit mode

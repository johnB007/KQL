ASR rules do not work in passive mode (block), since not all of the RTP and BM functionalities are enabled, since the customer is choosing to run the 3rd party AV as their primary.

1. The ASR Audit events do not generate toast notifications. However, since the LSASS ASR rule produces large volume of audit events and almost all of which are safe to ignore when the rule is enabled in Block mode, customers can choose to skip the Audit mode evaluation and jump to the Block mode deployment starting with the small set of devices and gradually moving to cover the rest.
2. The rule is designed to suppress the block reports/toasts for the friendly processes. It is also designed to drop the reports for duplicate blocks. As such, the rule is perfectly fine to be enabled in Block mode irrespective of the state of the Toast Notifications (enabled or disabled). 
3. MDAV has to be in active mode for ASR rules to work, period. It is a hard requirement. If an ASR rule blocked/audited something it will be in the Defender operational log in the event viewer on the device under applications and services. You can first validate that there is no block event there.

Show reports dashboard and walk through, configs, etc,  Run the top machines ASR query and then pivot to the device, and then  Show machine timeline and then filter by ASR events to show timeline.
<img width="2526" height="1338" alt="image" src="https://github.com/user-attachments/assets/e4c72b4d-ffe8-4656-bac4-a4816e22a331" />



Event Viewer Logs/ Log Name: Microsoft-Windows-Windows Defender/Operational

Event ID	Description

5007	Event when settings are changed

1121	Event when an attack surface reduction rule fires in block mode

1122	Event when an attack surface reduction rule fires in audit mode

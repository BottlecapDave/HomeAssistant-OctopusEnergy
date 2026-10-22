# Charge Pack

If your account has a home battery that Octopus controls (a Charge Pack, through SmartFlex), it's found automatically: any device on your account with the device type `INVERTERS` (e.g. a Sigenergy SigenStor shown as `INVERTERS · SMARTFLEX_CONNECT`). Each one gets its own device, named after it with `(Charge Pack)`, e.g. `Sigenergy SigenStor EC 12.0 SP (Charge Pack)`, with the calendars and sensors below. Its make and model come from Octopus (e.g. Sigenergy, SigenStor EC 12.0 SP).

Octopus's plan is read every 3 minutes. Octopus only lists the charges and discharges that haven't ended, and changes its plan often, so each calendar shows the plan as it is now, plus the ones that have started (as Octopus last listed them), kept for 30 days. One Octopus takes off the plan before it starts didn't happen, so it isn't kept.

## Charge Pack Charge

`calendar.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_charge`

When Octopus plans to charge the battery, e.g. `Charge 4.50 kWh`. The calendar is `on` during a charge, and its attributes show the charge running now or the next one.

## Charge Pack Discharge

`calendar.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_discharge`

When Octopus plans to discharge the battery (export), e.g. `Discharge 6.00 kWh`, as for the charges.

!!! note

    Octopus gives a charge a negative energy and a discharge a positive one; a dispatch with no energy (idle) isn't shown.

Both work with calendar triggers, e.g. 15 minutes before a discharge starts.

## Charge Pack State

`sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_state`

Octopus's state for the battery, as its API reports it, e.g. `SMART_CONTROL_CAPABLE`. Read with the plan, every 3 minutes.

| Attribute | Notes |
|-----------|-------|
| `status` | The device's status with Octopus, e.g. `LIVE` |
| `is_suspended` | `true` if Octopus's smart control of the battery is suspended |
| `data_last_retrieved` | When the data was last read from Octopus |

!!! note

    Octopus doesn't publish the battery's state of charge or power for these devices.

## Charge Pack Activity

`sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_activity`

What Octopus has the battery doing now, from its plan: `charging`, `discharging`, `idle` (a dispatch with no energy) or `none` (no dispatch running).

| Attribute | Notes |
|-----------|-------|
| `start` / `end` | The dispatch running now (none: not set) |
| `energy_kwh` | Its energy, either way |
| `minutes_left` | Until it ends |
| `data_last_retrieved` | When the plan was last read from Octopus |

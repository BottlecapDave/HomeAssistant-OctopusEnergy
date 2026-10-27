# Charge Pack

If your account has a home battery that Octopus controls through SmartFlex (e.g. a [Charge Pack](https://octopus.energy/blog/how-charge-pack-works/)), it's found automatically: any device on your account with the device type `INVERTERS` (e.g. a Sigenergy SigenStor shown as `INVERTERS · SMARTFLEX_CONNECT`). Each one gets its own device, named after it with `(Charge Pack)`, e.g. `Sigenergy SigenStor EC 12.0 SP (Charge Pack)`, with the entities below. Its make and model come from Octopus.

!!! warning

    If your battery is added to your account after you have installed the integration, you will need to reload the integration or restart your Home Assistant instance.

The calendars end with the account number, e.g. `Charge Pack Charge (A-12345678)`; the sensors end with the battery's device ID, as the intelligent device's entities do, named after the battery, e.g. `Sigenergy SigenStor EC 12.0 SP State (00000000-0011-4000-8020-000000000000)` and `Sigenergy SigenStor EC 12.0 SP Solar Power (00000000-0011-4000-8020-000000000000)`.

Octopus's plan, the battery's status and its readings are read together every 3 minutes. If Octopus can't send the status and readings, the plan is read on its own, and the status and readings keep their last values (their `data_last_retrieved` shows how old they are).

## Charge Pack Charge

`calendar.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_charge`

When Octopus plans to charge the battery, e.g. `Charge 4.50 kWh`. The calendar is `on` during a charge, so it can be used in calendar triggers (e.g. 15 minutes before a charge starts).

Octopus only lists the charges and discharges that haven't ended, and changes its plan often, so the calendar shows the plan as it is now, plus the ones that have started (as Octopus last listed them), kept for 30 days. One Octopus takes off the plan before it starts didn't happen, so it isn't kept.

!!! note

    Octopus gives a charge a negative energy and a discharge a positive one; a dispatch with no energy (idle) isn't shown.

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `string` | The summary of the charge running now or the next one, e.g. `Charge 4.50 kWh` |
| `start_time` | `datetime` | When that charge starts |
| `end_time` | `datetime` | When that charge ends |
| `description` | `string` | e.g. `Planned by Octopus Energy for Sigenergy SigenStor EC 12.0 SP (SMART)` |
| `all_day` | `boolean` | Always `false` |
| `location` | `string` | Always empty |
| `data_last_retrieved` | `datetime` | When the plan was last read from Octopus |

Each event has the summary (e.g. `Charge 4.50 kWh`), start, end and the description above.

## Charge Pack Discharge

`calendar.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_discharge`

When Octopus plans to discharge the battery (export), e.g. `Discharge 6.00 kWh`, as for the charges, with the same attributes.

## State

`sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_state`

Octopus's state for the battery, as its API reports it, e.g. `SMART_CONTROL_CAPABLE`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `status` | `string` | The device's status with Octopus, e.g. `LIVE` |
| `is_suspended` | `boolean` | `true` if Octopus's smart control of the battery is suspended |
| `battery_connection_status` | `string` | The battery's connection, e.g. `ONLINE` |
| `inverter_connection_status` | `string` | The inverter's connection, e.g. `ONLINE` |
| `data_last_retrieved` | `datetime` | When the status was last received from Octopus |

## Activity

`sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_activity`

What Octopus has the battery doing now, from its plan: `charging`, `discharging`, `idle` (a dispatch with no energy) or `none` (no dispatch running). This is Octopus's plan, not a reading: if the battery is controlled another way at the same time (e.g. locally), use the readings below for what it's actually doing.

| Attribute | Type | Description |
|-----------|------|-------------|
| `start` | `datetime` | When the dispatch running now started (none: not set) |
| `end` | `datetime` | When it ends |
| `energy_kwh` | `float` | Its energy in kWh, either way |
| `minutes_left` | `integer` | Minutes until it ends |
| `data_last_retrieved` | `datetime` | When the plan was last read from Octopus |

## Battery and inverter readings

The battery's live readings, as Octopus gets them from the inverter (its `telemetry`). They're passed on as Octopus sends them, except grid power, which is turned round to match the electricity meter's [current demand](./electricity.md#current-demand). Each is named after the battery, e.g. `Sigenergy SigenStor EC 12.0 SP Solar Power ({{DEVICE_ID}})`.

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_battery_state_of_charge` | % | The battery's state of charge |
| `sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_battery_power` | kW | The battery's power: positive while discharging, negative while charging |
| `sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_solar_power` | kW | The solar panels' power |
| `sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_grid_power` | kW | The grid's power: positive while importing, negative while exporting |
| `sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_inverter_power` | kW | The inverter's power: positive while it's putting power out, negative while it's taking power in (e.g. charging the battery from the grid) |
| `sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_site_consumption` | kW | What the site is using, as Octopus works it out: the solar and grid import, plus the battery while it's discharging. So it includes the battery while it's charging, and isn't the home's own use. It can be negative when something else on the inverter (e.g. a DC car charger discharging the car) is feeding the home |
| `sensor.octopus_energy_{{ACCOUNT_ID}}_{{DEVICE_ID}}_charge_pack_export_power` | kW | What's being exported: positive, and 0 while importing |

Each has these attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `data_last_retrieved` | `datetime` | When the readings were last received from Octopus |
| `connection_status` | `string` | Battery Power and Inverter Power only: the battery's or the inverter's connection, e.g. `ONLINE` |
| `peak_solar_power_kw` | `float` | Solar Power only: the solar panels' peak power, as set with Octopus |

!!! note

    The signs above are as seen on a Sigenergy SigenStor, both discharging and charging from the grid. Other inverters may report them differently.

!!! info

    These readings come from Octopus, which gets them from the inverter's own cloud, so they can be a few minutes behind the battery, the same as in the Octopus app. Octopus doesn't say when each reading was taken. For up-to-the-second readings, use a local integration for your inverter.

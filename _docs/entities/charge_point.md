# Charge Point

The following entities are available if you have an [Octopus Charge](https://octopus.energy/octopus-charge/) home EV charger registered against your account.

!!! note

    This is distinct from [Intelligent Octopus Go](./intelligent.md), which covers smart-charging dispatches for a wide range of third-party chargers. If your charger isn't an Octopus Charge unit, none of the entities below will be created - only the [Intelligent](./intelligent.md) entities apply to you.

!!! info

    These entities attach to the same device as your [Intelligent](./intelligent.md) entities, rather than creating a separate device, since they both represent the same physical charger.

## Operational State

`sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_operational_state`

This represents what the charger is currently doing. The possible values are

* `CHARGING`
* `BOOST_CHARGING`
* `NOT_CHARGING`
* `UNPLUGGED`
* `ONBOARDING`
* `SMART_CONTROL_SCHEDULED`

## Charging Method

`sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_charging_method`

This represents how charging is currently being controlled. The possible values are

* `SCHEDULED`
* `ON_DEMAND`

## Control Mode

`select.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_control_mode_select`

This represents, and can be used to change, whether the charger is being controlled automatically or manually. The possible values are

* `SMART`
* `MANUAL`

## LED Brightness

`number.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_led_brightness_number`

This represents, and can be used to change, the brightness of the charger's status LED, as a percentage between 0 and 100.

## Boost End Time

`sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_boost_end_time`

This represents when the current boost charge is due to end. This will be unavailable outside of an active boost charge.

## Live Power

`sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_live_power`

This represents the instantaneous power draw of the charger, in kW.

!!! info

    Unlike the other entities on this page, this one is push driven rather than polled - it opens a live connection to Octopus and streams readings as they arrive, only while the charger is actually `CHARGING` or `BOOST_CHARGING`. It closes the connection as soon as charging stops.

!!! note

    Since the connection is only opened/closed in response to the [operational state](#operational-state) sensor's own regular refresh, there can be up to a refresh interval's delay between charging actually starting or stopping and this sensor beginning or ending its updates.

## Schedule

`sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_schedule`

This represents a summary of the charger's configured weekly charging schedule. The full schedule (every day and period) is available in the sensor's attributes.

!!! note

    This is read only. Use the Octopus app to change your charger's schedule.

## Random Delay

`switch.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_random_delay_switch`

This represents, and can be used to turn on or off, random delay - a small random delay before charging starts to help smooth demand across the grid.

## Connected

`binary_sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_connected`

This determines if the charger is currently connected to the internet.

## Eco Mode

`switch.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_eco_mode_switch`

This represents, and can be used to turn on or off, eco mode.

## Away Mode

`switch.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_away_mode_switch`

This represents, and can be used to turn on or off, away mode.

## Cable Auto Lock

`switch.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_cable_auto_lock_switch`

This represents, and can be used to turn on or off, the charge cable auto lock.

!!! note

    This entity will only be available if your charger supports cable auto lock.

## Boost

`switch.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_boost_switch`

This can be used to start or stop a boost charge. Turning this on starts a boost charge for a fixed 1 hour duration; see the [boost end time](#boost-end-time) sensor for exactly when it'll finish.

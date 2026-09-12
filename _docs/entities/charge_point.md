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

This represents the instantaneous power draw of the charger, in kW. This will read `0` while the charger isn't actually charging.

!!! info

    Unlike the other entities on this page, this one is push driven rather than polled - it opens a live connection to Octopus and streams readings as they arrive, only while the charger is actually `CHARGING` or `BOOST_CHARGING`. It closes the connection as soon as charging stops.

!!! note

    Since the connection is only opened/closed in response to the [operational state](#operational-state) sensor's own regular refresh, there can be up to a refresh interval's delay between charging actually starting or stopping and this sensor beginning or ending its updates.

## Energy

`sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_energy`

This represents the charger's cumulative energy consumption, suitable for adding to the [Energy dashboard](https://www.home-assistant.io/docs/energy/individual-devices/).

!!! info

    Octopus's API doesn't provide a live cumulative energy reading for the charger - only a per-session total once a session has fully ended - so this is calculated by integrating the [live power](#live-power) sensor's own readings over time, the same approach Home Assistant's built-in "Integration - Riemann sum integral" helper uses.

!!! note

    This starts from 0 when the sensor is first created - there's no way to know your charger's actual historical lifetime total from the API, so it only reflects consumption from that point onward, not your charger's full lifetime usage.

## Schedule

`sensor.octopus_energy_charge_point_{{CHARGE_POINT_ID}}_schedule`

This represents a summary of the charger's configured weekly charging schedule. The full schedule (every day and period) is available in the sensor's attributes.

!!! note

    This is read only. Use the Octopus app to change your charger's schedule.

!!! info

    Every scheduled start/end time also arms a one-off timer that triggers the same fast burst-refresh as [boost](#boost) start/stop - so [operational state](#operational-state) and [live power](#live-power) pick up a scheduled charging transition quickly too, not just a manually-triggered one.

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

!!! info

    If you require boost to be on for a different amount of time, then you can use the [available service](../services.md#octopus_energyboost_charge_point).

!!! info

    Starting or stopping boost triggers a brief burst of much more frequent polling (every 10s for 60s), so [operational state](#operational-state) and [live power](#live-power) reflect the change quickly rather than waiting for the normal refresh interval.

## Services

There are some services available relating to these entities that you might find useful. They can be found in the [services docs](../services.md#charge-point).

# Wheel Of Fortune

To support the wheel of fortune that is awarded every month to customers.

A spins sensor is only created for a supply that has a meter on your account. For example, an electricity-only account will not have the gas spins sensor.

## Electricity Spins

`sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_electricity`

The number of spins remaining for electricity supply

## Gas Spins

`sensor.octopus_energy_{{ACCOUNT_ID}}_wheel_of_fortune_spins_gas`

The number of spins remaining for gas supply

## Services

There are some services available relating to these entities that you might find useful. They can be found in the [services docs](../services.md#wheel-of-fortune).
# 0002 - Intelligent Is Dispatching behavior changes

## Status
Accepted

## Context

The Octopus Intelligent feature was heavily based on an [existing integration](https://github.com/megakid/ha_octopus_intelligent), with [an original proposal from author](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/114). This resulted in the intelligent based entity behavior being identical to the existing integration.

Since inception, this integration has evolved and resulted in other sensors (i.e. [off peak](../entities/electricity.md#off-peak)) which have brought some inconsistencies in naming compared to behaviour (e.g. not turning on for **all** off peak times). Some of the intelligent sensors have also had inconsistencies in naming compared to behaviour (e.g. dispatching sensor turning on during standard off peak when the device isn't scheduled to be charged).

## Decision

The [Is Dispatching entity](../entities/intelligent.md#is-dispatching) will have its behaviour updated to only turn on when during a planned/scheduled dispatch period and the state of the intelligent device is in a "scheduled" mode.

The [Off peak entity](../entities/electricity.md#off-peak) will have its behaviour updated to turn on whenever an off peak rate is active. In the case of intelligent tariffs this will be during the standard off peak times (23:30-05:30 at time of writing) or when a planned/scheduled dispatch is active and the state of the intelligent device is in a "scheduled" mode.

## Consequences 

### Positive
- Expected behavior based on entity names, which will be easier for new users to understand
- Automations built around running off peak will continue to work as expected when moving from/to intelligent tariffs when using the off peak sensor with the new behaviour

### Negative
- Downstream integrations that rely on existing behavior will need to change
- Users using effected entities will need to update all references
- Some short-term disruption may occur as users adapt to the new entity behaviour. 
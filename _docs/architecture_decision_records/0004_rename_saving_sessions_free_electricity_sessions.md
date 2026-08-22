# 0004 - Rename saving sessions and free electricity sessions to power down and power up

## Status
Accepted

## Context

The integration provides sensors for Saving Sessions and Free Electricity Sessions. These have been renamed to power down and power up sessions respectively. Because of this the name of the provided sensors can bring confusion for newer Octopus Energy users. It can also provide confusion for existing Octopus Energy users who think the initiatives are new and that the integration doesn't provide functionality.

This has been driven from https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1759

## Decision

With new users coming on all of the time, it has been decided to provide new sensors with the new naming scheme.

The old sensors will continue to be available until **January 2027** when they will be removed, to ease with the transition.

Existing accounts will be notified of the change via a HA repair notice.

New accounts which are setup will only have access to the new sensors and will not receive the HA repair notice to avoid confusion to new users.

## Consequences 

### Positive
- Avoid confusion for users looking for power up/down functionality

### Negative
- Users using affected entities will need to update all references, including new blueprint references

# 0003 - Move to calendar entities for Octoplus events

## Status
Accepted

## Context

Currently binary sensors are provided to indicate when a saving or free electricity session is active for the current account. This also provides attributes for current and next start/end times.

Since the introduction of the saving session binary sensor, calendar entities have received more love within Home Assistant and become the preferred way of showing events. These are better supports in UI automations as you can offset calendar events easily (e.g. reminder 10 minutes before) without having to do template gymnastics. The calendar view of Home Assistant is also used by house hold members who are not as involved as other members in things like wall tablets. A few users move the data from the sensor data into a local calendar to produce this.

This request has been made on a few occasions, below are some samples

* https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/561#issuecomment-1826830172
* https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1397

## Decision

With more people coming on board to Home Assistant who don't necessarily come from a technological background, the automation UI becoming the preferred way of creating automations and the calendar entity getting more attention, it has been decided to convert the saving session and free electricity sessions into calendar entities.

The old sensors, `binary_sensor.octopus_energy_{{ACCOUNT_ID}}_octoplus_saving_sessions` and `binary_sensor.octopus_energy_{{ACCOUNT_ID}}_octoplus_free_electricity_session`, will continue to be available until **May 2026** when they will be removed, to ease with the transition.

## Consequences 

### Positive
- Automations around sessions will be easier via the calendar trigger
- Past and present sessions will be easily viewable in the Home Assistant Calendar view
- Standard approach for people used to calendar entities.

### Negative
- Users using effected entities will need to update all references
- Some short-term disruption may occur as users adapt to the new entity behaviour.
- Event duration (e.g. 60 minutes) will require templating still
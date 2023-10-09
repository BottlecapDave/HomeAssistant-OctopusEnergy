# Saving Sessions

To support Octopus Energy's [saving sessions](https://octopus.energy/saving-sessions/), the following entities are available

- [Saving Sessions](#saving-sessions)
  - [Saving Session Points](#saving-session-points)
  - [Saving Sessions](#saving-sessions-1)

## Saving Session Points

`sensor.octopus_energy_saving_session_points`

Supplies the points earned through the saving sessions

## Saving Sessions

`binary_sensor.octopus_energy_saving_sessions`

Binary sensor to indicate if a saving session that the account has joined is active. Also supplies the list of joined events including future events.

| Attribute | Type | Description |
|-----------|------|-------------|
| `joined_events` | `array` | The collection of saving sessions that you have joined |
| `next_joined_event_start` | `datetime` | The datetime the next saving session will start |
| `next_joined_event_end` | `boolean` | The datetime the next saving session will end |
| `next_joined_event_duration_in_minutes` | `float` | The duration in minutes of the next saving session |
# Entity IDs and names

Home Assistant generates entity IDs for electricity and gas meter entities using your configured entity naming scheme. The device name contains the meter identity, while the entity name contains the existing human-readable name with that device context removed.

For example:

| | Value |
|-|-|
| Device name | `Octopus Energy Electricity (A1B2C3/1234567890123)` |
| Entity name | `Current Rate` |
| Entity ID | `sensor.octopus_energy_electricity_a1b2c3_1234567890123_current_rate` |

Existing installations retain their registered entity IDs because the integration's unique IDs have not changed. Home Assistant generates a new entity ID only for a new entity, or when you explicitly use Home Assistant's `Recreate entity IDs` action.

With the `Device Entity` naming scheme, new and recreated entity IDs combine the meter device name with the entity-specific human-readable name. These IDs may differ from the historical IDs documented on the electricity and gas pages where the old display name and entity ID used different wording or word order.

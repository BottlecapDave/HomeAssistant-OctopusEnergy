# Blueprints

[Blueprints](https://www.home-assistant.io/docs/automation/using_blueprints/) are an excellent way to get you up and running with the integration quickly. Each blueprint will create a brand new automation which you can then adapt to your needs.

## Rates

### Alert when rates change

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fdevelop%2F_docs%2Fblueprints%2Foctopus_energy_rates_changed.yml) | [Source](./blueprints/octopus_energy_rates_changed.yml)

This blueprint will raise a persistent notification within HA when a rate updates.

## Octoplus

### Automatically join saving sessions

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fdevelop%2F_docs%2Fblueprints%2Foctopus_energy_octoplus_join_saving_session.yml) | [Source](./blueprints/octopus_energy_octoplus_join_saving_session.yml)

This blueprint will trigger when a new saving session has been discovered, join it, and send a notification alerting you to when it will start.

## Wheel of Fortune

### Automatically spin wheel of fortune (single)

[Install blueprint (single)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fdevelop%2F_docs%2Fblueprints%2Foctopus_energy_spin_wheel_of_fortune_single.yml) | [Source](./blueprints/octopus_energy_spin_wheel_of_fortune_single.yml)

This blueprint will trigger when the number of spins for a given energy source goes above zero, and will spin until the sensor reaches zero.

!!! warning

    Due to an ongoing issue with the underlying API, this will not award octopoints if used. If you are on Octoplus, it is advised not to use this blueprint.

### Automatically spin wheel of fortune (Dual)

[Install blueprint (single)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fdevelop%2F_docs%2Fblueprints%2Foctopus_energy_spin_wheel_of_fortune_dual.yml) | [Source](./blueprints/octopus_energy_spin_wheel_of_fortune_dual.yml)

This blueprint will trigger when either gas or electricity energy source spins are available, and will spin until the sensor reaches zero. This works as above, but combines both sensors into a single automation.

!!! info

    Due to the nature of this blueprint, you can't manually run this automation as it relies on triggers being present

!!! warning

    Due to an ongoing issue with the underlying API, this will not award octopoints if used. If you are on Octoplus, it is advised not to use this blueprint.
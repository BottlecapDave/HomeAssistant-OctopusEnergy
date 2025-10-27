# Blueprints

[Blueprints](https://www.home-assistant.io/docs/automation/using_blueprints/) are an excellent way to get you up and running with the integration quickly. They can also be used as a guide for setting up new automations which you can tailor to your needs. 

## Rates

### Alert when rates change

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_rates_changed.yaml) | [Source](./blueprints/octopus_energy_rates_changed.yaml)

This blueprint will raise a persistent notification within HA when a rate updates.

## Consumption

### Alert when gas anomaly detected

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_gas_anomaly.yaml) | [Source](./blueprints/octopus_energy_gas_anomaly.yaml)

This blueprint will fire a configured action when the consumption has 24 hours worth of records and all thirty minute periods exceed the configured threshold. This can be used to alert you to _potential_ gas leaks.

!!! warning

    Like everything else with this integration, this is provided _as is_ and should be used as a guide and early warning sign. It will only trigger if all data is available. If triggered, you should use your own judgment to determine if the warning is legitimate.

### Alert when consumption data is late

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_late_consumption_data.yaml) | [Source](./blueprints/octopus_energy_late_consumption_data.yaml)

This blueprint will fire a configured action when the latest available consumption data is x hours old, where x is configured via the blueprint.

## Octoplus

### Automatically join saving sessions

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_octoplus_join_saving_session.yaml) | [Source](./blueprints/octopus_energy_octoplus_join_saving_session.yaml)

This blueprint will trigger when a new saving session has been discovered, join it, and send a notification alerting you to when it will start.

If you wish to customise how the notification is delivered, you should install [this blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_octoplus_join_saving_session_custom_action.yaml) ([source](./blueprints/octopus_energy_octoplus_join_saving_session_custom_action.yaml))

### Automatically redeem Octoplus points for account credit

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_octoplus_redeem_points_for_account_credit.yaml) | [Source](./blueprints/octopus_energy_octoplus_redeem_points_for_account_credit.yaml)

This blueprint will automatically redeem all redeemable points for account credit when the number of redeemable points exceeds a configurable threshold.

!!! info

    This will only trigger when the redeemable points go from under the threshold to over. If it's already over the threshold, then the automation will not trigger. This is by [design of Home Assistant](https://www.home-assistant.io/docs/automation/trigger/#numeric-state-trigger).

    You can manually run the automation if the redeemable points is over the threshold to get it in a state where automatic redemption will happen in the future.

### Alert when current consumption is approaching saving sessions baseline

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_baseline_alert.yaml) | [Source](./blueprints/octopus_energy_baseline_alert.yaml)

This blueprint will fire a configured action when the consumption for the current interval (i.e. the current 30 minute period) reaches a configured percentage of the saving session baseline.

!!! warning

    This blueprint requires sensors provided by Octopus Energy Home Mini

### Alert when current consumption has reached free electricity sessions baseline

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_free_electricity_baseline_reached.yaml) | [Source](./blueprints/octopus_energy_free_electricity_baseline_reached.yaml)

This blueprint will fire a configured action when the consumption for the current interval (i.e. the current 30 minute period) reaches the current free electricity session baseline.

!!! warning

    This blueprint requires sensors provided by Octopus Energy Home Mini

## Intelligent

## Manual Intelligent Dispatch Refreshes

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_manual_intelligent_refresh.yaml) | [Source](./blueprints/octopus_energy_manual_intelligent_refresh.yaml)

This blueprint will fire the [intelligent dispatches service](./services.md#octopus_energyrefresh_intelligent_dispatches) either when a sensor from another integration determines the car has been plugged in (e.g. the plug status from the [MyEnergi integration](https://github.com/CJNE/ha-myenergi)) or when the data is stale and overdue a refresh (in case the dispatch information has changed).

!!! warning

    This blueprint requires you to be on an intelligent tariff and a way to determine that your car is plugged in from another integration.

## Wheel of Fortune

### Automatically spin wheel of fortune (single)

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_spin_wheel_of_fortune_single.yaml) | [Source](./blueprints/octopus_energy_spin_wheel_of_fortune_single.yaml)

This blueprint will trigger when the number of spins for a given energy source goes above zero, and will spin until the sensor reaches zero.

### Automatically spin wheel of fortune (Dual)

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_spin_wheel_of_fortune_dual.yaml) | [Source](./blueprints/octopus_energy_spin_wheel_of_fortune_dual.yaml)

This blueprint will trigger when either gas or electricity energy source spins are available, and will spin until the sensor reaches zero. This works as above, but combines both sensors into a single automation.

!!! info

    Due to the nature of this blueprint, you can't manually run this automation as it relies on triggers being present

## Cost Tracker

### Automatically update tracking (negative)

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_cost_tracker_negative.yaml) | [Source](./blueprints/octopus_energy_cost_tracker_negative.yaml)

This blueprint will automatically update the tracking state for the specified [cost tracker](./setup/cost_tracker.md) sensors when the monitored sensor goes negative.

### Automatically update tracking (positive)

[Install blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBottlecapDave%2FHomeAssistant-OctopusEnergy%2Fblob%2Fmain%2F_docs%2Fblueprints%2Foctopus_energy_cost_tracker_positive.yaml) | [Source](./blueprints/octopus_energy_cost_tracker_positive.yaml)

This blueprint will automatically update the tracking state for the specified [cost tracker](./setup/cost_tracker.md) sensors when the monitored sensor goes positive (including zero).

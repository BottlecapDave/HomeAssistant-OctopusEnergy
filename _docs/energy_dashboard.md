# Energy Dashboard

- [Energy Dashboard](#energy-dashboard)
  - [Current Consumption](#current-consumption)
    - [For Electricity](#for-electricity)
    - [For Gas](#for-gas)
  - [Previous Day Consumption](#previous-day-consumption)
    - [For Electricity](#for-electricity-1)
    - [For Gas](#for-gas-1)

## Current Consumption

### For Electricity

<img src="./assets/current_consumption_electricity.png" alt="HA modal electricity example" height="500">

This is only available if you have an Octopus Home Mini and a smart electricity meter.

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Consumption` under `Electricity Grid`
3. For `consumed energy` you want `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_consumption`
4. For `Use an entity with current price` option you want `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_rate`

> Please note that data will only appear in the energy dashboard from the point you configure the Home Mini within the integration. It doesn't backport any data.

### For Gas

<img src="./assets/current_consumption_gas.png" alt="HA modal gas example" height="500">

This is only available if you have an Octopus Home Mini and a smart gas meter.

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Gas Source` under `Gas Consumption`
3. For `consumed energy` you want `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_consumption`
4. For `Use an entity with current price` option you want `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_rate` 

> Please note that data will only appear in the energy dashboard from the point you configure the Home Mini within the integration. It doesn't backport any data.

## Previous Day Consumption

While you can add the `previous consumption` sensors to the dashboard, they will be associated with the wrong day. This is because the Energy dashboard uses the timestamp of when the sensor updates to determine which day the data should belong to.

Instead, you can use external statistics that are exported by the `previous consumption` sensors, which are broken down into hourly chunks. Please note it can take **up to 24 hours** for the external statistics to appear.

> Please note: I'm still investigating having hourly breakdowns imported on the entity themselves rather than as external statistics, but currently in doing so it's still including the spikes on the day of retrieval. I've opened a [forum post](https://community.home-assistant.io/t/help-needed-around-importing-historic-statistics/567726) but awaiting answers.

### For Electricity

<img src="./assets/previous_consumption_electricity.png" alt="HA modal electricity example" height="500">

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Consumption` under `Electricity Grid`
3. For `consumed energy` you want one of the following
* `octopus_energy:electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.
* `octopus_energy:electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_peak` - The total consumption reported by the meter for the previous day that applied during peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.
* `octopus_energy:electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_off_peak` - The total consumption reported by the meter for the previous day that applied during off peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.
1. For `Use an entity tracking the total costs` option you want one of the following
* `octopus_energy:electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day.
* `octopus_energy:electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_peak` - The total cost for the previous day that applied during peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.
* `octopus_energy:electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_off_peak` - The total cost for the previous day that applied during off peak hours. This is disabled by default. This will only be populated if you're on a tariff with two available rates.

### For Gas

<img src="./assets/previous_consumption_gas.png" alt="HA modal gas example" height="500">

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Gas Source` under `Gas Consumption`
3. For `consumed energy` you want one of the following
* `octopus_energy:gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day in m3. If your meter reports in m3, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value.
* `octopus_energy:gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_kwh` - The total consumption reported by the meter for the previous day in kwh. If your meter reports in kwh, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value.
4. For `Use an entity tracking the total costs` option you want the following
* `octopus_energy:gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day.

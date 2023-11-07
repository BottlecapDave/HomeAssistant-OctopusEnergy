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

You can only record current (i.e. today's) consumption in the Energy dashboard if you have a way of measuring live consumption in your home.

There are 4 possible ways to obtain this data:

#### 1. Octopus Home Mini

If you have an Octopus Home Mini and a smart electricity meter you can obtain live meter reading data into Home Assistant:

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Consumption` under `Electricity Grid`
3. For `consumed energy` you want `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_consumption` or `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_consumption`
4. For `Use an entity tracking the total costs` option you want `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_accumulative_cost`

<img src="./assets/current_consumption_electricity.png" alt="HA modal electricity example" height="500">

> Please note that data will only appear in the energy dashboard from the point you configure the Home Mini within the integration. It doesn't backport any data.

#### 2. Hildebrand Glow In Home Display

If you have a [Hildebrand Glow In Home Display](https://shop.glowmarkt.com/) and a smart meter you can retrieve live meter reading information in Home Assistant via local MQTT access - see this [Speak to the Geek article](https://www.speaktothegeek.co.uk/2022/06/hildebrand-glow-update-local-mqtt-and-home-assistant/) for setup instructions.

Setup in the Energy dashboard is very similar to that for the Octopus Home Mini, except that:

3. For `consumed energy` you want the name of the sensor you created to store the Hildebrand MQTT reading in, e.g. `sensor.smart_meter_electricity_energy_import`

#### 3. Hildebrand Glow DCC Integration

If you don't have a Hildebrand Glow IHD but do have a smart meter, you can still retrieve your daily consumption information from the central DCC smart meter database using the Hildebrand Glow API and the [Hildebrand Glow DCC Home Assistant integration](https://github.com/HandyHat/ha-hildebrandglow-dcc).  The data in the central DCC database is said to be delayed by 30 minutes but in practice has been seen to quite "lumpy" with big jumps in consumption throughout the day as meter reading updates feed through periodically into the central database.  Only a single daily consumption figure is provided so unless you are on a single daily flat rate consumption tariff this integration is not likely to be suitable for calculating daily costs.

3. The daily consumption is provided by `sensor.dcc_sourced_smart_electricity_meter_usage_today`

#### 4. Use an Energy Clamp or Inverter to measure Home Consumption

If you use an Energy CT Clamp such as the Shelly EM on the incoming supply cable you can feed live import and export energy information into Home Assistant. Or if you have an existing Solar/Battery inverter integrated into Home Assistant the inverter could well also have a sensor that provides Grid import information that you can use in the Energy dashboard.

Either of these approaches will also work regardless of whether you have a smart meter or not.

Do be aware that as you are not directly capturing the smart meter readings in Home Assistant there will always be a small measurement difference from what Octopus energy say you have used, but in practice the difference is likely to be quite small.

1. Create a utility meter to store the sensor information in.  Go to [Integrations dashboard](https://my.home-assistant.io/redirect/integrations/)
2. Click `Helpers` tab
3. Click `Create Helper` at the bottom right-hand corner
4. Choose `Utility Meter`
5. Enter a name for it, e.g. `Grid Import Today`
6. Choose the name of the sensor that is measuring your grid import. e.g. for a Shelly EM it will be `sensor.<EM channel name>_energy_total`; for a GivEnergy inverter using the GivTCP integration it will be `sensor.givtcp_XXyywwXnnn_import_energy_today_kwh`
7. For `Meter reset cycle` chose `Daily`
8. Click `Submit`
9. Then add the consumption information to the Energy dashboard as per the steps for Octopus Home Mini above.  For step 3, `consumed energy`, you want the utility meter you have just created above, e.g. `sensor.grid_import_today`

### For Gas

<img src="./assets/current_consumption_gas.png" alt="HA modal gas example" height="500">

This is only available if you have an Octopus Home Mini and a smart gas meter.

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Gas Source` under `Gas Consumption`
3. For `consumed energy` you want `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_consumption` or `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_accumulative_consumption`
4. For `Use an entity tracking the total costs` option you want `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_current_accumulative_cost` 

> Please note that data will only appear in the energy dashboard from the point you configure the Home Mini within the integration. It doesn't backport any data.

## Previous Day Consumption

If none of the methods above for feeding Current Day Consumption information into the Energy dashboard are suitable, you can add `previous consumption` sensors to the dashboard, using information retrieved via the Octopus API.  Note that the consumption information is only available on the following day so "today's" Energy dashboard will show zero values, but "yesterday's", "day before", etc will show the correct consumption for each day.

Beware: Whilst you can add the previous consumption sensors directly to the Energy dashboard, they will be associated with the wrong day. This is because the Energy dashboard uses the timestamp of when the sensor updates to determine which day the data should belong to.

Instead, you **must** use external statistics that are exported by the `previous consumption` sensors, which are broken down into hourly chunks. Please note it can take **up to 24 hours** for the external statistics to appear.

> Please note: I'm still investigating having hourly breakdowns imported on the entity themselves rather than as external statistics, but currently in doing so it's still including the spikes on the day of retrieval. I've opened a [forum post](https://community.home-assistant.io/t/help-needed-around-importing-historic-statistics/567726) but awaiting answers.

### For Electricity

<img src="./assets/previous_consumption_electricity.png" alt="HA modal electricity example" height="500">

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Consumption` under `Electricity Grid`
3. For `consumed energy` you want one of the following:
 * **`octopus_energy:`**`electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day.  **Please note the different name to the standard entity, do NOT choose sensor.electricity_{{METER}}_{{MPAN}}_previous_accumulative_consumption.**
 * **`octopus_energy:`**`electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_peak` - The total consumption reported by the meter for the previous day that applied during peak hours. This is [disabled by default](./faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.  **Please note the different name to the standard entity.**
 * **`octopus_energy:`**`electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_consumption_off_peak` - The total consumption reported by the meter for the previous day that applied during off peak hours. This is [disabled by default](./faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.  **Please note the different name to the standard entity.**
4. For `Use an entity tracking the total costs` option you want one of the following:
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day.
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_peak` - The total cost for the previous day that applied during peak hours. This is [disabled by default](./faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.
* `sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_previous_accumulative_cost_off_peak` - The total cost for the previous day that applied during off peak hours. This is [disabled by default](./faq.md#there-are-entities-that-are-disabled-why-are-they-disabled-and-how-do-i-enable-them). This will only be populated if you're on a tariff with two available rates.

### For Gas

<img src="./assets/previous_consumption_gas.png" alt="HA modal gas example" height="500">

1. Go to your [energy dashboard configuration](https://my.home-assistant.io/redirect/config_energy/)
2. Click `Add Gas Source` under `Gas Consumption`
3. For `consumed energy` you want one of the following
* `octopus_energy:gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption` - The total consumption reported by the meter for the previous day in m3. If your meter reports in m3, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value. **Please note the different name to the standard entity.**
* `octopus_energy:gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_consumption_kwh` - The total consumption reported by the meter for the previous day in kwh. If your meter reports in kwh, then this will be an accurate value reported by Octopus, otherwise it will be a calculated/estimated value. **Please note the different name to the standard entity.**
4. For `Use an entity tracking the total costs` option you want the following
* `sensor.octopus_energy_gas_{{METER_SERIAL_NUMBER}}_{{MPRN_NUMBER}}_previous_accumulative_cost` - The total cost for the previous day.

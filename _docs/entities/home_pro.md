# Home Pro

Entities to support the Home Pro device.

Once configured, the following entities will retrieve data locally from your Octopus Home Pro instead of via the Octopus Energy APIs at a target rate of every 10 seconds.

* [Electricity - Current Demand](./electricity.md#current-demand)
* [Electricity - Current Total Consumption](./electricity.md#current-total-consumption)
* [Gas - Current Total Consumption kWh](./gas.md#current-total-consumption-kwh)
* [Gas - Current Total Consumption m3](./gas.md#current-total-consumption-m3)

## Home Pro Screen

`text.octopus_energy_{{ACCOUNT_ID}}_home_pro_screen`

!!! info

    This is only available if you have setup the [Custom API](../setup/account.md#home-pro).

Allows you to set scrolling text on the home pro device. If the text is greater than 3 characters, then it will scroll on the device, otherwise it will be statically displayed.
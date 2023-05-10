# Community Contributions

- [Community Contributions](#community-contributions)
  - [Agile Price Table](#agile-price-table)
  - [Export Rates Chart](#export-rates-chart)

These are a few contributions by the community.

## Agile Price Table

If you're wanting to display upcoming prices in a nice readable format, then might I suggest you utilise the plugin developed by @lozzd available at https://github.com/lozzd/octopus-energy-rates-card.

## Export Rates Chart

Thanks to @fboundy you can use ApexCharts to plot the rates for the current day. After you have installed ApexCharts, you can use the following configuration

```yaml
type: custom:apexcharts-card
  header:
    show: true
    show_states: true
    colorize_states: true
    title: Agile Export Rates
  graph_span: 1d
  stacked: false
  span:
    start: day
  yaxis:
    - min: 0
      max: 35
      decimals: 1
  series:
    - entity: >-
        sensor.octopus_energy_electricity_{{METER_SERIAL_NUMBER}}_{{MPAN_NUMBER}}_current_rate
      type: column
      name: ''
      color: yellow
      opacity: 1
      stroke_width: 0
      unit: W
      show:
        in_header: false
        legend_value: false
      data_generator: |
        return entity.attributes.rates.map((entry) => {
           return [new Date(entry.from), entry.rate];
         });
      offset: '-15min'
```

which will produce something like the following...

![chart example](./assets/apex-chart.png)
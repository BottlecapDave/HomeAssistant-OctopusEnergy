# Community Contributions

- [Community Contributions](#community-contributions)
  - [Agile Price Table](#agile-price-table)
  - [Export Rates Chart](#export-rates-chart)
  - [Import And Export Rates Chart](#import-and-export-rates-chart)

These are a few contributions by the community.

## Agile Price Table

If you're wanting to display upcoming prices in a nice readable format, then might I suggest you utilise the [Octopus Engergy Rates card](https://github.com/lozzd/octopus-energy-rates-card).

<img src="https://github.com/lozzd/octopus-energy-rates-card/raw/main/assets/screenshot_1.png" height="300"/>

## Export Rates Chart

Thanks to @fboundy you can use [ApexCharts Card](https://github.com/RomRider/apexcharts-card) to plot the rates for the current day using the following configuration:

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

If you're looking for cost vs power using ApexCharts, then @plandregan has you covered:

```yaml
type: custom:apexcharts-card
experimental:
  color_threshold: true
header:
  show: true
  floating: true
  title: Cost vs Power
graph_span: 24h
show:
  last_updated: true
  loading: true
apex_config:
  legend:
    show: false
  chart:
    zoom:
      type: x
      enabled: true
      autoScaleYaxis: false
    toolbar:
      show: true
      autoSelected: zoom
    xaxis.type: datetime
  fill:
    type: gradient
    gradient:
      shadeIntensity: 0.1
      opacityFrom: 0.3
      opacityTo: 1
      inverseColors: true
series:
  - entity: sensor.octopus_energy_electricity_xxxxxxxxxxxx_xxxxxxxxxxxx_current_rate
    transform: return x * 100;
    type: area
    name: GBP/kWh
    yaxis_id: pence
    color: lightblue
    group_by:
      func: avg
      duration: 5m
    stroke_width: 2
    extend_to: now
    show:
      extremas: false
      header_color_threshold: true
  - entity: sensor.givtcp_xxxxxxxxxxxx_grid_power
    transform: return x /1000;
    type: line
    invert: true
    name: Power
    yaxis_id: kwh
    group_by:
      func: avg
      duration: 5m
    color: red
    stroke_width: 2
    extend_to: now
yaxis:
  - id: pence
    min: 0
    max: 35
    opposite: false
  - id: kwh
    min: 0
    max: 10
    opposite: true
```

which will produce something like the following...

![chart example](./assets/apex-chart-power-vs-cost.png)

## Import and Export Rates Chart

If you're looking to combine import and export rates then create a card with the configuration:


```yaml
type: custom:config-template-card
entities:
  - sensor.octopus_energy_electricity_21l4726127_2000021792976_current_rate
  - >-
    sensor.octopus_energy_electricity_21l4726127_2000060201274_export_current_rate
card:
  card_mod:
    style: |
      ha-card {
        --secondary-text-color: rgb(225,225,225)
      }
  type: custom:apexcharts-card
  show:
    loading: false
  color_list:
    - orange
    - green  
  header:
    title: Electricity tariffs with Octopus
    show: true
    show_states: true
    colorize_states: true
  span:
    start: day
  graph_span: 48h
  update_interval: 30mins
  all_series_config:
    type: area
    float_precision: 4
    extend_to: now
    stroke_width: 2
    fill_raw: 'null'
  series:
    - entity: sensor.octopus_energy_electricity_21l4726127_2000021792976_current_rate
      name: Import
      curve: stepline
      data_generator: |
        return entity.attributes.rates.map((entry) => {
          return [new Date(entry.from), entry.rate/100];
        });
    - entity: >-
        sensor.octopus_energy_electricity_21l4726127_2000060201274_export_current_rate
      name: Export
      curve: stepline
      data_generator: |
        return entity.attributes.rates.map((entry) => {
          return [new Date(entry.from), entry.rate/100];
        });
  apex_config:
    tooltip:
      x:
        format: ddd dd MMM - HH:mm
    xaxis:
      axisBorder:
        show: false
      tooltip:
        enabled: false
    grid:
      borderColor: '#7B7B7B'
    legend:
      show: false
      toolbar:
        show: true
        autoSelected: zoom
        tools:
          zoom: true
          zoomin: false
          zoomout: false
          pan: false
          reset: true
    annotations:
      xaxis:
        - x: ${ new Date().setHours(24,0,0,0) }
          label:
            text: Tomorrow
        - x: ${Date.now()}
          label:
            text: Now
            borderColor: '#00E396'
            style:
              color: '#fff'
              background: '#00E396'
            borderWidth: 0
    yaxis:
      min: 0
      max: 0.4
      tickAmount: 4
      labels:
        formatter: |
          EVAL:function (val) {
           return "£" + val.toFixed(2);
          }
      forceNiceScale: true
    chart:
      height: 150
      foreColor: '#7B7B7B'
      zoom:
        type: x
        enabled: true
        autoScaleYaxis: true
```

to generate this card:

![Chart example](./assets/apex-chart-tariffs.png)

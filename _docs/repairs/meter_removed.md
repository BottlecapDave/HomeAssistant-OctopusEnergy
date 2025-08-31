# Repairs - Meter removed

The integration regularly updates the account information. As part of this update, it checks if meters have changed since the last update. A meter can be deemed as "removed" for one of two reasons.

1. The meter is no longer part of your account
2. The meter no longer has an active tariff associated with it

If this is expected (e.g. you've had your meter replaced), then you can ignore this notification. If this is not expected, then continue.

## Troubleshooting removed meter

The best way to determine why this has occurred is to [download the diagnostics](../faq.md#ive-been-asked-for-my-meter-information-in-a-bug-request-how-do-i-obtain-this) for your meter. Once downloaded, it will look something like the following

```json
{
  ...
  "data": {
    "timestamp_captured": "2025-08-31T06:48:05.188073+01:00",
    "account": {
      "id": "**REDACTED**",
      "octoplus_enrolled": true,
      "heat_pump_ids": [],
      "electricity_meter_points": [
        {
          "mpan": 2,
          "meters": [
            {
              "active_from": {
                "__type": "<class 'datetime.date'>",
                "isoformat": "2000-01-01"
              },
              "active_to": null,
              "serial_number": 1,
              "is_export": false,
              "is_smart_meter": true,
              "device_id": "**REDACTED**",
              "manufacturer": "xxx",
              "model": "xxx",
              "firmware": "xxx",
              "latest_consumption": "2025-08-30T00:00:00+00:00",
              "device": {
                "total_consumption": 31221.6,
                "consumption": 0.1,
                "demand": 251.0,
                "start": "2025-08-31T05:30:00+00:00",
                "end": "2025-08-31T06:00:00+00:00"
              }
            }
          ],
          "agreements": [
            {
              "start": "2000-01-01T23:00:00+00:00",
              "end": "2001-01-01T23:00:00+00:00",
              "tariff_code": "E-1R-SUPER-GREEN-24M-21-07-30-L",
              "product_code": "SUPER-GREEN-24M-21-07-30"
            },
            ...
          ]
        }
      ],
      "gas_meter_points": [
        {
          "mprn": 4,
          "meters": [
            {
              "active_from": {
                "__type": "<class 'datetime.date'>",
                "isoformat": "2021-08-16"
              },
              "active_to": null,
              "serial_number": 3,
              "consumption_units": "m\u00b3",
              "is_smart_meter": true,
              "device_id": "**REDACTED**",
              "manufacturer": "xxx",
              "model": "xxx",
              "firmware": "xxx",
              "latest_consumption": "2025-08-30T00:00:00+00:00",
              "device": {
                "total_consumption": 150664.71746,
                "consumption": 0.0,
                "demand": null,
                "start": "2025-08-31T05:30:00+00:00",
                "end": "2025-08-31T06:00:00+00:00"
              }
            }
          ],
          "agreements": [
            {
              "start": "2000-01-01T23:00:00+00:00",
              "end": "2001-01-01T23:00:00+00:00",
              "tariff_code": "G-1R-SUPER-GREEN-24M-21-07-30-L",
              "product_code": "SUPER-GREEN-24M-21-07-30"
            },
            ...
          ]
        }
      ]
    },
    "using_cached_account_data": true,
    ...
  },
  ...
}
```

The meter MPAN/MPRN and Serial numbers are automatically changed to numbers for PII purposes, so you will need to find you meter either by it's active date or the manufacturer/model.

If the meter is no longer present or there is no active agreement, then you'll need to contact Octopus Energy to get this fixed. Otherwise, please raise an [issue](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues) with the diagnostic data and any associated errors in your logs to try and fix the problem.
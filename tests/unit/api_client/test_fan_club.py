from custom_components.octopus_energy.api_client.fan_club import FanClubResponse

def test_when_valid_dictionary_returned_then_it_can_be_parsed_into_fan_club_object():
  # Arrange
  data = {
    "fanClubStatus": [
      {
        "discountSource": "#1 Fan: Market Weighton - Carr Farm",
        "current": {
            "startAt": "2023-11-19T22:08:00.300415+00:00",
            "discount": "0.500"
        },
        "historic": [
          {
              "startAt": "2023-11-19T21:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T21:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T20:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T20:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T19:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T19:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T18:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T18:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T17:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T17:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T16:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T16:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T15:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T15:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T14:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T14:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T13:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T13:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T12:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T12:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T11:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T11:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T10:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T10:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T09:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T09:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T08:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T08:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T07:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T07:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T06:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T06:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T05:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T05:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T04:30:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-19T04:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T03:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T03:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T02:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T02:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T01:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T01:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T00:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-19T00:00:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-18T23:30:00+00:00",
              "discount": "0.500"
          },
          {
              "startAt": "2023-11-18T23:00:00+00:00",
              "discount": "0.200"
          },
          {
              "startAt": "2023-11-18T22:30:00+00:00",
              "discount": "0.200"
          }
        ],
        "forecast": {
            "baseTime": "2023-11-19T12:00:00+00:00",
            "data": [
              {
                  "validTime": "2023-11-19T23:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T00:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T01:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T02:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T03:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T04:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T05:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T06:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T07:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T08:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T09:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T10:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T11:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T12:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T13:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T14:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T15:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T16:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T17:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T18:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T19:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T20:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T21:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T22:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-20T23:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T00:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T01:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T02:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T03:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T04:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T05:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T06:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T07:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T08:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T09:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T10:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T11:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T12:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T13:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T14:00:00+00:00",
                  "projectedDiscount": "0.200"
              },
              {
                  "validTime": "2023-11-21T15:00:00+00:00",
                  "projectedDiscount": "0.000"
              },
              {
                  "validTime": "2023-11-21T16:00:00+00:00",
                  "projectedDiscount": "0.000"
              },
              {
                  "validTime": "2023-11-21T17:00:00+00:00",
                  "projectedDiscount": "0.000"
              },
              {
                  "validTime": "2023-11-21T18:00:00+00:00",
                  "projectedDiscount": "0.000"
              },
              {
                  "validTime": "2023-11-21T19:00:00+00:00",
                  "projectedDiscount": "0.000"
              },
              {
                  "validTime": "2023-11-21T20:00:00+00:00",
                  "projectedDiscount": "0.000"
              },
              {
                  "validTime": "2023-11-21T21:00:00+00:00",
                  "projectedDiscount": "0.000"
              },
              {
                  "validTime": "2023-11-21T22:00:00+00:00",
                  "projectedDiscount": "0.000"
              }
            ]
          }
      }
    ]
  }

  # Act
  result = FanClubResponse.parse_obj(data)

  # Assert
  assert result is not None

def test_when_forecast_is_none_then_it_can_be_parsed_into_fan_club_object():
  # Arrange
  input = {"data": {"fanClubStatus": [{"discountSource": "#1 Fan (GBR): Carr Farm", "current": {"startAt": "2025-05-27T09:44:00.187014+00:00", "discount": "0.000"}, "historic": [{"startAt": "2025-05-27T09:00:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T08:30:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T08:00:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T07:30:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T07:00:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T06:30:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T06:00:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T05:30:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T05:00:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T04:30:00+00:00", "discount": "0.200"}, {"startAt": "2025-05-27T04:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T03:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T03:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T02:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T02:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T01:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T01:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T00:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-27T00:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T23:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T23:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T22:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T22:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T21:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T21:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T20:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T20:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T19:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T19:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T18:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T18:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T17:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T17:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T16:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T16:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T15:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T15:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T14:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T14:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T13:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T13:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T12:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T12:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T11:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T11:00:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T10:30:00+00:00", "discount": "0.500"}, {"startAt": "2025-05-26T10:00:00+00:00", "discount": "0.500"}], "forecast": None}]}}

  # Act
  result = FanClubResponse.parse_obj(input["data"])

  # Assert
  assert result is not None
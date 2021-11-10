# [2.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v1.2.0...v2.0.0) (2021-11-10)


### Bug Fixes

* **api-client:** fixed get_account to find the first property that hasn't been moved out of ([970a7a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/970a7a58bdb00504b2c922d6e0a4632e71d9a17f))


### BREAKING CHANGES

* **api-client:** This change could cause the sensors associated with your meters to change, as they may have been
associated with a property you had moved out of

# [1.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v1.1.0...v1.2.0) (2021-10-30)


### Bug Fixes

* Updated how we determine if we're on an expired fixed tariff ([075766f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/075766f3ece1a021c889ab0032cd807c028e9300))


### Features

* Updated to move to variable tariffs if a meter's latest agreement was fixed term ([37ee143](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/37ee143737458ec3ead08d43bfb6b2cfed8680cc))

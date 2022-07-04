# [4.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.2.1...v4.3.0) (2022-07-04)


### Bug Fixes

* **api-client:** Updated get_account to use graphql so that inactive meters are ignored ([f05dcd9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f05dcd9e326c11c4e82ada503d9aceb2841b5738))
* **sensor:** Fixed gas sensor ([975f4fe](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/975f4fe1c03648b6cca44ae63480a739cafd7ebf))
* Updated translations to not include title as not needed ([43d1a0e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/43d1a0e5e2df6391418a557b4228bf1a379d80ee))


### Features

* **sensor:** Added rate information to current electricity rate sensor ([cfb4043](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cfb40433a5aa002944b6e16650a10499e57611b0))
* **sensor:** Updated electricity and gas sensors to be associated with devices ([38d8adb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/38d8adb18a5ca8d6ba0f0cd14fcea9bf14ea917b))

## [4.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.2.0...v4.2.1) (2022-06-18)


### Bug Fixes

* Fixed incorrect logging for debugging entries ([d5fad1d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d5fad1dbcd182e184063281152f2cb2b98aed49a))
* **sensor:** Fixed issue where gas consumption was being incorrectly calculated for SMETS1 sensors ([065ec88](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/065ec88df8758738bae41a14bb5b309968e956a0))

# [4.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.3...v4.2.0) (2022-05-07)


### Features

* **binary_sensor:** Updated target rate sensors to be updatable ([a6fbcca](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a6fbccad237c3d9d2294ba11a7e8029e78cb0bdb))
* **binary-sensor:** Added ability to apply offsets to target rate sensors ([faafa1b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/faafa1bdbe3434d571bc56761ff0efc9b3f58adc))
* **sensor:** Moved targeting sensor update logic to external functions ([74908e1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/74908e1f9bc06284178bbfba304be777bd54259d))
* **sensor:** Updated sensor icons to be gbp instead of usd ([66dfc54](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66dfc54a0e8b745472b7f24a4995fed89f028e94))

## [4.1.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.2...v4.1.3) (2022-03-23)


### Bug Fixes

* **sensor:** Fixed issue where active agreement was not being found, causing sensors to not appear ([85acdac](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/85acdacf7ba50bb65cd8512f14c1d4a118a11dfa))

## [4.1.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.1...v4.1.2) (2022-03-22)


### Bug Fixes

* **sensor:** More fixes to sensor logging. ([b0c4213](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b0c4213be7372480a7aef260d7fe711e15156211))

## [4.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.1.0...v4.1.1) (2022-03-22)


### Bug Fixes

* **sensor:** Fixed log when no active agreement present ([75af243](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/75af2439988c4090439c598b397db139f1e0132c))

# [4.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.0.0...v4.1.0) (2022-03-22)


### Features

* **sensor:** added info logs to indicate why sensors aren't added ([cc3fbeb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cc3fbebf413ef18397f604536f867af71a0205a2))

# [4.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.1.0...v4.0.0) (2022-03-07)


### Bug Fixes

* Fixed support for meters that both import and export electricity (Thanks [@696](https://github.com/696)GrocuttT) ([1391dc8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1391dc83fc23000d434dda70ea8fdd802721ef59))


### Features

* **config:** Updated selecting target meters for target sensors to be more user friendly ([b1dc00f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b1dc00f49db4a225de2c66317a1e9b45800dc145))
* **sensor:** Added tariff code to electricity and gas consumption sensors ([a728652](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a72865291a18e3d9cb38ecfa3ae7455b4339d216))
* **sensor:** Updated electricity sensors to include is_export attribute ([d35967e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d35967ed0b51474b4d23111f038bd613147b5e41))
* **sensor:** updated gas sensors to include mprn in name ([af528ef](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/af528efa98d99e46675f83fbc7214b960fbf474f))
* **sensor:** Updated previous gas consumption to display kwh and m3 values in attributes ([745c51f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/745c51f1c92e312b6cf55f8583acc36cccfd8700))


### BREAKING CHANGES

* **sensor:** This has been updated for consistency with the electricity sensor changes
* Unfortunately in order to support import/exports, electricity sensors now include both the mpan and serial number in their name. This means you will need to update any automations or dashboards that rely on these sensors.

# [3.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.4...v3.1.0) (2022-01-15)


### Bug Fixes

* **sensors:** Fixed current gas rate period to be for the day ([7a62150](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7a62150881f326904e181366f611614a01fcc31b))


### Features

* **sensor:** added current gas rate sensor ([ecfe774](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ecfe774190da1d6c80e969f7a024d29242add2aa))

## [3.0.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.3...v3.0.4) (2022-01-01)


### Bug Fixes

* **sensor:** Updated consumption to not require 48 entries ([9bd6790](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9bd6790f05c4fd6bf1a44cbe0cf9433f00050d3d))
* **sensor:** Updated sensors to not require 48 entries for consumption ([15fd45c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/15fd45c8df2f0b1964af13b34a5cd125c481dd07))

## [3.0.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.2...v3.0.3) (2022-01-01)


### Bug Fixes

* **api-client:** fixed retrieving rates for agile and go tariffs ([9a12ac5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9a12ac506ee5f9d4f9de71082e5ebd0ba4658d28))
* **api-client:** updated to treat server errors as not receiving any data ([c111463](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c11146311a72bdf05bb555082fb27ad1e784c434))

## [3.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.1...v3.0.2) (2021-12-28)


### Bug Fixes

* **api-client:** Added additional logging for failing to read json response ([fa3b33d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fa3b33de7990c53842d9fd862af5be860028a7b2))
* **sensor:** Added more logging around failing to retrieve consumption rate. ([dbec7a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dbec7a5fc88b157ee01288bd09b1787b3dd8f02e))

## [3.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v3.0.0...v3.0.1) (2021-12-23)


### Bug Fixes

* **sensor:** updated tariff code in sensor setup to be retrieved after it's been setup in the rate coordinator ([9caade9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9caade91eac4ff14a785bc4d5c1ec455ec047bba))

# [3.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v2.0.0...v3.0.0) (2021-12-22)


### Bug Fixes

* **sensor:** Removed code for falling back on fixed tariffs if no agreement is found ([9a5045b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9a5045bca5746e6fb289dda1616f795716e9fad1))


### Features

* **sensor:** Added sensors for accumulative cost of gas for the previous day ([42a1408](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/42a140827a4fc03694a5cc2d1fcaea31010003b5))
* **sensor:** Created coordinator for retrieving current reading and created initial electricity consumption cost ([4f09269](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4f092694a7a53040b2364ffb6cc74cbf8a6cff57))
* **sensor:** removed current consumption sensors due to insufficient data provided by Octopus Energy ([0470ff3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0470ff38c88f1bc480bbe949fed05f4bf16bf57b))
* **sensor:** Removed registering of current consumption sensors ([d263a68](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d263a6889d907506c6f797329e18c7ac14377b75))
* **sensor:** Updated previous day consumption to only be valid if enough data points are available ([9e71ef2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9e71ef28481cd5074ae0a1c4281c4e4166d87d0e))
* **sensor:** Updated previous day cost sensor to include breakdown and standing charges ([6618246](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66182462a8d23cde7ce745ddfcb3543e7920fe68))
* updated docs ([dff4d16](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dff4d16895025799364fd0ab00815c95e87150d8))


### BREAKING CHANGES

* We no longer fall back to fixed rate agreements if an active agreement can't be found. This was
added by mistake when people were not receiving sensors when they had moved home and therefore an
inactive house was being picked up. This means that some sensors may disapper, but these should just
be inactive meters.
* **sensor:** Latest consumption sensors are no longer available, which may cause issues anywhere they are used.

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

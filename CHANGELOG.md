## [17.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.1.0...v17.1.1) (2025-10-31)


### Bug Fixes

* Fixed blocking loop error for greener nights ([492afdf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/492afdfd999669001b189989d2e4d98aeded16a9))
* Fixed issue with heat pump zones where changing hvac mode incorrectly set temperature (15 minutes dev time) ([8baa4f1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8baa4f11d987d0bfd789aa3286116c123d75e9db))

# [17.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.3...v17.1.0) (2025-10-27)


### Bug Fixes

* Fixed issue where free electricity/saving session calendar next event was not resetting properly (5 minutes dev time) ([38e9e34](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/38e9e34787a3fb3e1925324b8be6a240804f4c3c))


### Features

* Added calendar entity for highlighted greener nights (1 hour dev time) ([24c25a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/24c25a506767f91e51ac4bc82b204451250956f6))
* Added service/action for retrieveing intelligent dispatches applicable at a given point in time via local data. This is useful to determine why off peak or dispatch sensors might have turned on (4.5 hours dev time) ([b803abb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b803abbfcab197804f4e4591457dc4f160c34b4b))
* Updated greenness forecast to use newer greener nights API (1 hour dev time) ([bafdb0d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bafdb0d266daebf862b45e8811b3ce5f8631e59b))

## [17.0.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.2...v17.0.3) (2025-10-23)


### Bug Fixes

* Fixed issue with saving config home mini settings are not enabled (15 minutes dev time) ([76f7dd6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/76f7dd6f490391f145f820582bf5c5923fdc9c82))

## [17.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.1...v17.0.2) (2025-10-18)


### Bug Fixes

* Fixed issue loading cached intelligent devices if they can't be retrieved live (5 minutes dev time) ([ecca499](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ecca499fe1088f481e055f59174cedef5ad96be2))

## [17.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.0...v17.0.1) (2025-10-15)


### Bug Fixes

* Reverted change to electricity and gas rate sensors to be measurements classes to match rate sensors in other native integrations and provide min/max/average stats. This is forcing some users to delete historic data for long term statistics to work. I'll try and bring back this feature in the future in some capacity. ([60672f4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/60672f4ee1d92ea866ee711a74563eba56ab1680))

# [17.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.3.1...v17.0.0) (2025-10-12)


### blueprints

* Updates extention of blueprints (Thanks [@reedy](https://github.com/reedy)) ([9f3ae03](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9f3ae03d76d7992d4f1787dbe3c269a5bd794508))


### Bug Fixes

* Added missing translations for event entities (30 minutes dev time) ([7af2561](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7af25619e57c8e81316168c381c4ad03e65a4410))
* Fixed diagnostics and intelligent devices not loading ([86f024b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/86f024bd95db64bb23ab85c983ba830d7dfe89f5))
* Fixed diagnostics not providing export data for home mini (15 minutes dev time) ([979bc31](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/979bc319408caf1b7e84cbd886f79555c02f2057))
* Fixed intelligent device type (5 minutes dev time) ([b06bdc0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b06bdc0fb9ba3add276ce5d76a1ea529e3685d1d))
* Fixed issue where intelligent maximum hourly calls check was being checked when data wasn't due to be refreshed ([fd74794](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd74794d508548f071d1ceb1f16065cbdb020103))
* Fixed issue where off peak rates flipped when multiple dispatch sources exist where one source is active and one isn't (1 hour dev time) ([72c2965](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/72c29651bf421a5934f02c988aadc0e865e1f91d))
* Fixed repair issues to obfuscate PII information from the key (1.5 hours dev time) ([13d2f42](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/13d2f42e8903030931aca4a0fd1e8c634c8a5c82))
* Incorrect number of arguments to async_create_issue ([0ad38cf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ad38cfba6a2d89a552085432302136b7689fd6d)), closes [#1479](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1479) (Thanks @TCWORLD)
* Updated cost trackers to handle entities with non-string unique_ids (Thanks [@dpwood](https://github.com/dpwood)) ([5c32d16](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5c32d16ca0084dc76da363bba7d8e16340454787))
* Updated heat pump water heater to use valid state to represent 'on' (30 minutes dev time) ([ae0b73d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ae0b73d839d348b96657f63e1ae10e01c591b577))
* Updated minimum hacs version to 2025.1 (Thanks @johncuthbertuk) ([fa77457](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fa774577007ee17df21ac488a6679b9f46bbe3b3))


### Features

* Added attribute to dispatch entity to determine if manual refreshing of dispatches is enabled (10 minutes dev time) ([6f4d5e4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6f4d5e4e3f9c493177b7660d3c80f647c3496164))
* Added calendars for representing free electricity and saving sessions. Existing binary sensors have been deprecated. See repair notice for more information (2 hours 15 mins dev time) ([5a1441a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5a1441a24c88b1d07bbf80c3ac00cb6d23f9b8d2))
* Added free electricity and saving session sensors to octoplus service device for easier discovery (30 minutes dev time) ([ef0f3c1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ef0f3c14fc9f562e352a1c5fc5e8a38cc60328a9))
* Added repair notice when no rates are retrievable (1.5 hours dev time) ([1dca50b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1dca50b124a30e74e9c2581c01ce974876c62de6))
* Added support for multiple EVs (6 hours 5 minutes dev time) ([1c2c3a9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1c2c3a967f4208a45daa53f5f57c2e002f63a381))
* Attached intelligent diagnostic sensors to intelligent device (15 minutes dev time) ([b0ca7d1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b0ca7d11c6f76a69921fb5f6b0ad542d6ccf634e))
* Updated dispatches diagnostics sensor to include maximum_requests_per_hour (15 minutes dev time) ([a48d7ce](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a48d7cea2f64e73ceb737e58515b81f60e82b1d4))
* Updated electricity and gas rate sensors to be measurements classes to match rate sensors in other native integrations and provide min/max/average stats (30 minutes dev time) ([4a7305e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4a7305e7924ba483357d95ba6e75d3cd053ee7f9))
* Updated electricity/gas/heat pump/octoplus diagnostic entities so they're attached to the correct devices (1 hour dev time) ([#1497](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1497)) ([2ce05ed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2ce05ed738c0ad3c6c71776fd7c1b73058e7de29))
* Updated off peak sensor to come on when intelligent devices are dispatching (30 minutes dev time) ([18e3eca](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/18e3eca01e21c9d63d0b30b78d01c70807bde5dd))
* Updated raised errors for heat pump and intelligent controls to be more user friendly (2 hours dev time) ([e60ce63](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e60ce637641dc1d570602aa3121d79b79b69092a))


### BREAKING CHANGES

* off_peak entity will now turn on during standard off peak rates as well as ad hoc scheduled
dispatches when on intelligent tariff. This is because the naming and behaviour was confusing (off
peak not turning on when in an ad-hoc off peak period). See
https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/architecture_decision_records/0002_intelligent_is_dispatching_behaviour_changes
for full details.
* Intelligent device related entity ids have been changed from including the account id to including the device id. This is to support multiple EVs as well as other future intelligent devices OE might want to add in the future (e.g. Snug)
* is_dispatching entity will now only show when the car is within a scheduled dispatching period. It will no longer turn on when within the standard off peak period. This is because the naming and behaviour was confusing with the name (on when it's not dispatching) and behavior in conjunction with the off peak sensor (off peak not turning on when in an ad-hoc off peak period). See https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/architecture_decision_records/0002_intelligent_is_dispatching_behaviour_changes for full details.
* If you are using blueprints provided by this integration, you will need to re-import them and potentially update automations in order to continue receiving updates. Please note the extensions for blueprints have changed from `.yml` to `.yaml`
* If you have automations that look at the heat pump water heater, then you'll need to update any reference to the state of 'on' to 'electric'
* Due to repair issue key structure changing, you may receive repair notices that you have previously ignored. You will need to ignore them again to hide them.

# [17.0.0-beta.5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.0-beta.4...v17.0.0-beta.5) (2025-10-07)


### Bug Fixes

* Added missing translations for event entities (30 minutes dev time) ([7af2561](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7af25619e57c8e81316168c381c4ad03e65a4410))
* Updated cost trackers to handle entities with non-string unique_ids (Thanks [@dpwood](https://github.com/dpwood)) ([5c32d16](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5c32d16ca0084dc76da363bba7d8e16340454787))


### Features

* Added calendars for representing free electricity and saving sessions. Existing binary sensors have been deprecated. See repair notice for more information (2 hours 15 mins dev time) ([5a1441a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5a1441a24c88b1d07bbf80c3ac00cb6d23f9b8d2))
* Added free electricity and saving session sensors to octoplus service device for easier discovery (30 minutes dev time) ([ef0f3c1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ef0f3c14fc9f562e352a1c5fc5e8a38cc60328a9))
* Attached intelligent diagnostic sensors to intelligent device (15 minutes dev time) ([b0ca7d1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b0ca7d11c6f76a69921fb5f6b0ad542d6ccf634e))
* Updated electricity and gas rate sensors to be measurements classes to match rate sensors in other native integrations and provide min/max/average stats (30 minutes dev time) ([4a7305e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4a7305e7924ba483357d95ba6e75d3cd053ee7f9))
* Updated electricity/gas/heat pump/octoplus diagnostic entities so they're attached to the correct devices (1 hour dev time) ([af0c285](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/af0c285675aebd10085f3d65b4f6c4897d9b4f34))
* Updated electricity/gas/heat pump/octoplus diagnostic entities so they're attached to the correct devices (1 hour dev time) ([#1497](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1497)) ([2ce05ed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2ce05ed738c0ad3c6c71776fd7c1b73058e7de29))

# [17.0.0-beta.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.0-beta.3...v17.0.0-beta.4) (2025-09-28)


### Bug Fixes

* Fixed issue where intelligent maximum hourly calls check was being checked when data wasn't due to be refreshed ([fd74794](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd74794d508548f071d1ceb1f16065cbdb020103))


### Features

* Updated dispatches diagnostics sensor to include maximum_requests_per_hour (15 minutes dev time) ([a48d7ce](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a48d7cea2f64e73ceb737e58515b81f60e82b1d4))

# [17.0.0-beta.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.0-beta.2...v17.0.0-beta.3) (2025-09-24)


### Bug Fixes

* Fixed intelligent device type (5 minutes dev time) ([b06bdc0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b06bdc0fb9ba3add276ce5d76a1ea529e3685d1d))
* Fixed issue where off peak rates flipped when multiple dispatch sources exist where one source is active and one isn't (1 hour dev time) ([72c2965](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/72c29651bf421a5934f02c988aadc0e865e1f91d))
* Incorrect number of arguments to async_create_issue ([0ad38cf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ad38cfba6a2d89a552085432302136b7689fd6d)), closes [#1479](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1479)

# [17.0.0-beta.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v17.0.0-beta.1...v17.0.0-beta.2) (2025-09-21)


### Bug Fixes

* Fixed diagnostics and intelligent devices not loading ([86f024b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/86f024bd95db64bb23ab85c983ba830d7dfe89f5))

# [17.0.0-beta.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.3.1...v17.0.0-beta.1) (2025-09-21)


### blueprints

* Updates extention of blueprints (Thanks [@reedy](https://github.com/reedy)) ([9f3ae03](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9f3ae03d76d7992d4f1787dbe3c269a5bd794508))


### Bug Fixes

* Fixed repair issues to obfuscate PII information from the key (1.5 hours dev time) ([13d2f42](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/13d2f42e8903030931aca4a0fd1e8c634c8a5c82))
* Updated heat pump water heater to use valid state to represent 'on' (30 minutes dev time) ([ae0b73d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ae0b73d839d348b96657f63e1ae10e01c591b577))
* Updated minimum hacs version to 2025.1 ([fa77457](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fa774577007ee17df21ac488a6679b9f46bbe3b3))
* Updated minimum hacs version to 2025.1 ([#1465](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1465)) ([39b9032](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/39b90320eedb1edf164919ae6bf6820cfe1e4c73))


### Features

* Added attribute to dispatch entity to determine if manual refreshing of dispatches is enabled (10 minutes dev time) ([6f4d5e4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6f4d5e4e3f9c493177b7660d3c80f647c3496164))
* Added repair notice when no rates are retrievable (1.5 hours dev time) ([1dca50b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1dca50b124a30e74e9c2581c01ce974876c62de6))
* Added support for multiple EVs (6 hours 5 minutes dev time) ([1c2c3a9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1c2c3a967f4208a45daa53f5f57c2e002f63a381))
* Updated off peak sensor to come on when intelligent devices are dispatching (30 minutes dev time) ([18e3eca](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/18e3eca01e21c9d63d0b30b78d01c70807bde5dd))
* Updated raised errors for heat pump and intelligent controls to be more user friendly (2 hours dev time) ([e60ce63](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e60ce637641dc1d570602aa3121d79b79b69092a))


### BREAKING CHANGES

* off_peak entity will now turn on during standard off peak rates as well as ad hoc scheduled
dispatches when on intelligent tariff. This is because the naming and behaviour was confusing (off
peak not turning on when in an ad-hoc off peak period). See
https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/architecture_decision_records/0002_intelligent_is_dispatching_behaviour_changes
for full details.
* Intelligent device related entity ids have been changed from including the account id to including the device id. This is to support multiple EVs as well as other future intelligent devices OE might want to add in the future (e.g. Snug)

is_dispatching entity will now only show when the car is within a scheduled dispatching period. It will no longer turn on when within the standard off peak period. This is because the naming and behaviour was confusing with the name (on when it's not dispatching) and behavior in conjunction with the off peak sensor (off peak not turning on when in an ad-hoc off peak period). See https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/architecture_decision_records/0002_intelligent_is_dispatching_behaviour_changes for full details.
* If you are using blueprints provided by this integration, you will need to re-import them and potentially update automations in order to continue receiving updates.
* If you have automations that look at the heat pump water heater, then you'll need to update any reference to the state of 'on' to 'electric'
* Due to repair issue key structure changing, you may receive repair notices that you have previously ignored. You will need to ignore them again to hide them.

## [16.3.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.3.0...v16.3.1) (2025-09-09)


### Bug Fixes

* Fixed setting intelligent target percentage and time to use new API (1 hour dev time) ([d233177](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d2331772738003ab8ad7614f336c60946368f6df))
* Fixed turning on/off intelligent smart charge (15 minutes dev time) ([86ed63b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/86ed63ba50388149e8ea18147a47870e68de11db))

# [16.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.2.0...v16.3.0) (2025-09-07)


### Bug Fixes

* Fixed error raised when no rates are discovered (5 minutes dev time) ([0ca2cd1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ca2cd19de5a8b38560e1842baceecc68e26cee3))


### Features

* Added config entry information to diagnostics (15 minutes dev time) ([036d092](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/036d0926265854f882361f588a3db69f36276dcd))
* Added intelligent control support for intelligent drive tariffs (15 minutes dev time) ([0ef5844](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ef58447f28d19029971343d55d9d543716a6309))
* Added intelligent features support for OCPP (5 minutes dev time) ([7d79292](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7d79292bdcbef7f2d143da3884d790ea5ec138ff))
* Added new service for boosting heat pump water heaters (1 hour dev time) ([afc1999](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/afc1999e270ea74d8bacd24618af8eda5d4d3f51))
* Added repair notices for new meters being added or existing meters being removed (2.5 hours dev time) ([8701494](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8701494b3d5a053e7f1dbc1dafb3609cd17d3650))
* Decreased account refreshes to every 6 hours due to infrequent changes (5 minutes dev time) ([83f426c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/83f426cb60c62678e39422d58386548064ac27be))

# [16.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.1.0...v16.2.0) (2025-08-27)


### Bug Fixes

* Fix warning around double quotes inside an f-string (Thanks [@reedy](https://github.com/reedy)) ([a10cb8c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a10cb8c72ccc42ebb059df83c367dde08099b1e7))
* Fixed deprecation warning around parse_obj (Thanks [@reedy](https://github.com/reedy)) ([4028082](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4028082bbf3b11fc9ac08409de315c96a1c3bae3))
* Fixed issue where started dispatches were not persisting correctly between reloads of the integration (2 hours dev time) ([8b9c13d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8b9c13dd31b6c6037038f1346f7cdb96f71d82d0))
* Fixes invalid escape sequence (Thanks [@reedy](https://github.com/reedy)) ([40a2fa9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/40a2fa99aedc59a6c6557df191b970aa3f022dd4))


### Features

* Added heat pump senors for configured weather compensation (1 hour dev time) ([12711b8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/12711b81bdb3ecf1a7a7b75692fe2f14be787dd6))
* Added repair notice when intelligent device is unregistered or changes (1 hour dev time) ([bd81fb2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bd81fb252dd0fe221351fd89fb90996159212348))

# [16.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.0.2...v16.1.0) (2025-08-15)


### Bug Fixes

* Fixed issue with refresh token becoming invalid after 7 days (1 hour dev time) ([a195ea7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a195ea729c24e09a50fc3fd1a77f46a546817056))
* Fixed warning around regex syntax (5 minutes dev time) ([1cdfea2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1cdfea2a329e36767190eed00eeb1b0de1b625d9))
* Updated planned dispatches to have charge in kwh if available (15 minutes dev time) ([34dc977](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/34dc977badc7847e729b927a4cf7e5ebe9126dc8))


### Features

* Added heat pump fixed flow temperature sensor (Thanks [@lwis](https://github.com/lwis)) ([85dd008](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/85dd0087f0f2a5e89379f0e6811487a2986c79e6))
* Moved update of configuration to "reconfigure" option to reduce bugs and follow HA practices (2 hours dev time) ([501d57c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/501d57cc77f066d617d2d5385043234758eb8bb0))

## [16.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.0.1...v16.0.2) (2025-08-01)


### Bug Fixes

* Fixed invalid home pro address caused by config restructuring in v16 (1 hour dev time) ([9c0dcd3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9c0dcd36e80fc81cda011959899c42c6de87aa73))

## [16.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v16.0.0...v16.0.1) (2025-07-26)


### Bug Fixes

* Fixed home pro configuration check (15 minutes dev time) ([bb69109](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bb69109ebbebfe2358f59ed5512a1e23b8ae6ba0))
* Fixed issue when updating config (15 minutes dev time) ([69565ee](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/69565ee8973f5e2a5244ac8d307c2af5f256fd72))
* Updated intelligent dispatches retrieval to take account of expected error code (30 minutes dev time) ([8999432](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/89994322b279a05dde46bc1541ecd034f4d157c9))
* Updated to use refresh token where possible for re-authentication (30 minutes dev time) ([c2d7b69](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c2d7b6971b097e2e1407901dc48f3a8a63e38379))

# [16.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v15.3.0...v16.0.0) (2025-07-12)


### Bug Fixes

* Updated API for wheel of fortune which now supports claiming octopoints (25 minutes dev time) ([6463d8b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6463d8b16fdd2fe87bee146e4aeb938cfe9f0e23))


### Features

* Added sensor for providing total exports provided by Home Mini - This is not available for all meters (30 minutes dev time) ([488c3bf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/488c3bfbebf2c36154e87c5563f2506539a76480))
* Tidied up main configuration screen (2 hours dev time) ([1e3a98a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1e3a98afebe3043f8355e4c0aa63023abdf6d749))
* Updated intelligent APIs for planned dispatches due to deprecations (45 minutes dev time) ([5f1dc1b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5f1dc1b5ad83f28031a8b01d636b6626d3c80b19))
* Updated water zone for heat pumps to be represented as water heaters ([6e32a44](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6e32a44fd48cf9131126cdf9b57f517acad351f3))


### BREAKING CHANGES

* The response from the new APIs have removed some features. This means the response available in the attributes of the dispatching sensor have changed. Please check the docs if you are using these.
* The water zone is no longer available as a climate sensor. You will need to update all references to point at the new water_heater sensor

# [15.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v15.2.0...v15.3.0) (2025-06-28)


### Bug Fixes

* Fixed intelligent sensor resetting to off upon integration reload when it was on before reload (30 minutes dev time) ([784bc50](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/784bc504ee8e796e11b2aba65d3a0cb2003e6b35))


### Features

* Updated diagnostics to include state and attribute information for related sensors (15 minutes dev time) ([3aded1d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3aded1d40ce1743b7082603a87d68e02e6ea7c3f))
* Updated started dispatch calculation to be more forgiving on how stale the data is. A planned dispatch will only transition to a started dispatch if data has been retrieved within the last 3 minutes (1 hour dev time) ([44d2db2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/44d2db281bffbf69ccc026cdbd60dbef49f26462))

# [15.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v15.1.0...v15.2.0) (2025-06-11)


### Features

* Added support for HUAWEI_V2 and MYENERGI_V2 intelligent providers (15 minutes dev time) ([96ac524](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/96ac524df5f854be6277fff0fd221ea4771b380d))

# [15.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v15.0.2...v15.1.0) (2025-05-31)


### Bug Fixes

* Fixed cost trackers handling low powered devices (1 hour dev time) ([b65ca55](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b65ca5566d7a9897a9dfb183c2c198e0bb1c2bfd))
* Handle temperature and retrieved at times not being provided for heat pumps (15 minutes dev time) ([4e59e29](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4e59e291ed8efc7e1ef1fa925043155073d7a06b))
* Updated tariff consumption overrides to only retrieve rate/standing charge information for periods that are missing (30 minutes dev time) ([0fa274e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0fa274e731bf8cd929a44a1626cec26f793a9270))


### Features

* Added support for Tesla V2 for intelligent tariffs (5 minutes dev time) ([f219012](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f219012f590d677094197a9bd8e69ac3fbfb4c44))
* Updated underlying intelligent bump charge API due to deprecation warning (30 minutes dev time) ([0d79c85](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0d79c8554fb34bfa62f08d6b7908650cb6dd9705))

## [15.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v15.0.1...v15.0.2) (2025-05-12)


### Bug Fixes

* Fixed issue with heatpump live cop not updating (30 minutes dev time) ([829e01e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/829e01e617bf9d887bdbb6195aa4ee052f26014f))
* Fixed issue with intelligent dispatches incorrect turning on when on OHME (2 hours dev time) ([46fb3a0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/46fb3a0df3816d36d934961af1fad50a711e8aad))
* Fixed spelling mistake in account config (5 minutes dev time) ([f0dcd1d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f0dcd1dcd9f734d08d56cdc51440f25a6e5cd685))

## [15.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v15.0.0...v15.0.1) (2025-05-05)


### Bug Fixes

* Fixed JEDLIX_V2 provider to match graphql provider ([af264bb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/af264bba05a3445c5d4df43bfdc8516891f807c9))
* Removed fault code references from heat pump as not used ([3cd8318](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3cd831852b731c6ae63d2532f57a3643172c9d8a))

# [15.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v14.0.4...v15.0.0) (2025-05-04)


### Bug Fixes

* Added tracking of started planned dispatches for intelligent tariffs to improve cost sensor accuracy (3.5 hours dev time) ([94a4f16](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94a4f16d80a78620d0f415cfd955a37604cd0356))
* Fixed cost tracker to handle sensors reporting in measurements other than kwh (2 hours dev time) ([3c3119e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3c3119ebb1fa94833209d98ecf5a476e161511c6))
* Fixed discrepencies between cost sensors and statistic sensors for energy dashboard. The calculation has been revised to meet OE recommendations (3 hours dev time) ([c314ae0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c314ae00571da05d140a528c4b7ed081a374d102))
* Fixed planned and completed dispatches not being ordered (5 minutes dev time) ([ff0519d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ff0519ddcc5bd9d3348d6f85fbf4a219d75f827a))
* Updated diagnostics to determine if cached account data was used (5 minutes dev time) ([4d5a79c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4d5a79c084207cabb2f52cac45fb532b36252b9f))
* Fixed issue when COP not provided by heat pump (10 minutes dev time) ([b98167f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b98167f438da704e4f18fec0f02007074c86b45a))
* Fixed issue when next refresh could be seconds out, causing a longer than advertised wait time for data to be refreshed (30 minutes dev time) ([abe855e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/abe855e3ec7aa6cbf3627e7a37792a141bd7e793))
* Fixed issue when processing API errors that don't have error codes provided (10 minutes dev time) ([d502160](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d5021605dd923174c620a81747e15d1147da23a5))
* Removed old way of preserving completed dispatches beyond the standard API timeframe (15 minutes dev time) ([00a1809](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/00a18090a7ec6783e01f29fe2ac57c32d5e2a23c))


### Features

* Added the ability to automatically discover cost tracker options (3 hours dev time) ([4e6d33c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4e6d33c4883acca8b80d6ad4c5a330d975996cee))
* Added intelligent rate mode for changing how pending/completed dispatches adjust rates (1 hour dev time) ([ea17a07](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ea17a07cee2f47ffa761ef47915e2a4bd4f61145))
* Added support for JEDLIX-V2 intelligent provider (5 minutes dev time) ([670f3d7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/670f3d7f703acdb64404b7f304f007e86f6383d5))
* Raise repair notice when active tariff not found for active meter (1 hour dev time) ([0b70277](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0b70277e55cb0583ef204f5f6fd80077d7959935))


### BREAKING CHANGES

* If you upgrade from before v14, then you might lose old completed dispatches as these will not be preserved using the new way before this version
* The rate adjustments for intelligent tariffs have moved from using completed dispatches to started dispatches. This means that cost sensors may be in accurate for a couple of days while data is gathered.

## [14.0.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v14.0.3...v14.0.4) (2025-04-11)


### Bug Fixes

* **custom:** added support for new fixed intelligent tariff (15 minutes dev time) ([dd607ea](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dd607ea68ffa168eefbfec6fc617f12f7ad291ff))

## [14.0.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v14.0.2...v14.0.3) (2025-02-18)


### Bug Fixes

* Fixed issue with indexing on startup ([e6972c6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e6972c62845d62f3108af0a19521ea3a17e3470d))
* fixed issue with intelligent dispatches when no planned or completed dispatches are retrieved (30 minutes dev time) ([9e53ba6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9e53ba650acf276ddae848f60627ca68e64fecdd))

## [14.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v14.0.1...v14.0.2) (2025-02-18)


### Bug Fixes

* fixed issue where cached intelligent dispatches didn't load correctly ([e541624](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e541624747b8e502efe60de00055e5bc80415b65))

## [14.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v14.0.0...v14.0.1) (2025-02-17)


### Bug Fixes

* **custom:** fixed issue where rates are not refreshed after reloading if intelligent dispatches refreshing is manual (2 hours dev time) ([011b0cd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/011b0cd4553c5e144d39059bd8e0455b173394df))
* **custom:** updated manual intelligent service to provide further clarification and point at setting instead of service (5 minutes dev time) ([1d34c41](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1d34c414e736f06a6a6a2dfb4418114c7b4fbbed))

# [14.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.5.4...v14.0.0) (2025-02-11)


### Bug Fixes

* **custom:** renamed total_cost_without_standing_charge attributes to total_without_standing_charge for consistency with docs and other sensors (10 minutes dev time) ([75f023c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/75f023c1e166d9c6a3e487e0033aa8470328df3c))
* Fixed issue where account information wasn't refreshed unless you were on intelligent or had a heat pump (15 minutes dev time) ([54e8c6d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/54e8c6d21859e8f57a16aaae4ec5b39940bc6df5))
* Fixed issue where current/next start/end attributes on dispatching sensor don't reset properly (15 minutes dev time) ([c70643b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c70643b4862ae565c55a76be1999914b264cb676))
* Fixed issue with importing previous consumption/cost when no data was available for the timeframe (5 minutes dev time) ([2fcd8e8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2fcd8e864d9dc9a687c4fba1fc440971d763d3f9))
* Removed unneccessary print statement (Thanks [@andrewaylett](https://github.com/andrewaylett)) ([11765a1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11765a1684861c597cf8e69122d3533add9bdef1))
* Updated heat pump related services to only register (5 minutes dev time) ([a2bfccc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a2bfccc42bc5d0a5ae92c257eb4341a8c6f21154))


### Features

* Added context headers to requests for OE (15 minutes dev time) ([1c4e41c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1c4e41c602f50eff7c4e467172e7b0b68b7e995a))
* Added new service for refreshing intelligent dispatches. This has some caveats, so please review the docs (4 hours 45 minutes dev time) ([11cc47c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11cc47c70a9e35f6d9a848b40afdee67506fb683))
* **custom:** added cool-off period for calling manual intelligent dispatch refreshes (45 minutes dev time) ([c1e397b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c1e397beed33b957eff5811417f83d7f5c28c285))
* Renamed "New Account" option to "Additional Account" to avoid confusion ([59e1093](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/59e10936874ee604472e5b5f2a3b88dfec4adbe4))
* updated current_consumption sensors (not current_accumulative_consumption) to be disabled by default ([ff32a09](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ff32a0972e30970bfc63325ebcb520d3e9120d42))
* updated intelligent target time (time based) sensor to be disabled by default ([33fd9a6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/33fd9a608c29a9185c89be749a83834b3e0ad7ff))


### BREAKING CHANGES

* If you use the electricity/gas current_consumption sensors (not current_accumulative_consumption),
you might need to re-enable the sensors after updating. These have been disabled by default as they
usually confuse new users and the current_accumulative_consumption sensors are usually what users
are after.
* **custom:** If you are using the total_cost_without_standing_charge attribute, then these references will need
to be updated to total_without_standing_charge
* The intelligent target time (time based) sensor is disabled by default. If you are using this
variation of the sensor, you might need to re-enable the sensor and you should disable the select
variation. If you are using the select variation, the time variation should be disabled. This is
instead of removing the time variation as previously advertised. See docs for side effects of these
sensors.

## [13.5.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.5.3...v13.5.4) (2025-01-20)


### Bug Fixes

* Added more guards against invalid data when retrieving previous consumption data (15 minutes dev time) ([68550fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/68550fba4346d62e38de3fb173b334e02f16a839))
* Fixed issue where OE sometimes returns more gas consumption data than requested, which caused issues in other parts of the system (15 minutes dev time) ([22ea34b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/22ea34b05462525e474816e4ee71e9385cb83dd7))
* Fixed issue with boosting water heat pump zones when target temperature is not defined. This will now boost with a default temperature. See docs for more information ([ff7fa9b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ff7fa9bc0f817387ce44983b863a61fe246fab78))

## [13.5.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.5.2...v13.5.3) (2025-01-04)


### Bug Fixes

* Fixed issue with changing intelligent target time always throwing an error (30 minutes dev time) ([7ce15bd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7ce15bd907e544bd7b24a76fc3140ab82517fdee))

## [13.5.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.5.1...v13.5.2) (2025-01-03)


### Bug Fixes

* Fixed intelligent charge target to support increments of 1 (5 minutes dev time) ([416dcf7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/416dcf7dec683f40c9876b381363cba6aceb3044))

## [13.5.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.5.0...v13.5.1) (2025-01-02)


### Bug Fixes

* Fixed issue with restoring sensors where the unit of measurement has been changed (1 hour dev time) ([0c61292](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0c61292994f052f1782c2163a46ff4c5d7c04471))

# [13.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.4.0...v13.5.0) (2025-01-01)


### Bug Fixes

* Fixed demand for Home Pro when divisor is not standard value (Thanks [@reidjr2](https://github.com/reidjr2)) ([d3cf93b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d3cf93b4f991d8e5199ed6ce51a0d12997362a17))
* Fixed guard against invalid data in home pro client ([e2dc331](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e2dc331aca8a6cb1706c01e72873b6a965be89e2))
* Fixed intelligent charge target to not send invalid value to OE (10 minutes dev time) ([52bb498](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/52bb498905e3db43f1069961fe651c7b35f00afe))
* Updated cost tracker sensor configuration to update when underlying entity id changes (30 minutes dev time) ([5701e4d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5701e4dfba2d4344e5822e25f153397792f81b51))


### Features

* Added additional lifetime and live sensors for heat pumps (Thanks [@lwis](https://github.com/lwis)) ([37b69c8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/37b69c842754f3312b0c2e6c0f2b814893d14f71))
* Added Cosy 6 Heat Pump support (10 hours 45 minutes dev time) ([7d59da8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7d59da8c550c0250a44102258e099afdf963dc92))
* Added manual reset mode to cost trackers (1.5 hours dev time) ([0bd38af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0bd38affc3178bde899a1d41ce7909a9d0e526e5))
* Added select sensor for intelligent target time to make it easier to pick a valid time. The existing time sensor is deprecated and will be removed in a future release (45 minutes dev time) ([7554228](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7554228bdc507e1f1f918f63d50874c995db6d5f))
* Added sensor to show the current raw intelligent state (1 hour dev time) ([fb0f8e3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fb0f8e3b0cd4c050cd5a99abc25dc0169172535e))
* Added sensor to show the current raw intelligent state (1 hour dev time) ([#1142](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/1142)) ([083ed1d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/083ed1dfadd5e37ae21fdda599090141f55e146c))
* Updated update target rate and rolling target rate services to support persisting changes between restarts (1 hour dev time) ([6cdffb0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6cdffb02ffb59543c707eeb6987baeaf35b17bbe))

# [13.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.3.0...v13.4.0) (2024-12-26)


### Bug Fixes

* Fixed state class for current total consumption sensors (5 minutes dev time) ([9af97a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9af97a54b7a9dfb091f4e48f0cd66f758e7e2629))
* Updated total consumption sensors to ignore zero based results reported by home pro (10 minute dev time) ([78748d1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/78748d169887227de1a2f1f8bc73dfd1bf281190))


### Features

* Added ability to apply weightings to rates from external sources for use with target rate and rolling target rate sensors (4 hours 30 minutes dev time) ([9350c3f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9350c3fbdb46514033a175e1db7e521b2fc07835))
* Added support for INDRA intelligent provider (5 minutes dev time) ([7c3596c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7c3596cc920957dfe7ca23e42828aad826e44c43))
* Updated Home Pro config to support custom API being optional if certain features are not required (see docs for more information) (45 minutes dev time) ([8b94c7d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8b94c7d15109476acb53f930762c7ee17a4e0ed6))
* Updated Home Pro to contact local API directly instead of via custom API (45 minutes dev time) ([0ace45e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ace45e325bdbb104a24787bc26556e09e3d804e))
* Updated target rates to support additional re-evaluation modes for target times. This is to assist with external weightings changing (30 minutes dev time) ([05db8c2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/05db8c2ffcbdc39341a6e419c77bf9113a6aebe6))

# [13.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.2.1...v13.3.0) (2024-12-16)


### Bug Fixes

* Fixed issue with downloading diagnostics breaks loading of data (15 minutes dev time) ([4589a6a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4589a6ad0565e4289d3de2d89b525e6110e0605b))
* Fixed issue with gas tariff comparison not persisting configured calorific value (1 hour dev time) ([b16cd1d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b16cd1dbeeac4224d62c4cdf05b0c845a3ac71dd))


### Features

* Updated cost tracker entities to be associated with device of tracked entity, if one exists (1 hour dev time) ([9fe69a0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9fe69a081b08f1bec3ecfb4ea3b4ed552cc665ef))

## [13.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.2.0...v13.2.1) (2024-12-01)


### Bug Fixes

* Fixed retrieving diagnostics (15 minutes dev time) ([c064051](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c0640516fffffc4601016119c60b7d356986932e))

# [13.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.1.3...v13.2.0) (2024-12-01)


### Bug Fixes

* Added missing translations for target and rolling target rate sensors ([1a69b9f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1a69b9f478c5a88cac53554957dbedb7d358f720))
* Fixed join saving session blueprint when available_events is None ([169bdc5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/169bdc5132af2de8854f6c95d56bcfb48bd56598))
* Fixed late consumption data blueprint when charges is none ([6b6a5c1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6b6a5c181b7d988ecc991fca500f5351e5e0bd1f))


### Features

* Added attempts and next refresh attributes to data diagnostic entities (15 minutes dev time) ([e45b219](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e45b2195b52097b6a5f43b32d69ef5d4ab68e9a4))
* Added last error attribute to data last retrieved diagnostic entities (1.5 hours dev time) ([1a0c91e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1a0c91ef63af230ed42453619b03f6884d97a716))
* Reduced number of warnings outputted when data can't be retrieved ([0a2eb52](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0a2eb52d3a584582084b0ea817d21a05df1955d3))
* Updated data last retrieved sensors to report retrieval correctly (1 hour dev time) ([0cd034f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0cd034f29ed4a8984b9b0448fc149974f7ac4470))
* Updated electricity and gas rates retrieval to not re-retrieve rates that are already available locally (2 hours dev time) ([6601b9f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6601b9f0099b6968f6ed0fd624eeaf3dff0bc032))
* Updated previous consumption retrieval to not re-retrieve rates and standing charges if already available (30 minutes dev time) ([b454805](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b4548053eaed7d35186601b3631c3055bc3bb648))
* Updated standing charge retrieval to not re-retrieve standing charges if already available (1 hour dev time) ([2025d2b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2025d2b734041ddbd669d9a539b4bb60f655ea26))
* Updated target rate and rolling target rate to support custom weighting during free electricity sessions (2.5 hours dev time) ([0d7d724](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0d7d724f4470f7bc3403cce459dcc1700698d5bd))

## [13.1.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.1.2...v13.1.3) (2024-11-12)


### Bug Fixes

* Fixed issue with intelligent device attempting to save cache with no data (5 minutes dev time) ([7e7290a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7e7290afbdc3c9aaa9eb5a43bc867f2ca25c85a5))

## [13.1.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.1.1...v13.1.2) (2024-11-10)


### Bug Fixes

* Fixed saving and loading of intelligent device cache (15 minutes dev time) ([6a9dc6e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6a9dc6e5d3f1bf74662a5e500afd83b805c7b644))

## [13.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.1.0...v13.1.1) (2024-11-09)


### Bug Fixes

* Fixed issue when standing charge could not be retrieved for current accumulative consumption/cost sensors (5 minutes dev time) ([a2c4f7c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a2c4f7c3cc13b48d6af04b8720768170023918a0))
* Removed debugging log (Thanks @TurnrDev) ([78e5c00](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/78e5c006384eb19158436f2f8c054d97e5f1d254))
* Updated user agent for sent requests to try and fix current throttling (1 hour dev time) ([0dd8587](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0dd8587890c4527a3bb1f7de54c0df904f3f6d4b))

# [13.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.0.3...v13.1.0) (2024-11-04)


### Bug Fixes

* Added fallback for target rate sensor calculation when data is in odd state and added additional logging to track down original issue (2 hours dev time) ([aba8c53](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/aba8c532e2318d6af813e6253061b191decbd113))
* Fixed issue with rates going into wrong buckets during daylight savings (2 hours dev time) ([426a218](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/426a2186c84c1a7ea939b7319cf194aa313b9ccd))
* Fixed various issues relating to sorting during daylight saving transitions (1 hour dev time) ([9615e4f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9615e4ffa8d5eadf6fba018a9c91f4d8bc0a6a00))


### Features

* Added sensors for tracking free electricity sessions (3 hours dev time) ([98cbafb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/98cbafbe718ea7fa0ce528152ef877f5ec25ff2d))
* Updated diagnostics to include home mini data (30 minutes dev time) ([745155e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/745155e8cfcd3affe09f669dce7981dbcd587795))
* Updated startup to fallback on cached account information if not available to reduce startup failures (45 minutes dev time) ([2c10a14](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2c10a14750a7a0ee0b9d22b265bef89ef42eb055))
* Updated startup to fallback on cached intelligent device information if not available to reduce startup failures (45 minutes dev time) ([6403589](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6403589b9252be1255978ad4f38e1e6b8bc96881))

## [13.0.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.0.2...v13.0.3) (2024-10-26)


### Bug Fixes

* Fixed issue where previous consumption data could be reported partially for the current day (30 minutes dev time) ([db4838d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/db4838ddcbbfa794402a432809d602facec96c46))
* Fixed rolling target rate sensor not turning on when in always evaluation mode (30 minutes dev time) ([b141ce2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b141ce2c060836f19597c7d49ff60dd0073fa3a9))
* Updated diagnostics to include additional information to assist with debugging (1.5 hours dev time) ([5b9136c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5b9136c5f4c76f5880cecd3faeec127b8db5044c))

## [13.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.0.1...v13.0.2) (2024-10-18)


### Bug Fixes

* Fixed issue with restoring target rate sensors when no target times are present ([7e38b6d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7e38b6d0d9d674f7d9a272dd132985c45c06ae8f))

## [13.0.2-beta.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.0.1...v13.0.2-beta.1) (2024-10-17)


### Bug Fixes

* Fixed issue with restoring target rate sensors when no target times are present ([7e38b6d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7e38b6d0d9d674f7d9a272dd132985c45c06ae8f))

## [13.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v13.0.0...v13.0.1) (2024-10-16)


### Bug Fixes

* Fixed issue with initialisation when account has no electricity meters ([936eed4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/936eed4e87f074f17b0ba6d063fbaef95672afcb))
* Fixed issue with loading sensors when electricity meters are not present ([1fdfff3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1fdfff3b459c6f515fddea63b6b4dc880183e731))
* Fixed issue with target rate and rolling target rate sensors when target times had not been previously evaluated ([cdc410d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cdc410df88b32ecb0a9abca96f740544944b9702))

# [13.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v12.2.1...v13.0.0) (2024-10-14)


### Bug Fixes

* **blueprint:** Fixed late consumption data blueprint based on changes to underlying sensors (15 minutes dev time) ([7d9223b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7d9223bad1d5eae56e1a150cceead20da2d5cbf3))
* Fixed HA warning for registering an entity service with a non entity service schema (15 minutes dev time) ([8decd8a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8decd8aabfca6c83eda6b1cede0a2523223ed645))
* Fixed issue when rate information isn't available on start up which prevented integration from starting (5 minutes dev time) ([ffb8911](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ffb8911dd0e6189f1573c5e5677b4a8b238f64af))
* Fixed issue where earliest period was not picked for continuous target rate sensors when multiple groups had the same total (1 hour dev time) ([1dedab4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1dedab4538c7d271e565ae72540bf9b5ec337469))
* Fixed issue where intelligent tariff can get into state where off peak sensors are not available (15 minutes dev time) ([6882f06](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6882f06cbb54d2848462ac5e2c01763b1ed28bed))
* Fixed issue with migrating config entries from older versions of the integration (15 minutes dev time) ([119c65e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/119c65e5518468a8d4fc3dcd623523000d670962))
* Fixed issue with restoring saving session baseline entity and current interval accumulative consumption sensor (5 minutes dev time) ([a7fa406](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a7fa40639536c0e130efc9ce625c2cb73e0b8705))
* Fixed issue with target rate sensors when weighting was applied with finding latest rates (1 hour dev time) ([07c37c6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/07c37c69938f5541658fb8d61372e2cb3e438431))
* Fixed smart charge sensor always being off - Thanks @HLFCode for your assistance (15 minutes dev time) ([4ae5d69](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4ae5d69afe10b184dc93386c6a83b1f18d21bf53))
* Fixed target rate not re-evaluating every minute when no rates are available for target period (15 minutes dev time) ([c2899ef](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c2899ef336731569b53ce0bb9ff675af8c9daa0d))


### Features

* Added intelligent support for FORD (Thanks [@grantbevis](https://github.com/grantbevis)) ([327d92c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/327d92cc1f050553f5967a708a837f440c6eb6b9))
* Added sensor for tracking saving session baselines (6 hours dev time) ([f3f0460](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f3f04600f873cd653376cea53775aa8772d46da7))
* Added sensor to display current 30 minute period of accumulative consumption for Home Mini. This is used for comparing with saving session baselines. (30 minutes dev time) ([1eeadaa](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1eeadaa5f449697d0a660db2b332de914782a144))
* Added sensors for storing data last retrieved for all shared data (3.5 hours dev time) ([cedb260](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cedb2600651a8f7b18735b82687bd8479cbcc27a))
* Added support for rolling target sensors (3 hours dev time) ([acfb113](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/acfb1134924f399989dff7dc26ad2a90082d91e3))
* **blueprint:** Added blueprint for saving session baselines (45 minutes dev time) ([3a30e21](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3a30e219b0e3472da8c58e1ba9496cd51b28124f))
* Increased intelligent refresh rate to 3 minutes (5 minutes dev time) ([4c5b669](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4c5b66944aae4e654f75585a602dd762dfe5815b))
* Migrated to use new intelligent APIs (2.5 hours dev time) ([80eb8bf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/80eb8bff1fbb772ee0511973661f121ca32b1433))
* Renamed intelligent charge limit to intelligent charge target to better reflect underlying API and purpose across providers. (15 minutes dev time) ([4da40f5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4da40f590bf961246ab9c5964d6973e359f01d37))
* Renamed intelligent ready time to intelligent target time to better reflect underlying API and purpose across providers. (15 minutes dev time) ([8b92442](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8b924420c78f81cdd1e58075b76db307df03e7f3))
* Updated previous consumption sensors to report latest available full day instead of at a fixed interval (2 hours dev time) ([bb7bb0a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bb7bb0abc3fca93fed56a548496da495f053e196))
* Updated target rate weightings to support decimal numbers for more precision (1 hour dev time) ([c4b78a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c4b78a5bbc994a72c947029950664bc2147f9de6))


### BREAKING CHANGES

* data_last_retrieved attribute has been removed from all sensors to reduce excessive database storage. This data is now available in separate diagnostic sensors. Please consult the docs for which diagnostic sensor is applicable for your target sensor.
* The previous consumption sensor will now dynamically adjust to show the latest available full day instead of at a fixed interval. The fixed interval settings will no longer be applicable.
* The intelligent ready time entity has been renamed. You will need to update any automations or dashboards that relied on the old naming.
* The intelligent charge limit entity has been renamed. You will need to update any automations or dashboards that relied on the old naming.
* vehicle_battery_size_in_kwh and charge_point_power_in_kw are no longer both provided together. It's either one or the other depending on which part is integrated into OE intelligent. This is due to not being available in the new APIs.

## [12.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v12.2.0...v12.2.1) (2024-08-26)


### Bug Fixes

* Fixed issue where target rate sensor could not be reconfigured if min/max rate were set (15 minutes dev time) ([e7168e4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e7168e41ff1d0462ccbbaf481d3ddca649f11b1e))

# [12.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v12.1.0...v12.2.0) (2024-08-18)


### Features

* Added hypervolt support for intelligent features (15 minutes dev time) ([6d8f695](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6d8f6959f7a3eaaed98d42e96886cca21d140e4a))
* Added repair notice and custom github issue template when intelligent  provider is not recognised (1 hour dev time) ([3118cc8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3118cc822ee01593b5114a7549e8b58544fdfadf))

# [12.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v12.0.2...v12.1.0) (2024-08-11)


### Features

* Added support for setting Home Pro screen. You will need to [reinstall](https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/setup/account/#prerequisites) the API on the Home Pro device to support this feature (3 hours dev time) ([a620052](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a620052fcff83c6a4c1a91c20c332970515b7bda))

## [12.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v12.0.1...v12.0.2) (2024-08-10)


### Bug Fixes

* Fixed issue where attributes were not initialised properly for certain sensors (15 minutes dev time) ([a21ec7d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a21ec7dfbcb8256d0d6de9beb28f2f156a53cf94))
* Fixed issue where previous rate information wasn't retrieved for intelligent tariffs where an intelligent device wasn't available (30 minutes dev time) ([60aa853](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/60aa85389edde64ca7f8be7da69fefa91de6e0b3))

## [12.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v12.0.0...v12.0.1) (2024-08-05)


### Bug Fixes

* Fixed issue where rate information wasn't retrieved for intelligent tariffs where an intelligent device wasn't available (2 hours dev time) ([50a7bdf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/50a7bdf8c2b5d09b0d8d08820fae0db90c422718))

# [12.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.2.2...v12.0.0) (2024-07-27)


### Bug Fixes

* fixed event based sensors (e.g. current_day_rates) to be situated in the correct domain (30 minutes dev time) ([239093f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/239093f46ac9cf2327d901fa438cd933a4a5bebc))
* Removed certain sensors for Octopus Home Pro as data is not available (5 minutes dev time) ([85ad59c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/85ad59c16ed8f3820c7d42abc3ca8b633117bb4d))
* removed last_evaluated attribute as this duplicates data already available via HA sensors and removed data_last_retrieved and target_times_last_evaluated from being stored by the recorder (2 hours dev time) ([20603f5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/20603f554e1ecd33396d672587bc54a6c63b441f))
* Updated unloading of account to properly close existing connections (15 minutes dev time) ([e56e62d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e56e62d328b5e0cdf6e03a14bfc2238a10f42dcc))


### Features

* Added hours mode for target rate sensors which allow the sensor to come on the minimum or maximum specified number of hours (2.5 hours dev time) ([a57f5c7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a57f5c77b096cb3c893d5da4e258eea72c195ffe))
* fixed issue with duel rate tariffs changing to non DD rates. Toggle is now available in config. (40 mins dev time) ([e427419](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e42741981f6c4cbf71e6932160363485e0dd51ed))
* removed deprecated default tariff override sensors (5 minutes dev time) ([21bf804](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/21bf80402248458e56f96c831fe9e73d0e71312c))


### BREAKING CHANGES

* last_evaluated attribute has been removed from all entities. You should use the inbuilt last_updated
state/attribute provided by HA
* Removed data_last_retrieved and
target_times_last_evaluated from being stored in the database to try and reduce footprint. This
follows HA guidelines around attributes that change frequently
* Removed the deprecated default tariff override sensors. If you still require this feature, you
should be using the new way to define them. See
https://bottlecapdave.github.io/HomeAssistant-OctopusEnergy/setup/tariff_comparison/ for more
details
* If you are referencing any of the event based sensors that have had their domains fixed, you will
need to update these references accordingly

## [11.2.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.2.1...v11.2.2) (2024-07-10)


### Bug Fixes

* Fixed division issue with cost tracker when an update event is fired but no change is detected (30 minutes dev tim) ([c0eba23](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c0eba23f44a749711b689f396efc276ae05c81d3))
* Fixed initialisation issue when only gas is supplied by OE (Thanks [@ksimuk](https://github.com/ksimuk)) ([1823628](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1823628193ee3be1a050d6a2bfeffada39138c3f))
* Fixed issue where current consumption sensors were not available if you configured only a Home Pro (30 minutes dev tim) ([6499cc1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6499cc1d72bdb43a27b2ad1e157853eef462ec01))
* Improved Home Pro error messages (5 minutes dev time) ([c5e6968](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c5e69686ce4b25c0487c1524376310e06ddcebd6))
* Separate stopping demand sensor from updating if total consumption is not available from Home Pro (30 minutes dev time) ([a03cfab](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a03cfab83baa7a8d5c1519a98a5215d8b060676b))
* Sort meters by most recently active to account for switching meters (15 minutes dev) ([27c39af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/27c39af46e749f6b0e8a313ce338d956975bfd06))

## [11.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.2.0...v11.2.1) (2024-06-29)


### Bug Fixes

* Fixed calculating total gas consumption from Home Pro when reported in cubic meters (1 hour dev time) ([09965b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/09965b5d90b8bdd8606880ecbacb2de908d48190))
* Fixed issue where home pro could not be unset ([2d419c9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2d419c99df7d642d8d1d6e2e975a09eb53bf7294))
* Fixed issue where old inactive meters were being registered (1 hour dev time) ([9ab2bf7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9ab2bf79954bd3f94c45e51cc52dbd5e0591d035))
* Improved Home Pro connection errors (30 minutes dev time) ([40582ae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/40582ae801e770e854a5727cca628906dc679019))
* Updated home pro installation command (Thanks @DJBenson) ([5502619](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/55026196aaa6e8744b63a81a4fe5274f15d4b305))
* Updated home pro to ignore total_consumption of zero (15 minutes dev) ([4a110f3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4a110f36b96c0bb018df08468c87df22f4bc190b))
* Updated home pro to report None if demand not available ([fd4cbbb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd4cbbb0abc946aef84e4c9eabf8fe3f8bc3ade6))

# [11.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.1.1...v11.2.0) (2024-06-16)


### Bug Fixes

* Add threshold for cost tracker to allow tradcked total_increasing sensor to decrease slightly without treating it as a reset (30 minutes dev) ([0de0bb3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0de0bb3f36bf92d0abc1a78e7148ce179bd09dc0))


### Features

* Added experimental support for Octopus Home Pro (3 hours dev time) ([2560b6b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2560b6b6597d4e1e6e4c66c9e2aeadcf95a0c5be))
* Added sensors for displaying current total consumption (40 minutes dev) ([dbb2b5d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dbb2b5da5956aa07a77211e0acbe5f6590a13351))
* Updated intelligent charge limit to be an input box rather than slider ([778f197](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/778f19774794f0506d2936524ec7d04feb0ce84f))

## [11.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.1.0...v11.1.1) (2024-06-12)


### Bug Fixes

* Fixed support for duel rate tariff that doesn't conform to normal structure (30 minutes dev work) ([3951db9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3951db981f1c9dfefa3d780159e8d91ebc5676ea))

# [11.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.2...v11.1.0) (2024-06-10)


### Bug Fixes

* Added some additional checks around cost tracker attributes ([79d339c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/79d339c4446a775304568d6bfd1cff4f9da80939))
* Fixed spin wheel of fortune service ([42a0f65](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/42a0f65ebed7f2493dbcc8e7abc4a8758aa0ef0a))
* Made tariff rate unique calculations more resilient to incomplete rate information ([3b8ce91](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3b8ce91dc32f6d763bd79a3dd4a7efd025788c4d))


### Features

* Added ability to compare multiple tariff which supersedes current overrides (4 hours dev time) ([effba64](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/effba64d7b1aec46ea328ef7a4653b24c41bd393))
* Added repair notice for when API key has become invalid (1 hour dev time) ([6a49f60](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6a49f608bc4158a07b15b3f36f74a030d5eb80b8))
* Added repair notice if rates change to a state where new entities become available or existing entities are no longer applicable (1 hour dev time) ([e207c23](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e207c23df70198c38586e49a001745544dd0015c))
* Added support for business tariffs (5 hours dev time) ([804cd9d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/804cd9d02ca40ba5145af273405188ab29ec3db4))

# [11.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.2...v11.1.0) (2024-06-10)


### Bug Fixes

* Added some additional checks around cost tracker attributes ([79d339c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/79d339c4446a775304568d6bfd1cff4f9da80939))
* Fixed spin wheel of fortune service ([42a0f65](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/42a0f65ebed7f2493dbcc8e7abc4a8758aa0ef0a))
* Made tariff rate unique calculations more resilient to incomplete rate information ([3b8ce91](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3b8ce91dc32f6d763bd79a3dd4a7efd025788c4d))


### Features

* Added ability to compare multiple tariff which supersedes current overrides (4 hours dev time) ([effba64](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/effba64d7b1aec46ea328ef7a4653b24c41bd393))
* Added repair notice for when API key has become invalid (1 hour dev time) ([6a49f60](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6a49f608bc4158a07b15b3f36f74a030d5eb80b8))
* Added repair notice if rates change to a state where new entities become available or existing entities are no longer applicable (1 hour dev time) ([e207c23](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e207c23df70198c38586e49a001745544dd0015c))
* Added support for business tariffs (5 hours dev time) ([804cd9d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/804cd9d02ca40ba5145af273405188ab29ec3db4))

## [11.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.1...v11.0.2) (2024-05-18)


### Bug Fixes

* Reverted requirement for target sensor to have target hours above zero (30 minutes dev) ([0098efa](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0098efa7151808deb9b2a73a69b39a19f7b86208))

## [11.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v11.0.0...v11.0.1) (2024-05-18)


### Bug Fixes

* Fixed export suffix for electricity meter device (1 minute) ([7c7d999](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7c7d999c05254f8a272dbc90d50ac689db932407))
* Fixed issue where old target rates are present when config is updated (45 minutes) ([6aeada6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6aeada69944802e25b29309e393d5a8b27a8da15))
* Fixed issue where start, end and offset could not be unset for target rate config (15 minutes) ([cb170af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cb170afa78de0940c17b333b76708ef5e9c834e8))
* Fixed refreshing gas consumption data service (15 minutes) ([fbe3f46](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fbe3f468c2a35928dd1142be346590e47fa444e3))
* Fixed target rate sensor not being able to set zero hours (20 minutes) ([022f30d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/022f30db7895f986cfd94fdefa5a51b2b1c8a0d5))

# [11.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.3.1...v11.0.0) (2024-05-12)


### Bug Fixes

* Accounted when intelligent device can come back with null data from OE ([53db610](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/53db610134fbb4356603b76634c56f71304280f7))
* Fixed issue when str error reported if config of target rate sensor fails first time ([c5cfd83](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c5cfd8310ad196b666d6ff3ed5c28fc6587e2b1b))
* Fixed issue with dispatching sensor if rate is off peak from now until the end of the available rate data ([c583b8b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c583b8b54c483ab6e6770e01b13b886511aa1596))
* fixed tariff override data having rate value in pounds and pence for consistency ([48f832a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/48f832afd9cb5ea846d655e7eb3ea7937520822b))
* Fixed updating cost tracker config ([c934614](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c934614ccd0a9b5ee471280be2c0d565000a9c52))
* Fixed warning for deprecated EventType reference ([e8786df](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e8786df9fb476a56fd4a4347f03ab46075c02be7))
* Limited backoff logic to 30 minutes between attempts so it doesn't increase forever ([f2de64d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f2de64d2ac176c26e7224b6ddeae04cf5f85d6ea))
* Updated attributes and events to have datetimes in local time (UTC in winter, BST in summer) ([19ac60f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/19ac60f10ae81f4a81bedbd448c5563c41e35805))
* Updated minimum Home Assistant version to 2024.5.0


### Features

* Added ability to configure optional minimum/maximum rates for target rate sensors ([95ac448](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/95ac4489653a97cd2a3d3274908543d73ff5827f))
* Added support for applying weightings to target rate slots ([80bbb52](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/80bbb52b413aa722a5a4a5eac654901fd51185f7))
* Added support for tracking 3 rate tariffs (e.g. Cosy) via separate sensors ([40d21d1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/40d21d1815ceb9f1e1eff1be7362b42b15950668))
* Added the ability to delete devices manually ([404d2e9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/404d2e9edef494348dfc9e95c86d0b410746f548))
* updated the default names of various sensors to be more useful in areas of HA when space is limited ([870c917](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/870c917fd4a166ea71a51971df9b98e7d75957bd))


### BREAKING CHANGES

* If you are relying on the previous default names of sensors then you will need to update your
sensors manually. Only the visual default name of the sensors have changed; the entity ids will
remain the same and therefore will not effect any automatmations. If you have manually changed the
names of the sensors, this should not effect you.
* For 3 rate tariffs (e.g. Cosy), the peak based sensors will no longer track consumption/cost for both peak and standard rates. There is now a third sensor (standard) which tracks the middle rate. In addition, if you are on a tariff that doesn't have off peak, standard or peak rates, the current off peak/peak based sensors will no longer be provided by the integration.
* If you were relying on datetime based sensor attributes or event properties being in UTC, you will
need to adapt accordingly
* If you were using tariff override rate information, you may need to adjust your use due to changes
in how value is reported

## [10.3.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.3.0...v10.3.1) (2024-04-20)


### Bug Fixes

* Removed excessive logging that did not adhere to log settings ([cb27d6d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cb27d6de4601d36e6527fb76945fec2bb444c0ee))

# [10.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.2.1...v10.3.0) (2024-04-15)


### Bug Fixes

* Fixed account setup descriptions to be clearer ([4107fb7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4107fb714fec41de2286223f5f664fe787f19068))
* Fixed peak/off peak cost calculations during BST time period ([11d5a9f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11d5a9f601f937052a9bf0e2785300b06bb4f34f))
* Fixed peak/offpeak consumption/cost sensors going into negative on energy dashboard ([c167f39](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c167f39a7c99ae5126cfacdedeeab86fd0ec3ac9))
* Fixed rate min/max/average calculations during BST ([fdccc5b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fdccc5b86031c01afd09cc0fa2613f7c9802411c))
* Increased minimum required version of home assistant ([e662659](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e662659aea551e9fdbf92268b2d703ab9d3cbd69))
* Updated electricity rates to not update initially until dispatch rates have been retrieved if on intelligent tariff ([756535e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/756535eb5c950d995a342f344cabf462177febf3))


### Features

* Added duration in minutes to saving sessions ([35d17dc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/35d17dc61df7879557e4ab8ec85cff61f874c9ce))
* Added redeemable points attribute that determines how many points can be converted into account credit ([9d1233d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9d1233da6db055447aa68b293564ed834b9853cf))
* Added service for redeeming octoplus points for account credit ([0390a33](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0390a33b89498f05fbeb9c6b413119bea2d43a3a))

## [10.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.2.0...v10.2.1) (2024-04-07)


### Bug Fixes

* Fixed logging issue with cost trackers ([cfdd927](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cfdd927ab0b94be9554cb7458789e9034c6605a5))
* Fixed target rate sensor picking times an hour before/after requested timeframe - timezone issue ([3651780](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3651780af51ba37c85f357925631174a298feed3))

# [10.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.4...v10.2.0) (2024-04-06)


### Bug Fixes

* Added missing account id information for previous accumulative gas consumption sensor ([6bd6387](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6bd63871d1ad77ceb9c12f5e8696b725b1d77a00))
* Fixed issue when consumption data from Octopus Home Mini is not defined but demand data is ([d51647c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d51647c2962d0f09c96ee81e9fa369879f901875))
* Fixed missing account id for repair message relating to octopus mini not being available. ([fa5650f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fa5650faf8726d81c1ed1bf2b8c6c222a8dab59b))


### Features

* Added attribute to previous consumption sensors to indicate the latest available data via the API ([cd735c6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/cd735c6c2ac0eb60ceb44f9dcf9629ece91cf701))
* Added cost tracker for weekly and monthly accumulations ([01c3733](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/01c3733111abeceff2edba2a0074fc49a279b41f))
* Added sensor for next greenness forecast ([0708271](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0708271eb5bf919d57e7fc421fbc5dbdd2fd10c3))
* Added service for adjusting specified dates within cost tracker accumulative sensors (e.g. week and month) ([26a9462](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/26a946228a1fc47fa82c1020584b4762b9973c91))
* Added service for adjusting standard daily cost tracker ([1378e47](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1378e4708e4846b46e05ec2fa557f04c49cb01fa))
* Added service for resetting a cost tracker back to zero. ([d28d63b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d28d63b17dec9d43604f44d96ead6dc35f9a967f))
* Added support for multiple different accounts ([c15b4af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c15b4af83b7075631871a7069f734b823c7e3504))
* Updated cost tracker config to be updatable ([c24db54](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c24db54df842d09ed86f383d2eca1bfd5c5e0342))

## [10.1.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.3...v10.1.4) (2024-02-22)


### Bug Fixes

* Fixed invalid reference ([0083b2d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0083b2df5de510c3a4fc8d2ae9d72563cd9f9abd))

## [10.1.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.2...v10.1.3) (2024-02-22)


### Bug Fixes

* Fixed issue when dispatch source is not defined to count as smart charge ([0af23b9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0af23b98d1702a847354b5bf28cec11507c551ea))
* Fixed issue when dispatching sensor would not stay on during full half hour when planned dispatch is active ([e64c694](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e64c69484dbdba271c5d3dd0adaeb7b839ff8b1b))
* Fixed issue where start/end times could be incorrect on next/previous rate sensors ([c431dac](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c431dac82e4172cbfc2ed9e59faa831ef1523e55))
* Fixed issue with calculating current rates for intelligent based tariffs ([6efcfc0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6efcfc0fd10eb5d23f4e2fb62ae04bfa28d26018))

## [10.1.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.1...v10.1.2) (2024-02-18)


### Bug Fixes

* Automatically removed devices associated with old meters ([e6905d0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e6905d096373ed40b6f8a7fb0cd62c4a8bd436a2))
* Fixed dispatching sensor incorrectly turning on when bump charges are activated ([b37e4b1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b37e4b1a4ae5447ebc8465839eb9c0c1a9f4be5c))
* Fixed issue where client is not cleaned up correctly on restart ([deac67b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/deac67ba099c251c4b21bc11ab32d7bd480548a1))
* Fixed issue with cost trackers when old state is unavailable/unknown ([599613b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/599613b6b4e4b5aa70670e2dd653f3f3f88ae605))

## [10.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.1.0...v10.1.1) (2024-02-17)


### Bug Fixes

* Fixed icon for update cost tracker service ([e1d048a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e1d048a1fc99655000163931f38b680a66915aa0))
* Fixed issue when rates were not adjusted for dispatches that started or ended part way through a rate ([fb3e3f2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fb3e3f2cf269a90c01b97162729dba2db98b8aa1))
* Fixed issue where previous cost is calculated incorrectly when on restart and on intelligent tariff and dispatches have not been retrieved ([406f2c8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/406f2c84f392d17e9fd836597ecda00f8e95c47d))
* Fixed issue where tariff attribute on entities would be old tariff when switched over ([a328fec](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a328fece656eda5a5f0bf432b3ef290517abab07))
* Fixed issue with cost tracker when used with total_increasing entities that reset ([6759317](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6759317099328d185cd4fa05fdc628f29b6b0d04))
* Fixed previous consumption cost not adapting when tariff changes ([2ec461e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2ec461eb1616f2f10ab583ba561823202bbf6706))
* Updated saving sessions to ignore octopus test events ([9488a37](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9488a370b0d703fe68eb34f9e4222fd18ff5d0ec))

# [10.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.4...v10.1.0) (2024-02-10)


### Bug Fixes

* Fixed charge limit sensor to behave like the app around accepted values ([c42a619](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c42a619fdffeee0c6e28fec92070396132146ebc))
* fixed issue with override costs getting stuck ([1b93638](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1b9363863a4e3f9567fd0d6060a1dd7d4e2270cf))
* Fixed issue with rate sensors not updating properly when intelligent dispatches update short notice ([f1623e5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f1623e5af0e36193f41d4abfab406e1036d528b1))
* Fixed issue with refreshing previous consumption and database lagged behind processing ([fbe9896](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fbe9896e1711586398070b19a728847182c8aedc))


### Features

* Add icons for services - Thanks [@andrew-codechimp](https://github.com/andrew-codechimp) ([0ef0a7c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ef0a7cfad2da1cf14c9d8bb2f7177cf104420a1))
* Added greenness forecast support ([872711e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/872711eb23b1d14434d6421a9328aeb757b59776))
* Updated dispatching sensor to include current start/end and next start/end attributes ([e2ed003](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e2ed00340dc4d94ba5700c03589a875518c89541))
* Updated off peak sensor to include current start/end and next start/end times as attributes ([8da4679](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8da46796871283227d3e96bd05eb65a70b755df7))

## [10.0.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.3...v10.0.4) (2024-01-29)


### Bug Fixes

* Added additional check in electricity rate calculations ([1e30999](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1e30999b0ff030de8bf6310e8000fbb40c75b4a6))
* Fixed current consumption sensors not updating if other sensors were disabled ([443a130](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/443a13075d5719cc20a4d1d38e4fd9350fe9c89a))
* Fixed issue with binary sensors not restoring previous state correctly ([5c85dae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5c85dae64b59d7d3c467fe6f8cf822acb040a1da))
* Fixed restoration of entities to handle "unavailable" state ([248e700](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/248e70099d462912cd29f8d5009124d04c9e0c86))
* Fixed target rate setup when invalid start/end time is set and on agile tariff ([fe1bad1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fe1bad197a7607b4763a515b849cb1ef6e1dd2cd))

## [10.0.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.2...v10.0.3) (2024-01-20)


### Bug Fixes

* Fixed current consumption not resetting to zero at midnight if data isn't available ([19ae707](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/19ae7074ead4e3ff6da210c7e027d831cab2a675))
* Fixed current consumption sensor resetting to zero after a minute when data hasn't refreshed ([a13edef](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a13edef4fb8af213334fddd05a1f2aed40b2c898))
* Fixed issue intelligent based electricity rates not being adjusted when dispatches are refreshed between rate refreshes ([f9514d3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f9514d3e068548ee20bfb189abad2d76bd92d2ef))
* Fixed issue when updating electricity rates and intelligent dispatches is unavailable ([9bd2b9c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9bd2b9c74046a54684a5c7d4100e18c30a613eaf))
* Fixed old Intelligent Go tariff not being picked up correctly ([c935206](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c9352060b10799c43941d7e322663593f718bf0a))
* Increased timeout limit to 20 seconds to try and resolve issues people have been having ([6de26f6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6de26f69a40decb816b8193511db44ebae7ddcc6))
* Removed duplicate logging of events ([1f4e3da](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1f4e3da9f89ae615d44b38eee7e916d4e7608308))
* Reset cost tracker every day at midnight ([3328562](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/33285628bb618ab3a2072f3fcb5e09769c27757f))
* Updated various sensors to update their state based on recommended HA practices ([9885528](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/988552865909d137e6ea85639cd364f073468546))

## [10.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.1...v10.0.2) (2024-01-07)


### Bug Fixes

* Removed entity migration as not working properly and putting things into weird state. Follow https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/678 for updates ([daa492f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/daa492ffbf2c83de78623b0268220841dc117d8b))

## [10.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v10.0.0...v10.0.1) (2024-01-06)


### Bug Fixes

* Added migration of accumulative gas consumption sensors - see https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/678 for more details ([f379786](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f37978673aec21f008d8d35c7bcfcba48bd59173))
* Fixed being unable to edit target rate configuration ([150d97a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/150d97af9149affa456801a30895f7e6b3be327f))
* Fixed initialising of integration to automatically retry if account information can't be retrieved ([320eb15](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/320eb15cc1fd1ff3039aaa0abfa7bc4f1c35ff6d))
* Fixed issue when intelligent device provider is unavailable ([6d9f469](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6d9f4693b335aa84caaaf4885d32fb9300921231))
* Fixed warning raised in charge limit sensor ([c43ef73](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c43ef73abb7553aec89985acf88b5672cbaaa6bd))
* Fixed where intelligent entities were incorrectly available to users on intelligent flux tariff ([0be466a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0be466a578f910e2af79ed3ccd63b26bdf3fd35e))

# [10.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.2.1...v10.0.0) (2024-01-04)


### Bug Fixes

* Added prevention around multiple access token requests ([0ecd453](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0ecd45325f90c4ad1599b0f73a305fb23982d354))
* Fixed deprecated HA references ([5751d3b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5751d3b0b301e18f60755aec56358bbc1152e087))
* Fixed issue with cost override when last retrieved is not defined ([59dbb7d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/59dbb7df4531e6c1ae50ba1583602d4fd3b5344a))
* Fixed off peak sensor turning on during extended intelligent off peak periods ([9b36f07](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9b36f07b5d53d05e82cac518748ae0013f320576))
* Fixed restoring of intelligent states ([faa3a32](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/faa3a32e942c5c57241e19e1fe18dde1d8802a66))
* reduced API calls for intelligent data during setup ([381c723](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/381c723885d2b068b4a4f2b9dd15883460861588))
* Reduced required data on startup to speed up initialisation. This may result in a slight delay to get updated data ([5a2838f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5a2838f3c61b688149d106ba42b9169d1c518206))
* removed various intelligent features for OHME as these were incorrectly exposed and not supported ([9d52884](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9d528841b992328d490bd1e051c58625d8fba270))


### Features

* added m3 representation of current accumualtive gas consumption for Octopus Home Mini ([bc1be66](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bc1be661dde383598812b92cd9ff03f05462e5cf))
* Added min/max/average rates to previous/current/next day rate events/entities ([58c3488](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/58c34885bc2125074b574112fbef477a56b635bf))
* Added support for custom sensors for tracking the cost of other entities ([54604fd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/54604fdb0c7f24cb65346010f00e299c3dd1e0df))


### BREAKING CHANGES

* The current and previous accumulative gas consumptions meter entity ids have been updated to include
suffixes representing the reported unit of measurement. Any references to these entities will need
to be updated.
* If you are on intelligent tariff and use OHME chargers, then various intelligent features will be
removed. These were incorrectly exposed. Please see
https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/573 for more information

## [9.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.2.0...v9.2.1) (2023-12-20)


### Bug Fixes

* Fixed issue where user agent version was not updated ([6660075](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66600758be135ab0a58a43ec4378ab6026bc6ea1))

# [9.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.1.0...v9.2.0) (2023-12-19)


### Bug Fixes

* Added missing translation for target rate config ([eb7c892](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/eb7c892ed3e05c4233f63b27ef458396b7d33073))
* Fixed issue with target rate when offset is applied twice to next time value ([20a1a8c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/20a1a8c322dda994e3a5cd51222d5c346013702e))
* Updated account config to include instructions for where to find account id and api key ([a409889](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a409889d723297ee0c0211252bc04d1000b2eb27))


### Features

* Added indicator to target rate sensor to indicate if rate information is incomplete and therefore target times cannot be calculated ([28676c3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/28676c38c9da81936137b166dd311ed782f76813))
* Improved how data is retrieved from APIs and added backoff logic when failing to contact APIs ([d461718](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d461718504243bcd0d6e304c85eb21d7967d54fc))

# [9.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.0.2...v9.1.0) (2023-11-28)


### Bug Fixes

* Added checks to ensure current gas consumptions were not negative ([b8418e1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b8418e13636c8a2fee2d960fd22fda8eabfe257c))
* Added defensive logic around loading of local completed intelligent dispatch data ([4049c6d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4049c6d10eb563d2615cbf83ebf30a7303138c19))
* Fixed expectation that charge_in_kwh is available in local intelligent dispatch data ([6e0c3ed](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6e0c3edff68d10fdf447025cb683937b57595721))
* Fixed issue where event entities were not being restored properly ([00ec35c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/00ec35c18767243dd448d1f1f817cabe89bb13ed))
* Fixed octoplus points sensor to not be available for users who have not enrolled on the programme ([3476fae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3476fae9b88b0c235b49e65e871e8e395b4d3682))
* Fixed restoring of attributes on target rate sensor ([7a384ef](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7a384efdbe348d828e8e14fd807fc83563ca2983))


### Features

* Added octopoints_per_kwh to joined saving session events (if known) ([350ad20](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/350ad20ccbae8c0e4360053d2af8bb4098e833d7))

## [9.0.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.0.1...v9.0.2) (2023-11-25)


### Bug Fixes

* Fixed issue with current consumption sensor not working properly in energy dashboard ([08af21b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/08af21b618d092c7a1e548193319dfdbbc9aac6e))
* Fixed issue with not being able to unset price caps that were set when the integration was configured initially ([838f2e3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/838f2e30f6c63290935cd717c4fc21da0fc32f69))
* When using the join saving session service, related data updates are forced in the next cycle ([626c1c1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/626c1c19ef908f45889ea62a108e6d44f8094f87))

## [9.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v9.0.0...v9.0.1) (2023-11-22)


### Bug Fixes

* Fixed issue where all previous day rates are not retrieved for agile tariff ([1ff0ce9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1ff0ce9cc0b641616756b1a4c3c26872966aa26f))
* Fixed issue where restore state was set to invalid unknown value ([24c09d6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/24c09d66e42f8c0e4385e2020ef16fda33dd62ef))
* Fixed refresh_previous_consumption_data for gas to populate kwh data ([e5b3a3e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e5b3a3ecf651eb8b88cfab5eb45bdf9504565c93))
* Removed stale last_updated_timestamp attributes ([763842f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/763842fff41e5e5357acbd5a3d9267813130bc06))
* Updated previous/current/next event rate sensors to not be disabled by default ([e10c6dd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e10c6dd2e1a7753e70ed8dbddd35fb6515f77458))

# [9.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.5.2...v9.0.0) (2023-11-20)


### Bug Fixes

* **custom:** updated value_inc_vat and rates to be in pounds/pence for consistency ([439c081](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/439c08162ff1ac6e2d04572bfbde141c5f717a42))
* Fixed issue calculating off peak costs when rate information isn't available ([fc155a1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fc155a1317fd0a078d45e11eb05b25ef6e9c4aa0))
* Fixed issue when failing to retrieve account during setup ([c9d04fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c9d04fb9573114dc9c4c79846d3b65eac73a4302))
* fixed issue where sensor attributes were always strings when restored after reload/restart ([53964ae](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/53964ae57e9420608651e8a1e3950608edd82c0a))
* Fixed issue where unit of measurement couldn't be changed/converted within HA ([f07da9d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f07da9d47e2ce66534ff1451afb1c2c7d3b4bb54))
* removed all_rates and applicable_rates attributes from rate sensors to fix statistics warning ([280e6d2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/280e6d25fcb18ce17df158734f9cba3cd7d92574))
* updated standing charge attribute on cost sensors to be in pound/pence for consistency ([913336a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/913336a3ecb9e0a3fdccc01132db3e930968a016))


### Features

* Added new events for new and all saving sessions ([b2b44b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b2b44b5697611e48b446a1066c4c7f8a41ef8a32))
* added new sensor for octoplus points ([800fc85](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/800fc8597d981090b87b1f659f924893f7215662))
* Added sensors for available wheel of fortune spins ([6273784](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6273784f03096a484105cb282439efae604d527c))
* Added service for joining a saving session ([01342b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/01342b58851214da6a3559f3d6385916f3f76365))
* Added service for spinning wheel of fortune ([effcc21](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/effcc2147e5266491c3eacb25adeff0c7e673966))
* Added two new attributes to various sensors determining when the underlying data was last retrieved and when the value was last evaluated. These will slowly be added to other entities. ([11f8878](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11f887815eec47c3665e0bb36641ac36da036427))
* created new event entity to capture available and joined octoplus saving session events ([b402c06](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b402c06e4ebe648aa0f4dd0d92da9a26809cdd2f))
* standardised attributes around time periods across the integration ([89a6985](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/89a6985af4647ce4cd7954a7f8d77a60a3260c0d))
* standardised attributes around time periods across the integration ([#535](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/535)) ([7f6712f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7f6712feb7312cbd7260293258435f7d3a1415ce))
* Updated config entry for account to have the account id as the title ([02ef313](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/02ef3131c437fee345a39f8c2a73e5e75acbdeb9))
* updated intelligent sensors to include account id. This is to support future functionality ([57e3d79](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/57e3d7929fddf863e47ba1c2408b3ac8e2acd8a8))
* updated last_calculated_timestamp attributes to last_evaluated for consistency ([702eb4a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/702eb4a42893afe28caeccf4d3add1be99138a1c))
* Updated saving session sensor to include account id. This is to support future functionality ([3136005](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/31360056bc8d95098a85fe6bc349c8a3bb84f415))
* Updated underlying config with some missing fields ([82e4564](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/82e4564bbaf40926a827392f73dc8f08d3fe23b7))
* updated various attributes to be their numberic value instead of strings with symbols ([727db53](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/727db53912eea34d4c778ee2337d4fe9388405d4))


### BREAKING CHANGES

* all_rates and applicable_rates attributes are no longer accessible in rate sensors. All rate
information is available in the events attribute. See
https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/discussions/444 for more information
* Any previous references to valid_from/valid_to,
interval_start/interval_end or from/to have now been changed to
start/end. This change may take a little while to propagate while old
data is replaced. Any reliances on these attribute names will need to be
updated.
* The joined events attribute has been removed from the saving session binary sensor in favour of the event entity
* Any references to last_calculated_timestamp attribute should be updated to last_evaluated
* saving session points sensor has been removed in favour of octoplus points sensor
* Any references to saving session entities will need to be updated based on name change including account id
* Any references to intelligent sensors will need to be updated based on name changes including account id
* All references to value_inc_vat and rates are now in pounds/pence. If you are relying on this
structure, you may need to update your logic
* Standing charge attribute on cost sensors are now in pound/pence. If you are using this, then you may
need to adjust any calculations etc.
* Various attributes have been updated to be numeric instead of strings with symbols (e.g. £1.50 -> 1.50). Any
logic that was used to remove these symbols will now break. In addition, some attributes had raw
representations, which have now been removed. Please review docs for more information.

## [8.5.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.5.1...v8.5.2) (2023-11-08)


### Bug Fixes

* Fixed previous consumption peak/off peak sensors ([b3d4f6f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b3d4f6f876f0d3630bedec350e20c7c7c9f541f5))

## [8.5.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.5.0...v8.5.1) (2023-11-02)


### Bug Fixes

* Fixed retrieving previous electricity consumption for intelligent tariffs ([40651a2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/40651a245dc3b40d84ea0d01ba2df39115f2826a))
* Fixed target rate sensor restoring old settings ([ec40fe2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ec40fe2503d7776c1c9ef6b8ec867aee4011887a))

# [8.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.4...v8.5.0) (2023-10-29)


### Bug Fixes

* Added check when configuring home mini, to make sure home mini support is actually available ([770edc4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/770edc470b2ce0ae675a99598d3985fd3f0beb49))
* Fixed clearing of price caps without needing checkbox ([f5fbc0c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f5fbc0cea9b4f65692a2998c3a3f340ebe65f909))
* Fixed off peak detection for octopus flex (should never be applicable) ([912efd7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/912efd7f7fc4f7d50af665b07c2f80a55b6b7a2a))


### Features

* Added last evaluated attribute to target rate sensor for more clarity ([fd5395d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd5395da9901740983e8d2093396bdbc17c1f6ad))

## [8.4.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.3...v8.4.4) (2023-10-14)


### Bug Fixes

* Added explicit timeout to OE server requests ([b516e4a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b516e4a54774f393d55a46921c2fa511505d5c6d))
* Fixed intelligent coordinator update frequency (thanks @Pixel-Gavin) ([8e1f80c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8e1f80c104405c7adf7b2992256dc87408619d45))
* Fixed update interval for data coordinators to be minutes not hours ([830604d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/830604d3347c56b93fe42e30e0bb875ca025e2e4))

## [8.4.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.2...v8.4.3) (2023-10-12)


### Bug Fixes

* Fixed intelligent settings reverting if multiple changed in quick succession ([0a4c95b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0a4c95badbc29dbe3adf6c65cf480702b819b46f))

## [8.4.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.1...v8.4.2) (2023-10-09)


### Bug Fixes

* Updated minimum version of Home Assistant to 2023.09 ([30157c0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/30157c0a7af8b6c519800393329413a2298e8272))

## [8.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.4.0...v8.4.1) (2023-10-07)


### Bug Fixes

* Fixed error in dispatching sensor ([0799002](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/079900299ce2500b440d32d6e309e03fb2da60cf))

# [8.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.3.0...v8.4.0) (2023-10-07)


### Bug Fixes

* Added additional checks in cost override sensors ([ba41e73](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ba41e7338491b5eceea0780fd343b5106dd16acf))
* Fixed entry already configured error ([6be5ea6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6be5ea6769a3a8f330a5de4892abdf300871e05c))
* Fixed issue where export rates were adjusted during intelligent hours ([df74d13](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/df74d1305a547a88ac7c07230b58a850f24c4528))
* Fixed previous consumption to run calls in parallel ([e621af1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e621af154257ea2285657d16624d025fc292b927))
* Removed tracker tariff potentially looking at wrong API for standing charges ([82fecf1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/82fecf1adde75547b2f9d475291e9bb546dc74ad))


### Features

* Added new sensors and events to expose various rate information ([1e0315e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1e0315e2d585a5d93544dae38b966d15c56b8296))
* Added service to support manually refreshing previous consumption data/costs ([a84a91d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a84a91d96e79bf91520e0329800a8f1372c5a512))

# [8.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.2.1...v8.3.0) (2023-09-23)


### Bug Fixes

* Added service for removing custom external statistics for meters with no active tariff ([2fe1d19](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2fe1d193d71caf23f51c4f74353bb5629e230951))
* **binary-sensor:** Fixed intelligent dispatching sensor not turning on during off peak times ([0901bfd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0901bfdd4177acba3a09e91228a75f2bf4b7dd69))
* Fixed target rate sensor not restoring state between restarts ([75bcc8f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/75bcc8fffda8534bc61b75f2516e5bbd2a236ddb))
* Raise error on startup if account information is not available, which will cause HA to retry ([4799400](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/47994001c979796eef16dd752d99c36d4ac8136d))


### Features

* Added location data to intelligent dispatches ([4e1a9bd](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4e1a9bd2e1d3903d85fe2d73d8d1567b670a38b4))
* Added support to adjust the day offset for previous consumption sensors beyond the previous day ([062ec3f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/062ec3f66d59e335f30c65d00ab3735f4ebcb7fa))
* **sensor:** Added sensor for indicating if rate is currently off peak ([94a5151](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94a5151f15fc4c07ccf5243825972ca32bcdd7f3))
* Separated Home mini electricity and gas refresh rates ([6651ebf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6651ebfe5ebe7ef789aeabfad65c6d81f9f5e345))

# [8.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.1.0...v8.2.0) (2023-08-26)


### Bug Fixes

* Fixed accumulative consumption sensors not starting until 1am ([dd2997b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dd2997b2f85f38d2730c034d32eca43b3ca7a6dd))
* Fixed retrieving standing charges that have no end date ([41b913d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/41b913d3032d3db6ac721567d8a92d71a60a9997))
* Removed unused/undocumented attribute from intelligent dispatching sensor ([56657a2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/56657a23f8c9cfc9f319056d822e9a6d3da6f404))


### Features

* Added repair notification when target rate sensor becomes invalid ([fd52777](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd527774f1e71185affa0ab7e72d30b674723696))
* **config:** Added more validation around target rates, including around agile tariffs ([8a00c1c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8a00c1c2341550e4e8b5e154ddb6fe4d3c45b5eb))

# [8.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v8.0.0...v8.1.0) (2023-08-12)


### Bug Fixes

* Added more checks around coordinators ([31205c5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/31205c5037be9ac8a50cc60d3535592263668df5))
* Fixed issue with accumulative cost sensors when used in the energy dashboard ([3db7228](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3db7228ac9d95f501e14abe96e9554a5437bcd44))
* Moved various sensor updates out of update loop and into state property which should stabilize updates ([662a32b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/662a32b8df00484408c2794aefa5d6ff00d2dfa6))
* Removed coordinator setup skipping if already setup ([54bb347](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/54bb347d56f36ad48ecc73a498f22050dc153040))


### Features

* Change order of rates/applicable rates attributes so they're last on rate sensors ([b4d0c6b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b4d0c6b0744312e42a4cd4e2ed86cc6661e8a2dd))
* Updated intelligent dispatching sensor to include vehicle battery size information and charge point power ([b7e0294](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b7e0294675aee0e4d5d5da7a0b7537cbd4443395))
* Updated planned/completed intelligent dispatches to include charge in kwh ([4fec0cf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4fec0cf2e3dfe9ef95a7dd47a59318725318acf8))

# [8.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.5.2...v8.0.0) (2023-08-05)


### Bug Fixes

* **api-client:** removed tracker fall-back API ([fd095cb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fd095cbc3a06b668c65daf547b220e7d95645ab8))
* Fixed "ignoring invalid device info" error ([c6219d7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c6219d7af3be83d4a44e84f658ba87a6bc818a69))
* **intelligent:** Fixed ready time state when initial value is returned ([8296fce](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8296fce0ab7b156e0be5bcb6131bf6f171177be0))
* Removed empty gas meter devices ([f0c4258](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f0c4258eb28d01b3719bf7bb1671916027d0386f))
* Removed last reset from current demand based on state class warning ([f452ee7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f452ee7665183f8be70ade67c7a6e78d2b2d7876))
* **sensor:** fixed issue with previous rate sensor going unknown when crossing midnight ([45b7e43](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/45b7e43ddd082aeea60cfa7ca681ee2ae9d26ea8))
* **sensors:** Fixed deprecated warning for charge limit sensor ([6b0e894](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6b0e894b9398a2ab079b90717aae865cd66fac15))


### Features

* Added peak/offpeak consumption/cost sensors for current accumlative elec/gas ([e0c756f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e0c756fe57e979a6289f65e7180fe71fb1bebb67))
* Added sensors for current elec/gas accumulative consumption ([d3315a5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d3315a5c86250157e5a242432d0c8935c76598d5))
* Added sensors for current elec/gas accumulative cost ([f6971f3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f6971f3802d4a6840f9b22f77a8545aed0265018))
* Added sensors for current elec/gas accumulative cost ([0dec111](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0dec11124acf00dcc6a887877c3200c05aa7d91c))
* **config:** Added refresh rate configuration for Home Mini ([dbfe805](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dbfe8052df409b9876fb1ac45e4f2ede8eb8ec8c))
* **config:** Improved target rate sensor config to show if an import or export meter is being picked ([e415b41](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e415b4155f43db1bd3fb2134db9fa2535fa3f9a0))
* **sensor:** Added next/previous rate sensors for gas ([dceb784](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dceb78455e7996abc5bff89027fd2b19efeca22c))
* **sensors:** Added functions for retrieving next/previous rates ([79e5471](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/79e5471caa2f61a54b09d90324329362222c4c39))
* **sensor:** updated next/previous electricity sensors to find rates that have a different value to current rate ([37ad6c1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/37ad6c1c82d06dcb4f93fce886ada265258057de))
* **target-rate:** Added ability to invert normal behaviour of target rate sensors when finding target rates ([080d2cc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/080d2cc2c829aaccb805b6b3ed959964aae644e6))
* Updated charges in cost sensors to include raw representation ([e981c27](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e981c2720d6abb561c6b88ca0523d136b38928ab))


### BREAKING CHANGES

* **api-client:** While this shouldn't have a negative effect on anyone, I'm marking the removal of the tracker
fallback API as a breaking change. This is because I believe it's cause bugs to be raised and there
are several threads within the OE forums that don't suggest using it for various reasons
https://forum.octopus.energy/t/finding-the-latest-gas-tracker-api/6021/9. This original tariff that
introduced this work around is now properly supported by the API.
* **sensor:** These sensors no longer look at the next/previous 30 minute rate so behaviour will change for all
tariffs. This is to make them more useful for non agile tariffs. Attributes of these sensors have
also changed. Please review docs for more information.
* **sensor:** The rates attribute on the previous/current/next rate sensors will now contain the previous days
rates. If you are using this attribute, you may need to adjust your use.

## [7.5.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.5.1...v7.5.2) (2023-07-21)


### Bug Fixes

* **sensor:** Fixes to various sensors and how they update their values ([92d8a57](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/92d8a57c5ba65f3ebbb0e9bc92562008f758a3d9))

## [7.5.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.5.0...v7.5.1) (2023-07-20)


### Bug Fixes

* **sensors:** Fixed issue with saving session evaluating incorrectly … ([#317](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/317)) ([66dc168](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/66dc168067fde3363c67809ce90ceb721a34d42f))
* **sensors:** Fixed issue with saving session evaluating incorrectly when data is unavailable ([94a03fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94a03fbf53e2b8539982517d66e84eba8ccb6553))

# [7.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.5...v7.5.0) (2023-07-14)


### Features

* **sensor:** Added various sensors for Octopus Intelligent to support various configurations ([0380377](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/03803772981a812adebe2c6aeb1070192b0e93ba))

## [7.4.5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.4...v7.4.5) (2023-07-04)


### Bug Fixes

* Fixed issue with dispatch times and electricity rates ([7a5b470](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7a5b470e542acc616b4fcc3c30e851195feb052a))

## [7.4.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.3...v7.4.4) (2023-07-01)


### Bug Fixes

* **api-client:** Fixed  api client to handle graphql errors ([78414d2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/78414d2ddf19afea0f55fda59f702d59feb33347))
* **sensor:** Fixed inclusion of intelligent dispatches in consumption costs and pricings ([34ef0e8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/34ef0e8213a773290db997184d8c4b2815ef7350))
* **sensor:** Fixed issue during BST with rate sensors ([dcfd1b6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dcfd1b62d740469ccd8398a796b7d8d4ca35f623))
* **sensor:** Updated retrieving of rates to try more frequently if rates are out of date ([a50e0bc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a50e0bccd2d75286c2eb9ba7666bbd0068938f37))
* Updated various sensors to update via coordinator callback ([16c1c75](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/16c1c750c2d4705a537ace81b002f7bf8f4707e3))

## [7.4.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.2...v7.4.3) (2023-06-16)


### Bug Fixes

* **api_client:** Improved detection of smart meters ([d614210](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d6142108c7e28601f3374c31c288c35c7d8b9f6e))

## [7.4.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.1...v7.4.2) (2023-06-04)


### Bug Fixes

* **binary-sensor:** Fixed next_time on target rate sensors to take account of configured offsets ([9673b4e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9673b4ecaa5881a9d2ec3c9f83c2543882b667b5))
* **sensor:** Fixed recovery of electricity rates if new rates fail to be retrieved ([210f6c4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/210f6c4ed6740c03e6147256c1a533c30e00618f))

## [7.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.4.0...v7.4.1) (2023-06-03)


### Bug Fixes

* **sensors:** Fixed handling the retrieving of tracker tariff data for non tracker tariffs ([6c277d4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6c277d4bbf26c347418b68604d7efb87c0c4fb49))

# [7.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.3.0...v7.4.0) (2023-06-03)


### Bug Fixes

* **config:** Updated mini configuration to have link to minimise confusion ([9d277af](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9d277afeb3a6b8d4bced614ee95ffaeacfb258a5))
* Updated api client to throw errors based on responses and caught appropriately in the coordinators ([c1c031a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c1c031a57587651b3ec34658e224cee75e3e0e17))


### Features

* **sensors:** Updated sensors to appear in disabled state if account info determines no smart meter is present ([b1f123a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b1f123a641defd9abd7fcaf6e6e335dbe575860e))

# [7.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.2.0...v7.3.0) (2023-05-28)


### Features

* **binary-sensor:** Added the ability to force target rate sensors to find the latest applicable set of rates ([dc2e456](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dc2e456e257404c8a29b9444666f6406b3fdec38))

# [7.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.3...v7.2.0) (2023-05-21)


### Bug Fixes

* Fixed issue when Octopus Home Mini data can't be retrieved for 1 week or beyond. ([1c05ea7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1c05ea737f5154f75938173bb0e7f93dcba1e859))
* **sensor:** Added missing last reset attribute restoration ([d596b3b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d596b3b005f13bde13096dccf00d4dc3a3bf8309))
* **sensor:** Fixed last_reset of previous electricity consumption/cost ([3996ab7](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3996ab7258b02afb157e514384b7c6b5a20db2d0))


### Features

* **sensor:** Added support for comparing previous consumption cost with another tariff ([44ef244](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/44ef244d90192a824b9a21982a760229713aa460))

## [7.1.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.2...v7.1.3) (2023-05-13)


### Bug Fixes

* **sensor:** Fixed peak/off peak calculations when off peak cost exceeds peak costs ([317e916](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/317e916602ca005827cdd351ffd67054fcdb620c))

## [7.1.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.1...v7.1.2) (2023-05-11)


### Bug Fixes

* **sensor:** Added additional checks around previous consumptions and costs when data is not available ([28b31b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/28b31b5e4d884d80ede288e5f22c3c69484a2ed1))

## [7.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.1.0...v7.1.1) (2023-05-11)


### Bug Fixes

* Added check for when standing charge can't be retrieved ([383ec65](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/383ec6534f4d7dbb500d13bc4e5e22a7c626eb4c))
* Added more checks around retrieving previous rates and consumption ([a1ec6fe](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a1ec6fe139c81532a25ed4048acaef0fcc70127d))

# [7.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v7.0.0...v7.1.0) (2023-05-11)


### Bug Fixes

* **sensor:** Fixed icon for previous gas consumption sensor ([91f9096](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/91f909636ae02672507708ba2fce4337c9a68e40))
* **sensor:** Fixed rate sensors not having long term statistics ([07db8f8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/07db8f85a1ddd153ce04564aa87195a1dda58be3))


### Features

* **config:** Added detail around target rate hours ([9b084c9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/9b084c99601afb7d22ccae27fba7aa287286022a))
* **sensor:** Added disabled sensors for representing electricity peak/off peak consumption and cost for previous day ([76de3fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/76de3fbfa8cba04a5b7186c1d4702a54b296108b))
* **sensor:** Added min/max/average rates to electricity rate sensors ([df82983](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/df8298350e4ded78c306ba40acdaa89985c4a85f))
* **sensors:** Added support for external statistics for previous consumption sensors (see energy dashboard instructions) ([4d4e460](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4d4e46002b3c8835bea794ba61f44de556554121))

# [7.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.6.1...v7.0.0) (2023-04-18)


### Bug Fixes

* Added check when gas rates are unavailable ([b90131a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b90131a58d9be3011507ae6cac9c3518ae971f43))
* fixed entity names to match documentation and include octopus_energy domain ([f6f589b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f6f589b93990740d236994a08acfdd69cb7a5fad))


### BREAKING CHANGES

* The name of the entity should stay how it was formed when the entities were first created, however
the names might change in either your HA instance or other dependent services.

## [6.6.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.6.0...v6.6.1) (2023-04-10)


### Bug Fixes

* Fixed average cost on target rate sensors to handle when no rates are available ([b67989e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b67989e5e28df55a1bba288b0592d60bee2fb20e))

# [6.6.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.5.0...v6.6.0) (2023-04-08)


### Bug Fixes

* Fixed fallback onto make/model if import/export meter not available ([2940e73](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2940e73361d924bcdcda85f6d7b8fc0993e8cd5e))


### Features

* **binary-sensor:** Added overall average, min and max costs for target rate sensors ([060ea63](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/060ea632a1cb6c66e51c9bd85842dcf39fb1ab3e))

# [6.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.4.1...v6.5.0) (2023-04-08)


### Bug Fixes

* **config:** Updated target rate sensor to support type and name to be updated ([4888976](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/48889765161abccaa57497b17fff51f1543635e4))
* Fixed consumption sensors to not be created for users with no smart meters ([34003f4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/34003f400132b7cffa9b930d17520b4282601db0))
* Updated tariff extraction to be more flexible with beta tariffs (e.g V2G) ([3a9c2fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3a9c2fb98378f7fbb8f0d60e4ab6ded9f26bcfd3))


### Features

* **binary-sensor:** Added cost attributes to target rate sensors ([98c0db9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/98c0db96a418c76707081303b8e67c89d468b70b))
* **sensor:** Updated saving session entity to display current event start/end/duration ([97b49d0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/97b49d03253cc5846ac48a6aee5f011f9614a9ee))
* Update device to include make, model and firmware where available ([f65c34a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f65c34aa524360e8b203e42361adac23ec06a2de))

## [6.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.4.0...v6.4.1) (2023-04-01)


### Bug Fixes

* Added more robust checks when retrieving account information ([5898f41](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/5898f41b936d453e07c0f66c2c7826096645abe5))
* **api-client:** Added more checks for when meters have no agreements ([ee86fe0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ee86fe0117dd39bc14ad08d4a1f2544f66a0dcd3))

# [6.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.3.2...v6.4.0) (2023-04-01)


### Features

* **config:** Added checks for tariffs to report repair errors if not valid ([3f7dc86](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3f7dc86789d6fbfe629f935fc8558094e4e0c510))

## [6.3.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.3.1...v6.3.2) (2023-03-29)


### Bug Fixes

* Added missing requirement for repairs ([69a4bcb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/69a4bcb5af30a8fc91d09fa53c48aa4ff8770702))
* Updated current rate sensors to indicate if prices are capped ([1368349](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/13683499a590fb30fa0afe6fbefd3a91350de519))

## [6.3.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.3.0...v6.3.1) (2023-03-28)


### Bug Fixes

* Handle when account cant be found and display repair message ([7c7801a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7c7801a77f9416dd680580dec66e54de2af712a2))

# [6.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.2.0...v6.3.0) (2023-03-21)


### Bug Fixes

* Updated diagnostics to redact device id ([093fc5a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/093fc5aa1b70110130f1ee8a7063aeb33868731d))


### Features

* Updated account to retrieve tariff product code ([3cdb4b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3cdb4b5378e3c9175a2d1b8d3f9569aa06c8557c))

# [6.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.1.1...v6.2.0) (2023-03-18)


### Bug Fixes

* **binary-sensor:** Fixed offset incorrectly being applied to target times upon discovery ([94ed934](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94ed934300d6996601766e5b9f1515df801954d1))


### Features

* **sensor:** Updated names of sensors to not include Octopus Energy ([07fdd8b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/07fdd8b86dec3d92a236f64086cddcdba963919c))

## [6.1.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.1.0...v6.1.1) (2023-03-18)


### Bug Fixes

* **sensor:** Fixed kwh gas sensor device class ([6a25058](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6a2505809a667347f7599dbbed614f4a7636bcd6))

# [6.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.0.1...v6.1.0) (2023-03-18)


### Bug Fixes

* **binary-sensor:** Fixed issue with offset being applied twice for "next_time" in target rate sensors ([d8596fb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d8596fb8ce5c22993d55d6dae426b818639b20a0))


### Features

* **sensor:** Added current consumption for gas through octopus mini ([df7b3dc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/df7b3dc6f13806e6f87d6eb63b98eac1974d5b47))
* **sensor:** Added the ability to configure current gas consumption for octopus mini ([6c6868a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/6c6868a5ee54924c47300198d66b4fc149359daf))

## [6.0.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v6.0.0...v6.0.1) (2023-03-02)


### Bug Fixes

* **sensor:** Fixed handling of tracker products ([2911ebb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2911ebb43d8126d988f90cda2b1cd2b7409420b0))
* **sensor:** Fixed rate sensors to update on the half hour ([2e2d795](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2e2d79532f48f82bcf6131950be4bd33df7d3139))

# [6.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.4.1...v6.0.0) (2023-02-25)


### Bug Fixes

* **fix(sensor):** Added "export" to export based sensors ([3df28bb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3df28bb298dd31bbad0b226c775f22e886164376))


### Features

* Added option to configure gas calorific value ([d3e3333](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d3e3333c68813face9bff1e89409774e7275eb61))
* Added price cap configuration ([fdd856a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fdd856ac94a8d03649ace52886e485061fd0fde8))
* Added support for home mini ([3f811e3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3f811e3c811ff4471469de1745b3fb83584ff9b2))


### BREAKING CHANGES

* **sensor:** The name of export based electricity sensors have been updated to include the term "export". This is to make it more discoverable for new users.

## [5.4.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.4.0...v5.4.1) (2023-02-07)


### Bug Fixes

* **api-client:** Fixed tracker lookup logic ([c59085a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c59085aefb7afe51ca7ac5f6763969a169e5a614))

# [5.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.3.1...v5.4.0) (2023-02-05)


### Bug Fixes

* **sensor:** Fixed restoring attributes from restart ([fdfd72e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fdfd72e5c16f362c5a10a08e4926bcd9d816cc8a))
* **sensor:** Fixed restoring attributes so they're not read only ([bbb3ef8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bbb3ef840f48dd10aaad670c6999a99ea6c96eeb))


### Features

* **api_client:** Updated rates and standing charge logic to route to tracker endpoint where appropriate ([3be23d0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/3be23d075ff36201e89f5ed3ad8aba6eafda330e))

## [5.3.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.3.0...v5.3.1) (2023-01-28)


### Bug Fixes

* **sensor:** Fixed gas rates to work with tracker products ([b2419dc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/b2419dc2179a8e54081cd0569d60b2ef19a0165b))

# [5.3.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.2.1...v5.3.0) (2023-01-20)


### Bug Fixes

* Added more defensive code for account retrieval ([a01513c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a01513c3aac33df3e1f45b4083a4112b6d075999))
* **binary-sensor:** Updated target rates to skip if not enough applicable rates exist for specified period ([e2a2376](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/e2a237697df595d5b734aa8b5dc2add5261abfdb))
* **sensor:** Fixed restoring rate sensors to not default to 0. ([85c38cc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/85c38cc7d32f1d6bc586c2416fdb8cf8444649df))


### Features

* **binary-sensor:** Added next duration in minutes for target rates ([bae76b2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/bae76b2bb1703b5849751c4e4cf2649cc1a659e1))
* **binary-sensor:** Added rolling target as attribute ([f1eaac9](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/f1eaac9bb08b933c091776d908b24749adf99ed1))
* **binary-sensor:** Updated target rate sensors to display how long the current active block is ([2bd037b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2bd037be741d4f4e7d0577e13e0f76798bfb7bdb))
* **sensor:** Added next rate sensor for electricity meters ([8167baf](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8167baf11892609219f02f31b9bf4070c7347d1f))

## [5.2.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.2.0...v5.2.1) (2023-01-16)


### Bug Fixes

* **binary-sensor:** Fixed issues with using update service through automations ([70d101d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/70d101d0709665d2e37b851d25e779ce2d7b2718))

# [5.2.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.1.0...v5.2.0) (2023-01-15)


### Bug Fixes

* **binary-sensor:** Fixed issue when start/end spans multiple dates ([a4d9550](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a4d9550d9453b476378efc62a2b37857138139b6))
* Removed "export" from name of target rate sensors ([1b22958](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1b229584de5ebf64612d57b36e8e3e1e350cb3f3))


### Features

* Added service for updating target rate config ([4c6a2bb](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4c6a2bbd0629ff2628076c8ec11631e69b4d5310))
* **binary-sensor:** Added support for end time being before start time ([8431801](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/8431801f5be7519bba6c5ac6ab2cdc2c61c3abad))
* **sensor:** Added new sensor to expose gas as kwh ([d365c45](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/d365c4517347059c8b9ed2b4ddff17afb01bcee7))

# [5.1.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v5.0.0...v5.1.0) (2022-12-28)


### Bug Fixes

* **sensor:** Added back m3/kWh calculations for gas sensors ([820abde](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/820abde97b05842f64f24e4a85654f68594b3b6f))
* **sensor:** Added last_reset attribute to cost/reading sensors ([2861796](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/286179692651f24308a26d7cb769b27086d3885b))
* **sensor:** Removed SMETS1 configuration as it's no longer used ([eb49841](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/eb498411d3f3f8d18fad573acc196acf7d4cb155))
* **sensor:** Updated min consumption data to be in calculation ([4f55e8d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4f55e8deccd01c22ab743fe6b804daf2345a82e9))


### Features

* **binary-sensor:** Updated next saving session to include end date and duration in minutes ([4d78a00](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4d78a00560eddc5908303495207edaddf606875c))
* **sensor:** Added sensors for current standing charges for electricity and gas ([24641f8](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/24641f82847dec5c15a5273099fb9a0ca7d22cc9))
* **sensor:** Updated standing charge to be more specific ([521d9fc](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/521d9fcf51736f7ae9e20411d0fdebc46bc07699))

# [5.0.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.7.1...v5.0.0) (2022-12-17)


### Bug Fixes

* **sensor:** Fixed state class for sensors to "total" ([fda8df6](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/fda8df6b1b0e7e65cefb7ce245088bc87d10b56b))


### BREAKING CHANGES

* **sensor:** This fix causes long term statistics for the sensors to break. To rectify this, visit https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/108

## [4.7.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.7.0...v4.7.1) (2022-12-08)


### Bug Fixes

* **sensor:** Only set latest date on gas rate sensor if rates are successfully retrieved. ([11f275f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/11f275f63aba585aabb66a9d3c180e35817f0434))

# [4.7.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.4...v4.7.0) (2022-12-04)


### Bug Fixes

* **binary-sensor:** Fixed issue with rates mismatch and multiple meters ([1050fd4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1050fd4ab2845db0c76504fedd7df623f552968b))
* **binary-sensor:** Updated target rate sensors to work with export based meters ([0d4757b](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/0d4757b82dbeaf69bd5d8daedf7c930a00f477db))
* **sensor:** Fixed issue with rates update ([a2fead5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/a2fead550b49467863ea1ed533bee5ecbe86deb0))
* **sensor:** Updated sensors to support being restored after reboots ([1f04b14](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/1f04b14f7074a7ed7afadcd2faefd3e7288e2c76))


### Features

* **binary-sensor:** Added sensor for when joined saving sessions is active ([93dbd9e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/93dbd9e025c173c62b2ef46d201491a6456940a4))
* **sensor:** Added saving sessions points sensor ([94e465c](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/94e465cb1957de719e6ac80a75d75a58e84d625e))

## [4.6.4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.3...v4.6.4) (2022-10-27)


### Bug Fixes

* Fixed issue with increased debug logging. Also reduced default logging to debug level ([2add166](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2add166b200b89320d5590102ff1a110bcc24fa1))

## [4.6.3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.2...v4.6.3) (2022-10-26)


### Bug Fixes

* Added additional logging around target rates ([6228020](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/62280200ad3cc1d81f22055c637e81ca219fe15c))

## [4.6.2](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.1...v4.6.2) (2022-10-25)


### Bug Fixes

* **api-client:** Fixed api_client incorrectly absorbing not found requests ([2a96c51](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/2a96c515d0d2e7aff2eadf3618edf1fc84a71c09))
* **sensor:** Update rate sensors to report back None if no current rate can be found ([86376ac](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/86376ac1dd9b44b1d499aef8158344943041f891))

## [4.6.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.6.0...v4.6.1) (2022-10-22)


### Bug Fixes

* **config:** Updated rates retrieval to take account of local time ([ccf67ee](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/ccf67ee4707055dad2e29f4ab7732d4dd9ce1a95))

# [4.6.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.5.1...v4.6.0) (2022-10-16)


### Bug Fixes

* **binary-sensor:** Fixed issue when sensor is active and calculated on the end date of the last rate ([917f9b5](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/917f9b57156dc4ca1c9f381d688d3211a317433a))


### Features

* **api-client:** Moved conversion of rates to 30 minute increments to separate testable function ([412599f](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/412599f3a3b37c018d680563c82fdd7cb3cecafa))

## [4.5.1](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.5.0...v4.5.1) (2022-10-02)


### Bug Fixes

* **binary-sensor:** Fixed text of rolling_target to reflect behaviour ([4840ff3](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4840ff36b29139d4ddec047dcd70fa959f1247cb))
* **config:** Fixed issue with configuring when star/end/offset not set ([4916f68](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/4916f6852b2ba2aeafa5fba2814b6986f0257400))
* **config:** Fixed loading binary sensor when start/end is not set ([dcafda4](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/dcafda4e239f443051685b2773943a5f9ca3e0a8))

# [4.5.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.4.0...v4.5.0) (2022-10-01)


### Bug Fixes

* **binary-sensor:** Fixed issue when start/end time isn't set ([7ab9b2d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/7ab9b2dff3220ce060db51d321fac4f6edafda8f))
* Fixed day/night times for economy 7 tariffs when using a smart meter. Thanks [@696](https://github.com/696)GrocuttT  ([c860a8a](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/c860a8a3eaaf0ca1a03059d1be87e51d4cc36831))
* Updated consumption sensors to wait for more than 2 charges to be present ([aa97647](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/aa97647ae407ddb75bc0c0fa2ccdb878f55ab47e))


### Features

* **binary-sensor:** Added facility to restrict target rates sensors from only reaching the target once a day ([67d2993](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/67d299354fd16dc7303837e292ed3aa73f5ea645))

# [4.4.0](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/compare/v4.3.0...v4.4.0) (2022-07-23)


### Features

* **device:** Added debug logging for account information (not redacted) ([576c93d](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/576c93d5e9d589e53140866a74cca27f22626fc4))
* **device:** Added support to download diagnostics which includes redacted account information ([01fdf4e](https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/commit/01fdf4e1b68822461813c719bb7756c12e9aabcb))

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

# HRA Recycling

[![buymecoffee][buymecoffeebadge]][buymecoffee]
[![validate_url][validate_badge]][validate_url]
[![Discord](https://img.shields.io/badge/Discord-mr--raw%237095-blue?logo=discord)](https://discord.com/users/303915063142776832)

## What is this?

This is a Home Assistant integration for the Norwegian waste collection company HRA (Hadeland Ringerike Avfallsselskap). It tracks the next pickup date for each waste fraction at your address, and can add all upcoming pickups to a Home Assistant calendar.

## Entities

One sensor per fraction, each with `device_class: date` (state is the next pickup date):

| Entity | Fraction |
| --- | --- |
| `sensor.hra_recycling_restavfall` | Residual waste |
| `sensor.hra_recycling_matavfall` | Food waste |
| `sensor.hra_recycling_papir_papp_og_kartong` | Paper and cardboard |
| `sensor.hra_recycling_plastemballasje` | Plastic packaging |
| `sensor.hra_recycling_glass_og_metallemballasje` | Glass and metal |

Each sensor also exposes two attributes:

- `date` — the next pickup date in ISO format
- `days_until` — days from today until that pickup, recalculated at midnight

Plus an optional calendar, `calendar.hra_recycling_hentekalender`, holding every upcoming pickup as an all-day event.

## Installation

Setup and configuration is done entirely in the UI. Enter your address in the format `Rådhusvegen 39, 2770 JAREN`; the integration resolves it against the HRA API and pulls the next 12 weeks of pickups, refreshing every 6 hours.

Under **Settings → Devices & Services → HRA Recycling → Configure** you can change:

- **Fractions to track** — one sensor per selected fraction, listing whatever your address actually has a schedule for. Unselecting a fraction removes its sensor.
- **Calendar** — on or off. Switching it off removes the calendar entity.
- **Weeks to fetch** — 1 to 52, default 12. This sets how far ahead the calendar reaches; the sensors only ever show the next pickup.

Version plans
- [x] 0.1.0 First release. Will have basic functionality. All the fractions will be shown. User mistakes will not be accounted for. This will break the integration and throw errors around.
- [x] 0.1.1 Small changes to the code. Did some refactoring. Using httpx instead of aiohttp.
- [x] 0.1.2 Fixed a templating issue in the README. Preparing for more customization in the setup process.
- [x] 0.4.0 Switched from HTML scraping to the JSON API. Added the pickup calendar and translated entity names.
- [x] 0.5.0 Sensors are proper `date` entities, `days_until` refreshes at midnight, options can be changed after setup, and one address can only be added once.
- [x] 0.6.0 Entities keep serving the last known schedule when a refresh fails, with a shorter retry after an error. Modernised internals: `runtime_data`, an explicit coordinator config entry, a shared base entity, `icons.json` and diagnostics.
- [x] 0.7.0 Choose which fractions to track and how many weeks to fetch, both from the options flow.
- [ ] 1.0.0 Final release. The integration has been thorougly tested.

## Examples

This template sensor shows how long until the next pickup, whichever fraction that is:

```yaml
template:
  - sensor:
      - name: "Days Until Garbage Pickup"
        state: >
          {% set sensors = [
            'sensor.hra_recycling_restavfall',
            'sensor.hra_recycling_matavfall',
            'sensor.hra_recycling_plastemballasje',
            'sensor.hra_recycling_glass_og_metallemballasje',
            'sensor.hra_recycling_papir_papp_og_kartong'
          ] %}
          {% set days = sensors | map('state_attr', 'days_until') | reject('none') | list %}
          {% if days %}
            {{ days | min }}
          {% else %}
            unknown
          {% endif %}
```

This automation sends a notification at 18:00 the day before a pickup (remember to change the notify target):

``` yaml
automation:
  - alias: Notify the day before garbage pickup
    description: Sends a notification at 18:00 the day before the next residual waste pickup
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.hra_recycling_restavfall', 'days_until') == 1 }}"
    action:
      - service: notify.<mobile_phone>
        data:
          message: "Reminder: Garbage pickup is tomorrow."
          title: "Pickup Reminder"
    mode: single

```

## Contact

If you have any questions, feel free to reach out to me on [Discord](https://discord.com/users/303915063142776832)

[hra_recycle]: https://github.com/mr-raw/hra_recycling
[buymecoffee]: https://www.buymeacoffee.com/erikraae
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg
[validate_url]: https://github.com/mr-raw/hra_recycling/actions/workflows/validate.yml
[validate_badge]: https://github.com/mr-raw/hra_recycling/actions/workflows/validate.yml/badge.svg?branch=master

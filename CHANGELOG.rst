Changelog
=========

- :feature:`-` Binary sensors for the wave's direction: ``falling`` mirrors
  ``rising``, and ``rising_step`` and ``falling_step`` follow the stepped
  target. The stepped ones are on only in an interval where the target
  changes, so they stay off across the flat top and bottom of the wave.
- :feature:`-` **Breaking**: the *visual* sensor is replaced by a *chart*
  image entity (``image.daily_temperature_wave_chart``), which the built-in
  Picture Entity card shows: today's wave, the stepped target, solar noon and
  now. Its ``points`` attribute is today's curve, as before.
- :feature:`-` The stepwise forecast sensor has a ``schedule`` attribute:
  today, midnight to midnight, with an entry only where the temperature
  changes, for setting up a thermostat schedule.
- :support:`-` ``docs/dashboard.md``: cards to graph the wave against measured
  temperatures (ApexCharts or History graph) and to show the schedule as a
  table (Markdown).
- :bug:`2` The integration loads: ``constants.py`` no longer fails on import,
  and the ``binary_sensor`` platform exists.
- :bug:`1` The config flow works: a stray handler that replaced it is gone,
  its fields have labels and help text, and temperatures are compared in
  Celsius (``80F`` vs ``25C``) rather than as strings.
- :bug:`-` The wave peaks at solar noon and bottoms out at solar midnight (it
  used to peak 6 hours late), and the 7-day forecast's high and low differ.
- :bug:`-` Solar noon is calculated for each day from the Home Assistant
  location, rather than around midnight from ``sun.sun``.
- :bug:`-` Fahrenheit temperatures (e.g. ``68F``) are converted, and
  temperatures follow the Home Assistant unit system.
- :bug:`-` Changing options takes effect (the entry reloads), and the solar
  noon override can be cleared.
- :feature:`-` **Breaking**: *wave spread* is now *peak sharpness*: the wave
  always repeats every 24 hours, and values above 1.0 sharpen the warm peak.
  Existing values give a different curve.
- :feature:`-` **Breaking**: the *unit system* option is removed; sensors are
  temperature sensors, shown in the Home Assistant unit system.
- :feature:`-` **Breaking**: forecast and chart data moved from the state
  (which was over Home Assistant's 255-character limit) to attributes; the
  states are now temperatures.
- :feature:`-` Stepwise sensors hold each value for the *step interval*, so
  they line up with thermostat schedules.
- :feature:`-` Entities belong to a device named after the entry, and more
  than one entry can be added.
- :support:`-` Tests use ``pytest-homeassistant-custom-component`` and test
  the integration itself; the project follows MinchinWeb's Python style
  guide (ruff, uv, invoke).

- :release:`1.0.0 <2025-12-24>`
- :feature:`-` Initial release: sine-wave temperature sensors (current,
  stepwise, 24-hour and 7-day forecasts, visualisation data), configurable
  through the UI.

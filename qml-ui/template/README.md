# Template GUI

Example VESC package that installs a custom GUI onto the controller. Any VESC
Tool that connects afterwards shows the GUI as its own tab: desktop, Android and
iPhone all render the same QML text.

## What it shows

- Battery voltage, ERPM, motor current and MOS temperature, polled at 10 Hz.
- A duty-cycle slider that only reaches the motor while the handle is held.
- A readout of custom app data, if a LispBM script on the device sends any.

## Install

1. Build the package: `make` (writes `template.vescpkg`).
2. In VESC Tool, open **Packages**, choose **Install from file**, and pick the
   `.vescpkg`. On a phone, use the same screen in the mobile app.
3. Reconnect. The GUI appears as a tab next to the standard pages.

Remove it with **Packages** → **Uninstall**; that erases the QML flash region.

## Safety

The slider commands duty cycle. Hold the wheel off the ground the first time, and
confirm the motor stops when you release the handle.

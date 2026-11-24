# VESC Express LispBM extensions (generated)

Every function the **VESC Express** (ESP32) firmware registers for LispBM, extracted by
`gen_express_extensions.py` from `lbm_add_extension("name", handler)` calls in the
vesc_express source. Signatures come from the `// (name arg ...)` or `signature (...)`
comment above each C handler where the firmware author wrote one.

Source: a `vesc_express` checkout (path passed with `--express-root`).  
Unique names: **277**, of which **56** carry a signature in the
source. 336 registrations across 6 modules.

Regenerate after updating the firmware checkout:

```sh
python3 gen_express_extensions.py --express-root /path/to/vesc_express
```

## How to use this file

- This is the **Express-only** surface: display, WiFi/TCP, BLE, NVS, crypto, image and
  board extensions that do not exist on an ESC. The shared language lives in `ref/`
  and the ESC-side API in `ref/vesc-esc-extensions.md`; `../README.md` in the bldc
  checkout is the prose reference for names common to both.
- A registration here means the name exists **in the firmware version you are reading**,
  not that it exists on your board: some are behind `#if` guards (shown inline) and
  some live in one board's `hwconf/` file.
- An empty Signature column is not an error: that handler has no signature comment in
  the C source. Read the body for argument order and return values:
  `grep -n "<handler>" <file>`.

## Modules

| Module | Unique names | Registrations | File(s) |
|---|---|---|---|
| Core (main/) | 197 | 197 | `main/lbm_color_extensions.c`, `main/lispif_vesc_extensions.c` |
| WiFi / TCP | 14 | 14 | `main/wifi/lispif_wifi_extensions.c` |
| BLE | 11 | 11 | `main/ble/lispif_ble_extensions.c` |
| Display | 11 | 20 | `main/display/disp_icna3306.c`, `main/display/disp_ili9341.c`, `main/display/disp_ili9488.c`, `main/display/disp_sh8501b.c`, `main/display/disp_ssd1351.c`, `main/display/disp_st7735.c`, `main/display/disp_st7789.c`, `main/display/lispif_disp_extensions.c` |
| RGB LED | 5 | 5 | `main/rgbled/lispif_rgbled_extensions.c` |
| Board-specific (hwconf/) | 42 | 89 | `main/hwconf/trampa/bms_rb/hw_bms_rb.c`, `main/hwconf/trampa/hw_disp_v1.c`, `main/hwconf/vesc/scope/hw_scope.c`, `main/hwconf/vesc/vbms16/hw_vbms16.c`, `main/hwconf/vesc/vbms32/hw_vbms32.c`, `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c`, `main/hwconf/vesc/vdisp_dual/hw_vdisp_dual.c` |

## Core (main/)

| Name | Signature | Source |
|---|---|---|
| `color-make` |  | `main/lbm_color_extensions.c:330` |
| `color-split` |  | `main/lbm_color_extensions.c:331` |
| `color-mix` |  | `main/lbm_color_extensions.c:332` |
| `color-add` |  | `main/lbm_color_extensions.c:333` |
| `color-sub` |  | `main/lbm_color_extensions.c:334` |
| `color-scale` |  | `main/lbm_color_extensions.c:335` |

### Various commands

| Name | Signature | Source |
|---|---|---|
| `print` |  | `main/lispif_vesc_extensions.c:6415` |
| `set-print-prefix` |  | `main/lispif_vesc_extensions.c:6416` |
| `set-fw-name` |  | `main/lispif_vesc_extensions.c:6417` |
| `puts` |  | `main/lispif_vesc_extensions.c:6418` |
| `get-bms-val` |  | `main/lispif_vesc_extensions.c:6419` |
| `set-bms-val` |  | `main/lispif_vesc_extensions.c:6420` |
| `send-bms-can` |  | `main/lispif_vesc_extensions.c:6421` |
| `set-bms-chg-allowed` |  | `main/lispif_vesc_extensions.c:6422` |
| `bms-force-balance` |  | `main/lispif_vesc_extensions.c:6423` |
| `bms-zero-offset` |  | `main/lispif_vesc_extensions.c:6424` |
| `bms-st` | (bms-st optCanId) -> (ok_ic ok_all cell_num (ok no-bal bal) ...) | `main/lispif_vesc_extensions.c:6425` |
| `get-adc` |  | `main/lispif_vesc_extensions.c:6426` |
| `systime` |  | `main/lispif_vesc_extensions.c:6427` |
| `secs-since` |  | `main/lispif_vesc_extensions.c:6428` |
| `event-enable` |  | `main/lispif_vesc_extensions.c:6429` |
| `send-data` |  | `main/lispif_vesc_extensions.c:6430` |
| `recv-data` |  | `main/lispif_vesc_extensions.c:6431` |
| `sysinfo` |  | `main/lispif_vesc_extensions.c:6432` |
| `import` |  | `main/lispif_vesc_extensions.c:6433` |
| `main-init-done` |  | `main/lispif_vesc_extensions.c:6434` |
| `crc16` |  | `main/lispif_vesc_extensions.c:6435` |
| `crc32` |  | `main/lispif_vesc_extensions.c:6436` |
| `buf-resize` |  | `main/lispif_vesc_extensions.c:6437` |

### Configuration

| Name | Signature | Source |
|---|---|---|
| `conf-get` |  | `main/lispif_vesc_extensions.c:6440` |
| `conf-set` |  | `main/lispif_vesc_extensions.c:6441` |
| `conf-store` |  | `main/lispif_vesc_extensions.c:6442` |
| `reboot` |  | `main/lispif_vesc_extensions.c:6443` |

### EEPROM

| Name | Signature | Source |
|---|---|---|
| `eeprom-store-f` |  | `main/lispif_vesc_extensions.c:6446` |
| `eeprom-read-f` |  | `main/lispif_vesc_extensions.c:6447` |
| `eeprom-store-i` |  | `main/lispif_vesc_extensions.c:6448` |
| `eeprom-read-i` |  | `main/lispif_vesc_extensions.c:6449` |
| `eeprom-erase` |  | `main/lispif_vesc_extensions.c:6450` |

### CAN-comands

| Name | Signature | Source |
|---|---|---|
| `can-start` |  | `main/lispif_vesc_extensions.c:6453` |
| `can-stop` |  | `main/lispif_vesc_extensions.c:6454` |
| `can-use-vesc` |  | `main/lispif_vesc_extensions.c:6455` |
| `can-scan` |  | `main/lispif_vesc_extensions.c:6456` |
| `can-ping` |  | `main/lispif_vesc_extensions.c:6457` |
| `can-send-sid` |  | `main/lispif_vesc_extensions.c:6458` |
| `can-send-eid` |  | `main/lispif_vesc_extensions.c:6459` |
| `can-recv-sid` |  | `main/lispif_vesc_extensions.c:6460` |
| `can-recv-eid` |  | `main/lispif_vesc_extensions.c:6461` |
| `can-cmd` |  | `main/lispif_vesc_extensions.c:6462` |
| `can-list-devs` |  | `main/lispif_vesc_extensions.c:6463` |
| `can-local-id` |  | `main/lispif_vesc_extensions.c:6464` |
| `can-update-baud` |  | `main/lispif_vesc_extensions.c:6465` |
| `can-msg-age` |  | `main/lispif_vesc_extensions.c:6467` |
| `canget-current` |  | `main/lispif_vesc_extensions.c:6468` |
| `canget-current-dir` |  | `main/lispif_vesc_extensions.c:6469` |
| `canget-current-in` |  | `main/lispif_vesc_extensions.c:6470` |
| `canget-duty` |  | `main/lispif_vesc_extensions.c:6471` |
| `canget-rpm` |  | `main/lispif_vesc_extensions.c:6472` |
| `canget-temp-fet` |  | `main/lispif_vesc_extensions.c:6473` |
| `canget-temp-motor` |  | `main/lispif_vesc_extensions.c:6474` |
| `canget-speed` |  | `main/lispif_vesc_extensions.c:6475` |
| `canget-dist` |  | `main/lispif_vesc_extensions.c:6476` |
| `canget-ppm` |  | `main/lispif_vesc_extensions.c:6477` |
| `canget-adc` |  | `main/lispif_vesc_extensions.c:6478` |
| `canget-vin` |  | `main/lispif_vesc_extensions.c:6479` |
| `canset-current` |  | `main/lispif_vesc_extensions.c:6481` |
| `canset-current-rel` |  | `main/lispif_vesc_extensions.c:6482` |
| `canset-duty` |  | `main/lispif_vesc_extensions.c:6483` |
| `canset-brake` |  | `main/lispif_vesc_extensions.c:6484` |
| `canset-brake-rel` |  | `main/lispif_vesc_extensions.c:6485` |
| `canset-rpm` |  | `main/lispif_vesc_extensions.c:6486` |
| `canset-pos` |  | `main/lispif_vesc_extensions.c:6487` |

### I2C

| Name | Signature | Source |
|---|---|---|
| `i2c-start` |  | `main/lispif_vesc_extensions.c:6491` |
| `i2c-tx-rx` |  | `main/lispif_vesc_extensions.c:6492` |
| `i2c-detect-addr` |  | `main/lispif_vesc_extensions.c:6493` |

### GPIO

| Name | Signature | Source |
|---|---|---|
| `gpio-configure` |  | `main/lispif_vesc_extensions.c:6496` |
| `gpio-write` |  | `main/lispif_vesc_extensions.c:6497` |
| `gpio-read` |  | `main/lispif_vesc_extensions.c:6498` |
| `gpio-hold` |  | `main/lispif_vesc_extensions.c:6499` |
| `gpio-hold-deepsleep` |  | `main/lispif_vesc_extensions.c:6500` |

### Math

| Name | Signature | Source |
|---|---|---|
| `throttle-curve` |  | `main/lispif_vesc_extensions.c:6503` |
| `rand` |  | `main/lispif_vesc_extensions.c:6504` |
| `rand-max` |  | `main/lispif_vesc_extensions.c:6505` |

### Bit operations

| Name | Signature | Source |
|---|---|---|
| `bits-enc-int` |  | `main/lispif_vesc_extensions.c:6508` |
| `bits-dec-int` |  | `main/lispif_vesc_extensions.c:6509` |

### Lbm settings

| Name | Signature | Source |
|---|---|---|
| `lbm-set-quota` |  | `main/lispif_vesc_extensions.c:6512` |
| `lbm-set-gc-stack-size` |  | `main/lispif_vesc_extensions.c:6513` |

### Plot

| Name | Signature | Source |
|---|---|---|
| `plot-init` |  | `main/lispif_vesc_extensions.c:6516` |
| `plot-add-graph` |  | `main/lispif_vesc_extensions.c:6517` |
| `plot-set-graph` |  | `main/lispif_vesc_extensions.c:6518` |
| `plot-send-points` |  | `main/lispif_vesc_extensions.c:6519` |

### IO-boards

| Name | Signature | Source |
|---|---|---|
| `ioboard-get-adc` |  | `main/lispif_vesc_extensions.c:6522` |
| `ioboard-get-digital` |  | `main/lispif_vesc_extensions.c:6523` |
| `ioboard-set-digital` |  | `main/lispif_vesc_extensions.c:6524` |
| `ioboard-set-pwm` |  | `main/lispif_vesc_extensions.c:6525` |

### ESP NOW

| Name | Signature | Source |
|---|---|---|
| `esp-now-start` |  | `main/lispif_vesc_extensions.c:6528` |
| `esp-now-add-peer` |  | `main/lispif_vesc_extensions.c:6529` |
| `esp-now-del-peer` |  | `main/lispif_vesc_extensions.c:6530` |
| `esp-now-send` |  | `main/lispif_vesc_extensions.c:6531` |
| `esp-now-recv` |  | `main/lispif_vesc_extensions.c:6532` |
| `get-mac-addr` |  | `main/lispif_vesc_extensions.c:6533` |
| `wifi-get-chan` |  | `main/lispif_vesc_extensions.c:6534` |
| `wifi-set-chan` |  | `main/lispif_vesc_extensions.c:6535` |
| `wifi-get-bw` |  | `main/lispif_vesc_extensions.c:6536` |
| `wifi-set-bw` |  | `main/lispif_vesc_extensions.c:6537` |
| `wifi-start` |  | `main/lispif_vesc_extensions.c:6538` |
| `wifi-stop` |  | `main/lispif_vesc_extensions.c:6539` |

### Logging

| Name | Signature | Source |
|---|---|---|
| `log-start` |  | `main/lispif_vesc_extensions.c:6542` |
| `log-stop` |  | `main/lispif_vesc_extensions.c:6543` |
| `log-config-field` |  | `main/lispif_vesc_extensions.c:6544` |
| `log-send-f32` |  | `main/lispif_vesc_extensions.c:6545` |
| `log-send-f64` |  | `main/lispif_vesc_extensions.c:6546` |

### GNSS

| Name | Signature | Source |
|---|---|---|
| `gnss-lat-lon` |  | `main/lispif_vesc_extensions.c:6549` |
| `gnss-height` |  | `main/lispif_vesc_extensions.c:6550` |
| `gnss-speed` |  | `main/lispif_vesc_extensions.c:6551` |
| `gnss-hdop` |  | `main/lispif_vesc_extensions.c:6552` |
| `gnss-date-time` |  | `main/lispif_vesc_extensions.c:6553` |
| `gnss-age` |  | `main/lispif_vesc_extensions.c:6554` |
| `ublox-init` |  | `main/lispif_vesc_extensions.c:6555` |
| `nmea-parse` |  | `main/lispif_vesc_extensions.c:6556` |
| `set-pos-time` |  | `main/lispif_vesc_extensions.c:6557` |

### Sleep

| Name | Signature | Source |
|---|---|---|
| `sleep-deep` |  | `main/lispif_vesc_extensions.c:6560` |
| `sleep-light` |  | `main/lispif_vesc_extensions.c:6561` |
| `sleep-config-wakeup-pin` |  | `main/lispif_vesc_extensions.c:6562` |
| `rtc-data` |  | `main/lispif_vesc_extensions.c:6563` |

### Native libraries

| Name | Signature | Source |
|---|---|---|
| `load-native-lib` |  | `main/lispif_vesc_extensions.c:6566` |
| `unload-native-lib` |  | `main/lispif_vesc_extensions.c:6567` |

### CAN-Messages

| Name | Signature | Source |
|---|---|---|
| `canmsg-recv` | (canmsg-recv slot timeout) | `main/lispif_vesc_extensions.c:6579` |
| `canmsg-send` | (canmsg-send can-id slot msg) | `main/lispif_vesc_extensions.c:6580` |

### File System

| Name | Signature | Source |
|---|---|---|
| `f-connect` | (f-connect pin-mosi pin-miso pin-sck pin-cs optSpiSpeed) -> t or nil | `main/lispif_vesc_extensions.c:6583` |
| `f-connect-nand` | (f-connect-nand pin-mosi pin-miso pin-sck pin-cs optSpiSpeed) -> t or nil | `main/lispif_vesc_extensions.c:6584` |
| `f-disconnect` | (f-disconnect) -> t | `main/lispif_vesc_extensions.c:6585` |
| `f-open` | (f-open path mode) -> file | `main/lispif_vesc_extensions.c:6586` |
| `f-close` | (f-close file) -> t, nil | `main/lispif_vesc_extensions.c:6587` |
| `f-read` | (f-read file size) -> array | `main/lispif_vesc_extensions.c:6588` |
| `f-readline` | (f-readline file maxlen) -> array | `main/lispif_vesc_extensions.c:6589` |
| `f-write` | (f-write file buf) -> t, nil | `main/lispif_vesc_extensions.c:6590` |
| `f-tell` | (f-tell file) -> position | `main/lispif_vesc_extensions.c:6591` |
| `f-seek` | (f-seek file pos) -> t, nil | `main/lispif_vesc_extensions.c:6592` |
| `f-mkdir` | (f-mkdir path) -> t, nil | `main/lispif_vesc_extensions.c:6593` |
| `f-rm` | (f-rm path) -> t, nil | `main/lispif_vesc_extensions.c:6594` |
| `f-ls` | (f-ls path 'size) -> ((path is-dir size) (path is-dir size) ...) | `main/lispif_vesc_extensions.c:6595` |
| `f-size` | (f-size path/file) -> size | `main/lispif_vesc_extensions.c:6596` |
| `f-rename` | (f-rename oldname newname) | `main/lispif_vesc_extensions.c:6597` |
| `f-sync` | (f-sync file) -> t, nil | `main/lispif_vesc_extensions.c:6598` |
| `f-fatinfo` | (f-fatinfo) -> (MB-free MB-total) | `main/lispif_vesc_extensions.c:6599` |

### Firmware update

| Name | Signature | Source |
|---|---|---|
| `fw-erase` | (fw-erase size optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6602` |
| `fw-write` | (fw-write offset data optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6603` |
| `fw-reboot` | (fw-reboot optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6604` |
| `fw-data` | (fw-data optOffset, optLen) | `main/lispif_vesc_extensions.c:6605` |
| `fw-write-raw` | (fw-write-raw offset data) | `main/lispif_vesc_extensions.c:6606` |
| `fw-info` | (fw-info optCanId) -> t\|nil | `main/lispif_vesc_extensions.c:6607` |

### Lbm and script update

| Name | Signature | Source |
|---|---|---|
| `lbm-erase` | (lbm-erase optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6610` |
| `lbm-write` | (lbm-write offset data optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6611` |
| `lbm-run` | (lbm-run running optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6612` |
| `qml-erase` | (qml-erase optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6613` |
| `qml-write` | (qml-write offset data optCanId) -> t, nil | `main/lispif_vesc_extensions.c:6614` |

### AS504x

| Name | Signature | Source |
|---|---|---|
| `as504x-init` |  | `main/lispif_vesc_extensions.c:6617` |
| `as504x-deinit` |  | `main/lispif_vesc_extensions.c:6618` |
| `as504x-angle` |  | `main/lispif_vesc_extensions.c:6619` |

### IMU

| Name | Signature | Source |
|---|---|---|
| `imu-start-lsm6` |  | `main/lispif_vesc_extensions.c:6622` |
| `imu-stop` |  | `main/lispif_vesc_extensions.c:6623` |
| `get-imu-rpy` |  | `main/lispif_vesc_extensions.c:6624` |
| `get-imu-quat` |  | `main/lispif_vesc_extensions.c:6625` |
| `get-imu-acc` |  | `main/lispif_vesc_extensions.c:6626` |
| `get-imu-gyro` |  | `main/lispif_vesc_extensions.c:6627` |
| `get-imu-mag` |  | `main/lispif_vesc_extensions.c:6628` |
| `get-imu-acc-derot` |  | `main/lispif_vesc_extensions.c:6629` |
| `get-imu-gyro-derot` |  | `main/lispif_vesc_extensions.c:6630` |

### UART

| Name | Signature | Source |
|---|---|---|
| `uart-start` | (uart-start uart-num rx-pin tx-pin baud) | `main/lispif_vesc_extensions.c:6633` |
| `uart-stop` |  | `main/lispif_vesc_extensions.c:6634` |
| `uart-write` |  | `main/lispif_vesc_extensions.c:6635` |
| `uart-read` | (uart-read array num optOffset optStopAt optTimeout) | `main/lispif_vesc_extensions.c:6636` |

### UARTCOMM

| Name | Signature | Source |
|---|---|---|
| `uartcomm-start` | (uartcomm-start uart-num rx-pin tx-pin baud) | `main/lispif_vesc_extensions.c:6639` |
| `uartcomm-stop` | (uartcomm-stop uart-num) | `main/lispif_vesc_extensions.c:6640` |

### PWM

| Name | Signature | Source |
|---|---|---|
| `pwm-start` | (pwm-start freq duty channel pin optBits) | `main/lispif_vesc_extensions.c:6643` |
| `pwm-stop` | (pwm-stop channel) | `main/lispif_vesc_extensions.c:6644` |
| `pwm-set-duty` | (pwm-set-duty duty channel) | `main/lispif_vesc_extensions.c:6645` |

### Compression

| Name | Signature | Source |
|---|---|---|
| `unzip` | (unzip input fileInZip optOutputFile) | `main/lispif_vesc_extensions.c:6648` |
| `zip-ls` | (zip-ls input) | `main/lispif_vesc_extensions.c:6649` |

### Connection checks

| Name | Signature | Source |
|---|---|---|
| `connected-wifi` |  | `main/lispif_vesc_extensions.c:6652` |
| `connected-hub` |  | `main/lispif_vesc_extensions.c:6653` |
| `connected-ble` |  | `main/lispif_vesc_extensions.c:6654` |
| `connected-usb` |  | `main/lispif_vesc_extensions.c:6655` |

### Crypto

| Name | Signature | Source |
|---|---|---|
| `aes-ctr-crypt` | (aes-ctr-crypt key counter data start-offset length) -> t | `main/lispif_vesc_extensions.c:6658` |

### NVS

| Name | Signature | Source |
|---|---|---|
| `nvs-read` | (nvs_read key) -> t | `main/lispif_vesc_extensions.c:6661` |
| `nvs-write` | (nvs_write key data) -> t | `main/lispif_vesc_extensions.c:6662` |
| `nvs-erase` |  | `main/lispif_vesc_extensions.c:6663` |
| `nvs-list` |  | `main/lispif_vesc_extensions.c:6664` |
| `nvs-qml-erase-partition` | (nvs_qml_erase) -> t | `main/lispif_vesc_extensions.c:6666` |
| `nvs-qml-init` | (nvs_qml_init) -> t | `main/lispif_vesc_extensions.c:6667` |
| `nvs-qml-read` | (nvs_qml_read key) -> t | `main/lispif_vesc_extensions.c:6668` |
| `nvs-qml-write` | (nvs_qml_write key data) -> t | `main/lispif_vesc_extensions.c:6669` |
| `nvs-qml-erase` | (nvs_qml_erase_key key) -> t | `main/lispif_vesc_extensions.c:6670` |
| `nvs-qml-list` |  | `main/lispif_vesc_extensions.c:6671` |

### Image

| Name | Signature | Source |
|---|---|---|
| `image-save` |  | `main/lispif_vesc_extensions.c:6674` |

### Commands

| Name | Signature | Source |
|---|---|---|
| `cmds-start-stop` |  | `main/lispif_vesc_extensions.c:6677` |
| `cmds-proc` |  | `main/lispif_vesc_extensions.c:6678` |

## WiFi / TCP

### an error has occurred

| Name | Signature | Source |
|---|---|---|
| `wifi-scan-networks` |  | `main/wifi/lispif_wifi_extensions.c:1555` |
| `wifi-connect` | (it's not very reliable though). Finally, nil is returned if the | `main/wifi/lispif_wifi_extensions.c:1556` |
| `wifi-connect-last` |  | `main/wifi/lispif_wifi_extensions.c:1557` |
| `wifi-disconnect` |  | `main/wifi/lispif_wifi_extensions.c:1558` |
| `wifi-status` |  | `main/wifi/lispif_wifi_extensions.c:1559` |
| `wifi-max-tx-power` |  | `main/wifi/lispif_wifi_extensions.c:1560` |
| `wifi-auto-reconnect` |  | `main/wifi/lispif_wifi_extensions.c:1561` |
| `wifi-ftm-measure` |  | `main/wifi/lispif_wifi_extensions.c:1562` |
| `tcp-connect` |  | `main/wifi/lispif_wifi_extensions.c:1563` |
| `tcp-close` | (@todo: be more precise). | `main/wifi/lispif_wifi_extensions.c:1564` |
| `tcp-status` |  | `main/wifi/lispif_wifi_extensions.c:1565` |
| `tcp-send` |  | `main/wifi/lispif_wifi_extensions.c:1566` |
| `tcp-recv` | (either because there were none available this instant, or | `main/wifi/lispif_wifi_extensions.c:1567` |
| `tcp-recv-to-char` | (Default: true) | `main/wifi/lispif_wifi_extensions.c:1568` |

## BLE

### Maybe return internal error here?

| Name | Signature | Source |
|---|---|---|
| `ble-start-app` | (ble-start-app) -> bool | `main/ble/lispif_ble_extensions.c:1271` |
| `ble-set-name` |  | `main/ble/lispif_ble_extensions.c:1272` |
| `ble-conf-adv` |  | `main/ble/lispif_ble_extensions.c:1273` |
| `ble-conf-adv-set-channels` | (ble-conf-adv-set-channels list) -> bool | `main/ble/lispif_ble_extensions.c:1274` |
| `ble-conf-adv-set-interval` | (ble-conf-adv-set-interval min:int max:int) -> bool | `main/ble/lispif_ble_extensions.c:1275` |
| `ble-add-service` | ('max-len . number) | `main/ble/lispif_ble_extensions.c:1277` |
| `ble-remove-service` |  | `main/ble/lispif_ble_extensions.c:1278` |
| `ble-attr-get-value` |  | `main/ble/lispif_ble_extensions.c:1279` |
| `ble-attr-set-value` |  | `main/ble/lispif_ble_extensions.c:1280` |
| `ble-get-services` |  | `main/ble/lispif_ble_extensions.c:1281` |
| `ble-get-attrs` |  | `main/ble/lispif_ble_extensions.c:1282` |

## Display

| Name | Signature | Source |
|---|---|---|
| `ext-disp-cmd` |  | `main/display/disp_icna3306.c:310`, `main/display/disp_ili9341.c:349`, `main/display/disp_ili9488.c:316`, `main/display/disp_sh8501b.c:301`, `main/display/disp_ssd1351.c:311`, `main/display/disp_st7735.c:349`, `main/display/disp_st7789.c:353` |
| `ext-disp-set-spi-mode` |  | `main/display/disp_icna3306.c:311` |
| `ext-disp-orientation` |  | `main/display/disp_ili9341.c:350`, `main/display/disp_ili9488.c:317`, `main/display/disp_st7735.c:350`, `main/display/disp_st7789.c:354` |

### Display Drivers

| Name | Signature | Source |
|---|---|---|
| `disp-load-sh8501b` |  | `main/display/lispif_disp_extensions.c:345` |
| `disp-load-ili9341` |  | `main/display/lispif_disp_extensions.c:346` |
| `disp-load-ssd1306` |  | `main/display/lispif_disp_extensions.c:347` |
| `disp-load-st7789` |  | `main/display/lispif_disp_extensions.c:348` |
| `disp-load-ili9488` |  | `main/display/lispif_disp_extensions.c:349` |
| `disp-load-st7735` |  | `main/display/lispif_disp_extensions.c:350` |
| `disp-load-ssd1351` |  | `main/display/lispif_disp_extensions.c:351` |
| `disp-load-icna3306` |  | `main/display/lispif_disp_extensions.c:352` |

## RGB LED

### no break

| Name | Signature | Source |
|---|---|---|
| `rgbled-init` |  | `main/rgbled/lispif_rgbled_extensions.c:448` |
| `rgbled-deinit` |  | `main/rgbled/lispif_rgbled_extensions.c:449` |
| `rgbled-buffer` |  | `main/rgbled/lispif_rgbled_extensions.c:450` |
| `rgbled-color` |  | `main/rgbled/lispif_rgbled_extensions.c:451` |
| `rgbled-update` |  | `main/rgbled/lispif_rgbled_extensions.c:452` |

## Board-specific (hwconf/)

### Wake up and initialize hardware

| Name | Signature | Source |
|---|---|---|
| `bms-init` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:717`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1280`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1319` |

### Put BMS hardware in sleep mode

| Name | Signature | Source |
|---|---|---|
| `bms-sleep` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:720`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1283`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1322` |

### Get list of cell voltages

| Name | Signature | Source |
|---|---|---|
| `bms-get-vcells` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:723`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1286`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1325` |

### Get list of temperature readings

| Name | Signature | Source |
|---|---|---|
| `bms-get-temps` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:726`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1289`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1328` |
| `bms-get-current` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:729`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1292`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1331` |

### Read and write balance IC registers

| Name | Signature | Source |
|---|---|---|
| `bms-read-reg` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:732` |
| `bms-write-reg` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:733` |

### Get output voltage after power switch

| Name | Signature | Source |
|---|---|---|
| `bms-get-vout` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:736`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1295`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1334` |

### Get charge input voltage

| Name | Signature | Source |
|---|---|---|
| `bms-get-vchg` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:739`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1298`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1337` |

### Get user button state

| Name | Signature | Source |
|---|---|---|
| `bms-get-btn` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:742`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1304`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1340` |
| `bms-set-btn-wakeup-state` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:745`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1307`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1343` |

### Enable/disable precharge switch

| Name | Signature | Source |
|---|---|---|
| `bms-set-pchg` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:748`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1310`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1346` |

### Enable/disable output switch

| Name | Signature | Source |
|---|---|---|
| `bms-set-out` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:751`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1313`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1349` |

### Enable/disable charge switch

| Name | Signature | Source |
|---|---|---|
| `bms-set-chg` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:754`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1316`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1352` |

### Set and get balancing state for cell

| Name | Signature | Source |
|---|---|---|
| `bms-set-bal` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:757`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1319`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1355` |
| `bms-get-bal` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:758`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1320`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1356` |
| `bms-set-cells` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:760` |

### Configuration

| Name | Signature | Source |
|---|---|---|
| `bms-get-param` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:763`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1329`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1365` |
| `bms-set-param` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:764`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1330`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1366` |
| `bms-store-cfg` |  | `main/hwconf/trampa/bms_rb/hw_bms_rb.c:765`, `main/hwconf/vesc/vbms16/hw_vbms16.c:1331`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1367` |

### Orientation

| Name | Signature | Source |
|---|---|---|
| `v-ext` |  | `main/hwconf/trampa/hw_disp_v1.c:271` |
| `v-btn` |  | `main/hwconf/trampa/hw_disp_v1.c:272` |
| `hw-init` |  | `main/hwconf/trampa/hw_disp_v1.c:273` |
| `hw-sleep` |  | `main/hwconf/trampa/hw_disp_v1.c:274` |
| `read-button` *(if DISP_HW_VERSION == DISP_V1_3)* |  | `main/hwconf/trampa/hw_disp_v1.c:276` |
| `set-io` *(if DISP_HW_VERSION == DISP_V1_3)* |  | `main/hwconf/trampa/hw_disp_v1.c:277` |

| Name | Signature | Source |
|---|---|---|
| `disp-init` |  | `main/hwconf/vesc/scope/hw_scope.c:79` |
| `bt1-pressed` |  | `main/hwconf/vesc/scope/hw_scope.c:80` |
| `bt2-pressed` |  | `main/hwconf/vesc/scope/hw_scope.c:81` |
| `sel-disp-left` |  | `main/hwconf/vesc/vdisp_dual/hw_vdisp_dual.c:75` |
| `sel-disp-right` |  | `main/hwconf/vesc/vdisp_dual/hw_vdisp_dual.c:76` |

### Get stack voltage

| Name | Signature | Source |
|---|---|---|
| `bms-get-vstack` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1301` |

### HW-specific commands

| Name | Signature | Source |
|---|---|---|
| `bms-direct-cmd` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1323`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1359` |
| `bms-subcmd-cmdonly` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1324`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1360` |
| `bms-read-reg` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1325`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1361` |
| `bms-write-reg` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1326`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1362` |

### Replace existing I2C-extensions

| Name | Signature | Source |
|---|---|---|
| `i2c-start` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1334`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1370`, `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c:771` |
| `i2c-tx-rx` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1335`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1371`, `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c:772` |
| `i2c-detect-addr` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1336`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1372`, `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c:773` |
| `bms-fw-version` |  | `main/hwconf/vesc/vbms16/hw_vbms16.c:1338`, `main/hwconf/vesc/vbms32/hw_vbms32.c:1374` |

### IO Expander

| Name | Signature | Source |
|---|---|---|
| `disp-set-bl` |  | `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c:765` |
| `disp-cmd` |  | `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c:766` |
| `disp-orientation` |  | `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c:767` |
| `btn-pull-en` |  | `main/hwconf/vesc/vdisp_900/hw_vdisp_900.c:768` |

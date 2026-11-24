# VESC C Interface API Reference

Auto-generated from `vesc_c_if.h` by `gen_vesc_c_if_docs.py`.
Regenerate: `python3 gen_vesc_c_if_docs.py`

All functions: `VESC_IF->function_name(args)`

## Key Types

| Type | Description |
|------|-------------|
| `lbm_value` | Encoded lisp value (uint32) |
| `lbm_uint` / `lbm_int` | Unsigned/signed integer (uint32/int32) |
| `lbm_cid` | Context ID (uint32) |
| `lbm_flat_value_t` | Serialized lisp value buffer |
| `lib_thread` / `lib_mutex` / `lib_semaphore` | Opaque handles (void*) |
| `systime_t` | System ticks (uint32). 1 tick = 100µs |

### `HW_TYPE`

- `HW_TYPE_VESC` = 0
- `HW_TYPE_VESC_BMS`
- `HW_TYPE_CUSTOM_MODULE`

### `mc_fault_code`

- `FAULT_CODE_NONE` = 0
- `FAULT_CODE_OVER_VOLTAGE`
- `FAULT_CODE_UNDER_VOLTAGE`
- `FAULT_CODE_DRV`
- `FAULT_CODE_ABS_OVER_CURRENT`
- `FAULT_CODE_OVER_TEMP_FET`
- `FAULT_CODE_OVER_TEMP_MOTOR`
- `FAULT_CODE_GATE_DRIVER_OVER_VOLTAGE`
- `FAULT_CODE_GATE_DRIVER_UNDER_VOLTAGE`
- `FAULT_CODE_MCU_UNDER_VOLTAGE`
- `FAULT_CODE_BOOTING_FROM_WATCHDOG_RESET`
- `FAULT_CODE_ENCODER_SPI`
- `FAULT_CODE_ENCODER_SINCOS_BELOW_MIN_AMPLITUDE`
- `FAULT_CODE_ENCODER_SINCOS_ABOVE_MAX_AMPLITUDE`
- `FAULT_CODE_FLASH_CORRUPTION`
- `FAULT_CODE_HIGH_OFFSET_CURRENT_SENSOR_1`
- `FAULT_CODE_HIGH_OFFSET_CURRENT_SENSOR_2`
- `FAULT_CODE_HIGH_OFFSET_CURRENT_SENSOR_3`
- `FAULT_CODE_UNBALANCED_CURRENTS`
- `FAULT_CODE_BRK`
- `FAULT_CODE_RESOLVER_LOT`
- `FAULT_CODE_RESOLVER_DOS`
- `FAULT_CODE_RESOLVER_LOS`
- `FAULT_CODE_FLASH_CORRUPTION_APP_CFG`
- `FAULT_CODE_FLASH_CORRUPTION_MC_CFG`
- `FAULT_CODE_ENCODER_NO_MAGNET`
- `FAULT_CODE_ENCODER_MAGNET_TOO_STRONG`
- `FAULT_CODE_PHASE_FILTER`

### `CAN_BAUD`

- `CAN_BAUD_125K` = 0
- `CAN_BAUD_250K`
- `CAN_BAUD_500K`
- `CAN_BAUD_1M`
- `CAN_BAUD_10K`
- `CAN_BAUD_20K`
- `CAN_BAUD_50K`
- `CAN_BAUD_75K`
- `CAN_BAUD_100K`

### `VESC_PIN`

- `VESC_PIN_COMM_RX` = 0
- `VESC_PIN_COMM_TX`
- `VESC_PIN_SWDIO`
- `VESC_PIN_SWCLK`
- `VESC_PIN_HALL1`
- `VESC_PIN_HALL2`
- `VESC_PIN_HALL3`
- `VESC_PIN_ADC1`
- `VESC_PIN_ADC2`
- `VESC_PIN_HALL4`
- `VESC_PIN_HALL5`
- `VESC_PIN_HALL6`
- `VESC_PIN_PPM`
- `VESC_PIN_HW_1`
- `VESC_PIN_HW_2`

### `VESC_PIN_MODE`

- `VESC_PIN_MODE_INPUT_NOPULL` = 0
- `VESC_PIN_MODE_INPUT_PULL_UP`
- `VESC_PIN_MODE_INPUT_PULL_DOWN`
- `VESC_PIN_MODE_OUTPUT`
- `VESC_PIN_MODE_OUTPUT_OPEN_DRAIN`
- `VESC_PIN_MODE_OUTPUT_OPEN_DRAIN_PULL_UP`
- `VESC_PIN_MODE_OUTPUT_OPEN_DRAIN_PULL_DOWN`
- `VESC_PIN_MODE_ANALOG`

### `CFG_PARAM`

- `CFG_PARAM_l_current_max` = 0
- `CFG_PARAM_l_current_min`
- `CFG_PARAM_l_in_current_max`
- `CFG_PARAM_l_in_current_min`
- `CFG_PARAM_l_abs_current_max`
- `CFG_PARAM_l_min_erpm`
- `CFG_PARAM_l_max_erpm`
- `CFG_PARAM_l_erpm_start`
- `CFG_PARAM_l_max_erpm_fbrake`
- `CFG_PARAM_l_max_erpm_fbrake_cc`
- `CFG_PARAM_l_min_vin`
- `CFG_PARAM_l_max_vin`
- `CFG_PARAM_l_battery_cut_start`
- `CFG_PARAM_l_battery_cut_end`
- `CFG_PARAM_app_can_mode`
- `CFG_PARAM_app_can_baud_rate`
- `CFG_PARAM_l_temp_fet_start`
- `CFG_PARAM_l_temp_fet_end`
- `CFG_PARAM_l_temp_motor_start`
- `CFG_PARAM_l_temp_motor_end`
- `CFG_PARAM_l_temp_accel_dec`
- `CFG_PARAM_l_min_duty`
- `CFG_PARAM_l_max_duty`
- `CFG_PARAM_IMU_accel_confidence_decay`
- `CFG_PARAM_IMU_mahony_kp`
- `CFG_PARAM_IMU_mahony_ki`
- `CFG_PARAM_IMU_madgwick_beta`
- `CFG_PARAM_IMU_rot_roll`
- `CFG_PARAM_IMU_rot_pitch`
- `CFG_PARAM_IMU_rot_yaw`
- `CFG_PARAM_IMU_ahrs_mode`
- `CFG_PARAM_IMU_sample_rate`
- `CFG_PARAM_IMU_accel_offset_x`
- `CFG_PARAM_IMU_accel_offset_y`
- `CFG_PARAM_IMU_accel_offset_z`
- `CFG_PARAM_IMU_gyro_offset_x`
- `CFG_PARAM_IMU_gyro_offset_y`
- `CFG_PARAM_IMU_gyro_offset_z`
- `CFG_PARAM_app_shutdown_mode`
- `CFG_PARAM_si_motor_poles`
- `CFG_PARAM_si_gear_ratio`
- `CFG_PARAM_si_wheel_diameter`
- `CFG_PARAM_si_battery_type`
- `CFG_PARAM_si_battery_cells`
- `CFG_PARAM_si_battery_ah`
- `CFG_PARAM_si_motor_nl_current`
- `CFG_PARAM_foc_motor_r`
- `CFG_PARAM_foc_motor_l`
- `CFG_PARAM_foc_motor_flux_linkage`

### `can_status_msg` (struct)

```c
struct {
  int id;
  systime_t rx_time;
  float rpm;
  float current;
  float duty;
} can_status_msg;
```

### `can_status_msg_2` (struct)

```c
struct {
  int id;
  systime_t rx_time;
  float amp_hours;
  float amp_hours_charged;
} can_status_msg_2;
```

### `can_status_msg_3` (struct)

```c
struct {
  int id;
  systime_t rx_time;
  float watt_hours;
  float watt_hours_charged;
} can_status_msg_3;
```

### `can_status_msg_4` (struct)

```c
struct {
  int id;
  systime_t rx_time;
  float temp_fet;
  float temp_motor;
  float current_in;
  float pid_pos_now;
} can_status_msg_4;
```

### `can_status_msg_5` (struct)

```c
struct {
  int id;
  systime_t rx_time;
  float v_in;
  int32_t tacho_value;
} can_status_msg_5;
```

### `can_status_msg_6` (struct)

```c
struct {
  int id;
  systime_t rx_time;
  float adc_1;
  float adc_2;
  float adc_3;
  float ppm;
} can_status_msg_6;
```

### `eeprom_var` (union)

```c
union {
  uint32_t as_u32;
  int32_t as_i32;
  float as_float;
} eeprom_var;
```

### `PACKET_STATE_t` (struct)

```c
struct {
  unsigned int rx_read_ptr;
  unsigned int rx_write_ptr;
  int bytes_left;
  unsigned char rx_buffer[PACKET_BUFFER_LEN];
  unsigned char tx_buffer[PACKET_BUFFER_LEN];
} PACKET_STATE_t;
```

### `gnss_data` (struct)

```c
struct {
  double lat;
  double lon;
  float height;
  float speed;
  float hdop;
  int32_t ms_today;
  int8_t yy;
  int8_t mo;
  int8_t dd;
  systime_t last_update;
} gnss_data;
```

### `lbm_flat_value_t` (struct)

```c
struct {
  uint8_t *buf;
  lbm_uint buf_size;
  lbm_uint buf_pos;
} lbm_flat_value_t;
```

### `lbm_array_header_t` (struct)

```c
struct {
  lbm_uint size;
  lbm_uint *data;
} lbm_array_header_t;
```

### `ATTITUDE_INFO` (struct)

```c
struct {
  float q0;
  float q1;
  float q2;
  float q3;
  float integralFBx;
  float integralFBy;
  float integralFBz;
  float accMagP;
  int initialUpdateDone;
  float acc_confidence_decay;
  float kp;
  float ki;
  float beta;
} ATTITUDE_INFO;
```

### `remote_state` (struct)

```c
struct {
  float js_x;
  float js_y;
  bool bt_c;
  bool bt_z;
  bool is_rev;
  float age_s;
} remote_state;
```

### `lib_info` (struct)

```c
struct {
  void *arg;
  uint32_t base_addr;
} lib_info;
```

## LBM

| Function | Signature | Description |
|----------|-----------|-------------|
| `lbm_add_extension` | `load_extension_fptr lbm_add_extension` | Register C function as lisp extension. Name must start with "ext-". |
| `lbm_block_ctx_from_extension` | `void lbm_block_ctx_from_extension()` | Block current lisp context (yields control while waiting for async result). |
| `lbm_unblock_ctx` | `bool lbm_unblock_ctx(lbm_cid, lbm_flat_value_t*)` | Unblock a context, optionally providing a flat value as result. |
| `lbm_get_current_cid` | `lbm_cid lbm_get_current_cid()` | Get context ID of the currently executing lisp process. |
| `lbm_set_error_reason` | `int lbm_set_error_reason(char *str)` | Set error reason string shown in VESC-Tool on extension error. |
| `lbm_pause_eval_with_gc` | `void lbm_pause_eval_with_gc(uint32_t num_free)` | Pause evaluator and GC to free at least num_free cells. |
| `lbm_continue_eval` | `void lbm_continue_eval()` | Resume evaluator after pause. |
| `lbm_send_message` | `int lbm_send_message(lbm_cid cid, lbm_value msg)` | Send lisp message to a context by CID. Only works when evaluator is paused. |
| `lbm_eval_is_paused` | `bool lbm_eval_is_paused()` | Returns true if evaluator is paused. |
| `lbm_cons` | `lbm_value lbm_cons(lbm_value car, lbm_value cdr)` | Create cons cell from car and cdr. |
| `lbm_car` | `lbm_value lbm_car(lbm_value val)` | Get first element of cons/list. |
| `lbm_cdr` | `lbm_value lbm_cdr(lbm_value val)` | Get rest (tail) of cons/list. |
| `lbm_list_destructive_reverse` | `lbm_value lbm_list_destructive_reverse(lbm_value list)` | Reverse list in-place. Returns new head. |
| `lbm_create_byte_array` | `bool lbm_create_byte_array(lbm_value *value, lbm_uint num_elt)` | Allocate byte array. Writes reference to *value. Returns true on success. |
| `lbm_add_symbol_const` | `int lbm_add_symbol_const(char *, lbm_uint *)` | Add constant symbol to symbol table. Writes ID to *out. |
| `lbm_get_symbol_by_name` | `int lbm_get_symbol_by_name(char *name, lbm_uint* id)` | Look up symbol ID by string name. Returns 0 on success. |
| `lbm_enc_i` | `lbm_value lbm_enc_i(lbm_int x)` | Encode signed int (28/56-bit) as lbm_value. |
| `lbm_enc_u` | `lbm_value lbm_enc_u(lbm_uint x)` | Encode unsigned int (28/56-bit) as lbm_value. |
| `lbm_enc_char` | `lbm_value lbm_enc_char(uint8_t x)` | Encode byte/char as lbm_value. |
| `lbm_enc_float` | `lbm_value lbm_enc_float(float f)` | Encode float as lbm_value. Heap-allocates on 32-bit. |
| `lbm_enc_u32` | `lbm_value lbm_enc_u32(uint32_t u)` | Encode uint32 as lbm_value. Heap-allocates on 32-bit. |
| `lbm_enc_i32` | `lbm_value lbm_enc_i32(int32_t i)` | Encode int32 as lbm_value. Heap-allocates on 32-bit. |
| `lbm_enc_sym` | `lbm_value lbm_enc_sym(lbm_uint s)` | Encode symbol ID as lbm_value. |
| `lbm_dec_as_float` | `float lbm_dec_as_float(lbm_value val)` | Decode lbm_value to float (converts between numeric types). |
| `lbm_dec_as_u32` | `uint32_t lbm_dec_as_u32(lbm_value val)` | Decode lbm_value to uint32. |
| `lbm_dec_as_i32` | `int32_t lbm_dec_as_i32(lbm_value val)` | Decode lbm_value to int32. |
| `lbm_dec_char` | `uint8_t lbm_dec_char(lbm_value x)` | Decode byte/char value. |
| `lbm_dec_str` | `char* lbm_dec_str(lbm_value)` | Get raw char* from string/byte-array lbm_value. |
| `lbm_dec_sym` | `lbm_uint lbm_dec_sym(lbm_value x)` | Extract symbol ID from lbm_value. |
| `lbm_is_byte_array` | `bool lbm_is_byte_array(lbm_value val)` | Check if value is a byte array (string). |
| `lbm_is_cons` | `bool lbm_is_cons(lbm_value x)` | Check if value is a cons cell. |
| `lbm_is_number` | `bool lbm_is_number(lbm_value x)` | Check if value is any numeric type. |
| `lbm_is_char` | `bool lbm_is_char(lbm_value x)` | Check if value is char/byte type. |
| `lbm_is_symbol` | `bool lbm_is_symbol(lbm_value x)` | Check if value is a symbol. |
| `lbm_enc_sym_nil` | `lbm_uint lbm_enc_sym_nil` | Pre-encoded nil symbol. |
| `lbm_enc_sym_true` | `lbm_uint lbm_enc_sym_true` | Pre-encoded true symbol. |
| `lbm_enc_sym_terror` | `lbm_uint lbm_enc_sym_terror` | Pre-encoded type-error symbol. |
| `lbm_enc_sym_eerror` | `lbm_uint lbm_enc_sym_eerror` | Pre-encoded eval-error symbol. |
| `lbm_enc_sym_merror` | `lbm_uint lbm_enc_sym_merror` | Pre-encoded memory-error symbol. |
| `lbm_is_symbol_nil` | `bool lbm_is_symbol_nil(lbm_uint)` | Check if symbol ID is nil. |
| `lbm_is_symbol_true` | `bool lbm_is_symbol_true(lbm_uint)` | Check if symbol ID is true. |

## Os

| Function | Signature | Description |
|----------|-----------|-------------|
| `sleep_ms` | `void sleep_ms(uint32_t ms)` | Sleep current thread for ms milliseconds (100 us resolution, integer ms exact). |
| `sleep_us` | `void sleep_us(uint32_t us)` | Sleep current thread; **rounds up to 100 us systicks** (`US2ST`), so `sleep_us(1)` sleeps 100 us. Never use it for sub-tick timing. |
| `system_time` | `float system_time()` | Time since boot in seconds (float). |
| `ts_to_age_s` | `float ts_to_age_s(systime_t ts)` | Convert system timestamp to age in seconds (handles overflow). |
| `printf` | `int printf(const char *str, ...)` | Print to lisp console in VESC-Tool. Printf-style formatting. |
| `malloc` | `void* malloc(size_t bytes)` | General allocator on `LBM_MEMORY` (the same 28 KiB pool as byte arrays, 64 B blocks, mutex-protected, rounds a request into the GC reserve via `lbm_malloc_reserve`). Safe from any thread; use it for extension state that must live outside the image. |
| `free` | `void free(void *prt)` | Free memory allocated by malloc. |
| `request_terminate` | `void request_terminate(lib_thread thd)` | Request thread stop. Waits 2s then crashes via WDT if thread won't die. |
| `should_terminate` | `bool should_terminate()` | Check if current thread should stop. Use in thread loop. |
| `get_arg` | `void** get_arg(uint32_t prog_addr)` | Get stored argument pointer for a loaded library by program address. |

## ST IO

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_pad_mode` | `void set_pad_mode(void *gpio, uint32_t pin, uint32_t mode)` | Set raw STM32 GPIO mode (void* gpio, pin, PAL mode). |
| `set_pad` | `void set_pad(void *gpio, uint32_t pin)` | Set raw GPIO pin high. |
| `clear_pad` | `void clear_pad(void *gpio, uint32_t pin)` | Set raw GPIO pin low. |

## Abstract IO

| Function | Signature | Description |
|----------|-----------|-------------|
| `io_set_mode` | `bool io_set_mode(VESC_PIN pin, VESC_PIN_MODE mode)` | Set VESC pin mode (VESC_PIN + VESC_PIN_MODE). Returns false if unavailable. |
| `io_write` | `bool io_write(VESC_PIN pin, int state)` | Write digital state to VESC pin. |
| `io_read` | `bool io_read(VESC_PIN pin)` | Read digital state from VESC pin. |
| `io_read_analog` | `float io_read_analog(VESC_PIN pin)` | Read ADC voltage (ADC1/ADC2 only). Returns -1.0 for non-ADC pins. |
| `io_get_st_pin` | `bool io_get_st_pin(VESC_PIN vesc_pin, void **gpio, uint32_t *pin)` | Convert VESC_PIN to raw STM32 GPIO port + pin. |

## CAN

| Function | Signature | Description |
|----------|-----------|-------------|
| `can_transmit_sid` | `void can_transmit_sid(uint32_t id, const uint8_t *data, uint8_t len)` | Send standard-ID (11-bit) CAN frame. Max 8 bytes. |
| `can_transmit_eid` | `void can_transmit_eid(uint32_t id, const uint8_t *data, uint8_t len)` | Send extended-ID (29-bit) CAN frame. Max 8 bytes. |
| `can_send_buffer` | `void can_send_buffer(uint8_t controller_id, uint8_t *data, unsigned int len, uint8_t send)` | Send buffer to remote VESC via CAN. Auto-fragments >8 bytes. |
| `can_set_duty` | `void can_set_duty(uint8_t controller_id, float duty)` | Set duty on remote VESC. Range: -1.0 to 1.0. |
| `can_set_current` | `void can_set_current(uint8_t controller_id, float current)` | Set current on remote VESC. Unit: Amps. |
| `can_set_current_off_delay` | `void can_set_current_off_delay(uint8_t controller_id, float current, float off_delay)` | Set current with auto-off delay on remote VESC. |
| `can_set_current_brake` | `void can_set_current_brake(uint8_t controller_id, float current)` | Set brake current on remote VESC. |
| `can_set_rpm` | `void can_set_rpm(uint8_t controller_id, float rpm)` | Set RPM on remote VESC. |
| `can_set_pos` | `void can_set_pos(uint8_t controller_id, float pos)` | Set position on remote VESC. Unit: degrees. |
| `can_set_current_rel` | `void can_set_current_rel(uint8_t controller_id, float current_rel)` | Set relative current (-1.0 to 1.0) on remote VESC. |
| `can_set_current_rel_off_delay` | `void can_set_current_rel_off_delay(uint8_t controller_id, float current_rel, float off_delay)` | Set relative current with auto-off delay. |
| `can_set_current_brake_rel` | `void can_set_current_brake_rel(uint8_t controller_id, float current_rel)` | Set relative brake current (0.0 to 1.0). |
| `can_ping` | `bool can_ping(uint8_t controller_id, HW_TYPE *hw_type)` | Ping remote controller. Returns true + writes HW_TYPE to *hw_type. |
| `can_get_status_msg_index` | `can_status_msg* can_get_status_msg_index(int index)` | Get CAN status 1 by index (0-9). Returns ptr to static struct. |
| `can_get_status_msg_id` | `can_status_msg* can_get_status_msg_id(int id)` | Get CAN status 1 by controller ID. NULL if not found. |
| `can_get_status_msg_2_index` | `can_status_msg_2* can_get_status_msg_2_index(int index)` | Status 2 by index (amp hours). |
| `can_get_status_msg_2_id` | `can_status_msg_2* can_get_status_msg_2_id(int id)` | Status 2 by controller ID. |
| `can_get_status_msg_3_index` | `can_status_msg_3* can_get_status_msg_3_index(int index)` | Status 3 by index (watt hours). |
| `can_get_status_msg_3_id` | `can_status_msg_3* can_get_status_msg_3_id(int id)` | Status 3 by controller ID. |
| `can_get_status_msg_4_index` | `can_status_msg_4* can_get_status_msg_4_index(int index)` | Status 4 by index (temps, input current, PID pos). |
| `can_get_status_msg_4_id` | `can_status_msg_4* can_get_status_msg_4_id(int id)` | Status 4 by controller ID. |
| `can_get_status_msg_5_index` | `can_status_msg_5* can_get_status_msg_5_index(int index)` | Status 5 by index (input voltage, tachometer). |
| `can_get_status_msg_5_id` | `can_status_msg_5* can_get_status_msg_5_id(int id)` | Status 5 by controller ID. |
| `can_get_status_msg_6_index` | `can_status_msg_6* can_get_status_msg_6_index(int index)` | Status 6 by index (ADC 1-3, PPM). |
| `can_get_status_msg_6_id` | `can_status_msg_6* can_get_status_msg_6_id(int id)` | Status 6 by controller ID. |

## Motor Control

| Function | Signature | Description |
|----------|-----------|-------------|
| `mc_motor_now` | `int mc_motor_now()` | Get active motor index (1 or 2). ISR-aware for dual-motor. |
| `mc_select_motor_thread` | `void mc_select_motor_thread(int motor)` | Select motor (1 or 2) for subsequent mc_* calls. |
| `mc_get_motor_thread` | `int mc_get_motor_thread()` | Get currently selected motor thread. |
| `mc_dccal_done` | `bool mc_dccal_done()` | Check if DC calibration completed. |
| `mc_get_fault` | `mc_fault_code mc_get_fault()` | Get current fault code. |
| `mc_fault_to_string` | `const char* mc_fault_to_string(mc_fault_code fault)` | Convert fault code to string. |
| `mc_set_duty` | `void mc_set_duty(float dutyCycle)` | Set duty cycle (-1.0 to 1.0). Ramps to target. |
| `mc_set_duty_noramp` | `void mc_set_duty_noramp(float dutyCycle)` | Set duty cycle immediately (no ramp). |
| `mc_set_pid_speed` | `void mc_set_pid_speed(float rpm)` | Set PID speed target (RPM). |
| `mc_set_pid_pos` | `void mc_set_pid_pos(float pos)` | Set PID position target (degrees). |
| `mc_set_current` | `void mc_set_current(float current)` | Set motor current (Amps). |
| `mc_set_brake_current` | `void mc_set_brake_current(float current)` | Set brake current (Amps). |
| `mc_set_current_rel` | `void mc_set_current_rel(float val)` | Set relative current (-1.0 to 1.0). |
| `mc_set_brake_current_rel` | `void mc_set_brake_current_rel(float val)` | Set relative brake current (0.0 to 1.0). |
| `mc_set_handbrake` | `void mc_set_handbrake(float current)` | Set handbrake current (Amps). |
| `mc_set_handbrake_rel` | `void mc_set_handbrake_rel(float val)` | Set relative handbrake (0.0 to 1.0). |
| `mc_set_tachometer_value` | `int mc_set_tachometer_value(int steps)` | Set tachometer (encoder steps). |
| `mc_release_motor` | `void mc_release_motor()` | Release motor control. |
| `mc_wait_for_motor_release` | `bool mc_wait_for_motor_release(float timeout)` | Wait for release. Returns true if within timeout (seconds). |
| `mc_get_duty_cycle_now` | `float mc_get_duty_cycle_now()` | Current duty cycle. |
| `mc_get_sampling_frequency_now` | `float mc_get_sampling_frequency_now()` | ADC sampling frequency (Hz). |
| `mc_get_rpm` | `float mc_get_rpm()` | Current RPM. |
| `mc_get_amp_hours` | `float mc_get_amp_hours(bool reset)` | Amp hours consumed. Pass true to reset. |
| `mc_get_amp_hours_charged` | `float mc_get_amp_hours_charged(bool reset)` | Amp hours regen. Pass true to reset. |
| `mc_get_watt_hours` | `float mc_get_watt_hours(bool reset)` | Watt hours consumed. Pass true to reset. |
| `mc_get_watt_hours_charged` | `float mc_get_watt_hours_charged(bool reset)` | Watt hours regen. Pass true to reset. |
| `mc_get_tot_current` | `float mc_get_tot_current()` | Total motor current (Amps). |
| `mc_get_tot_current_filtered` | `float mc_get_tot_current_filtered()` | Filtered motor current. |
| `mc_get_tot_current_directional` | `float mc_get_tot_current_directional()` | Directional current (negative = regen). |
| `mc_get_tot_current_directional_filtered` | `float mc_get_tot_current_directional_filtered()` | Filtered directional current. |
| `mc_get_tot_current_in` | `float mc_get_tot_current_in()` | Input (battery) current (Amps). |
| `mc_get_tot_current_in_filtered` | `float mc_get_tot_current_in_filtered()` | Filtered input current. |
| `mc_get_input_voltage_filtered` | `float mc_get_input_voltage_filtered()` | Filtered input voltage (Volts). |
| `mc_get_tachometer_value` | `int mc_get_tachometer_value(bool reset)` | Tachometer (encoder steps). Pass true to reset. |
| `mc_get_tachometer_abs_value` | `int mc_get_tachometer_abs_value(bool reset)` | Absolute tachometer. Pass true to reset. |
| `mc_get_pid_pos_set` | `float mc_get_pid_pos_set()` | PID position setpoint. |
| `mc_get_pid_pos_now` | `float mc_get_pid_pos_now()` | Current encoder position. |
| `mc_update_pid_pos_offset` | `void mc_update_pid_pos_offset(float angle_now, bool store)` | Update PID position offset. store=true persists to flash. |
| `mc_temp_fet_filtered` | `float mc_temp_fet_filtered()` | MOSFET temperature (°C). |
| `mc_temp_motor_filtered` | `float mc_temp_motor_filtered()` | Motor temperature (°C). |
| `mc_get_battery_level` | `float mc_get_battery_level(float *wh_left)` | Battery level (0.0-1.0). Writes remaining Wh to *wh_left. |
| `mc_get_speed` | `float mc_get_speed()` | Vehicle speed (m/s, uses wheel diameter + gear ratio config). |
| `mc_get_distance` | `float mc_get_distance()` | Distance traveled (meters, since reset). |
| `mc_get_distance_abs` | `float mc_get_distance_abs()` | Absolute distance (meters). |
| `mc_get_odometer` | `uint64_t mc_get_odometer()` | Total odometer (meters). |
| `mc_set_odometer` | `void mc_set_odometer(uint64_t new_odometer_meters)` | Set odometer (meters). |
| `mc_set_current_off_delay` | `void mc_set_current_off_delay(float delay_sec)` | Auto-off delay for current commands (seconds). |
| `mc_stat_speed_avg` | `float mc_stat_speed_avg()` | Average speed since stat reset (m/s). |
| `mc_stat_speed_max` | `float mc_stat_speed_max()` | Max speed since stat reset. |
| `mc_stat_power_avg` | `float mc_stat_power_avg()` | Average power since stat reset (Watts). |
| `mc_stat_power_max` | `float mc_stat_power_max()` | Max power since stat reset. |
| `mc_stat_current_avg` | `float mc_stat_current_avg()` | Average current since stat reset (Amps). |
| `mc_stat_current_max` | `float mc_stat_current_max()` | Max current since stat reset. |
| `mc_stat_temp_mosfet_avg` | `float mc_stat_temp_mosfet_avg()` | Average MOSFET temp since stat reset (°C). |
| `mc_stat_temp_mosfet_max` | `float mc_stat_temp_mosfet_max()` | Max MOSFET temp since stat reset. |
| `mc_stat_temp_motor_avg` | `float mc_stat_temp_motor_avg()` | Average motor temp since stat reset (°C). |
| `mc_stat_temp_motor_max` | `float mc_stat_temp_motor_max()` | Max motor temp since stat reset. |
| `mc_stat_count_time` | `float mc_stat_count_time()` | Stats collection period (seconds). |
| `mc_stat_reset` | `void mc_stat_reset()` | Reset all motor statistics. |

## Comm

| Function | Signature | Description |
|----------|-----------|-------------|
| `send_app_data` | `void send_app_data(unsigned char *data, unsigned int len)` | Send custom app data to VESC-Tool / connected client. |

## UART

| Function | Signature | Description |
|----------|-----------|-------------|
| `uart_start` | `bool uart_start(uint32_t baudrate, bool half_duplex)` | Init UART at baudrate. Disables running UART app. Optional half-duplex. |
| `uart_write` | `bool uart_write(const uint8_t *data, uint32_t size)` | Write data to UART. Handles half-duplex RE pin automatically. |
| `uart_read` | `int32_t uart_read()` | Read one byte (non-blocking). Returns -1 if empty. |

## Packets

| Function | Signature | Description |
|----------|-----------|-------------|
| `packet_reset` | `void packet_reset(PACKET_STATE_t *)` | Reset packet state (clear buffers). |
| `packet_process_byte` | `void packet_process_byte(uint8_t, PACKET_STATE_t *)` | Feed one byte into packet state machine. |
| `packet_send_packet` | `void packet_send_packet(unsigned char *, unsigned int len, PACKET_STATE_t *)` | Send packet (handles framing + CRC). |

## IMU

| Function | Signature | Description |
|----------|-----------|-------------|
| `imu_startup_done` | `bool imu_startup_done()` | Check if IMU init is complete. |
| `imu_get_roll` | `float imu_get_roll()` | Roll angle (degrees). |
| `imu_get_pitch` | `float imu_get_pitch()` | Pitch angle (degrees). |
| `imu_get_yaw` | `float imu_get_yaw()` | Yaw angle (degrees). |
| `imu_get_rpy` | `void imu_get_rpy(float *rpy)` | All three Euler angles [roll, pitch, yaw] at once. |
| `imu_get_accel` | `void imu_get_accel(float *accel)` | Raw accelerometer [x, y, z] in g. |
| `imu_get_gyro` | `void imu_get_gyro(float *gyro)` | Raw gyroscope [x, y, z] in deg/s. |
| `imu_get_mag` | `void imu_get_mag(float *mag)` | Raw magnetometer [x, y, z]. |
| `imu_derotate` | `void imu_derotate(const float *input, float *output)` | Transform vector from body to earth frame. |
| `imu_get_accel_derotated` | `void imu_get_accel_derotated(float *accel)` | Accelerometer in earth frame. |
| `imu_get_gyro_derotated` | `void imu_get_gyro_derotated(float *gyro)` | Gyroscope in earth frame. |
| `imu_get_quaternions` | `void imu_get_quaternions(float *q)` | Orientation as quaternion [w, x, y, z]. |
| `imu_get_calibration` | `void imu_get_calibration(float yaw, float * imu_cal)` | Run IMU calibration. yaw=current heading. Results in imu_cal. |
| `imu_set_yaw` | `void imu_set_yaw(float yaw_deg)` | Set yaw angle (degrees). |

## EEPROM

| Function | Signature | Description |
|----------|-----------|-------------|
| `read_eeprom_var` | `bool read_eeprom_var(eeprom_var *v, int address)` | Read eeprom_var (uint32/int32/float union) from address. |
| `store_eeprom_var` | `bool store_eeprom_var(eeprom_var *v, int address)` | Write eeprom_var. Releases motor during write. |

## Timeout

| Function | Signature | Description |
|----------|-----------|-------------|
| `timeout_reset` | `void timeout_reset()` | Reset timeout watchdog. |
| `timeout_has_timeout` | `bool timeout_has_timeout()` | Check if timeout fault occurred. |
| `timeout_secs_since_update` | `float timeout_secs_since_update()` | Seconds since last control input. |

## Plot

| Function | Signature | Description |
|----------|-----------|-------------|
| `plot_init` | `void plot_init(const char *namex, const char *namey)` | Init real-time plot in VESC-Tool with X/Y axis names. |
| `plot_add_graph` | `void plot_add_graph(const char *name)` | Add named graph line to plot. |
| `plot_set_graph` | `void plot_set_graph(int graph)` | Select graph for subsequent points. |
| `plot_send_points` | `void plot_send_points(float x, float y)` | Send (x, y) point to selected graph. |

## Custom config

| Function | Signature | Description |
|----------|-----------|-------------|
| `conf_custom_clear_configs` | `void conf_custom_clear_configs()` | Unregister all custom configs. |
| `get_cfg_float` | `float get_cfg_float(CFG_PARAM p)` | Read float config parameter by CFG_PARAM. |
| `get_cfg_int` | `int get_cfg_int(CFG_PARAM p)` | Read int config parameter by CFG_PARAM. |
| `set_cfg_float` | `bool set_cfg_float(CFG_PARAM p, float value)` | Write float config. Applies HW limits. |
| `set_cfg_int` | `bool set_cfg_int(CFG_PARAM p, int value)` | Write int config. |
| `store_cfg` | `bool store_cfg()` | Persist motor + app config to flash. |
| `mc_gnss` | `volatile gnss_data* mc_gnss()` | Get pointer to gnss_data struct (lat, lon, height, speed, hdop, time, date). |

## Mutex

| Function | Signature | Description |
|----------|-----------|-------------|
| `mutex_create` | `lib_mutex mutex_create()` | Create mutex (LBM-allocated). Free with VESC_IF->free(). |
| `mutex_lock` | `void mutex_lock(lib_mutex)` | Lock mutex. Blocks. Has priority inheritance. |
| `mutex_unlock` | `void mutex_unlock(lib_mutex)` | Unlock mutex. |
| `lbm_symbol_to_io` | `bool lbm_symbol_to_io(lbm_uint sym, void **gpio, uint32_t *pin)` | Convert lisp symbol to STM32 GPIO. Only safe from extensions. |
| `timer_time_now` | `uint32_t timer_time_now()` | TIM5 count at **14 MHz**: a delta is `1/14 us`, so divide by 14 for microseconds (wraps every 306.8 s). For busy-wait timing. |
| `timer_seconds_elapsed_since` | `float timer_seconds_elapsed_since(uint32_t time)` | Seconds elapsed since a timer_time_now() capture. |
| `timer_sleep` | `void timer_sleep(float seconds)` | Busy-wait sleep (seconds). High precision, blocks thread. |
| `sys_lock` | `void sys_lock()` | System lock (disables interrupts). Counting — pair with sys_unlock. |
| `sys_unlock` | `void sys_unlock()` | System unlock. Re-enables interrupts on outermost call. |
| `ahrs_init_attitude_info` | `void ahrs_init_attitude_info(ATTITUDE_INFO *att)` | Init ATTITUDE_INFO with defaults. |
| `ahrs_update_initial_orientation` | `void ahrs_update_initial_orientation(const float *accelXYZ, const float *magXYZ, ATTITUDE_INFO *att)` | Set initial orientation from accel + mag. |
| `ahrs_update_mahony_imu` | `void ahrs_update_mahony_imu(const float *gyroXYZ, const float *accelXYZ, float dt, ATTITUDE_INFO *att)` | Update with Mahony filter (gyro + accel). |
| `ahrs_update_madgwick_imu` | `void ahrs_update_madgwick_imu(const float *gyroXYZ, const float *accelXYZ, float dt, ATTITUDE_INFO *att)` | Update with Madgwick filter (gyro + accel). |
| `ahrs_get_roll` | `float ahrs_get_roll(const ATTITUDE_INFO *att)` | Roll from ATTITUDE_INFO (degrees). |
| `ahrs_get_pitch` | `float ahrs_get_pitch(const ATTITUDE_INFO *att)` | Pitch from ATTITUDE_INFO (degrees). |
| `ahrs_get_yaw` | `float ahrs_get_yaw(const ATTITUDE_INFO *att)` | Yaw from ATTITUDE_INFO (degrees). |
| `store_backup_data` | `bool store_backup_data()` | Persist backup data (odometer, runtime, HW config) to flash. |

## Input Devices

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_remote_state` | `remote_state get_remote_state()` | Nunchuk/remote: joystick X/Y, buttons C/Z, reverse, age. |
| `get_ppm` | `float get_ppm()` | Decoded PPM (-1.0 to 1.0). Auto-starts decoder if needed. |
| `get_ppm_age` | `float get_ppm_age()` | Seconds since last PPM pulse. |
| `app_is_output_disabled` | `bool app_is_output_disabled()` | True if apps should disable output. |

## NVM

| Function | Signature | Description |
|----------|-----------|-------------|
| `read_nvm` | `bool read_nvm(uint8_t *v, unsigned int len, unsigned int address)` | Read from NVM (128KB flash sector). |
| `write_nvm` | `bool write_nvm(uint8_t *v, unsigned int len, unsigned int address)` | Write to NVM (byte-by-byte flash programming). |
| `wipe_nvm` | `bool wipe_nvm()` | Erase entire NVM sector. |

## FOC

| Function | Signature | Description |
|----------|-----------|-------------|
| `foc_get_id` | `float foc_get_id()` | FOC d-axis current (filtered, Amps). |
| `foc_get_iq` | `float foc_get_iq()` | FOC q-axis current (filtered, Amps). |
| `foc_get_vd` | `float foc_get_vd()` | FOC d-axis voltage. |
| `foc_get_vq` | `float foc_get_vq()` | FOC q-axis voltage. |
| `foc_set_openloop_current` | `void foc_set_openloop_current(float current, float rpm)` | Open-loop at given current (Amps) and RPM. |
| `foc_set_openloop_phase` | `void foc_set_openloop_phase(float current, float phase)` | Open-loop at given current (Amps) and electrical phase (degrees). |
| `foc_set_openloop_duty` | `void foc_set_openloop_duty(float dutyCycle, float rpm)` | Open-loop at given duty and RPM. |
| `foc_set_openloop_duty_phase` | `void foc_set_openloop_duty_phase(float dutyCycle, float phase)` | Open-loop at given duty and electrical phase. |

## Flat values

| Function | Signature | Description |
|----------|-----------|-------------|
| `lbm_start_flatten` | `bool lbm_start_flatten(lbm_flat_value_t *v, size_t buffer_size)` | Start building serialized lisp value. Allocates buffer. |
| `lbm_finish_flatten` | `bool lbm_finish_flatten(lbm_flat_value_t *v)` | Finalize flat value. |
| `f_cons` | `bool f_cons(lbm_flat_value_t *v)` | Write cons marker into flat value. |
| `f_sym` | `bool f_sym(lbm_flat_value_t *v, lbm_uint sym)` | Write symbol into flat value. |
| `f_i` | `bool f_i(lbm_flat_value_t *v, lbm_int i)` | Write integer into flat value. |
| `f_b` | `bool f_b(lbm_flat_value_t *v, uint8_t b)` | Write byte into flat value. |
| `f_i32` | `bool f_i32(lbm_flat_value_t *v, int32_t w)` | Write int32 into flat value. |
| `f_u32` | `bool f_u32(lbm_flat_value_t *v, uint32_t w)` | Write uint32 into flat value. |
| `f_float` | `bool f_float(lbm_flat_value_t *v, float f)` | Write float into flat value. |
| `f_i64` | `bool f_i64(lbm_flat_value_t *v, int64_t w)` | Write int64 into flat value. |
| `f_u64` | `bool f_u64(lbm_flat_value_t *v, uint64_t w)` | Write uint64 into flat value. |
| `f_lbm_array` | `bool f_lbm_array(lbm_flat_value_t *v, uint32_t num_elts, uint8_t *data)` | Write byte array into flat value. |
| `lbm_unblock_ctx_unboxed` | `bool lbm_unblock_ctx_unboxed(lbm_cid cid, lbm_value unboxed)` | Unblock a context with a raw lbm_value (no flattening). FW 6.05+. |
| `system_time_ticks` | `systime_t system_time_ticks()` | Current ChibiOS systick count: **1 tick = 100 us** (10 kHz). Wraps every 119.3 h; compare deltas with `ts_to_age_s`. |
| `sleep_ticks` | `void sleep_ticks(systime_t ticks)` | Sleep current thread for that many systicks (100 us each). |

## FOC Audio

| Function | Signature | Description |
|----------|-----------|-------------|
| `foc_beep` | `bool foc_beep(float freq, float time, float voltage)` | Beep: freq=Hz, time=sec, voltage=0.0-1.0. Returns true if busy. |
| `foc_play_tone` | `bool foc_play_tone(int channel, float freq, float voltage)` | Continuous tone on channel (0/1). freq=Hz, voltage=0.0-1.0. |
| `foc_stop_audio` | `void foc_stop_audio(bool reset)` | Stop audio. reset=true clears sample tables. |
| `foc_set_audio_sample_table` | `bool foc_set_audio_sample_table(int channel, const float *samples, int len)` | Set float sample table for a channel. |
| `foc_get_audio_sample_table` | `const float* foc_get_audio_sample_table(int channel)` | Get sample table pointer for a channel. |
| `foc_play_audio_samples` | `bool foc_play_audio_samples(const int8_t *samples, int num_samp, float f_samp, float voltage)` | Play raw int8 samples at f_samp Hz. |

## Semaphore

| Function | Signature | Description |
|----------|-----------|-------------|
| `sem_create` | `lib_semaphore sem_create()` | Create semaphore (count=0). Free with VESC_IF->free(). |
| `sem_wait` | `void sem_wait(lib_semaphore)` | Block on semaphore. |
| `sem_signal` | `void sem_signal(lib_semaphore)` | Signal (increment) semaphore. |
| `sem_wait_to` | `bool sem_wait_to(lib_semaphore, systime_t)` | Wait with timeout (ticks). Returns false on timeout. |
| `sem_reset` | `void sem_reset(lib_semaphore)` | Reset count to 0, wake all waiters. |
| `thread_set_priority` | `void thread_set_priority(int priority)` | Thread priority: -5 (lowest) to 5 (highest), 0=normal. FW 6.06+. |
| `shutdown_disable` | `void shutdown_disable(bool disable)` | Disable auto-shutdown (momentary button HW). FW 6.06+. |
| `foc_set_fw_override` | `void foc_set_fw_override(float current)` | Override the field-weakening current (Amps). FW 7.00+. C-only: no `foc-set-fw-override` lisp extension is registered upstream. |

## Macros

| Macro | Description |
|-------|-------------|
| `VESC_IF` | `((vesc_c_if*)(0x1000F800))` — the interface struct |
| `HEADER` | Declare program pointer (required at file scope) |
| `INIT_FUN` | Declare init function (called on load) |
| `INIT_START` | First line in INIT_FUN body |
| `PROG_ADDR` | `((uint32_t)&prog_ptr)` — this program's address |
| `ARG` | `(*VESC_IF->get_arg(PROG_ADDR))` — stored argument |
| `SYSTEM_TICK_RATE_HZ` | `10000` (100µs per tick) |

#!/usr/bin/env python3
"""
Generate clean API reference docs from vesc_c_if.h for the vesc-lispbm skill.

Parses the function pointer struct, groups by known categories, and produces
concise agent-facing documentation (signatures, behavior, usage — not implementation).

Usage:
    python3 gen_vesc_c_if_docs.py [--header /path/to/vesc_c_if.h] [--out /path/to/output]

Defaults:
    --header  ../c_libs/vesc_c_if.h relative to this script, the bldc checkout layout
    --out     native-extensions/ next to this script
"""

import re
import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_HEADER = SCRIPT_DIR.parent / "c_libs" / "vesc_c_if.h"
DEFAULT_OUT = SCRIPT_DIR / "native-extensions"

# Categories in order, with the comment marker that starts each section in the struct.
# Only these exact comments (on their own line) are treated as category boundaries.
CATEGORIES = [
    ("LBM", "// LBM"),
    ("Os", "// Os"),
    ("ST IO", "// ST IO"),
    ("Abstract IO", "// Abstract IO"),
    ("CAN", "// CAN"),
    ("Motor Control", "// Motor Control"),
    ("Comm", "// Comm"),
    ("UART", "// UART"),
    ("Packets", "// Packets"),
    ("IMU", "// IMU"),
    ("Terminal", "// Terminal"),
    ("EEPROM", "// EEPROM"),
    ("Timeout", "// Timeout"),
    ("Plot", "// Plot"),
    ("Custom config", "// Custom config"),
    ("Settings", "// Settings"),
    ("GNSS", "// GNSS"),
    ("Mutex", "// Mutex"),
    ("Timer", "// Timer"),
    ("System lock", "// System lock"),
    ("IMU AHRS", "// IMU AHRS"),
    ("Encoder", "// Set custom encoder"),
    ("Backup", "// Store backup"),
    ("Input Devices", "// Input Devices"),
    ("NVM", "// NVM"),
    ("FOC", "// FOC"),
    ("Flat values", "// Flat values"),
    ("FOC Audio", "// FOC Audio"),
    ("Semaphore", "// Semaphore"),
    ("Thread priority", "// Set priority"),
]


def parse_vesc_c_if(header_path: Path) -> list[dict]:
    """Parse the vesc_c_if struct into categorized entries."""
    text = header_path.read_text(encoding='utf-8')

    # Find vesc_c_if struct by locating the closing brace first, then matching backwards
    end_match = re.search(r'\}\s*vesc_c_if\s*;', text)
    if not end_match:
        raise ValueError("Could not find vesc_c_if struct")
    # Walk backwards from end to find the opening typedef struct {
    end_pos = end_match.start()
    # Find the last 'typedef struct {' before end_pos
    start_pos = text.rfind('typedef struct {', 0, end_pos)
    if start_pos == -1:
        raise ValueError("Could not find vesc_c_if struct opening")
    body = text[start_pos + len('typedef struct {'):end_pos]

    # Build category marker lookup: comment_text -> category_name
    marker_to_cat = {}
    for cat_name, marker in CATEGORIES:
        marker_to_cat[marker.strip()] = cat_name

    current_cat = "LBM"  # struct starts with // LBM
    entries = []

    for line in body.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue

        # Check for category boundary comment (exact match, standalone line)
        if stripped in marker_to_cat:
            current_cat = marker_to_cat[stripped]
            continue

        # Skip other comments (inline comments, firmware version markers)
        if stripped.startswith('//'):
            continue

        # Function pointer: ret_type (*name)(params);
        fp = re.match(r'([\w\s\*]+?)\s*\(\*(\w+)\)\s*\(([^)]*)\)\s*;', stripped)
        if fp:
            entries.append({
                'kind': 'func',
                'name': fp.group(2),
                'ret': fp.group(1).strip(),
                'params': fp.group(3).strip(),
                'category': current_cat,
            })
            continue

        # Data field: type name;
        df = re.match(r'([\w]+)\s+(\w+)\s*;', stripped)
        if df:
            entries.append({
                'kind': 'field',
                'name': df.group(2),
                'ret': df.group(1),
                'params': '',
                'category': current_cat,
            })

    return entries


def parse_enums(header_path: Path) -> dict:
    """Extract enum definitions."""
    text = header_path.read_text(encoding='utf-8')
    enums = {}
    for m in re.finditer(r'typedef enum\s*\{(.*?)\}\s*(\w+)\s*;', text, re.DOTALL):
        name = m.group(2)
        values = []
        for line in m.group(1).split('\n'):
            line = line.strip().rstrip(',')
            vm = re.match(r'(\w+)\s*(?:=\s*(.+))?', line)
            if vm:
                values.append((vm.group(1), vm.group(2)))
        if values:
            enums[name] = values
    return enums


def parse_type_defs(header_path: Path) -> dict:
    """Extract non-vesc_c_if struct and union definitions."""
    text = header_path.read_text(encoding='utf-8')
    types = {}
    for m in re.finditer(r'typedef (struct|union)\s*\{(.*?)\}\s*(\w+)\s*;', text, re.DOTALL):
        kind = m.group(1)
        name = m.group(3)
        if name == 'vesc_c_if':
            continue
        fields = []
        for line in m.group(2).split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            line = re.sub(r'//.*$', '', line).strip()
            # Skip function pointer fields
            if '(' in line and '*' in line:
                continue
            if line:
                fields.append(line)
        if fields:
            types[name] = {'kind': kind, 'fields': fields}
    return types


# Concise descriptions for every function/field in vesc_c_if
DESC = {
    # LBM Core
    'lbm_add_extension': 'Register C function as lisp extension. Name must start with "ext-".',
    'lbm_block_ctx_from_extension': 'Block current lisp context (yields control while waiting for async result).',
    'lbm_unblock_ctx': 'Unblock a context, optionally providing a flat value as result.',
    'lbm_unblock_ctx_unboxed': 'Unblock a context with a raw lbm_value (no flattening). FW 6.05+.',
    'lbm_get_current_cid': 'Get context ID of the currently executing lisp process.',
    'lbm_set_error_reason': 'Set error reason string shown in VESC-Tool on extension error.',
    'lbm_pause_eval_with_gc': 'Pause evaluator and GC to free at least num_free cells.',
    'lbm_continue_eval': 'Resume evaluator after pause.',
    'lbm_eval_is_paused': 'Returns true if evaluator is paused.',
    'lbm_send_message': 'Send lisp message to a context by CID. Only works when evaluator is paused.',
    'lbm_cons': 'Create cons cell from car and cdr.',
    'lbm_car': 'Get first element of cons/list.',
    'lbm_cdr': 'Get rest (tail) of cons/list.',
    'lbm_list_destructive_reverse': 'Reverse list in-place. Returns new head.',
    'lbm_create_byte_array': 'Allocate byte array. Writes reference to *value. Returns true on success.',
    'lbm_add_symbol_const': 'Add constant symbol to symbol table. Writes ID to *out.',
    'lbm_get_symbol_by_name': 'Look up symbol ID by string name. Returns 0 on success.',
    'lbm_enc_i': 'Encode signed int (28/56-bit) as lbm_value.',
    'lbm_enc_u': 'Encode unsigned int (28/56-bit) as lbm_value.',
    'lbm_enc_char': 'Encode byte/char as lbm_value.',
    'lbm_enc_float': 'Encode float as lbm_value. Heap-allocates on 32-bit.',
    'lbm_enc_u32': 'Encode uint32 as lbm_value. Heap-allocates on 32-bit.',
    'lbm_enc_i32': 'Encode int32 as lbm_value. Heap-allocates on 32-bit.',
    'lbm_enc_sym': 'Encode symbol ID as lbm_value.',
    'lbm_dec_as_float': 'Decode lbm_value to float (converts between numeric types).',
    'lbm_dec_as_u32': 'Decode lbm_value to uint32.',
    'lbm_dec_as_i32': 'Decode lbm_value to int32.',
    'lbm_dec_char': 'Decode byte/char value.',
    'lbm_dec_str': 'Get raw char* from string/byte-array lbm_value.',
    'lbm_dec_sym': 'Extract symbol ID from lbm_value.',
    'lbm_is_byte_array': 'Check if value is a byte array (string).',
    'lbm_is_cons': 'Check if value is a cons cell.',
    'lbm_is_number': 'Check if value is any numeric type.',
    'lbm_is_char': 'Check if value is char/byte type.',
    'lbm_is_symbol': 'Check if value is a symbol.',
    'lbm_enc_sym_nil': 'Pre-encoded nil symbol.',
    'lbm_enc_sym_true': 'Pre-encoded true symbol.',
    'lbm_enc_sym_terror': 'Pre-encoded type-error symbol.',
    'lbm_enc_sym_eerror': 'Pre-encoded eval-error symbol.',
    'lbm_enc_sym_merror': 'Pre-encoded memory-error symbol.',
    'lbm_is_symbol_nil': 'Check if symbol ID is nil.',
    'lbm_is_symbol_true': 'Check if symbol ID is true.',
    # OS
    'sleep_ms': 'Sleep current thread for ms milliseconds (100 us resolution, integer ms exact).',
    'sleep_us': 'Sleep current thread; **rounds up to 100 us systicks** (`US2ST`), so `sleep_us(1)` sleeps 100 us. Never use it for sub-tick timing.',
    'system_time': 'Time since boot in seconds (float).',
    'ts_to_age_s': 'Convert system timestamp to age in seconds (handles overflow).',
    'printf': 'Print to lisp console in VESC-Tool. Printf-style formatting.',
    'malloc': 'General allocator on `LBM_MEMORY` (the same 28 KiB pool as byte arrays, 64 B blocks, mutex-protected, rounds a request into the GC reserve via `lbm_malloc_reserve`). Safe from any thread; use it for extension state that must live outside the image.',
    'free': 'Free memory allocated by malloc.',
    'spawn': 'Create thread. Function must be static. Returns opaque handle. Max 20 threads.',
    'request_terminate': 'Request thread stop. Waits 2s then crashes via WDT if thread won\'t die.',
    'should_terminate': 'Check if current thread should stop. Use in thread loop.',
    'get_arg': 'Get stored argument pointer for a loaded library by program address.',
    # IO
    'set_pad_mode': 'Set raw STM32 GPIO mode (void* gpio, pin, PAL mode).',
    'set_pad': 'Set raw GPIO pin high.',
    'clear_pad': 'Set raw GPIO pin low.',
    'io_set_mode': 'Set VESC pin mode (VESC_PIN + VESC_PIN_MODE). Returns false if unavailable.',
    'io_write': 'Write digital state to VESC pin.',
    'io_read': 'Read digital state from VESC pin.',
    'io_read_analog': 'Read ADC voltage (ADC1/ADC2 only). Returns -1.0 for non-ADC pins.',
    'io_get_st_pin': 'Convert VESC_PIN to raw STM32 GPIO port + pin.',
    'lbm_symbol_to_io': 'Convert lisp symbol to STM32 GPIO. Only safe from extensions.',
    # UART
    'uart_start': 'Init UART at baudrate. Disables running UART app. Optional half-duplex.',
    'uart_write': 'Write data to UART. Handles half-duplex RE pin automatically.',
    'uart_read': 'Read one byte (non-blocking). Returns -1 if empty.',
    # CAN
    'can_set_sid_cb': 'Register callback for standard-ID CAN frames. Return true to consume.',
    'can_set_eid_cb': 'Register callback for extended-ID CAN frames.',
    'can_transmit_sid': 'Send standard-ID (11-bit) CAN frame. Max 8 bytes.',
    'can_transmit_eid': 'Send extended-ID (29-bit) CAN frame. Max 8 bytes.',
    'can_send_buffer': 'Send buffer to remote VESC via CAN. Auto-fragments >8 bytes.',
    'can_set_duty': 'Set duty on remote VESC. Range: -1.0 to 1.0.',
    'can_set_current': 'Set current on remote VESC. Unit: Amps.',
    'can_set_current_off_delay': 'Set current with auto-off delay on remote VESC.',
    'can_set_current_brake': 'Set brake current on remote VESC.',
    'can_set_rpm': 'Set RPM on remote VESC.',
    'can_set_pos': 'Set position on remote VESC. Unit: degrees.',
    'can_set_current_rel': 'Set relative current (-1.0 to 1.0) on remote VESC.',
    'can_set_current_rel_off_delay': 'Set relative current with auto-off delay.',
    'can_set_current_brake_rel': 'Set relative brake current (0.0 to 1.0).',
    'can_ping': 'Ping remote controller. Returns true + writes HW_TYPE to *hw_type.',
    'can_get_status_msg_index': 'Get CAN status 1 by index (0-9). Returns ptr to static struct.',
    'can_get_status_msg_id': 'Get CAN status 1 by controller ID. NULL if not found.',
    'can_get_status_msg_2_index': 'Status 2 by index (amp hours).',
    'can_get_status_msg_2_id': 'Status 2 by controller ID.',
    'can_get_status_msg_3_index': 'Status 3 by index (watt hours).',
    'can_get_status_msg_3_id': 'Status 3 by controller ID.',
    'can_get_status_msg_4_index': 'Status 4 by index (temps, input current, PID pos).',
    'can_get_status_msg_4_id': 'Status 4 by controller ID.',
    'can_get_status_msg_5_index': 'Status 5 by index (input voltage, tachometer).',
    'can_get_status_msg_5_id': 'Status 5 by controller ID.',
    'can_get_status_msg_6_index': 'Status 6 by index (ADC 1-3, PPM).',
    'can_get_status_msg_6_id': 'Status 6 by controller ID.',
    # Motor
    'mc_motor_now': 'Get active motor index (1 or 2). ISR-aware for dual-motor.',
    'mc_select_motor_thread': 'Select motor (1 or 2) for subsequent mc_* calls.',
    'mc_get_motor_thread': 'Get currently selected motor thread.',
    'mc_dccal_done': 'Check if DC calibration completed.',
    'mc_set_pwm_callback': 'Register callback on each PWM cycle.',
    'mc_get_fault': 'Get current fault code.',
    'mc_fault_to_string': 'Convert fault code to string.',
    'mc_set_duty': 'Set duty cycle (-1.0 to 1.0). Ramps to target.',
    'mc_set_duty_noramp': 'Set duty cycle immediately (no ramp).',
    'mc_set_pid_speed': 'Set PID speed target (RPM).',
    'mc_set_pid_pos': 'Set PID position target (degrees).',
    'mc_set_current': 'Set motor current (Amps).',
    'mc_set_brake_current': 'Set brake current (Amps).',
    'mc_set_current_rel': 'Set relative current (-1.0 to 1.0).',
    'mc_set_brake_current_rel': 'Set relative brake current (0.0 to 1.0).',
    'mc_set_handbrake': 'Set handbrake current (Amps).',
    'mc_set_handbrake_rel': 'Set relative handbrake (0.0 to 1.0).',
    'mc_set_tachometer_value': 'Set tachometer (encoder steps).',
    'mc_release_motor': 'Release motor control.',
    'mc_wait_for_motor_release': 'Wait for release. Returns true if within timeout (seconds).',
    'mc_get_duty_cycle_now': 'Current duty cycle.',
    'mc_get_sampling_frequency_now': 'ADC sampling frequency (Hz).',
    'mc_get_rpm': 'Current RPM.',
    'mc_get_amp_hours': 'Amp hours consumed. Pass true to reset.',
    'mc_get_amp_hours_charged': 'Amp hours regen. Pass true to reset.',
    'mc_get_watt_hours': 'Watt hours consumed. Pass true to reset.',
    'mc_get_watt_hours_charged': 'Watt hours regen. Pass true to reset.',
    'mc_get_tot_current': 'Total motor current (Amps).',
    'mc_get_tot_current_filtered': 'Filtered motor current.',
    'mc_get_tot_current_directional': 'Directional current (negative = regen).',
    'mc_get_tot_current_directional_filtered': 'Filtered directional current.',
    'mc_get_tot_current_in': 'Input (battery) current (Amps).',
    'mc_get_tot_current_in_filtered': 'Filtered input current.',
    'mc_get_input_voltage_filtered': 'Filtered input voltage (Volts).',
    'mc_get_tachometer_value': 'Tachometer (encoder steps). Pass true to reset.',
    'mc_get_tachometer_abs_value': 'Absolute tachometer. Pass true to reset.',
    'mc_get_pid_pos_set': 'PID position setpoint.',
    'mc_get_pid_pos_now': 'Current encoder position.',
    'mc_update_pid_pos_offset': 'Update PID position offset. store=true persists to flash.',
    'mc_temp_fet_filtered': 'MOSFET temperature (°C).',
    'mc_temp_motor_filtered': 'Motor temperature (°C).',
    'mc_get_battery_level': 'Battery level (0.0-1.0). Writes remaining Wh to *wh_left.',
    'mc_get_speed': 'Vehicle speed (m/s, uses wheel diameter + gear ratio config).',
    'mc_get_distance': 'Distance traveled (meters, since reset).',
    'mc_get_distance_abs': 'Absolute distance (meters).',
    'mc_get_odometer': 'Total odometer (meters).',
    'mc_set_odometer': 'Set odometer (meters).',
    'mc_set_current_off_delay': 'Auto-off delay for current commands (seconds).',
    'mc_stat_speed_avg': 'Average speed since stat reset (m/s).',
    'mc_stat_speed_max': 'Max speed since stat reset.',
    'mc_stat_power_avg': 'Average power since stat reset (Watts).',
    'mc_stat_power_max': 'Max power since stat reset.',
    'mc_stat_current_avg': 'Average current since stat reset (Amps).',
    'mc_stat_current_max': 'Max current since stat reset.',
    'mc_stat_temp_mosfet_avg': 'Average MOSFET temp since stat reset (°C).',
    'mc_stat_temp_mosfet_max': 'Max MOSFET temp since stat reset.',
    'mc_stat_temp_motor_avg': 'Average motor temp since stat reset (°C).',
    'mc_stat_temp_motor_max': 'Max motor temp since stat reset.',
    'mc_stat_count_time': 'Stats collection period (seconds).',
    'mc_stat_reset': 'Reset all motor statistics.',
    # Comm
    'commands_process_packet': 'Process VESC protocol packet with reply callback.',
    'send_app_data': 'Send custom app data to VESC-Tool / connected client.',
    'set_app_data_handler': 'Register callback for incoming app data. NULL to unregister.',
    'commands_unregister_reply_func': 'Unregister a reply function.',
    # Packets
    'packet_init': 'Init packet state with send + process callbacks.',
    'packet_reset': 'Reset packet state (clear buffers).',
    'packet_process_byte': 'Feed one byte into packet state machine.',
    'packet_send_packet': 'Send packet (handles framing + CRC).',
    # IMU
    'imu_startup_done': 'Check if IMU init is complete.',
    'imu_get_roll': 'Roll angle (degrees).',
    'imu_get_pitch': 'Pitch angle (degrees).',
    'imu_get_yaw': 'Yaw angle (degrees).',
    'imu_get_rpy': 'All three Euler angles [roll, pitch, yaw] at once.',
    'imu_get_accel': 'Raw accelerometer [x, y, z] in g.',
    'imu_get_gyro': 'Raw gyroscope [x, y, z] in deg/s.',
    'imu_get_mag': 'Raw magnetometer [x, y, z].',
    'imu_derotate': 'Transform vector from body to earth frame.',
    'imu_get_accel_derotated': 'Accelerometer in earth frame.',
    'imu_get_gyro_derotated': 'Gyroscope in earth frame.',
    'imu_get_quaternions': 'Orientation as quaternion [w, x, y, z].',
    'imu_get_calibration': 'Run IMU calibration. yaw=current heading. Results in imu_cal.',
    'imu_set_yaw': 'Set yaw angle (degrees).',
    'imu_set_read_callback': 'Register IMU read callback: func(acc, gyro, mag, dt).',
    # AHRS
    'ahrs_init_attitude_info': 'Init ATTITUDE_INFO with defaults.',
    'ahrs_update_initial_orientation': 'Set initial orientation from accel + mag.',
    'ahrs_update_mahony_imu': 'Update with Mahony filter (gyro + accel).',
    'ahrs_update_madgwick_imu': 'Update with Madgwick filter (gyro + accel).',
    'ahrs_get_roll': 'Roll from ATTITUDE_INFO (degrees).',
    'ahrs_get_pitch': 'Pitch from ATTITUDE_INFO (degrees).',
    'ahrs_get_yaw': 'Yaw from ATTITUDE_INFO (degrees).',
    # Terminal
    'terminal_register_command_callback': 'Register terminal command (shows in "help"). Callback gets argc/argv.',
    'terminal_unregister_callback': 'Unregister terminal command.',
    # EEPROM
    'read_eeprom_var': 'Read eeprom_var (uint32/int32/float union) from address.',
    'store_eeprom_var': 'Write eeprom_var. Releases motor during write.',
    # Timeout
    'timeout_reset': 'Reset timeout watchdog.',
    'timeout_has_timeout': 'Check if timeout fault occurred.',
    'timeout_secs_since_update': 'Seconds since last control input.',
    # Plot
    'plot_init': 'Init real-time plot in VESC-Tool with X/Y axis names.',
    'plot_add_graph': 'Add named graph line to plot.',
    'plot_set_graph': 'Select graph for subsequent points.',
    'plot_send_points': 'Send (x, y) point to selected graph.',
    # Custom Config
    'conf_custom_add_config': 'Register custom config panel with get/set/XML callbacks.',
    'conf_custom_clear_configs': 'Unregister all custom configs.',
    # Settings
    'get_cfg_float': 'Read float config parameter by CFG_PARAM.',
    'get_cfg_int': 'Read int config parameter by CFG_PARAM.',
    'set_cfg_float': 'Write float config. Applies HW limits.',
    'set_cfg_int': 'Write int config.',
    'store_cfg': 'Persist motor + app config to flash.',
    # GNSS
    'mc_gnss': 'Get pointer to gnss_data struct (lat, lon, height, speed, hdop, time, date).',
    # Mutex
    'mutex_create': 'Create mutex (LBM-allocated). Free with VESC_IF->free().',
    'mutex_lock': 'Lock mutex. Blocks. Has priority inheritance.',
    'mutex_unlock': 'Unlock mutex.',
    # Timer
    'timer_time_now': 'TIM5 count at **14 MHz**: a delta is `1/14 us`, so divide by 14 for microseconds (wraps every 306.8 s). For busy-wait timing.',
    'timer_seconds_elapsed_since': 'Seconds elapsed since a timer_time_now() capture.',
    'timer_sleep': 'Busy-wait sleep (seconds). High precision, blocks thread.',
    # System
    'sys_lock': 'System lock (disables interrupts). Counting — pair with sys_unlock.',
    'sys_unlock': 'System unlock. Re-enables interrupts on outermost call.',
    'thread_set_priority': 'Thread priority: -5 (lowest) to 5 (highest), 0=normal. FW 6.06+.',
    'shutdown_disable': 'Disable auto-shutdown (momentary button HW). FW 6.06+.',
    'system_time_ticks': 'Current ChibiOS systick count: **1 tick = 100 us** (10 kHz). Wraps every 119.3 h; compare deltas with `ts_to_age_s`.',
    'sleep_ticks': 'Sleep current thread for that many systicks (100 us each).',
    'foc_set_fw_override': 'Override the field-weakening current (Amps). FW 7.00+. C-only: no `foc-set-fw-override` lisp extension is registered upstream.',
    # FOC
    'foc_get_id': 'FOC d-axis current (filtered, Amps).',
    'foc_get_iq': 'FOC q-axis current (filtered, Amps).',
    'foc_get_vd': 'FOC d-axis voltage.',
    'foc_get_vq': 'FOC q-axis voltage.',
    'foc_set_openloop_current': 'Open-loop at given current (Amps) and RPM.',
    'foc_set_openloop_phase': 'Open-loop at given current (Amps) and electrical phase (degrees).',
    'foc_set_openloop_duty': 'Open-loop at given duty and RPM.',
    'foc_set_openloop_duty_phase': 'Open-loop at given duty and electrical phase.',
    # Audio
    'foc_beep': 'Beep: freq=Hz, time=sec, voltage=0.0-1.0. Returns true if busy.',
    'foc_play_tone': 'Continuous tone on channel (0/1). freq=Hz, voltage=0.0-1.0.',
    'foc_stop_audio': 'Stop audio. reset=true clears sample tables.',
    'foc_set_audio_sample_table': 'Set float sample table for a channel.',
    'foc_get_audio_sample_table': 'Get sample table pointer for a channel.',
    'foc_play_audio_samples': 'Play raw int8 samples at f_samp Hz.',
    # Flat Values
    'lbm_start_flatten': 'Start building serialized lisp value. Allocates buffer.',
    'lbm_finish_flatten': 'Finalize flat value.',
    'f_cons': 'Write cons marker into flat value.',
    'f_sym': 'Write symbol into flat value.',
    'f_i': 'Write integer into flat value.',
    'f_b': 'Write byte into flat value.',
    'f_i32': 'Write int32 into flat value.',
    'f_u32': 'Write uint32 into flat value.',
    'f_float': 'Write float into flat value.',
    'f_i64': 'Write int64 into flat value.',
    'f_u64': 'Write uint64 into flat value.',
    'f_lbm_array': 'Write byte array into flat value.',
    # Semaphore
    'sem_create': 'Create semaphore (count=0). Free with VESC_IF->free().',
    'sem_wait': 'Block on semaphore.',
    'sem_signal': 'Signal (increment) semaphore.',
    'sem_wait_to': 'Wait with timeout (ticks). Returns false on timeout.',
    'sem_reset': 'Reset count to 0, wake all waiters.',
    # Encoder
    'encoder_set_custom_callbacks': 'Set custom encoder: read_deg, has_fault, print_info.',
    # Backup
    'store_backup_data': 'Persist backup data (odometer, runtime, HW config) to flash.',
    # Input
    'get_remote_state': 'Nunchuk/remote: joystick X/Y, buttons C/Z, reverse, age.',
    'get_ppm': 'Decoded PPM (-1.0 to 1.0). Auto-starts decoder if needed.',
    'get_ppm_age': 'Seconds since last PPM pulse.',
    'app_is_output_disabled': 'True if apps should disable output.',
    # NVM
    'read_nvm': 'Read from NVM (128KB flash sector).',
    'write_nvm': 'Write to NVM (byte-by-byte flash programming).',
    'wipe_nvm': 'Erase entire NVM sector.',
}


def format_sig(e: dict) -> str:
    if e['kind'] == 'field':
        return f"{e['ret']} {e['name']}"
    p = e['params'] if e['params'] and e['params'] != 'void' else ''
    return f"{e['ret']} {e['name']}({p})"


def generate_markdown(entries: list, enums: dict, types: dict) -> str:
    lines = [
        "# VESC C Interface API Reference",
        "",
        "Auto-generated from `vesc_c_if.h` by `gen_vesc_c_if_docs.py`.",
        "Regenerate: `python3 gen_vesc_c_if_docs.py`",
        "",
        "All functions: `VESC_IF->function_name(args)`",
        "",
        "## Key Types",
        "",
        "| Type | Description |",
        "|------|-------------|",
        "| `lbm_value` | Encoded lisp value (uint32) |",
        "| `lbm_uint` / `lbm_int` | Unsigned/signed integer (uint32/int32) |",
        "| `lbm_cid` | Context ID (uint32) |",
        "| `lbm_flat_value_t` | Serialized lisp value buffer |",
        "| `lib_thread` / `lib_mutex` / `lib_semaphore` | Opaque handles (void*) |",
        "| `systime_t` | System ticks (uint32). 1 tick = 100µs |",
        "",
    ]

    # Enums
    for name, values in enums.items():
        lines.append(f"### `{name}`")
        lines.append("")
        for vname, vval in values:
            lines.append(f"- `{vname}`" + (f" = {vval}" if vval else ""))
        lines.append("")

    # Structs/unions
    for name, info in types.items():
        lines.append(f"### `{name}` ({info['kind']})")
        lines.append("")
        lines.append("```c")
        lines.append(f"{info['kind']} {{")
        for f in info['fields']:
            lines.append(f"  {f}")
        lines.append(f"}} {name};")
        lines.append("```")
        lines.append("")

    # Group entries by category
    by_cat = {}
    for e in entries:
        by_cat.setdefault(e['category'], []).append(e)

    for cat_name, _ in CATEGORIES:
        cat_entries = by_cat.get(cat_name, [])
        if not cat_entries:
            continue
        lines.append(f"## {cat_name}")
        lines.append("")
        lines.append("| Function | Signature | Description |")
        lines.append("|----------|-----------|-------------|")
        for e in cat_entries:
            sig = format_sig(e)
            desc = DESC.get(e['name'], '')
            lines.append(f"| `{e['name']}` | `{sig}` | {desc} |")
        lines.append("")

    # Macros
    lines.extend([
        "## Macros",
        "",
        "| Macro | Description |",
        "|-------|-------------|",
        "| `VESC_IF` | `((vesc_c_if*)(0x1000F800))` — the interface struct |",
        "| `HEADER` | Declare program pointer (required at file scope) |",
        "| `INIT_FUN` | Declare init function (called on load) |",
        "| `INIT_START` | First line in INIT_FUN body |",
        "| `PROG_ADDR` | `((uint32_t)&prog_ptr)` — this program's address |",
        "| `ARG` | `(*VESC_IF->get_arg(PROG_ADDR))` — stored argument |",
        "| `SYSTEM_TICK_RATE_HZ` | `10000` (100µs per tick) |",
        "",
    ])

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--header", type=Path, default=DEFAULT_HEADER)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.header.exists():
        print(f"ERROR: {args.header} not found")
        return 1

    entries = parse_vesc_c_if(args.header)
    enums = parse_enums(args.header)
    types = parse_type_defs(args.header)
    md = generate_markdown(entries, enums, types)

    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / "vesc_c_if_api.md"
    out_file.write_text(md, encoding='utf-8')

    n_func = sum(1 for e in entries if e['kind'] == 'func')
    n_field = sum(1 for e in entries if e['kind'] == 'field')
    n_cat = len(set(e['category'] for e in entries))
    print(f"Generated: {out_file}")
    print(f"  {n_func} functions, {n_field} fields in {n_cat} categories")
    print(f"  {len(enums)} enums, {len(types)} structs/unions")
    return 0


if __name__ == "__main__":
    exit(main())

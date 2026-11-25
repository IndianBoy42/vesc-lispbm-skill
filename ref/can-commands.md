# CAN commands: receiving, reacting, intercepting

Three rungs, and only two of them are available to a Lisp script:

| Rung | What you can do | Where |
|---|---|---|
| **Observe** | get a copy of a frame after the firmware has already acted on it | Lisp: `can-recv-sid` / `can-recv-eid` / `event-can-*` |
| **Intercept** | take the frame *instead of* the firmware, so `CAN_PACKET_SET_RPM`/`SET_POS` never reach the built-in PID | native library: `can_set_eid_cb` / `can_set_sid_cb` |
| **Control** | run your own loop on the motor | Lisp `set-current`/`set-duty`, or a native lib thread / `mc_set_pwm_callback` |

A Lisp-only script cannot intercept. `lispif_process_can` is called *after* `decode_msg`, has no return value, and consuming semantics exist only in the C callback layer. Everything below about wire format, ids and timeouts applies to all three rungs.

Paths are relative to `$VESC_FW`, a
[`vedderb/bldc`](https://github.com/vedderb/bldc) checkout. Firmware sources the
skill bundles are in `ref/upstream/`.

## The receive path

`comm/comm_can.c:1390-1421` (the `eid_callback`/`sid_callback`/`decode_msg` receive block), `cancom_process_thread` (NORMALPRIO, 2 KB stack — `cancom_process_thread_wa` and its `chThdCreateStatic` call in `comm/comm_can.c`):

```c
// extended (29-bit) — what VESC control frames use
if (eid_callback) eid_cb_used = eid_callback(rxmsg.EID, rxmsg.data8, rxmsg.DLC);
if (!eid_cb_used) {
    if (!bms_process_can_frame(...)) {
        decode_msg(...);                 // ACTS on SET_RPM/SET_POS/SET_CURRENT...
        lispif_process_can(...);         // Lisp gets a copy
    }
}

// standard (11-bit)
if (sid_callback) sid_cb_used = sid_callback(rxmsg.SID, ...);
if (!sid_cb_used) sid_cb_used = bms_process_can_frame(...);
if (!sid_cb_used) lispif_process_can(...);       // decode_msg is NOT called at all
```

Consequences that decide designs:

- **Returning `true` from a callback is total.** That frame then reaches neither BMS, nor `decode_msg`, nor Lisp. Doc comment: the `comm_can_set_sid_cb`/`comm_can_set_eid_cb` block in `comm/comm_can.c`.
- **In `CAN_MODE_VESC`, 11-bit frames are never executed by the firmware** — no `decode_msg` in that branch. VESC's own control frames are 29-bit EID (see the `CAN_ID_...` transmit block in `comm_can_transmit_sid/eid`), so intercepting `SET_RPM` means the **EID** callback. A SID callback answers a different question.
- **The callback fires before BMS**, so a BMS-consumed frame also never reaches Lisp. Return `false` for anything you did not handle.
- Both CAN interfaces land in one queue: `comm_can_get_rx_frame(0)` drains CAN1 and CAN2 indistinguishably (in `comm/comm_can.c`), so a callback cannot tell which wire a frame arrived on.

`CAN_MODE` gates the whole path (`cancom_process_thread`'s mode check in `comm/comm_can.c`). In `UAVCAN` this thread bails before touching the queue and libcanard drains it instead (`canard_driver.c`, its `bxCAN` receive path). In `COMM_BRIDGE`/`UNUSED` the callbacks and Lisp still run, `COMM_BRIDGE` forwards each frame to the commands interface *before* them, and `decode_msg` never runs — nothing to intercept. Interception is only meaningful in `CAN_MODE_VESC`.

## Wire format

EID = `(packet_id << 8) | vesc_id`; payload is big-endian `int32` scaled by the table below (`buffer_append_int32`/`buffer_get_int32` in `util/buffer.c`; reference: `documentation/comm_can.md`).

| Command | id | Scale | Payload |
|---|---|---|---|
| `CAN_PACKET_SET_DUTY` | 0 | 1e5 | duty |
| `CAN_PACKET_SET_CURRENT` | 1 | 1e3 | amps |
| `CAN_PACKET_SET_RPM` | 3 | 1 | rpm, raw int32 |
| `CAN_PACKET_SET_POS` | 4 | 1e6 | degrees |
| `CAN_PACKET_SET_CURRENT_REL` | 10 | 1e5 | fraction |

`SET_CURRENT` is the one oddity: with `len >= 6` the *first* 2 bytes are an off-delay and the current follows (`CAN_PACKET_SET_CURRENT` case in `decode_msg`), while the sender writes current first (the same packet in `comm_can_transmit_sid/eid`). Read current from a 4-byte frame, or read it last from a 6-byte one.

Addressing rule copied from `decode_msg` (in `comm/comm_can.c`): `id == 255 || id == controller_id` (plus `controller_id + 1` on dual-motor hardware, `utils_second_motor_id` in `util/utils_sys.c`). Match the same set, so other ESCs' setpoints pass through untouched.

Getting your own id:

```clj
(can-local-id)              ; ext_can_local_id in lispBM/lispif_vesc_extensions.c
(conf-get 'controller-id)   ; same field, ext_conf_get
```

Both read `appconf->controller_id`, which is never -1 at runtime: the default falls back to a UUID-derived id (`hw_id_from_uuid` in `hwconf/hw.c`), and `App Settings → General → VESC ID` overwrites it.

`(conf-get 'controller-id 1)` returns the *hardware default*, not the configured value (`ext_conf_get` branches on the second arg).

## Observe from Lisp

```clj
; one thread blocks in can-recv-eid; returns (id data) or the symbol timeout
(loopwhile t
  (let ((frame (can-recv-eid 0.1)))
    (if (eq frame 'timeout)
        nil
        (proc-cmd (car frame) (car (cdr frame))))))
```

or the event style (`lispBM/README.md:5330-5400`):

```clj
(defun ev-handler ()
  (loopwhile t
    (recv
      ((event-can-eid . ((? id) . (? data))) (proc-cmd id data))
      (_ nil))))
(event-register-handler (spawn ev-handler))
(event-enable 'event-can-eid)
```

Traps, all verified in `lispBM/lispif_vesc_extensions.c` (the `can-recv-*` extensions and the `lbm_event` CAN handlers; see the `ext_can_recv_*` and `event-can-*` handlers):

- **One receiver per direction.** `can_recv_sid_cid` / `can_recv_eid_cid` are single globals: a second thread calling `can-recv-eid` overwrites the first, which then blocks forever. Frames also go either to the blocked thread *or* to the event handler — never both.
- **A frame can vanish in the gap after a timeout.** The timeout wakes the thread without clearing `can_recv_*_cid`, so a frame arriving before the thread re-enters `can-recv-*` is delivered to a cid that is no longer blocked: the evaluator finds no blocked context, frees the payload and resets the cid to `-1` (`handle_event_unblock_ctx` in `lispBM/lispBM/src/eval_cps.c`, the `ext_can_recv_*` timeout path in `lispBM/lispif_vesc_extensions.c`). A tight re-blocking loop loses nothing; a loop that does work between timeouts silently drops frames.
- **Events drop silently when the handler's mailbox is full** (`lbm_event` returns `false`, `lispBM/lispBM/src/eval_cps.c:459-476`, `event_internal`). `event-can-eid` is a firehose on a busy bus: every status frame from every device arrives. Filter on `(shr id 8)` immediately.
- **The handler runs on the evaluator, at the bottom of the stack.** `lbm_event` queues the frame into the handler thread's mailbox from the CAN process thread; the handler itself is a Lisp thread, so it executes on the eval thread (NORMALPRIO-1, `eval_thread_wa`'s `chThdCreateStatic` call in `lispBM/lispif.c`) below the CAN reader (NORMALPRIO+1, `cancom_process_thread_wa`) and the motor ISR. Jitter is unbounded by design; a control loop does not belong here.
- **The frame you receive is already history.** `decode_msg` ran first, so `SET_RPM` has already put the speed PID in charge. Calling `set-current` from the handler wins for a few control iterations and then loses again when the next `SET_RPM` arrives. This is the "don't" case, not an alternative to interception.

## Intercept from a native library

The consume hooks are C function pointers with no Lisp binding (`sid_callback`/`eid_callback` in `comm/comm_can.c`), exported to native libs as `can_set_sid_cb` / `can_set_eid_cb` (`lispBM/c_libs/vesc_c_if.h:400-401`, wired in `lispBM/lispif_c_lib.c`'s `lib_can_set_*` functions). Build with `lispBM/c_libs/rules.mk`, see `native-extensions/SKILL.md`, `lispBM/c_libs/examples/*`.

```c
#include "vesc_c_if.h"
HEADER

static volatile float sp_rpm;
static volatile float sp_pos;
static volatile uint8_t sp_kind;      // 3 = SET_RPM, 4 = SET_POS, 0 = nothing yet
static uint8_t my_id;

// Runs on the CAN process thread: copy and return. No sleeps, no printf, no malloc.
static bool can_eid_cb(uint32_t id, uint8_t *data, uint8_t len) {
    if (len < 4) return false;
    uint8_t dst = id & 0xFF;
    if (dst != my_id && dst != 255) return false;       // someone else's setpoint

    int32_t raw = (int32_t)(((uint32_t)data[0] << 24) | ((uint32_t)data[1] << 16) |
                            ((uint32_t)data[2] << 8)  |  (uint32_t)data[3]);

    switch (id >> 8) {
    case 3: sp_rpm = (float)raw;         sp_kind = 3; break;   // SET_RPM
    case 4: sp_pos = (float)raw * 1e-6f; sp_kind = 4; break;   // SET_POS
    default: return false;                                     // not ours
    }

    VESC_IF->timeout_reset();   // decode_msg would have done this; it no longer runs
    return true;                // consumed: no PID, no BMS, no Lisp event
}

// (ext-ladrc-init my-id) -> t
static lbm_value ext_init(lbm_value *args, lbm_uint argn) {
    if (argn != 1 || !VESC_IF->lbm_is_number(args[0])) return VESC_IF->lbm_enc_sym_eerror;
    my_id = (uint8_t)VESC_IF->lbm_dec_as_i32(args[0]);
    VESC_IF->can_set_eid_cb(can_eid_cb);
    return VESC_IF->lbm_enc_sym_true;
}

// (ext-ladrc-setpoint) -> (kind . value) or nil
static lbm_value ext_setpoint(lbm_value *args, lbm_uint argn) {
    (void)args; (void)argn;
    if (sp_kind == 0) return VESC_IF->lbm_enc_sym_nil;
    lbm_value kind = VESC_IF->lbm_enc_i(sp_kind);
    lbm_value val = VESC_IF->lbm_enc_float(sp_kind == 3 ? sp_rpm : sp_pos);
    return VESC_IF->lbm_cons(kind, val);
}

static void stop(void *arg) {
    (void)arg;
    VESC_IF->can_set_eid_cb(0);      // code is about to be unloaded: drop the pointer
}

INIT_FUN(lib_info *info) {
    INIT_START
    info->stop_fun = stop;           // without this the loader cannot track the lib
    VESC_IF->lbm_add_extension("ext-ladrc-init", ext_init);
    VESC_IF->lbm_add_extension("ext-ladrc-setpoint", ext_setpoint);
    return true;
}
```

```clj
(load-native-lib ladrc-bin)
(ext-ladrc-init (can-local-id))     ; pass the id in: no CIF getter exists
```

Binding rules that bite:

- **`info->stop_fun` is mandatory here.** The loader keys "loaded" on it (the `find_loaded_lib`/`lib_load` block in `lispBM/lispif_c_lib.c`) and only calls it on unload/restart (`lib_unload`). Without it, `unload-native-lib` reports "Library not loaded" and the callback keeps pointing at unloaded code.
- **One slot, no chaining.** `can_set_eid_cb` assigns a single pointer; a second registrant (another lib, `applications/finn` code) silently replaces the first. Clear it to `0` on stop.
- **Extensions must be named `ext-…`**, enforced by `lib_add_extension` (in `lispBM/lispif_c_lib.c`).
- **The local CAN id is not readable from C.** `get_cfg_int`/`CFG_PARAM` cover a fixed subset with no controller-id member (`vesc_c_if.h`, the `CFG_PARAM` macro table; `lib_get_cfg` in `lispif_c_lib.c`). Pass it from Lisp, as above — do not parse EEPROM for it.
- **Consumed means consumed.** The frame no longer reaches `lispif_process_can`, so your lib is the only path to Lisp. Publish it through an extension (above), or block a Lisp thread and unblock it from the callback with `lbm_unblock_ctx` + the `f_*` flatten helpers (`vesc_c_if.h`, the `f_i/f_f/f_u32/...` block), which is the pattern `can-recv-eid` itself uses.
- **Dual-motor boards bypass both callbacks for local sends.** `comm_can_transmit_eid_replace` calls `decode_msg` directly when the target id is this board's (in `comm/comm_can.c`), so a native `canset-rpm` to the sibling motor is never intercepted.

### Where the control loop goes

Two viable homes, neither in the CAN callback:

- **A lib thread** (`VESC_IF->spawn`, NORMALPRIO — the `spawn` member of `vesc_c_if` in `lispBM/c_libs/vesc_c_if.h`) reading the volatile setpoint. Add `VESC_IF->thread_set_priority` if it must outrank other app threads; keep it below `NORMALPRIO + 1` so the CAN reader still runs.
- **`mc_set_pwm_callback`** (the `vesc_c_if` member → `mc_interface_set_pwm_callback` in `motor/mc_interface.c`, called from the FOC ADC ISR at `motor/mcpwm_foc.c:3819-3822` → `motor/mc_interface.c:1938-1940`): the honest place for a per-cycle controller. It runs at the control-loop rate, not the raw ISR rate: 25 kHz with `foc_control_sample_mode` V0_V7, 12.5 kHz in the default V0 mode (`motor/mcconf_default.h:262-263,382-383`, `motor/mc_interface.c:1028-1041`). ISR context: no blocking, no allocation, and it is another single shared slot.

## Timeouts and safety

`timeout_reset()` is called by `decode_msg` for every control packet (in `comm/comm_can.c`) and by the Lisp setters (the `ext_set_*` block in `lispBM/lispif_vesc_extensions.c`). A consumed frame resets nothing, so the app timeout — `APPCONF_TIMEOUT_MSEC` 1000 by default (`applications/appconf_default.h`) — will brake the motor mid-run unless your callback calls `VESC_IF->timeout_reset()` (the `timeout_reset` member of `vesc_c_if`) or your Lisp loop calls `(timeout-reset)`.

Losing the host therefore looks the same as before interception: after the timeout the firmware brakes/releases (`timeout.c`, the timeout thread's brake branch). Do not disable the timeout to "fix" a missing `timeout_reset`; fix the reset.

## Verify it actually intercepted

```clj
(can-local-id)          ; the id your callback must match
(get-rpm-set)           ; mcpwm_foc_get_pid_speed_set (ext_get_rpm_set in lispBM/lispif_vesc_extensions.c)
(get-pos)               ; mc_interface_get_pid_pos_now
```

Send a `SET_RPM` to this VESC from the bench host. If interception works, the motor does not follow it and `get-rpm-set` stays where it was; the terminal's `events` command shows no `set_pid_speed` entry (`mc_interface_set_pid_speed` logs it, in `motor/mc_interface.c`). If the motor follows the frame, the callback either is not registered or returned `false`.

Frame visibility, without guessing: `COMM_CAN_FWD_FRAME` re-transmits a frame you pass it onto the bus (its case in `comm/commands.c`) — useful to mirror frames to a sniffer, not to observe what this VESC received. `can-msg-age` / `canget-*` read the cached status frames the *other* devices sent (the `ext_can_msg_age`/`ext_can_get_*` handlers).

## Off-target

The bundled x86 REPL stubs every CAN entry point with `lbm_enc_sym(SYM_EERROR)` (`lispBM/lispBM/repl/bldc_extension_stubs.c`, the `can-recv-sid`/`can-recv-eid`/`conf-get` stubs). A script that calls `can-recv-eid` there returns an error immediately, so test the control logic against injected frames (`ref/testing.md`) and leave the CAN plumbing for the bench.

## What does not exist

- No Lisp binding for the consume hooks, and no `can-consume` / `can-set-cb`.
- No `can-send` — the senders are `can-send-sid` / `can-send-eid` (`ext_can_send_*` in `lispBM/lispif_vesc_extensions.c`).
- No hardware acceptance filter to select by packet id: this firmware never calls `canSTM32SetFilters`, so ChibiOS programs its accept-everything default (`can_lld.c`, the `CAN_LLD_FILTER`/accept-all init in `ChibiOS_3.0.5`). Every decision is made in software, per frame — including for frames the firmware then drops.

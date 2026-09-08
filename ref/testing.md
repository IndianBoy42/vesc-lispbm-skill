# Running and testing lispBM scripts without a VESC

The upstream lispBM tree in this checkout contains a working x86-64 REPL, and the
checked-in binary runs as is (no build, no 32-bit multilib):

```sh
LP=~/dev/vesc/lispBM/lispBM
$LP/repl/repl --terminate --history_file "" -H 12000 -M 10 -s /tmp/myscript.lisp
```

- `-s FILE` loads and evaluates a script; `--terminate` exits at EOF instead of dropping
  into the interactive REPL. `-e EXPR` evaluates one expression instead.
- `--history_file ""` keeps a headless run from writing `~/.lbm_history`.
- `-H cells` / `-M index` raise the memory budget. **The defaults (2048 cons cells, 10K
  words of array memory) are much smaller than the ESC's (~2761 cells, 28 KB) and a script
  with ring buffers will die with `out_of_memory` without these.**
- `-M` takes an index, not bytes: `1`=128 words, `6`=10K, `10`=32K, and so on (see the
  switch in `repl/repl.c` or run `repl --help`).

Time: `systime` is **microseconds** on the host REPL and 10 kHz ChibiOS ticks on the ESC, so
never do arithmetic on it — it is an opaque token. `secs-since` is seconds in both, which is
what a script should measure its sample period with.

## Stubbing the VESC-only functions

The REPL has no `get-temp-fet`, `conf-get`, `plot-*`, and so on. Rather than modify the
script for the test, define those names as lisp functions **before** the script is loaded
and let the script run unmodified. Concatenating three files is enough:

```sh
cat stubs.lisp script.lbm driver.lisp > /tmp/test.lisp
$LP/repl/repl --terminate -H 12000 -M 10 -s /tmp/test.lisp
```

```lisp
; stubs.lisp -- must come first, the script calls some of these at load time
(def syn-tau 200.0)
(defun syn-temp (tt) (+ 100.0 (* -75.0 (pow 2.718281828 (/ (- 0.0 (+ tt syn-tau)) syn-tau)))))
(defun get-temp-fet (n) (syn-temp (secs-since syn-t0)))   ; synthetic, on the real clock
(defun get-temp-mot () 48.0)
(defun conf-get (sym) 85.0)
(defun plot-init (x y) nil)
(defun plot-add-graph (n) nil)
(defun plot-set-graph (i) nil)
(defun plot-send-points (x y) { (setq syn-n (+ syn-n 1)) nil })
(def syn-t0 (systime))
```

Points that make this work:

- Driving the synthetic signal from `(secs-since syn-t0)` rather than from a sample counter
  keeps it consistent with whatever sample period the loop actually achieves, so a script
  that measures its own `dt` still sees a correct exponential.
- `loopwhile-thd` expands to `(spawn n (fn () (loopwhile cond body)))`, so the monitor runs
  in a thread while the main thread continues. With `--terminate` the REPL exits at EOF and
  kills it, so the driver must keep the main thread alive, e.g. wait on a counter the
  script bumps and bail out after a bounded number of iterations:

  ```lisp
  (def bail 0)
  (loopwhile (and (< samples-taken 1400) (< bail 3000)) { (sleep 0.02) (setq bail (+ bail 1)) })
  ```
- To watch the estimator's internal state, note that the script's globals are visible to
  the driver: `(ix fet-st ST-CNT)`, `(ix fet-out OUT-TAU)`, and so on print from the driver.
- To run a script whose sample period or window is minutes long, copy it and patch the
  config values with `sed` instead of waiting. Patch only the config: the algorithm is what
  is under test.

Do **not** use `--bldc_stubs` / `--vesc_express_stubs`: those load placeholder
implementations that return EERROR and collide with the REPL's own extensions — with
`--bldc_stubs` even `(print "x")` fails with `eval_error` (verified). Write your own stubs.

## Verifying the maths separately

The host REPL's scheduling is far worse than the ESC's: sample periods wander by tens of
percent and a GC or a printf can stall a "1 ms" sleep for tens of ms. Anything that depends
on wall-clock accuracy (a time constant, a rate) is therefore only indicative on the host.
For a numerical routine, mirror it in Python with `struct.pack('f', ...)` rounding at each
step and check it against a synthetic signal with exact known parameters; then use the REPL
to prove the script *runs*, wraps its buffers, prints, and handles the branches. Between the
two you cover both the maths and the plumbing.

## Verified gotchas

Each of these cost real debugging time; all were reproduced in this checkout.

| Symptom | Cause |
|---|---|
| `type_error` in `+`, reported `At: t` | **A binding named `t`.** `t` (and `nil`) are self-evaluating constants: `(defun f (t) (+ t 5.0))` fails because `t` reads as the symbol, not the argument. Rename it. |
| A function silently does only its first statement | **`defun`'s body is a single expression.** `(defun f (x) a b)` defines the body as `a` and drops `b`, with no warning. Wrap the body in `{ ... }`. |
| A statement after a loop runs after the loop | Same rule for the loops: `(loopwhile c body)` and `(loopfor i s c u body)` take one body expression. A second trailing form is not part of the loop. |
| `variable_not_bound: e-9` | **No scientific notation.** `1e-9` parses as the symbol `e-9`. Write `0.000000001`. |
| `eval_error` in `buflen` | `buflen` is for byte buffers; calling it on a general `array` is an error. |
| Reading a float gives rubbish | `bufget-f32`/`bufset-f32` index in **bytes**, not elements: element `i` is at `(* 4 i)`. |
| `variable_not_bound` for a name that is clearly assigned | `def`/`define` always write the **global** environment, even inside a function or a `{}` block; a value meant to be local should use `let`. |
| Index goes negative and `mod` does not fix it | LispBM's `mod` follows the sign of the dividend; add the modulus before the `mod` for a guaranteed non-negative result. |
| A global counter shared with a spawned thread does not advance | It does work; check that the thread is still alive first. A raised error kills only that thread, and the driver's output goes on. |
| Printed numbers are `1.500000f32` on the host | The host build is 64-bit lispBM with float32 values; the ESC is the same float32 (`lbm_float = float`). Both are single precision, which is what a numeric script has to be designed for. |

Types and literals (from `ref/02-numbers-and-numerical-types.md`): an integer literal is a
28-bit `i` (56-bit on the host build), a literal with a decimal point is `f32`, and other
widths need a qualifier (`1u`, `1i32`, `1.0f64`). Operations promote to the largest
operand type, so `(+ 1 3.14)` is a float. There is no need for a decimal point on integers,
but there is no way to write a float without one.

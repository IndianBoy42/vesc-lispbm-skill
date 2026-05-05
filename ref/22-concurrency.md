## Concurrency

The concurrency support in LispBM is provided by the set of functions, `spawn`, `wait`, `yield` and `atomic` described below.  Concurrency in LispBM is scheduled by a round-robin scheduler that splits the runtime system evaluator fairly (with caveats, below) between all running processes. 

When a process is scheduled to run, made active, it is given a quota of evaluator "steps" to use up. The process then runs until that quota is exhausted or the process itself has signaled it wants to sleep by yielding or blocking (for example by waiting for a message using the message passing system). 

A process can also request to not be "pre-empted" while executing a certain expression by invoking `atomic`. One should take care to make blocks of atomic code as small as possible as it disrupts the fairness of the scheduler. While executing inside of an atomic block the process has sole ownership of the shared global environment and can perform atomic read-modify-write sequences to global data. 


---


### spawn

Use `spawn` to launch a concurrent process. Spawn takes a closure and arguments to pass to that closure as its arguments. The form of a spawn expression is `(spawn opt-name opt-stack-size closure arg1 ... argN)`. 

Each process has a runtime-stack which is used for the evaluation of expressions within that process. The stack size needed by a process depends on  1. How deeply nested expressions evaluated by the process are.  2. Number of recursive calls (Only if a function is NOT tail-recursive).  3. The Number of arguments that functions called by the process take. 

Having a stack that is too small will result in a `out_of_stack` error. 

The default stack size is 256 words (1K Bytes) and should be more than enough for reasonable programs. Many processes will work perfectly fine with a lot less stack. You can find a good size by trial and error. 




---


### spawn-trap

Use `spawn-trap` to spawn a child process and enable trapping of exit conditions for that child. The form of a `spawn-trap` expression is `(spawn-trap opt-name opt-stack-size closure arg1 .. argN)`.  If the child process is terminated because of an error, a message is sent to the parent process of the form `(exit-error tid err-val)`. If the child process terminates successfully a message of the form `(exit-ok tid value)` is sent to the parent. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(defun thd nil
  (+ 1 2))
(spawn-trap thd)
(recv ((exit-error (? tid) (? e)) 'crash)
      ((exit-ok (? tid) (? v)) 'ok))
```


</td>
<td>


```clj
ok
```


</td>
</tr>
<tr>
<td>


```clj
(defun thd nil
  (+ 1 kurt-russel))
(spawn-trap thd)
(recv ((exit-error (? tid) (? e)) 'crash)
      ((exit-ok (? tid) (? v)) 'ok))
```


</td>
<td>


```clj
crash
```


</td>
</tr>
</table>




---


### self

Use `self` to obtain the thread-id of the thread in which `self` is evaluated. The form of a `self` expression is `(self)`. The thread id is of an integer type. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(self)
```


</td>
<td>

```clj
4279
```


</td>
</tr>
</table>




---


### wait

Use `wait` to wait for a spawned process to finish. The argument to `wait` should be a process id. The `wait` blocks until the process with the given process id finishes. When the process with with the given id finishes, the wait function returns True. 

Be careful to only wait for processes that actually exist and do finish. Otherwise you will wait forever. 




---


### yield

To put a process to sleep, call `yield`. The argument to `yield` is number indicating at least how many microseconds the process should sleep. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(yield 10)
```


</td>
<td>

```clj
t
```


</td>
</tr>
</table>




---


### sleep

'sleep' puts a thread to sleep and differs from 'yield' only in the argument. 'sleep' takes a floating point number indicating how long in seconds the thread should sleep at least. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(sleep 1.000000f32)
```


</td>
<td>

```clj
t
```


</td>
</tr>
</table>




---


### atomic

> ***Special form***

`atomic` can be used to execute a LispBM one or more expression without allowing the runtime system to switch process during that time. `atomic` is similar to progn with the addition of being uninterruptible. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(atomic (+ 1 2)
        (+ 3 4)
        (+ 4 5))
```


</td>
<td>

```clj
9
```


</td>
</tr>
</table>




---


### exit-ok

The `exit-ok` function terminates the thread in a "successful" way and returns a result specified by the programmer. The form of an `exit-ok` expression is `(exit-ok value)`.  If the process that calls `exit-ok` was created using `spawn-trap` a message of the form `(exit-ok tid value)` is be sent to the parent of this process. 




---


### exit-error

The `exit-error` function terminates the thread with an error specified by the programmer.  The form of an `exit-error` expression is `(exit-error err_val)`. If the process that calls `exit-error` was created using `spawn-trap` a message of the form `(exit-error tid err_val)` is sent to the parent of this process. 




---


### kill

The `kill` function allows you to force terminate another thread. It has the signature `(kill thread-id-expr val-expr)`, where `thread-id-expr` is the thread that you want to terminate, and `val-expr` is the final result the thread dies with. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(defun f nil
  (f))
(define id (spawn f))
(kill id nil)
```


</td>
<td>


```clj
t
```


</td>
</tr>
</table>

The `val-expr` can be observed if the thread exit status is captured using `spawn-trap` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(defun f nil
  (f))
(define id (spawn-trap f))
(kill id 'kurt-russel)
(recv ((? x) x))
```


</td>
<td>


```clj
(exit-ok 111050 kurt-russel)
```


</td>
</tr>
</table>

The `val-expr` could be used to communicate to a thread monitor that the thread it monitors has been intentionally but externally killed. 




---
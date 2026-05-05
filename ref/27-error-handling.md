## Error handling

If an error occurs while evaluating a program, the process that runs that program is killed.  The result of the killed process is set to an error symbol indicating what went wrong. 

If the process was created using `spawn` (or equivalently, started by a issuing a command in the repl), the process dies and an error message is presented over the registered printing callback (dependent on how LispBM is integrated into your system). The `ctx_done_callback` is also called and performs other integration dependent tasks related to the shutting down of a process. 

If the process was created using `spawn-trap`, in addition to the above, a message is sent to the parent process (the process that executed the spawn-trap) containing information about the process that struck an error. See <a href="#spawn-trap">spawn-trap</a>. The parent process can now choose to restart the process that crashed or to take some other action. 

Another way to catch errors is to use `trap` which works similar to `spawn-trap` but it does not spawn a thread. `trap` takes one argument which is an expressions. The expression is evaluated and if it fails `(trap expr)` returns an object representing the error. For more information on `trap`, see  <a href="#trap">trap</a>. 


### read_error

The `read_error` symbol is returned if the reader cannot parse the input code. Read errors are most likely caused by syntactically incorrect input programs. 

   - Check that all opening parenthesis are properly closed.




---


### type_error

The `type_error` symbol is returned by built-in functions or extensions if the values passed in are of incompatible types. 




---


### eval_error

The `eval_error` symbol is returned if evaluation could not proceed to evaluate the expression. This could be because the expression is malformed. 

Evaluation error happens on programs that may be syntactically correct (LispBM has a very low bar for what is considered syntactically correct), but semantically nonsensical. 

   - Check the program for mistakes.
   - Are your parenthesis enclosing the correct subterms?
   - Check that you haven't written, for example, (1 + 2) where it should be (+ 1 2).




---


### out_of_memory

The `out_of_memory` symbol is returned if the heap is full and running the garbage collector was not able to free any memory up. 

The program you have written requires more memory. 

   - Increase the heap size.
   - Rewrite the application to use less memory.




---


### fatal_error

The `fatal_error` symbol is returned in cases where the LispBM runtime system cannot proceed. Something is corrupt and it is not safe to continue. 

   - If this happens please send the program and the full error message to blog.joel.svensson@gmail.com. It will be much appreciated.




---


### out_of_stack

The `out_of_stack` symbol is returned if the evaluator runs out of continuation stack (this is its runtime-stack). You are most likely writing a non-tail-recursive function that is exhausting all the resources. 

   - Check your program for recursive functions that are not tail-recursive Rewrite these in tail-recursive form.
   - If you spawned this process in a small stack. For example (spawn 10 prg), try to spawn it with a larger stack.




---


### division_by_zero

The `division_by_zero` symbol is returned when dividing by zero. 

   - Check your math.
   - Add 0-checks into your code at a strategic position.




---


### variable_not_bound

The `variable_not_bound` symbol is returned when evaluating a variable (symbol) that is neighter bound nor special (built-in function). 




---
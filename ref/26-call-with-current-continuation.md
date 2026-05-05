## Call with current continuation

"Call with current continuation" is called `call-cc` in LBM. Call with current continuation saves the "current continuation", which encodes what the evaluator will do next, into an object in the language. This encoded continuation object behaves as a function taking one argument. 

The `call-cc` should be given a function, `f`, as the single argument. This function, `f`, should also take a single argument, the continuation. At any point in the body of `f` the continuation can be applied to a value, in essense replacing the entire `call-cc` with that value. All side-effecting operations operations up until the application of the continuation will take effect. 

From within a `call-cc` application it is possible to bind the continuation to a global variable which will allow some pretty arbitrary control flow. 

The example below creates a macro for a `progn` facility that allows returning at an arbitrary point.

 ```clj
 (define do (macro (body)
                   `(call-cc (lambda (return) (progn ,@body)))))
 ```

 The example using `do` below makes use of `print` which is not a built-in feature of lispBM. There are just to many different ways a programmer may want to implement `print` on an microcontroller. Use the lispBM extensions framework to implement your own version of `print`

 ```clj
 (do ((print 10)
      (return 't)
      (print 20)))
 ```

 In the example above only "10" will be printed. Below is an example that conditionally returns.

 ```clj
 (define f (lambda (x)
             (do ((print "hello world")
                  (if (= x 1)
                      (return 't)
                      nil)
                  (print "Gizmo!")))))
 ```

 


### call-cc

> ***Special form***

The form of a `call-cc` expression is `(call-cc f)`, where f is a function taking a continuation k. In code most uses of call-cc will have the form `(call-cc (lambda (k) expr ))`. When using `call-cc` the expr above is allowed to bind `k` to a global variable. 



---


### call-cc-unsafe

> ***Special form***

`call-cc-unsafe` is similar to `call-cc` in form. `(call-cc-unsafe f)` and in code usually as `(call-cc-unsafe (lambda (k) expr))`. When using call-cc-unsafe you must NOT let the `k` leak out of the scope created by the enclosing `call-cc-unsafe`! That is, if `k` is used at all, it must be within `expr`. Binding `k` (directly or indirectly) to a global is a violation of the trust I am putting in you. 



---
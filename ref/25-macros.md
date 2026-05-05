## Macros

LispBM macros are created using the `macro` keyword. A macro is quite similar to [`lambda`](#lambda) in lispBM except that arguments are passed in unevaluated. Together with the code-splicing capabilities given by [quasiquotation](#quasiquotation), this provides a powerful code-generation tool. 

A macro application is run through the interpreter two times. Once to evaluate the body of the macro on the unevaluated arguments. The result of this first application should be a program. The resulting program then goes through the interpreter again to compute final values. 

Given this repeated evaluation, macros are not a performance boost in lispbm.  Macros are really a feature that should be used to invent new programming abstractions in cases where it is ok to pay a little for the overhead for benefits in expressivity. 


### macro

> ***Special form***

The form of a `macro` expression is: `(macro args body)` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define defun (macro (name args body)
                    `(define ,name (lambda ,args ,body))))
```


</td>
<td>

```clj
(macro (name args body) (append '(define) (list name) (list (append '(lambda) (list args) (list body)))))
```


</td>
</tr>
<tr>
<td>

```clj
(defun inc (x)
  (+ x 1))
```


</td>
<td>

```clj
(closure (x) 
  (+ x 1)
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(inc 1)
```


</td>
<td>

```clj
2
```


</td>
</tr>
</table>




---
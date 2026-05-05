## Special forms

Special forms are like functions except that they choose what arguments are evaluated. This is in contrast to "normal functions", usually referred to as *"forms"* in other Lisps, which always evaluate every argument they are given. 

Note that some special forms are located in other sections to improve the document flow. These are: 

   - [`quote`](#quote)
   - [`and`](#and)
   - [`or`](#or)
   - [`match`](#match)
   - [`recv`](#recv)
   - [`recv-to`](#recv-to)
   - [`call-cc`](#call-cc)
   - [`call-cc-unsafe`](#call-cc-unsafe)
   - [`atomic`](#atomic)
   - [`macro`](#macro)
   - [`move-to-flash`](#move-to-flash)


---


### if

> ***Special form***

Conditionals are written as `(if cond-expr then-expr else-exp)`. If the `cond-expr` evaluates to [`nil`](#nil) the `else-expr` will be evaluated. For any other value of `cond-expr` the `then-expr` will be evaluated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(if t 1 2)
```


</td>
<td>

```clj
1
```


</td>
</tr>
<tr>
<td>

```clj
(if nil 1 2)
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


### cond

> ***Special form***

`cond` is a generalization of `if` to discern between n different cases based on boolean expressions. The form of a `cond` expression is: `(cond ( cond-expr1 expr1) (cond-expr2 expr2) ... (cond-exprN exprN))`. The conditions are checked from first to last and for the first `cond-exprN` that evaluates to true, the corresponding `exprN` is evaluated. 

If no `cond-exprN` evaluates to true, the result of the entire conditional is `nil`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define a 0)
(cond ((< a 0) 'abrakadabra)
      ((> a 0) 'llama)
      ((= a 0) 'hello-world))
```


</td>
<td>


```clj
hello-world
```


</td>
</tr>
<tr>
<td>


```clj
(define a 5)
(cond ((= a 1) 'doughnut)
      ((= a 7) 'apple-strudel)
      ((= a 10) 'baklava))
```


</td>
<td>


```clj
nil
```


</td>
</tr>
</table>




---


### lambda

> ***Special form***

You create an anonymous function with lambda. The function can be given a name by binding the lambda expression using <a href="#define">define</a> or <a href="#let">let</a>. A lambda expression has the form `(lambda param-list body-expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(lambda (x)
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
((lambda (x)
   (+ x 1)) 1)
```


</td>
<td>

```clj
2
```


</td>
</tr>
</table>

You can give more arguments to a function created using lambda. The extra arguments can be accessed in the lambda body by calling the `rest-args` function which gives back auxiliary arguments as a list. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
((lambda (x)
   (cons x (rest-args))) 1 2 3 4 5 6)
```


</td>
<td>

```clj
(1 2 3 4 5 6)
```


</td>
</tr>
<tr>
<td>

```clj
((lambda (x)
   (cons x (rest-args))) 1)
```


</td>
<td>

```clj
(1)
```


</td>
</tr>
</table>

`rest-args` takes an optional numerical argument that is used to index into the list containing the rest of the arguments. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
((lambda (x)
   (rest-args 0)) 1 2 3 4 5)
```


</td>
<td>

```clj
2
```


</td>
</tr>
<tr>
<td>

```clj
((lambda (x)
   (rest-args 1)) 1 2 3 4 5)
```


</td>
<td>

```clj
3
```


</td>
</tr>
<tr>
<td>

```clj
((lambda (x)
   (rest-args 2)) 1 2 3 4 5)
```


</td>
<td>

```clj
4
```


</td>
</tr>
<tr>
<td>

```clj
((lambda (x)
   (rest-args 3)) 1 2 3 4 5)
```


</td>
<td>

```clj
5
```


</td>
</tr>
</table>




---


### closure

> ***Special form***

A <a href="#lambda"> lambda </a> expression evaluates into a closure which is very similar to a <a href="#lambda">lambda</a> but extended with a captured environment for any names unbound in the param-list appearing in the body-expr.  The form of a closure is `(closure param-list body-exp environment)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(lambda (x)
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
(let ((a 1))
     (lambda (x)
       (+ a x)))
```


</td>
<td>

```clj
(closure (x) 
  (+ a x)
  ((a . 1)))
```


</td>
</tr>
<tr>
<td>

```clj
(let ((a 1)
      (b 2))
     (lambda (x)
       (+ a b x)))
```


</td>
<td>

```clj
(closure (x) 
  (+ a b x)
  ((b . 2) (a . 1)))
```


</td>
</tr>
</table>




---


### let

> ***Special form***

Local environments are created using let. The let binding in lispbm allows for mutually recursive bindings. The form of a let is `(let list-of-bindings body-expr)` and evaluating this expression means that body-expr is evaluted in an environment extended with the list-of-bindings. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(let ((a 1)
      (b 2))
     (+ a b))
```


</td>
<td>

```clj
3
```


</td>
</tr>
<tr>
<td>

```clj
(let ((f (lambda (x)
           (if (= x 0) 0 (g (- x 1)))))
      (g (lambda (x)
           (if (= x 0) 1 (f (- x 1))))))
     (f 11))
```


</td>
<td>

```clj
1
```


</td>
</tr>
</table>

You can deconstruct composite values while let binding. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(let (((a b) (list 1 2)))
     (+ a b))
```


</td>
<td>

```clj
3
```


</td>
</tr>
<tr>
<td>

```clj
(let (((a . as) (list 1 2 3 4 5 6)))
     (cons a (reverse as)))
```


</td>
<td>

```clj
(1 6 5 4 3 2)
```


</td>
</tr>
</table>




---


### loop

> ***Special form***

loop allows to repeatedly evaluate an expression for as long as a condition holds. The form of a loop is `(loop list-of-local-bindings condition-exp body-exp)`. 

The  `list-of-local-bindings` are very similar to how `let` works, just that here the `body-exp` is repeated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define sum 0)
(loop ((a 0))
      (<= a 10)
      (progn 
          (setq sum (+ sum a))
          (setq a (+ a 1))))
sum
```


</td>
<td>


```clj
55
```


</td>
</tr>
</table>




---


### define

> ***Special form***

You can give names to values in a global scope by using define. The form of define is `(define name expr)`. The given expression is evaluated and the result is stored in the global environment under `name`. In lispbm you can redefine already defined values. It is also possible to remove bindings from the global environment, see [`undefine`](#undefine). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define apa 10)
```


</td>
<td>

```clj
10
```


</td>
</tr>
</table>




---


### setq

> ***Special form***

The `setq` special-form is similar to `set` and to `setvar` but expects the first argument to be a symbol. The first argument to `setq` is NOT evaluated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define a 10)
(setq a 20)
a
```


</td>
<td>


```clj
20
```


</td>
</tr>
</table>

Just like `set` and `setvar`, `setq` can be used on variables that are bound locally such as in the body of a `let` or a `progn`-local variable created using `var`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(progn 
    (var a 10)
    (setq a 20)
    a)
```


</td>
<td>


```clj
20
```


</td>
</tr>
</table>




---


### progn

> ***Special form***

The progn special form allows you to sequence a number of expressions. The form of a progn expression is `(progn expr1 ... exprN)`. 

The evaluation result of a progn sequence is the value that the last `exprN` evaluated to. This is useful for sequencing of side-effecting operations. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(progn 
    1
    2
    3)
```


</td>
<td>

```clj
3
```


</td>
</tr>
<tr>
<td>

```clj
(progn 
    (define a 10)
    (define b 20)
    (+ a b))
```


</td>
<td>

```clj
30
```


</td>
</tr>
</table>




---


### {

> ***Special form***

The curlybrace `{` syntax is a short-form (syntactic sugar) for `(progn`. The reader replaces occurrences of `{` with `(progn`. The `{` should be closed with an `}`. 

These two programs are thus equivalent: 

```clj
 (progn
   (define a 10)
   (define b 20)
   (+ a b))
 ```
 

And 

```clj
 {
   (define a 10)
   (define b 20)
   (+ a b)
 }
 ```
 




---


### }

The closing curlybrace `}` should be used to close an opening `{` but purely for esthetic reasons. The `}` is treated identically to a regular closing parenthesis `)`. 

The opening `{` and closing `}` curlybraces are used as a short-form for `progn`-blocks of sequences expressions. 




---


### var

> ***Special form***

The var special form allows local bindings in a progn expression. A var expression is of the form (var symbol expr) and the symbol `symbol` is bound to the value that `expr` evaluates to withing the rest of the progn expression. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(progn 
    (var a 10)
    (var b 20)
    (+ a b))
```


</td>
<td>

```clj
30
```


</td>
</tr>
<tr>
<td>

```clj
(progn 
    (var a 10)
    (var b (+ a 10))
    (+ a b))
```


</td>
<td>

```clj
30
```


</td>
</tr>
</table>

You can deconstruct composite value while var binding. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(progn 
    (var (a b) (list 1 2))
    (+ a b))
```


</td>
<td>

```clj
3
```


</td>
</tr>
<tr>
<td>

```clj
(progn 
    (var (a . as) (list 1 2 3 4 5 6))
    (cons a (reverse as)))
```


</td>
<td>

```clj
(1 6 5 4 3 2)
```


</td>
</tr>
</table>




---


### trap

> ***Special form***

`trap` lets you catch an error rather than have the evaluation context terminate. The form of a trap expression is `(trap expr)`. If expr crashes with an error `e` then `(trap expr)` evaluates to `(exit-error e)`. If expr successfully runs and returns `r`, then `(trap expr)` evaluates to `(exit-ok r)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(trap (/ 1 0))
```


</td>
<td>

```clj
(exit-error division_by_zero)
```


</td>
</tr>
<tr>
<td>

```clj
(trap (+ 1 2))
```


</td>
<td>

```clj
(exit-ok 3)
```


</td>
</tr>
</table>

`trap` catches any error except for fatal errors. A fatal error will still lead to the context being terminated. 




---
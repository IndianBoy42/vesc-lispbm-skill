## Built-in operations


---


### identity

The identity function takes one argument which it directly returns. The form of an `identity` expression is `(identity expr)`, where expr is an arbitrary lisp expression. `(identity expr)` is a function application so all normal function application rules apply. The most important property of function applications in this case is that the argument is evaluated which differentiates `identity` from `quote` which returns the argument unevaluated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(identity 1)
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
(identity (+ 1 2))
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
(identity 'apa)
```


</td>
<td>

```clj
apa
```


</td>
</tr>
<tr>
<td>

```clj
(identity 'kurt-russel)
```


</td>
<td>

```clj
kurt-russel
```


</td>
</tr>
<tr>
<td>

```clj
(identity '(+ 1 2))
```


</td>
<td>

```clj
(+ 1 2)
```


</td>
</tr>
</table>




---


### rest-args

`rest-args` are related to user defined functions. As such `rest-args` is also given a brief explanation in the section about the  <a href="#lambda">lambda</a>. 

`rest-args` is a mechanism for handling optional arguments in functions. Say you want to define a function with 2 arguments and an optional 3rd argument. You can do this by creating a 3 argument function and check if argument 3 is valid or not in the body of the function 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(defun my-fun (x y opt)
  (if opt (+ x y opt) (+ x y)))
```


</td>
<td>

```clj
(closure (x y opt) 
  (if opt (+ x y opt) (+ x y))
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 1 2 nil)
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
(my-fun 1 2 100)
```


</td>
<td>

```clj
103
```


</td>
</tr>
</table>

This approach works well if your function has 1,2 or some other small number of optional arguments. However, functions with many optional arguments will look messy at the application site, `(my-fun 1 2 nil nil nil nil 32 nil kurt-russel)` for examples 

Functions you create, using lambda or defun, do actually take an arbitrary number of arguments. In other words, it is no error to pass in 5 arguments to a 2 argument defun or lambda function. The extra arguments will by default just be ignored. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(defun my-fun (x y)
  (+ x y))
```


</td>
<td>

```clj
(closure (x y) 
  (+ x y)
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 1 2)
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
(my-fun 1 2 100 200 300 400 500)
```


</td>
<td>

```clj
3
```


</td>
</tr>
</table>

all of those extra arguments, `100 200 300 400 500` passed into my-fun are ignored. But if we want to, we can access these extra arguments through the `rest-args` operation. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(defun my-fun (x y)
  (apply + (cons x (cons y (rest-args)))))
```


</td>
<td>

```clj
(closure (x y) 
  (apply + (cons x (cons y (rest-args))))
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 1 2 100)
```


</td>
<td>

```clj
103
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 1 2 100 1000 10000)
```


</td>
<td>

```clj
11103
```


</td>
</tr>
</table>

`rest-args` gives a clean looking interface to functions taking arbitrary optional arguments. Functions that make use of `rest-args` must, however, be written specifically to do so and are themself responsible for the figuring out the positional semantics of extra arguments. 

One was to explicitly carry the semantics of an optional argument into the function body is to add optional arguments as key-value pairs where the key states the meaning. Then `rest-args` becomes essentially an association list that you query using `assoc`. For example: 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(defun my-fun (x)
  (assoc (rest-args) x))
```


</td>
<td>

```clj
(closure (x) 
  (assoc (rest-args) x)
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 'kurt-russel '(apa . 10) '(bepa . 20) '(kurt-russel . is-great))
```


</td>
<td>

```clj
is-great
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 'apa '(apa . 10) '(bepa . 20) '(kurt-russel . is-great))
```


</td>
<td>

```clj
10
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 'bepa '(apa . 10) '(bepa . 20) '(kurt-russel . is-great))
```


</td>
<td>

```clj
20
```


</td>
</tr>
</table>

The `rest-args` operation also, itself, takes an optional numerical argument that acts as an index into the list of rest arguments. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(defun my-fun (i)
  (rest-args i))
```


</td>
<td>

```clj
(closure (i) 
  (rest-args i)
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(my-fun 0 1 2 3)
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
(my-fun 1 1 2 3)
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
(my-fun 2 1 2 3)
```


</td>
<td>

```clj
3
```


</td>
</tr>
</table>



---


### set

The `set` form is used to change the value of some variable in an environment. You can use `set` to change the value of a global definition or a local definition. An application of the `set` form looks like `(set var-expr val-expr)` where `var-expr` should evaluate to a symbol. The `val-expr` is evaluated before rebinding the variable. `set` returns the value that `val-expr` evaluates to. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define a 10)
(set 'a 20)
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

`set` works in local environments too such as in the body of a `let` or in a `progn`-local variable created using `var`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(progn 
    (var a 10)
    (set 'a 20)
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

See  [`setq`](#setq)  for a version which does't evaluate `var-expr`, similarly to  [`define`](#define). 




---


### setvar

`setvar` is an alias of  [`set`](#set). 




---


### undefine

A definition in the global environment can be removed using undefine.  The form of an undefine expression is `(undefine name-expr)` where `name-expr` should evaluate to a symbol (for example `'apa`). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(undefine 'apa)
```


</td>
<td>

```clj
t
```


</td>
</tr>
</table>

It is also possible to undefine several bindings at the same time by providing a list of names. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(undefine '(apa bepa cepa))
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


### eval

Evaluate data as an expression. The data must represent a valid expression. The form of an `eval` expression is `(eval expr)`. An optional environment can be passed in as the first argument: `(eval env-expr expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(eval (list + 1 2))
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
(eval '(+ 1 2))
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
(eval '((a . 100)) '(+ a 1))
```


</td>
<td>

```clj
101
```


</td>
</tr>
<tr>
<td>

```clj
(eval `(+ 1 ,@(range 2 5)))
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


### eval-program

Evaluate a list of data where each element represents an expression. The form of an `eval-program` expression is `(eval-program program-expr)`. A `program-expr` is a list of expressions where each element in the list can be evaluated by `eval`. 

Note that eval-program can not take any extra environment argument. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(eval-program (list (list + 1 2) (list + 3 4)))
```


</td>
<td>

```clj
7
```


</td>
</tr>
<tr>
<td>

```clj
(eval-program '((+ 1 2) (+ 3 4)))
```


</td>
<td>

```clj
7
```


</td>
</tr>
<tr>
<td>

```clj
(eval-program (list (list define 'a 10) (list + 'a 1)))
```


</td>
<td>

```clj
11
```


</td>
</tr>
<tr>
<td>

```clj
(eval-program '( (define a 10) (+ a 1)))
```


</td>
<td>

```clj
11
```


</td>
</tr>
</table>




---


### apply

An apply expression has the form `(apply fun-expr args-expr)`, and it  applies `args-expr` to `fun-expr`. It can loosely be emulated by  `(eval (cons fun-expr args-expr))`, except for the property that the elements of `args-expr` aren't evaluated when you use `apply`.  `args-expr` itself is of course evaluated, but given the emulated form, the individual elements of the list would be evaluated again. This is a problem when your argument list may include symbols or any other values which change when evaluated. 

Note that `fun-expr` doesn't necessarily have to be a user defined function, but can be any value which can be applied, that is, a value which can be the first item in a list expression: `(fun ...)`. This includes (but is not limited to) user define functions (which end up as [`closure`](#closure) values), built-in functions, extensions, [`macro`](#macro)s, and even special forms  (but see **Footgun: Special forms** below). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(defun my-fun (arg1 arg2)
  (str-join (list (to-str arg1) (to-str arg2)) " "))
```


</td>
<td>

```clj
(closure (arg1 arg2) 
  (str-join (list (to-str arg1) (to-str arg2)) " ")
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(apply my-fun '(a b))
```


</td>
<td>

```clj
"a b"
```


</td>
</tr>
<tr>
<td>

```clj
(apply + (list 1 2 3 4 5))
```


</td>
<td>

```clj
15
```


</td>
</tr>
<tr>
<td>

```clj
(apply list '(a b c))
```


</td>
<td>

```clj
(a b c)
```


</td>
</tr>
<tr>
<td>

```clj
(trap (eval (cons my-fun '(symbol-a symbol-b))))
```


</td>
<td>

```clj
(exit-error variable_not_bound)
```


</td>
</tr>
<tr>
<td>

```clj
(call-cc (lambda (return)
           (apply return '(return-through-apply))))
```


</td>
<td>

```clj
return-through-apply
```


</td>
</tr>
</table>

**Footgun: Special forms**  
[Special forms](#special-forms) are built in functions which control how their arguments are evaluated. This means that their implementations has custom logic for how to evaluate the arguments, which has the unfortunate consequence that to apply a list of arguments to them "without evaluating" said arguments would require specific logic for each special form's implementation. Given LispBM's nature of running in an embedded environment where binary size is a luxury this becomes highly impractical. Therefore the argument list is passed on unmodified to special forms. So `(apply def '(a 'symbol))` is *precisely* equivalent to `(eval (cons def '(a 'symbol)))`, `'symbol` will be evaluated!. 

This is most noticeable with `and` and `or`. They are special forms due to their short-circuiting behavior, where later arguments may not be evaluated depending on the previous arguments. Given that you only given them the symbol `t` or `nil` their special form status isn't a problem when it comes to `apply` since those symbols evaluate to themselves. The problem appears when you give `and` or `or` other "unstable" values like arbitrary symbols. Since they're special forms they will evaluate them another time. 

This behavior may be changed in the future, so please avoid writing programs which depend on this behavior. For the case of `and` and `or` you can define your own function which re-implement their behavior, which would be subject to `apply`'s non-evaluating property (see example below). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(apply or '(nil t))
```


</td>
<td>


```clj
t
```


</td>
</tr>
<tr>
<td>


```clj
(trap (apply and '(symbol-a symbol-b)))
```


</td>
<td>


```clj
(exit-error variable_not_bound)
```


</td>
</tr>
<tr>
<td>


```clj
(trap (apply or '(nil symbol-b)))
```


</td>
<td>


```clj
(exit-error variable_not_bound)
```


</td>
</tr>
<tr>
<td>


```clj
(defun safe-and nil
  (foldl (lambda (acc x)
           (and acc x)) t (rest-args)))
(apply safe-and '(symbol-a symbol-b))
```


</td>
<td>


```clj
symbol-b
```


</td>
</tr>
</table>




---


### read

Parses a string resulting in either an expression or the <a href="#read_error">read_error</a> in case the string can not be parsed into an expression. The form of a read expression is `(read string)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(read "1")
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
(read "(+ 1 2)")
```


</td>
<td>

```clj
(+ 1 2)
```


</td>
</tr>
<tr>
<td>

```clj
(read "(lambda (x) (+ x 1))")
```


</td>
<td>

```clj
(lambda (x)
  (+ x 1))
```


</td>
</tr>
</table>




---


### read-program

Parses a string containing multiple sequenced expressions. The resulting list of expressions can be evaluated as a program using <a href="#eval-program">eval-program</a>. The form of a read-program expression is `(read-program string)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(read-program "(define apa 1) (+ 2 apa)")
```


</td>
<td>

```clj
((define apa 1) (+ 2 apa))
```


</td>
</tr>
</table>




---


### read-eval-program

Parses and evaluates a program incrementally. `read-eval-program` reads a top-level expression then evaluates it before reading the next. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(read-eval-program "(define a 10) (+ a 10)")
```


</td>
<td>

```clj
20
```


</td>
</tr>
</table>

`read-eval-program` supports the  [`@const-start`](#const-start) and [`@const-end`](#const-end) annotations which move all global definitions created in the program to constant memory (flash). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(read-eval-program "@const-start (define a 10) (+ a 10) @const-end")
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


### type-of

The `type-of` function returns a symbol that indicates what type the argument is. The form of a `type-of` expression is `(type-of expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(type-of 1)
```


</td>
<td>

```clj
type-i
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 1u)
```


</td>
<td>

```clj
type-u
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 1i32)
```


</td>
<td>

```clj
type-i32
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 1u32)
```


</td>
<td>

```clj
type-u32
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 1i64)
```


</td>
<td>

```clj
type-i64
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 1u64)
```


</td>
<td>

```clj
type-u64
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 3.140000f32)
```


</td>
<td>

```clj
type-float
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 3.140000f64)
```


</td>
<td>

```clj
type-double
```


</td>
</tr>
<tr>
<td>

```clj
(type-of 'apa)
```


</td>
<td>

```clj
type-symbol
```


</td>
</tr>
<tr>
<td>

```clj
(type-of (list 1 2 3))
```


</td>
<td>

```clj
type-list
```


</td>
</tr>
</table>




---


### sym2str

The `sym2str` function converts a symbol to its string representation. The resulting string is a copy of the original so you cannot destroy built in symbols using this function. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(sym2str 'lambda)
```


</td>
<td>

```clj
"lambda"
```


</td>
</tr>
<tr>
<td>

```clj
(sym2str 'lambda)
```


</td>
<td>

```clj
"lambda"
```


</td>
</tr>
</table>




---


### str2sym

The `str2sym` function converts a string to a symbol. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(str2sym "hello")
```


</td>
<td>

```clj
hello
```


</td>
</tr>
</table>




---


### sym2u

The `sym2u` function returns the numerical value used by the runtime system for a symbol. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(sym2u 'lambda)
```


</td>
<td>

```clj
259u
```


</td>
</tr>
<tr>
<td>

```clj
(sym2u 'lambda)
```


</td>
<td>

```clj
259u
```


</td>
</tr>
</table>




---


### u2sym

The `u2sym` function returns the symbol associated with the numerical value provided. This symbol may be undefined in which case you get as result a unnamed symbol. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(u2sym 259u)
```


</td>
<td>

```clj
lambda
```


</td>
</tr>
<tr>
<td>

```clj
(u2sym 66334u)
```


</td>
<td>

```clj

```


</td>
</tr>
</table>




---


### gc

The `gc` function runs the garbage collector so that it can reclaim values from the heap and LBM memory that are no longer needed. 

**Note** that one should not need to run this function. GC is run automatically when needed. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(gc)
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
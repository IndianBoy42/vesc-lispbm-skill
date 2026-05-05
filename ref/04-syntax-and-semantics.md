## Syntax and semantics

Opinions on Lisp syntax varies widely depending on a persons programming experience and preferences. If you look around, or ask around you could find any of the following, and probably more views on lisp syntax: 

   - **Concise and expressive** Lisp syntax is quite minimalist, you can do a lot with very little syntax to learn about.
   - **Uniform and elegant** Data and code are represented in the same way. This property is called Homoiconicity.
   - **Too many parenthesis** A common complaint is that it can be easy to get lost in all the parantheses. While it may be easy to write lisp, it can be very hard to read someone elses code.

Lisp programs are written using S-expressions, a notation introduced by [McCarthy](http://www-formal.stanford.edu/jmc/recursive.pdf). An S-expression describes a tree in an unambiguous way. An example of an S-expression is `(+ 1 2)` and the tree it represents is shown below: 

![Graph representation of s-expression](./images/add_one_two.png)

Another example `(+ (* a a) (* b b))` which as a lisp program means $a^2 + b^2$: 

![Graph representation of s-expression](./images/sum_of_squares.png)

In Lisp, which stands for "LISt Processor", a list is a right leaning tree ending in the symbol "nil". By convention these right leaning expressions are easy to write and requires only a few parentheses. The example below shows how the list created by lisp program `(list 1 2 3 4)` is represented as a tree: 

![Graph representation of s-expression](./images/list_1234.png)

A left leaning structure requires full parenthesization and can be expressed in lisp as `(cons (cons (cons (cons nil 4) 3) 2) 1)`. 

![Graph representation of s-expression](./images/snoc_1234.png)

The conventions strongly favor the right leaning case. 

There are no two different trees that correspond to a given S-expression and thus parsing of S-expressions is unambiguous. The unambiguous nature of S-expressions is useful in areas other than lisp programming as well. [KiCad](https://dev-docs.kicad.org/en/file-formats/sexpr-intro/) uses S-expressions to represent tree data in some of its file formats. Apparently [WebAssembly](https://developer.mozilla.org/en-US/docs/WebAssembly/Understanding_the_text_format) uses S-expressions as well to describe WebAssembly modules 


S-expressions are built from two things, **Atoms** and **Pairs** of S-expressions. So an S-expression is either: 


   -  An **Atom** *a* 
   -  A **Pair** *a*,*b* of S-expressions `(a . b)` 

In LispBM the set of atoms consist of: 

   - [Numbers](#numbers-and-numerical-types): Such as `1`, `2`, `3.14`, `65b`, `2u32`
   - [Strings](#strings): Such as "hello world", "door" ...
   - Byte Arrays: Such as [1 2 3 4 5]
   - [Symbols](#about-symbols): Such as `a`, `lambda`, `define`, `kurt-russel` ...

In LispBM a pair of S-expressions is created by an application of `cons` as `(cons a b)` which creates the pair `(a . b)`. Convention is that `(e0 e1 ... eN)` = `(e0 . ( e1 . ... ( eN . nil)))`. 

A structure such as `(e0 e1 ... eN)` is called a list. 

### The meaning (semantics) that LispBM imposes on S-Expressions

The S-expressions discussed in the previous section are merely tree structures. The Lisp evaluator provides a computational interpretation for these trees. However, not all trees are valid Lisp programs. This section focuses on those trees that do make sense as Lisp programs and their meaning to the Lisp evaluator. 

**Values and expressions** 

The LispBM evaluator transforms expressions into values. For instance, the expression  `(+ 1 2)` is evaluated to the value `3`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(+ 1 2)
```


</td>
<td>

```clj
3
```


</td>
</tr>
</table>

In LispBM the distinction between expressions and values is often blurred. For example, it is possible to write a function that returns a result that can itself be interpreted as code 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(defun mk-code (x) `(+ ,x 1))
```


</td>
<td>

```clj
(closure (x) 
  (append '(+) (list x) '(1))
  nil)
```


</td>
</tr>
<tr>
<td>

```clj
(mk-code 10)
```


</td>
<td>

```clj
(+ 10 1)
```


</td>
</tr>
</table>

The result of evaluating `(mk-code 10)` is the list containing a `+`, `10` and `1`. This list is the value that `(mk-code 10)` evaluates to. Now, the result of `(mk-code 10)`, since it is valid lisp, can be evaluated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(eval (mk-code 10))
```


</td>
<td>

```clj
11
```


</td>
</tr>
</table>

In most cases this is quite natural and our functions will result in, Strings, lists and numbers that are easily and naturally understood as values. 

Still, it is worthwhile to remember that values can be expressions and expressions can be values. 

**Errors** 

Some times evaluation is impossible. This could be because the program is malformed, a type mismatch or a division by zero (among many other possibilities). Errors terminate the evaluation of the expression. To recover from an error the programmer needs to explicitly `trap` it. 

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
</table>

**Environments** 

LispBM expressions are evaluated in relation to a global and a local environment. An environment is a key-value store where the key is a lisp symbol and the value is any lisp value. 

The rest of this section will now explain the meaning of LBM programs by informally showing **expressions**, what **values** they evaluate into and how they change and depend on the environments 

**Atoms** 

Some atoms, such as Numbers, Strings and byte arrays cannot be further evaluated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
10
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
"hello world"
```


</td>
<td>

```clj
"hello world"
```


</td>
</tr>
<tr>
<td>

```clj
[1 2 3 4]
```


</td>
<td>

```clj
[1 2 3 4]
```


</td>
</tr>
</table>

Symbols evaluate by a lookup in the environment. First, the local environment is searched for a binding of the symbol. If unable to find a binding in the local environment, the global environment is searched. If unable to find a binding in the global environment as well, the runtime system attempts to dynamically load a binding using a system provided callback function. If all of the above fails to provide a value a `variable_not_bound` error is produced. 

**Composite forms** 

A composite form, such as `(e1 ... eN)` is evaluated in different ways depending on what `e1` is. There are three major categories that `e1` can fall into. Either `e1` is something that represents a function and `(e1 ... eN)` is a function application. Or `e1` is a so-called *special-form* that form the core of the LBM language. Or lastly, `e1` is anything else and the composite form is malformed and will ultimately result in an error. 

The composite form `(e1 ... eN)` is evaluated by first checking if `e1` is a special form or not. if `e1` is a special form the composite form is passed to a special-form evaluator. if `e1` is not a special form,  the composite form is evaluated as a function application. These two major branches of composite form evaluation are described below. 

**Special form evaluation** 

Below are a selection of basic special-forms in lispBM together with their evaluation process 

   - **quote**: `(quote a)` evaluates to a for any a
   - **define**: `(define s e)`, `e` is evaluated into `v` and the global environment is augmented with the pair `(s . v)`
   - **lambda**: `(lambda params body)` is evaluated into '(closure params body env)`. `env` is the local environment there the lambda expression is evaluated.
   - **if**: `(if e1 e2 e3)` is evaluated by evaluating `e1` into `v1` if `v1` is nil, `e3` is evaluated otherwise `e2` is evaluated.
   - **progn**: `(progn e1 e2 ... eN)` is evaluated by evaluating `e1` then `e2` and so on until `eN`. The value `v` that `eN` evaluats into is the value `(progn e1 e2 ... eN)` evaluates to.
   - **and**: `(and e1 e2 ... eN)` evaluates the `eI` expressions from left to right as long as they result in a non-nil value.
   - **or**: `(or e1 e2 ... eN)` evaluates the `eI` expressions from left to right until there is a non-nil result.

`and`, `or`, `progn` and `if` evaluates expressions in sequence. `if` evaluates first the condition expression and then either the true or false branch. `progn` evaluates all of the expressions in sequence. In the case of `and`, `or`, `progn` and `if`, the constituent expressions are all evaluated in the same local environment. Any extensions to the local environment performed by an expression in the sequence is only visible within that expression itself. 

   - **let**: `(let ((s1 e1) (s2 e2) ... (sN eN) e)` eI are evaluated in order into `vI`. The local environment is extended with `(sI . vI)`. `sI` is visible in `eJ` for `J >= I`. `e` is then evaluated in the extended local environment.
   - **setq**: `(setq s e)` is evaluated by first evaluating `e` into `v`. The environments are then scanned for a binding of `s`. local environment is searched first followed by global. If a binding of `s` is found it is modified into `(s . v)`.

If no binding of `s` is found when evaluating `(setq s e)` a `variable_not_bound` error is triggered. 

**Function application evaluation** 

The evaluation strategies explained here are applied to composite expressions of the `(e1 ... eN)` form where `e1` does not fall into the category of "special forms". 

In LispBM an `(e1 ... eN)` is evaluated by first evaluating `e1`. This is because depending on what kind of function object `e1` evaluates into, the application if evaluated in different ways. 

`e1` should evaluate into a `closure`, a "fundamental operation" or an "extension". fundamental operations and extensions take their arguments passed on the stack while a closure is applied in an environment extended with the argument value bindings. 

Depending on the value of `e1` the arguments are either evaluated left to right and the results are pushed onto the stack, or they are evaluated left to right and used to extend the environment. 

**The quote and the quasiquote** 

The LBM parser (Reader) expands usages of the character sequences: `'`, `` ` ``, `,` and `,@`. The `'` as in `'a` is expanded into `(quote a)` for any a. The remaining `` ` ``, `,` and `,@` are expanded into applications of `quote`, `append` and `cons` using the algorithms described by Bawden in [quasiquotation in lisp](https://brics.dk/NS/99/1/BRICS-NS-99-1.pdf#page=6). 

### Concurrency and Semantics

TODO: Finish section.
## Quotes and Quasiquotation

Code and data share the same representation, it is only a matter of how you look at it. The tools for changing view, or interpretation, are the quotation and quasiquotation operations. 


---


### quote

> ***Special form***

When the `'` quote operator is encountered by the reader it is removed and the code to the right is wrapped in `(quote ...)`. Evaluating a quoted expression `(quote a)` results in `a` unevaluated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
'(+ 1 2)
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
'kurt
```


</td>
<td>

```clj
kurt
```


</td>
</tr>
</table>




---


### `

The backwards tick operator `` ` `` is called the quasiquote. It is similar to `'` but allows splicing in results of computations using the [`,`](#comma) and the [`,@`](#commaat) operators. 

The result of `'(+ 1 2)` and `` `(+ 1 2)`` are similar in effect. Both result in the result value of `(+ 1 2)`, that is a list containing +, 1 and 2.  When `` `(+ 1 2)`` is read into the heap it is expanded into the expression `(append (quote (+)) (append (quote (1)) (append (quote (2)) (quote nil))))` which evaluates to the list `(+ 1 2)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
`(+ 1 2)
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
`(+ 1 ,(+ 1 1))
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
(append '(+ 1) (list (+ 1 1)))
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


### , <a name="comma"></a>

The comma is used to splice the result of a computation into a quasiquotation. 

The expression `` `(+ 1 ,(+ 1 1))`` is expanded by the reader into `(append (quote (+)) (append (quote (1)) (append (list (+ 1 1)) (quote nil))))`. Evaluating the expression above results in the list `(+ 1 2)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
`(+ 1 ,(+ 1 1))
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


### ,@ <a name="commaat"></a>

The comma-at operation is used to splice in the result of a computation (that returns a list) into a list when quasiquoting. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
`(1 2 3 ,@(range 4 10))
```


</td>
<td>

```clj
(1 2 3 4 5 6 7 8 9)
```


</td>
</tr>
</table>




---
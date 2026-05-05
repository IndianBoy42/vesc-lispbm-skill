## Pattern-matching


---


### match

> ***Special form***

Pattern-matching is expressed using match. The form of a match expression is `(match expr (pat1 expr1) ... (patN exprN))`. Pattern-matching compares the shape of an expression to each of the `pat1` ... `patN` and evaluates the expression `exprM` of the pattern that matches. In a pattern you can use a number of match-binders or wildcards: `_`, `?`, `?i`,`?u`,`?float`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(match 'orange
       (green 1)
       (orange 2)
       (blue 3))
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


### no_match

The `no_match` symbol is returned from pattern matching if no case matches the expression. 

   - Add a catch-all case to your pattern-matching. `_`.




---


### _

The underscore pattern matches anything. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(match 'fish
       (horse 'its-a-horse)
       (pig 'its-a-pig)
       (_ 'i-dont-know))
```


</td>
<td>

```clj
i-dont-know
```


</td>
</tr>
</table>




---


### ?

The `?` pattern matches anything and binds that anything to variable. Using the `?` pattern is done as `(? var)` and the part of the expression that matches is bound to `var`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(match '(orange 17)
       ((green (? n)) (+ n 1))
       ((orange (? n)) (+ n 2))
       ((blue (? n)) (+ n 3)))
```


</td>
<td>

```clj
19
```


</td>
</tr>
</table>




---


### Match with guards

Patterns used in a match expressions can be augmented with a boolean guard to further discern between cases. A pattern with a guard is of the form `(pattern-expr guard-expr expr)`. A pattern with a guard, matches only if the pattern structurally matches and if the guard-expr evaluates to true in the match environment. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define x 1)
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
(match x
       ((? y) (< y 0) 'less-than-zero)
       ((? y) (> y 0) 'greater-than-zero)
       ((? y) (= y 0) 'equal-to-zero))
```


</td>
<td>

```clj
greater-than-zero
```


</td>
</tr>
</table>




---
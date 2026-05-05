## Comparisons


---


### eq

Compare values for equality. The `eq` operation implements structural equality. The form of an 'eq` expression is `(eq expr1 ... exprN)`. 
 Structural equality means that the values must have the identical in memory representations to be considered equal. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(eq (+ 1 2) 3)
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
(eq 1 1 1 1)
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
(eq 1 1 2 1)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(eq (+ 3 4) (+ 2 5) (+ 1 6))
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
(eq (list 1 2 3 4) (list 1 2 3 4))
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
(eq (list 1 2 4 5) (list 1 2 3 4))
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


### not-eq

`not-eq` implements the negation of eq. In other words, `(not-eq a b c)` evaluates to the same result as `(not (eq a b c))`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(not-eq (+ 1 2) 3)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(not-eq 1 1 1 1)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(not-eq 1 1 2 1)
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
(not-eq (+ 3 4) (+ 2 5) (+ 1 6))
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(not-eq (list 1 2 3 4) (list 1 2 3 4))
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(not-eq (list 1 2 4 5) (list 1 2 3 4))
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


### =

The `=` operation can only be used on numerical arguments. If you know you are comparing numbers, it will be more efficient to use `=`. 
 An important difference between `eq` and `=` is that `=` compare the numerical values of the arguments. A 3 is a 3 independent of them being different types. `eq` on the other hand compares the representations of the arguments exactly and they must match in structure, type and value to be considered equal. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(= 1 1)
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
(= 1 2)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(= (+ 2 3) (+ 1 4))
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
(= (+ 1 2) (+ 2 3))
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


### >

Greater than comparison. A greater than comparison has the form `(> expr1 ... exprN)` and evaluates to `t` if expr1 is greater than all of expr2 ... exprN. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(> 5 2)
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
(> 2 5)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(> 3.140000f32 1)
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
(> 1 3.140000f32)
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


### <

Less than comparison. A less than comparison has the form `(> expr1 ... exprN)` and evaluates to `t` if expr1 is less than all of expr2 ... exprN. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(< 5 2)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(< 5 2)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(< 3.14 1)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(< 1 3.14)
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


### >=

Greater than or equal comparison. A greater than comparison has the form `(>= expr1 ... exprN)` and evaluates to `t` if expr1 is greater than or equal to all of expr2 ... exprN. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(>= 1 1)
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
(>= 5 2)
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
(>= 2 5)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(>= 3.14 1)
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
(>= 1 3.14)
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


### <=

Less than or equal comparison. A less than or equal comparison has the form `(<= expr1 ... exprN)` and evaluates to `t` if expr1 is less than or equal to all of expr2 ... exprN. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(<= 1 1)
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
(<= 5 2)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(<= 2 5)
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
(<= 3.14 1)
```


</td>
<td>

```clj
nil
```


</td>
</tr>
<tr>
<td>

```clj
(<= 1 3.14)
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
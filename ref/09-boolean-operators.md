## Boolean operators


---


### and

> ***Special form***

Boolean `and` operation between n arguments. The form of an `and` expression is `(and expr1 ... exprN)`.  This operation treats all non-nil values as true. Boolean `and` is "short-circuiting" and only evaluates until a false is encountered. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(and t t)
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
(and t t (+ 1 2))
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
(and t (< 5 3))
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


### or

> ***Special form***

Boolean `or` operation between n arguments. The form of an `or` expression is `(or expr1 ... exprN)`.  This operation treats all non-nil values as true. Boolean `or` is "short-circuiting" and only evaluates until a true is encountered. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(or nil nil)
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
(or nil t)
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
(or t nil)
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
(or t t)
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
(or nil (+ 1 2))
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


### not

Boolean `not` takes one argument. The form of a `not` expression is `(not expr)`. All non-nil values are considered true. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(not t)
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
(not nil)
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
(not 42)
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
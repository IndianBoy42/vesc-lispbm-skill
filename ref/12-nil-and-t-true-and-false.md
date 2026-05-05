## nil and t, true and false


---


### nil

Represents the empty list. The nil value is also considered to be false by conditionals. `nil` is a symbol but it cannot be redefined and will always evaluate to itself. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cons 1 nil)
```


</td>
<td>

```clj
(1)
```


</td>
</tr>
<tr>
<td>

```clj
(if nil 3 100)
```


</td>
<td>

```clj
100
```


</td>
</tr>
<tr>
<td>

```clj
nil
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


### t

All non nil values are considered true in conditionals. `t` should be used in cases where an explicit true makes sense. `t` is a symbol but it cannot be redefined and will always evaluate to itself. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cons 1 t)
```


</td>
<td>

```clj
(1 . t)
```


</td>
</tr>
<tr>
<td>

```clj
(if t 3 100)
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
t
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


### false

`false` is an alias for `nil`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cons 1 false)
```


</td>
<td>

```clj
(1)
```


</td>
</tr>
<tr>
<td>

```clj
(if false 3 100)
```


</td>
<td>

```clj
100
```


</td>
</tr>
<tr>
<td>

```clj
false
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


### true

`true` is an alias for `t`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cons 1 true)
```


</td>
<td>

```clj
(1 . t)
```


</td>
</tr>
<tr>
<td>

```clj
(if true 3 100)
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
true
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
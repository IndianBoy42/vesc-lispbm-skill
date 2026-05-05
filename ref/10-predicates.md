## Predicates


---


### list?

the `list?` predicate is true for all lists, empty (nil) or not. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(list? nil)
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
(list? 'nil)
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
(list? (list 1 2 3))
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
(list? '(1 2 3))
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
(list? 2)
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
(list? 'kurt-russel)
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


### number?

the `number?` predicate is true for all numbers. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(number? nil)
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
(number? 1)
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
(number? 2u)
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
(number? 3.140000f32)
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
(number? 'michael-shanks)
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
(number? 'james-spader)
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
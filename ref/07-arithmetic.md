## Arithmetic


---


### +

Adds up an arbitrary number of values. The form of a `+` expression is `(+ expr1 ... exprN)`. 

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
<tr>
<td>

```clj
(+ 1 2 3 4)
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
(+ 1 1u)
```


</td>
<td>

```clj
2u
```


</td>
</tr>
<tr>
<td>

```clj
(+ 2i 3.14)
```


</td>
<td>

```clj
5.140000f32
```


</td>
</tr>
</table>




---


### -

Subtract an arbitrary number of values from a value. The form of a `-` expression is `(- expr1 ... exprN)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(- 5 3)
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
(- 10 5 5)
```


</td>
<td>

```clj
0
```


</td>
</tr>
<tr>
<td>

```clj
(- 10 2u)
```


</td>
<td>

```clj
8u
```


</td>
</tr>
<tr>
<td>

```clj
(- 10 3.14)
```


</td>
<td>

```clj
6.860000f32
```


</td>
</tr>
</table>




---


### *

Multiplying an arbitrary number of values. The form of a `*` expression is `(* expr1 ... exprN)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(* 2 2)
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
(* 2 3 4 5)
```


</td>
<td>

```clj
120
```


</td>
</tr>
<tr>
<td>

```clj
(* 10 2u)
```


</td>
<td>

```clj
20u
```


</td>
</tr>
<tr>
<td>

```clj
(* 4 3.14)
```


</td>
<td>

```clj
12.560000f32
```


</td>
</tr>
</table>




---


### /

Division. The form of a `/` expression is `(/ expr1 ... exprN)`. The resulting type is the same as the inputs (after their types have been promoted of course). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(/ 128 2)
```


</td>
<td>

```clj
64
```


</td>
</tr>
<tr>
<td>

```clj
(/ 6.28 2)
```


</td>
<td>

```clj
3.140000f32
```


</td>
</tr>
<tr>
<td>

```clj
(/ 256 2 2 2 2 2 2 2)
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
(/ 5 2)
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


### mod

Modulo operation. The form of a `mod` expression is `(mod expr1 exp2)`. The modulo operation is not generalised to n arguments. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(mod 5 3)
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
(mod 1024 100)
```


</td>
<td>

```clj
24
```


</td>
</tr>
<tr>
<td>

```clj
(mod -7 5)
```


</td>
<td>

```clj
-2
```


</td>
</tr>
</table>




---


### //

Integer division operation. Like normal division except if the result is a floating point value it is cast to an integer, which floors the result. The form of a `//` expression is `(// expr1 ... exprN)`. Can be used as a elegant complement to `mod`, with `//` returning the quotient and `mod` returning the remainder of a division. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(// 5.000000f32 2)
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
(progn 
    (var total-seconds 62.500000f32)
    (var minutes (// total-seconds 60))
    (var seconds (mod total-seconds 60))
    (str-join (list (str-from-n minutes) "m " (str-from-n seconds) "s") [0]))
```


</td>
<td>

```clj
"1m 2.5s"
```


</td>
</tr>
</table>



---
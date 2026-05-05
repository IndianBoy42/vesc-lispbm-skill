## Bit level operations


---


### shl

The shift left operation takes two arguments. The first argument is a value to shift and the second argument is the number of bit positions to shift the value. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(shl 1 2)
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
(shl 1u32 2)
```


</td>
<td>

```clj
4u32
```


</td>
</tr>
<tr>
<td>

```clj
(shl 1u64 2)
```


</td>
<td>

```clj
4u64
```


</td>
</tr>
</table>




---


### shr

The shift right operation takes two arguments. The first argument is a value to shift and the second argument in the number of bit positions to shift the value. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(shr 4 2)
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
(shr 4u32 2)
```


</td>
<td>

```clj
1u32
```


</td>
</tr>
<tr>
<td>

```clj
(shr 4u64 2)
```


</td>
<td>

```clj
1u64
```


</td>
</tr>
</table>




---


### bitwise-and

Performs the bitwise and operation between two values. The type of the result is the same type as the first of the arguments. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(bitwise-and 1048831u32 65535)
```


</td>
<td>

```clj
255u32
```


</td>
</tr>
</table>




---


### bitwise-or

Performs the bitwise or operation between two values. The type of the result is the same type as the first of the arguments. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(bitwise-or 1048816 15)
```


</td>
<td>

```clj
1048831
```


</td>
</tr>
</table>




---


### bitwise-xor

Performs the bitwise exclusive or operation between two values. The type of the result is the same type as the first of the arguments. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(bitwise-xor 1048816 255)
```


</td>
<td>

```clj
1048591
```


</td>
</tr>
</table>




---


### bitwise-not

Performs the bitwise negation operations on a value. The result is of same type as the argument. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(bitwise-not 4096u32)
```


</td>
<td>

```clj
4294963199u32
```


</td>
</tr>
</table>




---
## Flat values

Lisp values can be "flattened" into an array representation. The flat representation of a value contains all information needed so that the value can be recreated, "unflattened", in another instance of the runtime system (for example running on another microcontroller). 

Not all values can be flattened, custom types for example cannot. 

Flat values are designed for recursive encoding and decoding each sub-value contains all information about its size either implicitly or explicitly (as is the case with arrays). 

multibyte values are stored in network byte order (big endian). 

**Cons** A cons cell is encoded into a byte 0x1 followed by the encoding of the car and then the cdr field of that cons cell. 


|cons |car value|cdr value|
|:----:|:----:|:----:|
|0x1|M bytes|N bytes|

**Symbol as value** A symbol value can be flattened. Note that symbol values only make sense locally. A flattened symbol value will only make sense in the same runtime system instance that flattened it. 


|symbol-value|value|
|:----:|:----:|
|0x2|4 bytes on 32bit, 8 bytes on 64bit|

**Symbol as string** A symbol can be flattened as a string and thus make sense across runtime system instances. 


|symbol-string|string|
|:----:|:----:|
|0x3|zero terminated C style string|

**Byte Arrays** Byte arrays can be flattened and the length is stored explicitly. 


|byte array|size in bytes|data|
|:----:|:----:|:----:|
|0xD|4 bytes|size bytes|

The rest of the atomic types are flattened according to the following: 


|type|flat-id|value|
|:----:|:----:|:----:|
|byte|0x4|1 Byte|
|i28|0x5|4 Bytes|
|u28|0x6|4 Bytes|
|i32|0x7|4 Bytes|
|u32|0x8|4 Bytes|
|float|0x9|4 Bytes|
|i64|0xA|8 Bytes|
|u64|0xB|8 Bytes|
|double|0xC|8 Bytes|
|i56|0xE|8 Bytes|
|u56|0xF| 8 Bytes|

Note that some of the types are only present of 32Bit runtime systems and some only on 64 bit. i28 is present on 32 bit and i56 on 64 bit. likewise for u28 and u56. 

When LispBM unflattens a i56 or u56 on a 32bit system it creates a i64 or u64 in its place. 

Symbols as values, are not possible to transfer between runtime systems in general and is even more pointless between a 32 and 64 bit runtime system. 


### flatten

The `flatten` function takes a value as single argument and returns the flat representation if successful. A flatten expression has the form `(flatten expr)`. Note that `expr` is evaluated before the flattening. A flat value can be turned back into a normal lisp value applying `unflatten` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define a (flatten (+ 1 2 3)))
```


</td>
<td>

```clj
[5 0 0 0 6]
```


</td>
</tr>
<tr>
<td>

```clj
(unflatten a)
```


</td>
<td>

```clj
6
```


</td>
</tr>
<tr>
<td>

```clj
(define a (flatten '(+ 1 2 3)))
```


</td>
<td>

```clj
[1 3 43 0 1 5 0 0 0 1 1 5 0 0 0 2 1 5 0 0 0 3 3 110 105 108 0]
```


</td>
</tr>
<tr>
<td>

```clj
(unflatten a)
```


</td>
<td>

```clj
(+ 1 2 3)
```


</td>
</tr>
</table>

A flat value is a byte-array containing an encoding of the value. 




---


### unflatten

`unflatten` converts a flat value back into a lisp value. Te form of an `unflatten` expression is `(unflatten flat-value)` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define a (flatten (+ 1 2 3)))
```


</td>
<td>

```clj
[5 0 0 0 6]
```


</td>
</tr>
<tr>
<td>

```clj
(unflatten a)
```


</td>
<td>

```clj
6
```


</td>
</tr>
<tr>
<td>

```clj
(define a (flatten '(+ 1 2 3)))
```


</td>
<td>

```clj
[1 3 43 0 1 5 0 0 0 1 1 5 0 0 0 2 1 5 0 0 0 3 3 110 105 108 0]
```


</td>
</tr>
<tr>
<td>

```clj
(unflatten a)
```


</td>
<td>

```clj
(+ 1 2 3)
```


</td>
</tr>
</table>




---
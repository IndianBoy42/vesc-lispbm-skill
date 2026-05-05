## Byte buffers


---


### bufcreate

Create an array of bytes. The form of a `bufcreate` expression is `(bufcreate size-expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define data (bufcreate 10))
```


</td>
<td>

```clj
[0 0 0 0 0 0 0 0 0 0]
```


</td>
</tr>
<tr>
<td>

```clj
(define empty-array (bufcreate 0))
```


</td>
<td>

```clj
[]
```


</td>
</tr>
</table>

Alternatively a buffer can be allocated from a compactable memory region (defrag mem). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define dm (dm-create 1000))
```


</td>
<td>

```clj
DM
```


</td>
</tr>
<tr>
<td>

```clj
(define data-in-dm (bufcreate dm 10))
```


</td>
<td>

```clj
[0 0 0 0 0 0 0 0 0 0]
```


</td>
</tr>
</table>

For more information about defragmentable memory see <a href=#Defragmentable_memory>Defragmentable memory</a>. 




---


### buflen

Returns the size of a buffer in number of bytes. The form of an `buflen` expression is `(buflen buf-expr)` where buf-expr has to evaluate into a buffer. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(buflen data)
```


</td>
<td>

```clj
10
```


</td>
</tr>
</table>




---


### bufget-[X]

Read a value from a buffer. The contents of a buffer can be read as a sized integer or unsigned value using as many bytes from the buffer as the X portion of the function name implies. The form of a bufget expression is `(bufget-[X] buf-expr ix-expr)` where `ix-expr` evaluates to a number indicating the byte position to start reading from. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define data [255 255 255 255 255 255 255 255])
```


</td>
<td>

```clj
[255 255 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufget-i8 data 0)
```


</td>
<td>

```clj
-1
```


</td>
</tr>
<tr>
<td>

```clj
(bufget-i16 data 0)
```


</td>
<td>

```clj
-1
```


</td>
</tr>
<tr>
<td>

```clj
(bufget-i32 data 0)
```


</td>
<td>

```clj
-1
```


</td>
</tr>
<tr>
<td>

```clj
(bufget-u8 data 0)
```


</td>
<td>

```clj
255
```


</td>
</tr>
<tr>
<td>

```clj
(bufget-u16 data 0)
```


</td>
<td>

```clj
65535
```


</td>
</tr>
<tr>
<td>

```clj
(bufget-u32 data 0)
```


</td>
<td>

```clj
4294967295u32
```


</td>
</tr>
</table>




---


### bufset-[X]

The `bufset` functions performs a destructive updates to a buffer. The form of a `bufset` expression is `(bufset-[X] buf-expr ix-expr val-expr)` where `ix-expr` evaluates to a number indicating where in the buffer to start writing and `val-expr` is the value to write. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define data [255 255 255 255 255 255 255 255])
```


</td>
<td>

```clj
[255 255 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufset-i8 data 0 10)
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
data
```


</td>
<td>

```clj
[10 255 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufset-i16 data 0 20)
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
data
```


</td>
<td>

```clj
[0 20 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufset-i32 data 0 -1)
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
data
```


</td>
<td>

```clj
[255 255 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufset-u8 data 0 10)
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
data
```


</td>
<td>

```clj
[10 255 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufset-u16 data 0 20)
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
data
```


</td>
<td>

```clj
[0 20 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufset-u32 data 0 4294967295u32)
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
data
```


</td>
<td>

```clj
[255 255 255 255 255 255 255 255]
```


</td>
</tr>
</table>




---


### bufclear

To clear a byte array the function bufclear can be used `(bufclear arr optByte optStart optLen)` Where arr is the byte array to clear, optByte is the optional argument of what to clear with (default 0), optStart is the optional argument of which position to start clearing (default 0) and optLen is the optional argument of how many bytes to clear after start (default the entire array). Example: 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define data [255 255 255 255 255 255 255 255])
```


</td>
<td>

```clj
[255 255 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufclear data)
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
data
```


</td>
<td>

```clj
[0 0 0 0 0 0 0 0]
```


</td>
</tr>
<tr>
<td>

```clj
(bufclear data 255)
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
data
```


</td>
<td>

```clj
[255 255 255 255 255 255 255 255]
```


</td>
</tr>
<tr>
<td>

```clj
(bufclear data 1 5)
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
data
```


</td>
<td>

```clj
[255 255 255 255 255 1 1 1]
```


</td>
</tr>
<tr>
<td>

```clj
(bufclear data 1 5 8)
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
data
```


</td>
<td>

```clj
[255 255 255 255 255 1 1 1]
```


</td>
</tr>
<tr>
<td>

```clj
(bufclear data 170 1 5)
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
data
```


</td>
<td>

```clj
[255 170 170 170 170 170 1 1]
```


</td>
</tr>
</table>




---


### Byte buffer literal syntax

Byte buffer literals can be created using the `[` and `]` syntax to enclose values to initialize the array with. The `[` and `]` syntax is complete resolved in the reader and thus cannot contain arbitrary lisp terms. the values listed between the `[` and the `]` must be literals! 

The form of the `[` and `]` syntax is `[ val1 ... valN ]`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
[1 2 3 4 5 6 7 8 9 10]
```


</td>
<td>

```clj
[1 2 3 4 5 6 7 8 9 10]
```


</td>
</tr>
</table>




---
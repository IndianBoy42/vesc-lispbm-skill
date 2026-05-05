## Arrays

LispBM supports arrays of arbitrary lisp values (including other arrays). 


### array literals

An array literal are specified as a sequence of lisp values between `[|` and `|]`. Values in a literal array are not evaluated. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define my-arr [|1 2 3|])
```


</td>
<td>

```clj
[|1 2 3|]
```


</td>
</tr>
<tr>
<td>

```clj
(define my-arr [|daniel jackson|])
```


</td>
<td>

```clj
[|daniel jackson|]
```


</td>
</tr>
<tr>
<td>

```clj
(define my-arr [|(apa . bepa) (1 . 2)|])
```


</td>
<td>

```clj
[|(apa . bepa) (1 . 2)|]
```


</td>
</tr>
<tr>
<td>

```clj
(define my-arr [|(+ 1 2) (+ 3 4)|])
```


</td>
<td>

```clj
[|(+ 1 2) (+ 3 4)|]
```


</td>
</tr>
<tr>
<td>

```clj
(define my-arr [|[|1 2 3|] [|4 5 6|]|])
```


</td>
<td>

```clj
[|[|1 2 3|] [|4 5 6|]|]
```


</td>
</tr>
<tr>
<td>

```clj
(ix my-arr 0)
```


</td>
<td>

```clj
[|1 2 3|]
```


</td>
</tr>
<tr>
<td>

```clj
(ix my-arr 1)
```


</td>
<td>

```clj
[|4 5 6|]
```


</td>
</tr>
<tr>
<td>

```clj
(ix (ix my-arr 0) 1)
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
(ix (ix my-arr 1) 2)
```


</td>
<td>

```clj
6
```


</td>
</tr>
</table>

All arrays have an associated heap-cell that acts as a liaison in relation to the garbage collector. When garbage collection frees the liaison, it also frees the array data in buffers and arrays memory (lbm_memory). 

![In memory representation of an array](./images/array_literal.png)




---


### array

`array` takes n arguments and creates an array holding those arguments as values. The form of an `array` expression is `(array expr1 ... exprN)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define my-arr (array 1 2 3))
```


</td>
<td>

```clj
[|1 2 3|]
```


</td>
</tr>
<tr>
<td>

```clj
(define my-arr (array (+ 1 2) (+ 3 4)))
```


</td>
<td>

```clj
[|3 7|]
```


</td>
</tr>
</table>




---


### mkarray

Allocate an array with `mkarray`. Arrays are allocated in arrays and byte buffer memory. The form an `mkarray` expression is `(mkarray num-expr)`. 

Note that there is currently no literal syntax for arrays. 

The example below allocates an array in "lbm_memory" (arrays and byte-buffer memory). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define my-arr (mkarray 10))
```


</td>
<td>

```clj
[|nil nil nil nil nil nil nil nil nil nil|]
```


</td>
</tr>
</table>




---


### ix

Index into an array using the `ix` function. The form of an `ix` expression is `(ix array-expr index-expr)`. Indexing starts from 0 and if you index out of bounds the result is nil. A negative index accesses values starting from the end of the array. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(ix [|1 2 3 4|] 1)
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
(ix [|1 2 3 4|] -1)
```


</td>
<td>

```clj
4
```


</td>
</tr>
</table>




---


### setix

Destructively update an element in an array. The form of a `setix` expression is `(setix arr-expr index-expr value-expr)`. Indexing starts from 0 and if you index out of bounds the result is nil. A negative value -n will update the nth value from the end of the list. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(setix [|1 2 3 4 5|] 2 77)
```


</td>
<td>

```clj
[|1 2 77 4 5|]
```


</td>
</tr>
<tr>
<td>

```clj
(setix [|1 2 3 4 5|] -2 66)
```


</td>
<td>

```clj
[|1 2 3 66 5|]
```


</td>
</tr>
</table>




---
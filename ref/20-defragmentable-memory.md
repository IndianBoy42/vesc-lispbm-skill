## Defragmentable memory

LBM has two types of memory, the HEAP and the LBM_MEMORY. Lists and pairs are all stored on the heap. Arrays and large values (such as 64bit numbers are stored on LBM_MEMORY. The HEAP has a nice property that all allocations on it are the same size and therefore the HEAP is immune to the problems caused by fragmentation. On LBM_MEMORY arbitrarily sized arrays can be allocated and fragmentation can cause an allocation to fail even though there is enough free bytes. 

One way to resolve the fragmentation problem is to use a compacting garbage collector. We have opted to not use a compacting garbage collector on the LBM_MEMORY as it is quite complicated. It is extra complicated given how this memory is a shared resource between C extensions and the lisp runtime system. 

Our solution is to allow the programmer to create a memory block inside of the LBM_MEMORY in which we will run a defragmentation routine when needed. The defragmentable memory can only be used to allocate non-zero sized byte arrays on the lisp side. The idea is that the programmer calculates the maximum size of simultaneously used arrays (+ the overhead of 3 words per allocation) needed for a small critical set of arrays used in the program and allocates a defragmentable memory of that size. 

The LBM (non-compacting) gabage collector frees arrays from a defragmentable memory area automatically. An allocation in the defragmentable memory area that fails triggers garbage collection followed by compaction (if needed). 


---


### dm-create

`dm-create` creates a region of defragmentable memory for bytearrays within LBM memory. The form of a `dm-create` expression is `(dm-create size-expr)`. 

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
</table>



---


### dm-alloc

`dm-alloc` is used to allocate a byte-array from a region of defragmentable memory. The form of a `dm-alloc` expression is `(dm-alloc DM-expr size-expr)`. where `DM-expr` evaluates to the defragmentable region to allocate from and `size-expr` is the number of bytes to allocate. Each allocation uses up 12 extra bytes of header that you do not include in `size-expr`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define arr10 (dm-alloc dm 10))
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
(define arr100 (dm-alloc dm 100))
```


</td>
<td>

```clj
[0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]
```


</td>
</tr>
</table>



---
## Flash memory

Flash memory can be used to store data and functions that are constant. Things can be moved to flash explicitly using the `move-to-flash` function or as part of the reading procedure. To move things automatically to flash during reading, there are `@`directives. 


---


### @const-start

`@const-start` opens a block of code where each global definition is moved to constant memory (flash) automatically. This can be used only together with the incremental reader (such as `read-eval-program`). 

A `@const-start` opened block should be closed with a `@const-end`. Constant blocks cannot be nested. 

```clj
@const-start
(defun f (x) (+ x 1))
@const-end

(+ (f 1) 2)
```



---


### @const-end

`@const-end` closes an block opened by `@const-start`. 




---


### move-to-flash

> ***Special form***

A value can be moved to flash storage to save space on the normal evaluation heap or lbm memory.  A `move-to-flash` expression is of the form `(move-to-flash sym opt-sym1 ... opt-symN)`.  The symbols `sym`, `opt-sym1 ... opt-symN` should be globally bound to the values you want moved to flash. After the value has been moved, the environment binding is updated to point into flash memory. **CAUTION** This function should be used carefully. Ideally a value should be moved to flash immediately after it is created so there is no chance that other references to original value exists. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define a [1 2 3 4 5 6])
(move-to-flash a)
a
```


</td>
<td>


```clj
[1 2 3 4 5 6]
```


</td>
</tr>
<tr>
<td>


```clj
(define ls '(1 2 3 4 5))
(move-to-flash ls)
ls
```


</td>
<td>


```clj
(1 2 3 4 5)
```


</td>
</tr>
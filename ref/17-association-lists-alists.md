## association lists (alists)

Association lists (alists) are, just like regular lists, built out of cons-cells. The difference is that an alist is a list of pairs where the first element in each par can be thought of as a key and the second element can be thought of as the value. So alists implement a key-value lookup structure. 

`(list '(1 . horse) '(2 . donkey) '(3 . shark))` is an example of an alist with integer keys and symbol values. 


### acons

The `acons` form is similar to `cons`, it attaches one more element onto an alist. The element that is added consists of a key and a value so `acons` takes one more argument than `cons`. The form of an `acons` expression is `(acons key-expr val-expr alist-expr)`. The `alist-expr` should evaluate to an alist but there are no checks to ensure this. 

Example that adds the key `4` and associated value `lemur` to an existing alist. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(acons 4 'lemur (list '(1 . horse) '(2 . donkey) '(3 . shark)))
```


</td>
<td>

```clj
((4 . lemur) (1 . horse) (2 . donkey) (3 . shark))
```


</td>
</tr>
</table>




---


### assoc

The `assoc` function looks up the first value in an alist matching a given a key.  The form of an `assoc` expression is `(assoc alist-expr key-expr)` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(assoc (list '(1 . horse) '(2 . donkey) '(3 . shark)) 2)
```


</td>
<td>

```clj
donkey
```


</td>
</tr>
</table>




---


### cossa

The `cossa` function looks up the first key in an alist that matches a given value. The form of an `cossa` expression is `(cossa alist-expr value-expr)` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cossa (list '(1 . horse) '(2 . donkey) '(3 . shark)) 'donkey)
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


### setassoc

The `setassoc` function destructively updates a key-value mapping in an alist. The form of a `setassoc` expression is `(setassoc alist-expr key-expr value-expr)`. If you assign a key which doesn't exist in the original alist, it is left unchanged, while another association pair is added to the returned list. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define apa (list '(1 . horse) '(2 . donkey) '(3 . shark)))
(setassoc apa 2 'llama)
```


</td>
<td>


```clj
((1 . horse) (2 . llama) (3 . shark))
```


</td>
</tr>
<tr>
<td>


```clj
(setassoc apa 4 'mouse)
```


</td>
<td>


```clj
((4 . mouse) (1 . horse) (2 . llama) (3 . shark))
```


</td>
</tr>
<tr>
<td>


```clj
apa
```


</td>
<td>


```clj
((1 . horse) (2 . llama) (3 . shark))
```


</td>
</tr>
</table>




---
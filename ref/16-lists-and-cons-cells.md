## Lists and cons cells

Lists are built using cons cells. A cons cell is represented by the lbm_cons_t struct in the implementation and consists of two fields named the `car` and the `cdr`. There is no special meaning associated with the `car` and the `cdr` each can hold a lbm_value. See <a href="#cons">cons</a> and <a href="#list">list</a> for two ways to create structures of cons cells on the heap. 

![cons cell](images/cons_cell.png "cons cell")

A cons cell can be used to store a pair of values. You create a pair by sticking a value in both the car and cdr field of a cons cell using either `'(1 . 2)` or `(cons 1 2)`. 

![pair](images/pair.png "pair")

A list is a number of cons cells linked together where the car fields hold values and the cdr fields hold pointers (the last cdr field is nil). The list below can be created either as `'(1 2 3)` or as `(list 1 2 3)`. 

![Graph representation of s-expression](./images/list_1_2_3.png)


### car

Use `car` to access the `car` field of a cons cell. A `car` expression has the form `(car expr)`. 

Taking the `car` of a number of symbol type is in general a <a href="#type_error">type_error</a>. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(car (cons 1 2))
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
(car (list 9 8 7))
```


</td>
<td>

```clj
9
```


</td>
</tr>
</table>




---


### first

`first` is an alternative  name for the `car` operation. Use `first` to access the first element of a list or pair. A `first` expression  has the form `(first expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(car (cons 1 2))
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
(car (list 9 8 7))
```


</td>
<td>

```clj
9
```


</td>
</tr>
</table>




---


### cdr

Use `cdr` to access the `cdr` field of a cons cell. A `cdr` expression has the form `(cdr expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cdr (cons 1 2))
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
(cdr (list 9 8 7))
```


</td>
<td>

```clj
(8 7)
```


</td>
</tr>
</table>




---


### rest

`rest` is an alternative name for the `cdr` operation. Use `rest` to access all elements except the first one of a list, or to access the second element in a pair. A `rest` expression has the form `(rest expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cdr (cons 1 2))
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
(cdr (list 9 8 7))
```


</td>
<td>

```clj
(8 7)
```


</td>
</tr>
</table>




---


### cons

The `cons` operation allocates a cons cell from the heap and populates the `car` and the `cdr` fields of this cell with its two arguments. The form of a `cons` expression is `(cons expr1 expr2)`. To build well formed lists the innermost cons cell should have nil in the cdr field. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(cons 1 (cons 2 (cons 3 nil)))
```


</td>
<td>

```clj
(1 2 3)
```


</td>
</tr>
<tr>
<td>

```clj
(cons 1 2)
```


</td>
<td>

```clj
(1 . 2)
```


</td>
</tr>
<tr>
<td>

```clj
(cons + 1)
```


</td>
<td>

```clj
(+ . 1)
```


</td>
</tr>
<tr>
<td>

```clj
(cons (cons 1 2) (cons 3 4))
```


</td>
<td>

```clj
((1 . 2) 3 . 4)
```


</td>
</tr>
</table>




---


### .

The dot, `.`, operation creates a pair. The form of a dot expression is `(expr1 . expr2)`. By default the evaluator will attempt to evaluate the result of `(expr1 . expr2)` unless it is prefixed with `'`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
'(1 . 2)
```


</td>
<td>

```clj
(1 . 2)
```


</td>
</tr>
<tr>
<td>

```clj
'((1 . 2) . 3)
```


</td>
<td>

```clj
((1 . 2) . 3)
```


</td>
</tr>
</table>




---


### list

The `list` function is used to create proper lists. The function takes n arguments and is of the form `(list expr1 ... exprN)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(list 1 2 3 4)
```


</td>
<td>

```clj
(1 2 3 4)
```


</td>
</tr>
</table>




---


### length

Computes the length of a list. The `length` function takes one argument and is of the form `(length expr)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(length (list 1 2 3 4))
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


### range

The `range` function computes a list with integer values from a range specified by its endpoints. The form of a range expression is `(range start-expr end-expr)`. The end point in the range is excluded. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(range 4 8)
```


</td>
<td>

```clj
(4 5 6 7)
```


</td>
</tr>
<tr>
<td>

```clj
(range 0 10)
```


</td>
<td>

```clj
(0 1 2 3 4 5 6 7 8 9)
```


</td>
</tr>
<tr>
<td>

```clj
(range -4 4)
```


</td>
<td>

```clj
(-4 -3 -2 -1 0 1 2 3)
```


</td>
</tr>
</table>




---


### append

The `append` function combines two lists into a longer list. An `append` expression is of the form `(append expr1 expr2)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(append (list 1 2 3 4) (list 5 6 7 8))
```


</td>
<td>

```clj
(1 2 3 4 5 6 7 8)
```


</td>
</tr>
</table>




---


### ix

Index into a list using the `ix` function. The form of an `ix` expression is `(ix list-expr index-expr)`. Indexing starts from 0 and if you index out of bounds the result is nil. A negative index accesses values starting from the end of the list. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(ix (list 1 2 3 4) 1)
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
(ix (list 1 2 3 4) -1)
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

Destructively update an element in a list. The form of a `setix` expression is `(setix list-expr index-expr value-expr)`. Indexing starts from 0 and if you index out of bounds the result is nil. A negative value -n will update the nth value from the end of the list. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(setix (list 1 2 3 4 5) 2 77)
```


</td>
<td>

```clj
(1 2 77 4 5)
```


</td>
</tr>
<tr>
<td>

```clj
(setix (list 1 2 3 4 5) -2 66)
```


</td>
<td>

```clj
(1 2 3 66 5)
```


</td>
</tr>
</table>




---


### member

Check if a value is included in list. The form of an `member` expression is `(member value-expr list-expr)`. Equality is checked structurally, in the same way as [`eq`](#eq), meaning if you're checking numbers the types must match (see the following examples). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(member 3 (list 1 2 3))
```


</td>
<td>

```clj
(1 2 3)
```


</td>
</tr>
<tr>
<td>

```clj
(member 3u (list 1 2 3))
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
(member '(b c) '((a b) (b c)))
```


</td>
<td>

```clj
((a b) (b c))
```


</td>
</tr>
</table>

This function can be used as a readable and efficient way of checking if a value is in some constant set of values. This often results in significantly less code than unrolling it as a series of [`eq`](#eq)s inside an [`or`](#or) expression. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(defun is-pet? (thing)
  (member thing '(cat dog)))
(is-pet? 'cat)
```


</td>
<td>


```clj
(cat dog)
```


</td>
</tr>
<tr>
<td>


```clj
(is-pet? 'car)
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
(defun is-pet-unrolled? (thing)
  (or (eq thing 'cat) (eq thing 'dog)))
(eq (is-pet? 'cat) (is-pet-unrolled? 'cat))
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


### setcar

The `setcar` is a destructive update of the car field of a cons-cell. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define apa '(1 . 2))
(setcar apa 42)
apa
```


</td>
<td>


```clj
(42 . 2)
```


</td>
</tr>
<tr>
<td>


```clj
(define apa (list 1 2 3 4))
(setcar apa 42)
apa
```


</td>
<td>


```clj
(42 2 3 4)
```


</td>
</tr>
</table>




---


### setcdr

The `setcdr` is a destructive update of the cdr field of a cons-cell. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define apa '(1 . 2))
(setcdr apa 42)
apa
```


</td>
<td>


```clj
(1 . 42)
```


</td>
</tr>
<tr>
<td>


```clj
(define apa (list 1 2 3 4))
(setcdr apa (list 99 100))
apa
```


</td>
<td>


```clj
(1 99 100)
```


</td>
</tr>
</table>




---


### take

`take` creates a list containing the `n` first elements of another list. The form of a `take` expression is `(take list-exp n-exp)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define apa (list 1 2 3 4 5 6 7 8 9 10))
(take apa 5)
```


</td>
<td>


```clj
(1 2 3 4 5)
```


</td>
</tr>
</table>




---


### drop

`drop` creates a list from another list by dropping the `n` first elements of that list. The form of a `drop` expression is `(drop list-exp n-exp)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define apa (list 1 2 3 4 5 6 7 8 9 10))
(drop apa 5)
```


</td>
<td>


```clj
(6 7 8 9 10)
```


</td>
</tr>
</table>




---


### reverse

`reverse` creates a list containing the same elements as an existing list but in reverse order. The form of a `reverse` expression is `(reverse list-exp)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define apa (list 1 2 3 4 5 6 7 8 9 10))
(reverse apa)
```


</td>
<td>


```clj
(10 9 8 7 6 5 4 3 2 1)
```


</td>
</tr>
</table>




---


### rotate

`rotate` creates a list containing the same elements as an existing list but rotated some number of step along a direction. The form of a `rotate` expression is `(rotate list-exp dist-expr)`. The sign of the value dist-expr evaluates to, decides direction of rotation. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(define apa (list 1 2 3 4 5 6 7 8 9 10))
```


</td>
<td>

```clj
(1 2 3 4 5 6 7 8 9 10)
```


</td>
</tr>
<tr>
<td>

```clj
(rotate apa 1)
```


</td>
<td>

```clj
(10 1 2 3 4 5 6 7 8 9)
```


</td>
</tr>
<tr>
<td>

```clj
(rotate apa -1)
```


</td>
<td>

```clj
(2 3 4 5 6 7 8 9 10 1)
```


</td>
</tr>
<tr>
<td>

```clj
(rotate apa 3)
```


</td>
<td>

```clj
(8 9 10 1 2 3 4 5 6 7)
```


</td>
</tr>
<tr>
<td>

```clj
(rotate apa -3)
```


</td>
<td>

```clj
(4 5 6 7 8 9 10 1 2 3)
```


</td>
</tr>
</table>

Rotating a list in the negative direction is slightly faster than rotating in the positive direction. The chart below shows the time 1 Million 3 step rotations take in each direction at varying list lengths. The data is collected on x86. 

![Performance of list rotate](images/rotate_pos_neg.png "Performance of list rotate")




---


### merge

`merge` merges two lists that are ordered according to a comparator into a single ordered list. The form of a `merge` expression is `(merge comparator-exp list-exp1 list-exp2)`. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define a (list 2 4 6 8 10 12))
(define b (list 1 3 5))
(merge < a b)
```


</td>
<td>


```clj
(1 2 3 4 5 6 8 10 12)
```


</td>
</tr>
</table>




---


### sort

`sort` orders a list of values according to a comparator. The sorting algorithm used is an in-place merge-sort. A copy of the input list is created at the beginning of the sort to provide a functional interface from the user's point of view. The form of a sort expression is `(sort comparator-exp list-exp)` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(define a (list 1 9 2 5 1 8 3))
(sort < a)
```


</td>
<td>


```clj
(1 1 2 3 5 8 9)
```


</td>
</tr>
</table>




---
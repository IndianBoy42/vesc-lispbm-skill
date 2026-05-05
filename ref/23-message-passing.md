## Message-passing


### send

Messages can be sent to a process by using `send`. The form of a `send` expression is `(send pid msg)`. The message, msg, can be any LispBM value. 




---


### recv

> ***Special form***

To receive a message use the `recv` command. A process will block on a `recv` until there is a matching message in the mailbox. The `recv` syntax is very similar to [match](#match). 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(send (self) 28)
(recv ((? n) (+ n 1)))
```


</td>
<td>


```clj
29
```


</td>
</tr>
</table>




---


### recv-to

> ***Special form***

Like [recv](#recv), `recv-to` is used to receive messages but `recv-to` takes an extra timeout argument. It then receives a message containing the symbol `timeout` after the timeout period ends. 

The form of an `recv-to` expression is `(recv-to timeout-secs (pattern1 exp1) ... (patternN expN))` 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(send (self) 28)
(recv-to 0.100000f32
         (timeout 'no-message)
         ((? n) (+ n 1)))
```


</td>
<td>


```clj
29
```


</td>
</tr>
</table>

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>


```clj
(send (self) 'not-foo)
(recv-to 0.100000f32
         (foo 'got-foo)
         (timeout 'no-message))
```


</td>
<td>


```clj
no-message
```


</td>
</tr>
</table>




---


### set-mailbox-size

Change the size of the mailbox in the current process. Standard mailbox size is 10 elements. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(set-mailbox-size 100)
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
(set-mailbox-size 5000000)
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
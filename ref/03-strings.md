## Strings

LBM supports string literals, consisting of a pair of double quotes (`"`) with a string of characters in between. These evaluate to a byte array containing the bytes of these characters (in the source code's encoding), followed by a zero byte. 

Special characters can be written using escape sequences. They take the form of a backslash character (`\`) followed by some character from the list below and are replaced with their corresponding character at read time. A backslash followed by any other character is a read error. 


|Escape sequence|ASCII value|C equivalent|Character represented|
|:----:|:----:|:----:|:----:|
|`\0`|0x0|`\0`|Zero byte|
|`\a`|0x7|`\a`|[Bell character](https://en.wikipedia.org/wiki/Bell_character)|
|`\b`|0x8|`\b`|[Backspace](https://en.wikipedia.org/wiki/Backspace#^H)|
|`\t`|0x9|`\t`|[Horizontal Tab](https://en.wikipedia.org/wiki/Horizontal_Tab)|
|`\n`|0xA|`\n`|[Newline](https://en.wikipedia.org/wiki/Newline)|
|`\v`|0xB|`\v`|[Vertical tab](https://en.wikipedia.org/wiki/Vertical_Tab)|
|`\f`|0xC|`\f`|[Form feed](https://en.wikipedia.org/wiki/Formfeed)|
|`\r`|0xD|`\r`|[Carriage return](https://en.wikipedia.org/wiki/Carriage_Return)|
|`\e`|0x1B|`\e`|[Escape character](https://en.wikipedia.org/wiki/Escape_character#ASCII_escape_character)|
|`\s`|0x20|-|Space ` `|
|`\"`|0x22|`\"`|Double quote `"`|
|`\\`|0x5C|`\\`|[Backslash](https://en.wikipedia.org/wiki/Backslash) `\`|
|`\d`|0x7F|-|[Delete character](https://en.wikipedia.org/wiki/Delete_character)|

Note that unlike other languages, single quotes (`'`) can't be used to form string literals as it's busy being used for [quoting](#quotes-and-quasiquotation)! Therefore it doesn't need to be escaped within string literals. 


### Character literals

Individual characters can be written using character literals. They take the form of `\#` followed by any ASCII character (e.g. `\#a` or `\#X`), and evaluate to their corresponding numerical byte value (note the type!). Like strings, character literals also support escape sequences, in which case they evaluate to its value from the above table, and any invalid characters result in a read error. 

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
\#a
```


</td>
<td>

```clj
97b
```


</td>
</tr>
<tr>
<td>

```clj
\#A
```


</td>
<td>

```clj
65b
```


</td>
</tr>
<tr>
<td>

```clj
\# 
```


</td>
<td>

```clj
32b
```


</td>
</tr>
<tr>
<td>

```clj
\#\n
```


</td>
<td>

```clj
10b
```


</td>
</tr>
<tr>
<td>

```clj
\#\\
```


</td>
<td>

```clj
92b
```


</td>
</tr>
<tr>
<td>

```clj
\#\0
```


</td>
<td>

```clj
0b
```


</td>
</tr>
</table>
## Numbers and numerical types

LBM supports signed and unsigned integer types as well as float and double. The numerical types in LBM are 

   - byte   - unsigned 8bit value.
   - i      - signed 28bit value  (56bits on 64bit platforms).
   - u      - unsigned 28bit value (56bits on 64bit platforms).
   - i32    - signed 32bit value.
   - u32    - unsigned 32bit value.
   - i64    - signed 64bit value.
   - u64    - unsigned 64bit value.
   - f32    - (float) a 32bit floating point value.
   - f64    - (double) a 64bit floating point value.

The byte and the char value have identical representation and type, thus char is an unsigned 8 bit type in LBM. 

An integer literal is interpreted to be of type `i`, a 28/56bit signed integer value.  A literal with decimal point is interpreted to be a type `f32` or float value. 

To specify literals of the other types, the value must be postfixed with a qualifier string.  The qualifiers available in LBM are: `b`, `i`, `u`, `i32`, `u32`, `i64`, `u64`, `f32` and `f63`.  The `i` and `f32` qualifiers are never strictly needed but can be added if one so wishes. An alternative way of writing byte literals is using [Character literals](#character-literals) (e.g. `\#a`). 

So for example: 

   - `1b`     - Specifies a byte typed value of 1
   - `1.0f64` - Specifies a 64bit float with value 1.0.
   - `\#a`   - Specifies a byte type value of 97.

**Note** that it is an absolute requirement to include a decimal when writing a floating point literal in LBM. 

We are trying to make type conversions feel familiar to people who know a bit of  C programming. On a 32bit platform LBM numerical types are ordered according to: `byte < i < u < i32 < u32 < i64 < u64 < float < double`.  Operations such as `(+ a b)`, figures out the largest type according to the ordering above and converts all the values to this largest type. 

Example: 

   - `(+ 1u 3i32)` - Promotes the 1u value type i32 and performs the addition, resulting in 4i32.
   - `(+ 1  3.14)` - Here the value 1 is of type `i` which is smaller than `f32`, the result 4.14f32.

A potential source of confusion is that `f32` is a larger type than `i64` and `u64`. this means that if you, for example, add 1.0 to an `i64` value you will get an `f32` back. If you instead wanted the float to be converted into a double before the addition, this has to be done manually. 

Example: 

   -  `(+ (to-double 1.0) 5i64)`    - Manually convert a value to double.

The `type-of` operation can be used to query a value for its type. On the numerical types the `type-of` operation answers as follows: 

   - `(type-of 1b)`     -> `type-char`
   - `(type-of 1)`      -> `type-i`
   - `(type-of 1u)`     -> `type-u`
   - `(type-of 1i32)`   -> `type-i32`
   - `(type-of 1u32)`   -> `type-u32`
   - `(type-of 1i64)`   -> `type-i64`
   - `(type-of 1u64)`   -> `type-u64`
   - `(type-of 1.0)`    -> `type-float`
   - `(type-of 1.0f64)` -> `type-double`


### Overflow behaviour

Operations on fixed bitwidth numerical types can lead to overflow. The ranges representable in 32bit LBMs integer types are the following: 

   - `type-char`  : 0 - 255
   - `type-i`     : -134217728 - 1342177272
   - `type-u`     : 0 - 268435455
   - `type-i32`   : -2147483648 - 2147483647
   - `type-u32`   : 0- 4294967295
   - `type-i64`   : -9223372036854775808 - 9223372036854775807
   - `type-u64`   : 0 - 18446744073709551615

<table>
<tr>
<td> Example </td> <td> Result </td>
</tr>
<tr>
<td>

```clj
(+ 255b 1b)
```


</td>
<td>

```clj
0b
```


</td>
</tr>
<tr>
<td>

```clj
(- 0b 1b)
```


</td>
<td>

```clj
255b
```


</td>
</tr>
<tr>
<td>

```clj
(+ 134217727 1)
```


</td>
<td>

```clj
-134217728
```


</td>
</tr>
<tr>
<td>

```clj
(- -134217728 1)
```


</td>
<td>

```clj
134217727
```


</td>
</tr>
<tr>
<td>

```clj
(+ 268435455u 1u)
```


</td>
<td>

```clj
0u
```


</td>
</tr>
<tr>
<td>

```clj
(- 0u 1u)
```


</td>
<td>

```clj
268435455u
```


</td>
</tr>
<tr>
<td>

```clj
(+ 2147483647i32 1i32)
```


</td>
<td>

```clj
-2147483648i32
```


</td>
</tr>
<tr>
<td>

```clj
(- -2147483648i32 1i32)
```


</td>
<td>

```clj
2147483647i32
```


</td>
</tr>
<tr>
<td>

```clj
(+ 4294967295u32 1)
```


</td>
<td>

```clj
0u32
```


</td>
</tr>
<tr>
<td>

```clj
(- 0u32 1)
```


</td>
<td>

```clj
4294967295u32
```


</td>
</tr>
<tr>
<td>

```clj
(+ 9223372036854775807i64 1i64)
```


</td>
<td>

```clj
-9223372036854775808i64
```


</td>
</tr>
<tr>
<td>

```clj
(- -9223372036854775808i64 1i64)
```


</td>
<td>

```clj
9223372036854775807i64
```


</td>
</tr>
<tr>
<td>

```clj
(+ 18446744073709551615u64 1u64)
```


</td>
<td>

```clj
0u64
```


</td>
</tr>
<tr>
<td>

```clj
(- 0u64 1u64)
```


</td>
<td>

```clj
18446744073709551615u64
```


</td>
</tr>
</table>


### Cost of numerical operations

All Values in LBM are encoded in one way or another. The encoded value holds additional information about type and garbage collection mark bit.  Operations that operate on an LBM value needs to unpack this encoded format and extract the actual numerical information from the representation. This has a cost and operations on numbers are in general a bit slower than what one gets in, for example C. 

The chart below shows the time it takes to perform 10 million additions on the x86 architecture (a i7-6820HQ) in 32 and 64 Bit mode. 

![Performance of 10 million additions at various types on X86](./images/lbm_arith_pc.png "Performance of 10 million additions at various types on X86")

In 64Bit mode the x86 version of LBM shows negligible differences in cost of additions at different types. 

For addition performance on embedded systems, we use the the EDU VESC motorcontroller as the STM32F4 candidate and the VESC EXPRESS for a RISCV data point. 

![Performance of 100000 additions at various types on ESP32C3 and STM32F4](./images/lbm_arith_embedded.png "Performance of 100000 additions at various types on ESP32C3 and STM32F4")

In general, on 32Bit platforms, the cost of operations on numerical types that are 32Bit or less are about equal in cost. The costs presented here was created by timing a large number of 2 argument additions. Do not see these measurements as the "truth carved in stone", LBM performance keeps changing over time as we make improvements, but use them as a rough guiding principle.
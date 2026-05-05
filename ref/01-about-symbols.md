## About Symbols

Symbols are very important and central to LispBM and also perhaps a bit different from identifiers/names used in languages such as C. A short introduction to symbols could be a good place to start. 

One way to think about a symbol is as a name. Used as a name, a symbol can identify a value or function in the environment. A symbol can also be used as data in and of itself, more on this later. 



---

**NOTE**
Symbols are expressed as strings in your program such as `a`, `let`, `define`, `+` or `orange`. The "reader", the part of LBM that parses code, translates each symbol into a 28bit value. The string `orange` for example is only of interest if you print a symbol and then the runtime system will look up what string corresponds to the 28bit identifier you want to print. So the runtime system is never wasting time comparing strings to see if a symbol is this or that symbol, it's all integer comparisons. 


---

You associate values with symbols using, <a href="#define">define</a>, <a href="#let">let</a> and you can change the value bound to a "variable" using <a href="#set">set</a>, <a href="#setvar">setq</a> or <a href="#setvar">setvar</a>. 

Not all symbols are treated the same in LBM. Some symbols are treated as special because of their very fundamental nature. Among these special symbols you find `define`, `let` and `lambda` for example. These are things that you should not be able to redefine and trying to redefine them leads to an error. Symbols that start with `ext-` are special and reserved for use together with extensions that are loaded and bound at runtime. 

Examples of symbols used as data are `nil` and `t`. `nil` represents "nothing", the empty list or other similar things and `t` represents true.  But any symbol can be used as data by quoting it `'`, see <a href="#quotes-and-quasiquotation"> Quotes and Quasiquotation </a>. 

### Valid Symbol Names

A symbol is a string of characters following the rules: 1. The first character is a one of 'a' - 'z' or 'A' - 'Z' or '+-*/=<>#!'. 2. The rest of the characters are in 'a' - 'z' or 'A' - 'Z' or '0' - '9' or '+-*/=<>!?_'. 3. At most 256 characters long. 

Note that lower-case and upper-case alphabetical letters are considered identical so the symbol `apa` is the same symbol as `APA`. 

examples of valid symbols: ``` apa apa? !apa kurt_russel_is_great ```
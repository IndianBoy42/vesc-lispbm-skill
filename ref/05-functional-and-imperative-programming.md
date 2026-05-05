## Functional and Imperative programming

To differentiate from Imperative and Functional, think of imperative programs  as sequences of operations that update a state and  functional programs as transformations of values through application  of compositions of functions. Functional programming languages often let functions be values, which means that functions  can be stored in lists, returned from other functions and so on 

LispBM is a multiparadigm programming language. Most languages are a mix of functional and imperative and differ in what style it makes most convenient. At one end of this spectrum we find C which makes imperative easy and functional hard,  and in the other end Haskell with the opposite favoritism. In LispBM we try to not unfairly favour any particular style over the other. 

Picking a functional or an imperative style does have consequences though. Functional LispBM programs have properties such as persistence of data, that can be broken using the imperative part of the language. 

With the imperative features of the language it is also in some  places possible to peek under the hood of the runtime system. you can detect when and how environments are shared or copied for example. Please avoid exploiting the power of destructive updates for evil purposes. 

The list below shows imperative operations from the core of LispBM. In the extension libraries there are many more of the kind. 

   - **set**      - Destructively update a binding. Similar to C's =
   - **setq**     - Destructively update a binding. Similar to C's =
   - **setix**    - Destructive update of element in list.
   - **setcar**   - Destructive update of car field in cons cell.
   - **sercdr**   - Destructive update of cdr field in cons cell.
   - **setassoc** - Destructive update of field in association list
   - **bufset**   - The bufset family of functions destructively updates ByteArrays.
   - **bufclear** - Destructive clear of ByteArray.
   - **progn**    - Sequence operations.
   - **define**   - In LispBM, variables can be defined more than once. A second define of a variable is a destructive update.
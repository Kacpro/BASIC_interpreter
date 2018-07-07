Simple BASIC interpreter
Author: Kacper Janda


Functions included in program:
	- load - loading .bas file
	- run - running a loaded program
	- renum - updating lane numbers
	- new - creating a new program
	- list - printing the current program
	- stop - shutting the interpreter down
	- save - saving the current program to the file


Supported instructions from BASIC language:
	- input
	- print
	- goto
	- end
	- let
	- if then [else]
	- repeat until
	- while
	- for


Interpreter supprots fixed-point arithmetic.
One should use lower-case letters only.
Arithmetic operations are done using standard Python operators.


Example programs:
	div.bas - program for listing dividers of the given number
	nwd.bas - program for calculating the smallest common divider
	arm.bas - program for listing all narcissistic numbers smaller than the given number


Sources:
	- https://en.wikipedia.org/wiki/BASIC
	- https://en.wikipedia.org/wiki/Narcissistic_number

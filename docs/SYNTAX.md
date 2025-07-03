# BScript Syntax

## Printing<br>
````
print "At least we have support for basic strings";
````
<br>Or a variable:<br>
````
print a;
````
<br>You can even use the single string! (More on that later.)<br>
````
print str
````

## Creating Variables:<br>
````
var a;
````
<br>(always starts at 0)

## Adding/subtracting to variables

````
a +; //Addition by 1
b -; //Subtraction by 1
````
(Do note that if a variables goes above the number 256, it resets to 0)

## Loops
````
(a,b) {
    //loops until the first variable is equal to the second.
}
````

## The Single String:
In BScript, you get access to a single string, `str`. You can set it using:
````
str "something"
````

## Inputs

This simply sets a user input to the Single String

````
input
````

# Advanced

These are advanced functions for speicial use cases.

## Single String to ASCII

Sets the the ASCII value of the index of the string to a variable.

````
ascii 0,a
````
(Do note the indexes start at 0)

## ASCII to Single String

Adds the ASCII value to the String.

````
revascii a
````

(Do note the strings do not reset when you call this. You may have to call `string ""` if you want this to work correctly.)
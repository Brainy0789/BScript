# Basics

PLEASE NOTE DOCUMENTATION IS UNDER ACTIVE CONSTRUCTION. COMMANDS MARKED WITH (X) AREN'T SUPPORTED BY THE COMPILER AT THE MOMENT.

## Printing<br>
````
print "At least we have support for basic strings!";
````
<br>Or a variable:<br>
````
print a;
````
<br>You can even use the single string! (More on that later.)<br>
````
print str;
````

## Creating Variables:<br>
````
var a;
````
<br>(always starts at 0)

## Setting Variables

````
a=5; //Setting to an integer
a=b; //Setting to another variable
````

## Adding/subtracting to variables

````
a +; //Addition by 1
b -; //Subtraction by 1
````
(Do note that if a variables goes above the number 255, it wraps around to 0)

## Loops
````
(a,b) {
    //loops until the first variable is equal to the second.
}
````

## The Single String:
In BScript, you get access to a single string, `str`. You can set it using:
````
str "something";
````

## Inputs

This simply sets a user input to the Single String

````
input;
````

[Next Page >](functions.html)

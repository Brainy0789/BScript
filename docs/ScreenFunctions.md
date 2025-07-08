# Screen Functions

## Creating Windows (X)

````
window;
````

Running this creates a window. Simple as that. Before you run this command, you'll may want to use a couple other commands

## Window Parameters (X)

````
windowSize 255,255;
windowTitle "Window Name";
window; //Only open the window AFTER the parameters are set. If not, the commands won't do anything.
````

The window paremeters should be pretty self explanatory, but `windowSize` sets the dimensions of the window and `WindowTitle` sets the window title.

(Do note the max size for a window is 255.)

## Drawing Pixels (X)

````
pixel x,y,r,g,b;
````
Displays a pixel at x,y with colors r,g,b.

For example, this code below shows a red at the center of the screen.

````
windowSize 100,100
window;

pixel 50,50,255,0,0;
````

## Clearing the Screen (X)

````
clearScreen r,g,b;
````

Clears screen with r,g,b color.

The code below will never display the `pixel` command because of the clear command.

````
windowSize 100,100;
windowTitle Clear Test;
window;

pixel 50,50,255,0,0; //This pixel will never be shown.
clearScreen 0,0,0;
````

[< Previous Page](functions.html) | [Next Page >](advanced.html) 
// Generated C code from BScript
#include <stdio.h>
#include <string.h>

char str[256] = "";

unsigned char add(unsigned char x, unsigned char y) {
    unsigned char w = 0;
    while (w != y) {
        x = (x + 1) % 256;
        w = (w + 1) % 256;
    }
    return x;
}
unsigned char subtract(unsigned char x, unsigned char y) {
    unsigned char w = 0;
    while (w != y) {
        x = (x - 1 + 256) % 256;
        w = (w + 1) % 256;
    }
    return x;
}
unsigned char toInt() {
    unsigned char a = 0;
    unsigned char b = 0;
    unsigned char result = 0;
    a = (unsigned char)str[0];
    b = (unsigned char)str[1];
    // Convert ASCII to digits
    unsigned char FORTYEIGHT = 0;
    a = subtract(a, FORTYEIGHT);
    b = subtract(b, FORTYEIGHT);
    // Multiply a by 10 (a * 10)
    a = add(a, a);
    a = add(a, a);
    a = add(a, a);
    unsigned char temp = 0;
    a = add(a, a);
    a = add(a, a);
    // Instead let's do:
    // a * 10 = (a * 8) + (a * 2)
    a = add(a, a);
    a = add(a, a);
    a = add(a, a);
    a = add(a, temp);
    result = add(a, b);
    return result;
}
unsigned char i = 0;
unsigned char j = 0;
unsigned char k = 0;
int main() {
fgets(str, sizeof(str), stdin);
i = toInt;
fgets(str, sizeof(str), stdin);
j = toInt;
k = add(i, j);
printf("%d", k);
    return 0;
}

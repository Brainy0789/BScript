// Generated C code from BScript
#include <stdio.h>
#include <string.h>

int main() {
    char str[256] = "";
    // GLOBAL STRING TEST
    strcpy(str, "Hello, World!");
    unsigned char a = 0;
    printf("%s", str);
    // LOOP TEST
    unsigned char b = 0;
    b = (b + 1) % 256;
    b = (b + 1) % 256;
    b = (b + 1) % 256;
    b = (b + 1) % 256;
    while (a != b) {
        printf("%c", a);
        a = (a + 1) % 256;
    }
    // COMMENTS SHOULD BE GENERATING INTO THE C FILE.
    return 0;
}
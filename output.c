#include <stdio.h>
#include <string.h>

int main() {
    char str[256] = "";
    unsigned char a = 0;
    unsigned char b = 0;
    strcpy(str, "A");
    a = (unsigned char)str[0];
    printf("%s", str);
    a = (a + 1) % 256;
    printf("%c", a);
    while (b != a) {
        a = (a - 1 + 256) % 256;
    }
    return 0;
}
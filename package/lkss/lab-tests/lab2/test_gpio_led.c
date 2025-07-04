#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
	int fd = open("/dev/gpio_led", O_WRONLY);
	if (fd < 0) {
		perror("open");
		return 1;
	}

	printf("Turning LED ON...\n");
	write(fd, "1", 1);
	sleep(1);
	printf("Turning LED OFF...\n");
	write(fd, "0", 1);
	printf("Done...\n");

	close(fd);
	return 0;
}

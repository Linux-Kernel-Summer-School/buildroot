#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

#define GPIO_LED_MAGIC	'L'
#define GPIO_LED_ON	_IO(GPIO_LED_MAGIC, 1)
#define GPIO_LED_OFF	_IO(GPIO_LED_MAGIC, 2)

int main() {
	int fd = open("/dev/gpio_led", O_RDWR);
	if (fd < 0) {
		perror("open");
		return 1;
	}

	printf("Turning LED ON via ioctl...\n");
	ioctl(fd, GPIO_LED_ON);
	sleep(1);

	printf("Turning LED OFF via ioctl...\n");
	ioctl(fd, GPIO_LED_OFF);
	printf("Done...\n");

	close(fd);
	return 0;
}

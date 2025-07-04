#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <stdbool.h>

#define LED_SET_DUTY_CYCLE _IOW('l', 0x3, unsigned int)

int main(int argc, char *argv[])
{
	int fd, ret, duty_cycle;

	if (argc != 3) {
		printf("Usage: ./test_led_dimmer DEVICE DUTY_CYCLE\n");
		return 1;
	}

	duty_cycle = atoi(argv[2]);

	if (duty_cycle < 0 || duty_cycle > 100) {
		printf("duty cycle needs to be between 0 and 100\n");
		return 1;
	}

	fd = open(argv[1], O_WRONLY);
	if (fd < 0) {
		printf("failed to open device: %d\n", fd);
		return 1;
	}

	ret = ioctl(fd, LED_SET_DUTY_CYCLE, duty_cycle);
	if (ret) {
		printf("failed to set duty cycle: %d\n", ret);
		close(fd);
		return 1;
	}

	close(fd);

	return 0;
}

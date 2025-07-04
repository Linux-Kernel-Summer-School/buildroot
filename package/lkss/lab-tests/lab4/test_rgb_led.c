#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <stdbool.h>

#define RGB_RED_SET_DUTY_CYCLE		_IOW('l', 0x0, unsigned int)
#define RGB_BLUE_SET_DUTY_CYCLE		_IOW('l', 0x1, unsigned int)
#define RGB_GREEN_SET_DUTY_CYCLE	_IOW('l', 0x2, unsigned int)

#define STEPS 100
#define SLEEP_TIME 0.5

#define ARRAY_SIZE(array) (sizeof(array) / sizeof(array[0]))

struct rgb {
	int red;
	int blue;
	int green;
};

static struct rgb colors[] = {
	{ .red = 100, .blue = 0, .green = 0 }, // RED
	{ .red = 0, .blue = 100, .green = 0 }, // BLUE
	{ .red = 0, .blue = 0, .green = 100 }, // GREEN
};

static int set_color(int fd, int red, int blue, int green)
{
	int ret;

	ret = ioctl(fd, RGB_RED_SET_DUTY_CYCLE, red);
	if (ret) {
		printf("failed to set RED duty cycle: %d\n", ret);
		return ret;
	}

	ret = ioctl(fd, RGB_BLUE_SET_DUTY_CYCLE, blue);
	if (ret) {
		printf("failed to set BLUE duty cycle: %d\n", ret);
		return ret;
	}

	ret = ioctl(fd, RGB_GREEN_SET_DUTY_CYCLE, green);
	if (ret) {
		printf("failed to set GREEN duty cycle: %d\n", ret);
		return ret;
	}

	return 0;
}

static int do_interpolation(int fd, struct rgb *start, struct rgb *end)
{
	int red, blue, green;
	int i, ret;
	float step;

	for (i = 0; i < STEPS; i++) {
		step = (float) i / STEPS;

		red = start->red + (end->red - start->red) * step;
		blue = start->blue + (end->blue - start->blue) * step;
		green = start->green + (end->green - start->green) * step;

		ret = set_color(fd, red, blue, green);
		if (ret) {
			printf("failed to set color: %d\n", ret);
			return ret;
		}

		sleep(SLEEP_TIME);
	}

	return 0;
}

int main(int argc, char *argv[])
{
	int fd, i, ret;
	struct rgb *start, *end;

	if (argc != 2) {
		printf("Usage: ./test_rgb_led DEVICE\n");
		return 1;
	}

	fd = open(argv[1], O_WRONLY);
	if (fd < 0) {
		printf("failed to open device: %d\n", fd);
		return 1;
	}

	start = &colors[0];
	end = &colors[1];
	i = 0;

	while (true) {
		start = &colors[i];
		end = &colors[(i + 1) % ARRAY_SIZE(colors)];

		i = (i + 1) % ARRAY_SIZE(colors);

		ret = do_interpolation(fd, start, end);
		if (ret) {
			printf("failed to perform interpolation: %d\n", ret);
			close(fd);
			return 1;
		}
	}

	close(fd);

	return 0;
}

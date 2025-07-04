all: test_simple_char test_reverse_char test_gpio_led test_gpio_led_ioctl test_gpio_led_blink

test_simple_char: test_simple_char.o
test_reverse_char: test_reverse_char.o
test_gpio_led: test_gpio_led.o
test_gpio_led_ioctl: test_gpio_led_ioctl.o
test_gpio_led_blink: test_gpio_led_blink.o

clean:
	rm -rf *.o
	rm -rf test_simple_char
	rm -rf test_reverse_char
	rm -rf test_gpio_led
	rm -rf test_gpio_led_ioctl
	rm -rf test_gpio_led_blink

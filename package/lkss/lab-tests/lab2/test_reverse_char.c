#include<stdio.h>
#include<stdlib.h>
#include<errno.h>
#include<fcntl.h>
#include<string.h>
#include<unistd.h>

#define BUFFER_LENGTH 256		// The buffer length (crude but fine)
static char receive[BUFFER_LENGTH];	// The receive buffer from the LKM

int main()
{
	int ret, fd;
	char stringToSend[BUFFER_LENGTH];

	printf("Starting device test code example...\n");
	fd = open("/dev/reverse_char", O_RDWR);	// Open the device with read/write access
	if (fd < 0) {
		perror("Failed to open the device...");
		return errno;
	}

	printf("Type in a short string to send to the kernel module:\n");
	if (scanf("%[^\n]%*c", stringToSend) != 1) { // Read in a string (with spaces)
		perror("Invalid input\n");
		return errno;
	}

	printf("Writing message to the device [%s].\n", stringToSend);
	ret = write(fd, stringToSend, strlen(stringToSend));	// Send the string to the LKM
	if (ret < 0) {
		perror("Failed to write the message to the device.");
		return errno;
	}

	printf("Press ENTER to read back from the device...\n");
	getchar();

	printf("Reading from the device...\n");
	ret = read(fd, receive, BUFFER_LENGTH);	// Read the response from the LKM
	if (ret < 0) {
		perror("Failed to read the message from the device.");
		return errno;
	}

	printf("The received message is: [%s]\n", receive);
	printf("End of the program\n");
	return 0;
}

LKSS_VERSION = 2025.0
LKSS_SITE=$(TOPDIR)/package/lkss
LKSS_SITE_METHOD=local

define LKSS_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
endef

define LKSS_INSTALL_TARGET_CMDS
	rsync	-a 					\
		--exclude='*.o'				\
		--exclude='Makefile'			\
		--exclude='*.c'				\
		--exclude='*.h'				\
		$(@D)/lab-tests $(TARGET_DIR)/root/
endef

$(eval $(generic-package))

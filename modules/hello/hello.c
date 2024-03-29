// SPDX-License-Identifier: GPL-2.0-only

#include <linux/module.h>

static int __init hello_init(void)
{
	pr_info("Hello, World\n");
	return 0;
}

static void __exit hello_exit(void)
{
	pr_info("Goodbye!\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("Kamal Heib <kheib@redhat.com>");
MODULE_DESCRIPTION("Hello World Kernel module");

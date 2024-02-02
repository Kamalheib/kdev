// SPDX-License-Identifier: GPL-2.0-only

#include <linux/module.h>
#include <linux/netdevice.h>
#include <linux/rtnetlink.h>
#include <net/rtnetlink.h>
#include <linux/etherdevice.h>

#define DRV_NAME "netdev"

static int netdev_dev_init(struct net_device *netdev)
{
    return 0;
}

static void netdev_dev_uninit(struct net_device *netdev)
{
}

static netdev_tx_t netdev_dev_start_xmit(struct sk_buff *skb,
                                     struct net_device *netdev)
{
    dev_kfree_skb(skb);
    return NETDEV_TX_OK;
}


static const struct net_device_ops netdev_netdev_ops ={
    .ndo_init = netdev_dev_init,
    .ndo_uninit = netdev_dev_uninit,
    .ndo_start_xmit = netdev_dev_start_xmit,
};

static void netdev_setup(struct net_device *netdev)
{
    ether_setup(netdev);

    netdev->netdev_ops = &netdev_netdev_ops;
    netdev->needs_free_netdev = true;

    netdev->flags |= IFF_NOARP;
    netdev->flags &= ~IFF_MULTICAST;
    netdev->priv_flags |= IFF_LIVE_ADDR_CHANGE | IFF_NO_QUEUE;
    netdev->features   |= NETIF_F_SG | NETIF_F_FRAGLIST;
    netdev->features   |= NETIF_F_GSO_SOFTWARE;
    netdev->features   |= NETIF_F_HW_CSUM | NETIF_F_HIGHDMA | NETIF_F_LLTX;
    netdev->features   |= NETIF_F_GSO_ENCAP_ALL;
    netdev->hw_features |= netdev->features;
    netdev->hw_enc_features |= netdev->features;
    eth_hw_addr_random(netdev);

    netdev->min_mtu = 0;
    netdev->max_mtu = 0;

}

static struct rtnl_link_ops netdev_link_ops __read_mostly = {
    .kind = DRV_NAME,
    .setup = netdev_setup,
};

static int __init netdev_init_one(void)
{
    struct net_device *netdev;
    int rc;

    netdev = alloc_netdev(0, "netdev%d", NET_NAME_ENUM, netdev_setup);
    if (!netdev)
        return -ENOMEM;

    netdev->rtnl_link_ops = &netdev_link_ops;
    rc = register_netdevice(netdev);
    if (rc < 0) {
        pr_err("Failed to register netdev\n");
        goto out;
    }

    return 0;

out:
    free_netdev(netdev);
    return rc;
}

static int __init netdev_init(void)
{
    int rc;

    rtnl_lock();
    rc = __rtnl_link_register(&netdev_link_ops);
    if (rc < 0)
        goto out;

    rc = netdev_init_one();
    if (rc) {
        __rtnl_link_unregister(&netdev_link_ops);
        goto out;
    }

    cond_resched();

    pr_info("netdev loaded successfully!\n");

out:
    rtnl_unlock();
    return rc;
}

static void __exit netdev_exit(void)
{
    rtnl_link_unregister(&netdev_link_ops);
    pr_info("netdev unload successfully");
}

module_init(netdev_init);
module_exit(netdev_exit);
MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("Kamal Heib <kheib@redhat.com>");
MODULE_DESCRIPTION("Network device implementaion");

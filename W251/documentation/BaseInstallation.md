# Setting up a base server in the project

Create the VM - something like

    slcli -y vs create -t Git/MIDS_W251_YetAnotherTwitterSentimentAnalysis_YATSA/SoftLayerTemplates/small_2disk_private.slcli --hostname=cashost1

Copy packages from gateway server, login to the gateway server and run:

	scp /software/local.repo root@<IP>:/etc/yum.repos.d/
	scp -r /software/pip root@<IP>:/tmp/

Login to new server:

    ssh root@<IP>

Update:

    yum -y update; reboot

Install required packages, python, iptables:

    yum -y install iptables-services python36u python36u-pip.noarch

Update python:

    pip3.6 install --upgrade pip
    pip3.6 install --upgrade --no-index --find-links file:///tmp/pip pip

Setup iptables firewall: Edit /etc/sysconfig/iptables and make and after the first line starting with -A add:

        -A INPUT -s 10.0.0.0/8 -j ACCEPT

Disable firewall and enable and start iptables:

    systemctl disable firewalld
    systemctl stop firewalld
    systemctl mask firewalld
    systemctl enable iptables
    systemctl start iptables

Edit `/etc/hosts`, comment out the lines with the hostname in them and add the 10.X.Y.Z address (obtained with “ip addr show”), don’t fo
rget the ipv6 addresses.

Enable passwordless ssh (key based logins only).  Edit the /etc/ssh/sshd_config and set:

	PasswordAuthentication no

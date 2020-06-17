# Setting up the gateway server

The gateway server provides several services to the internal network.  Documented here in case we need to move it.

1. Passwordless ssh.  Edit /etc/ssh/sshd_config and change PasswordAuthentication to no

2. Add everyones public key to /root/.ssh/authorized_keys

3. Install iptables and add the rule to allow connections from the 10.0.0.0/8 subnets

4. Install epel/ius repo: 

	yum -y install https://centos7.iuscommunity.org/ius-release.rpm
	yum -y install python36u python36u-pip.noarch
	pip3.6 install --upgrade pip

5. Install SoftLayer commands:

	pip3 install softlayer

6. Set up the /root/.softlayer with the credentials for SoftLayer then test by running "slcli vs list"

7. Add the servers public key to SoftLayer: 

	slcli sshkey add -f .ssh/id_rsa.pub FinalProj

8. Install git and download this repo:

	yum -y install git
	git clone https://github.com/daxaurora/MIDS_W251_Benchmarking

9. Create a disk for storing software.  This will be used to store:
	* a copy of the epel/ius repo so that private only servers can have access,
	* Extra software for the tools we need for the project
This directory was set up as /software

10. Set up an Apache httpd server and point the DocumentRoot to /software
	yum -y install httpd
edit /etc/httpd/conf/httpd.conf and set the DocumentRoot

11. Start the httpd server:

	systemctl enable httpd
	systemctl start httpd

12. Download the epel/ius repositories and create the repos from them:

	yum -y install yum-utils createrepo
	reposync --repoid=epel --download_path=/software/epel
	reposync --repoid=ius --download_path=/software/ius
	createrepo /software/epel
	createrepo /software/ius

12. Create the repo file to be uploaded to all internal servers.  Create the file /software/local.repo with the following contents

	[localepel]
	Name = gatewaylocal
	baseurl=http://10.73.183.212/epel/
	gpgcheck=0
	enabled=1

	[localius]
	name = gatewaylocalius
	baseurl=http://10.73.183.212/ius/
	gpgcheck=0
	enabled=1

Note: the ip address will need to be changed to the gateway ip address if the server changes
Note2: If we have to redo this then we should use http rather than ftp so that we can also do a pip repository

13. Get the software for cassandra:

	mkdir /software/Cassandra
	cd /software/Cassandra
	wget https://www.apache.org/dist/cassandra/redhat/311x/cassandra-3.11.2-1.noarch.rpm
	wget http://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/j/jemalloc-3.6.0-1.el7.x86_64.rpm

Also need to get a copy of jre-8u181-linux-x64.rpm, the Oracle version of Java, but I didn't find a direct URL for that so needed to transfer it in.

14. Download python libraries locally so they can be transferred to the internal nodes:

	mkdir /software/pip
	cd /software/pip
	pip3 download SoftLayer pip kafka-python python-twitter tweepy cassandra-driver

Will likely need lots more here before the end

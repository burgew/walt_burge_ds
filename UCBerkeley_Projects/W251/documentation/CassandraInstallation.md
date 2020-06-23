# Setting up Cassandra

Create the VM - requires a 2 disk server

    slcli -y vs create -t Git/MIDS_W251_YetAnotherTwitterSentimentAnalysis_YATSA/SoftLayerTemplates/small_2disk_private.slcli --hostname=cashost1

Copy packages from gateway server, login to the gateway server and run:

	scp -r /software/Cassandra root@<IP>:/tmp/
	scp /software/local.repo root@<IP>:/etc/yum.repos.d/
	scp -r /software/pip root@<IP>:/tmp/

Login to new Cassandra server:

    ssh root@<IP>

Update:

    yum -y update; reboot

Set up the second disk:

	1. Identiify the disk using:
		fdisk -l | egrep "^Disk /dev"
		we assume /dev/xvdc for the rest of the instructions, but change as appropriate
	2. Use fdisk to add a partition
		fdisk /dev/xvdc
	3. Type n (new) and keep pressing enter to take the default for each question.  At the end type w to save.  This creates the new partition which is the same as the device with '1' at the end.
	4. Create the filesystem:
		mkfs.ext4 /dev/xvdc1
	5. Set it up to be mounted:
		echo "/dev/xvdc1	/var/lib/cassandra   ext4   defaults,noatime 0 0" >> /etc/fstab
	6. Create the directory:
		mkdir /var/lib/cassandra
	7. Mount it:
		mount -a

Install the software packages for Cassandra:

    rpm -ivh /tmp/Cassandra/jre-8u181-linux-x64.rpm
	rpm -ivh /tmp/Cassandra/cassandra-3.11.2-1.noarch.rpm
	rpm -ivh /tmp/Cassandra/jemalloc-3.6.0-1.el7.x86_64.rpm

Clean up these temporary files:

	/bin/rm -rf /tmp/Cassandra

Update and reread the system parameters:

	echo -e "vm.max_map_count = 1048575\nvm.swappiness = 10"  >> /etc/sysctl.conf && sysctl -p

Get the 10.X.Y.Z ip address of the host and record it

	ip addr show

Edit the /etc/hosts file, comment out the lines where the hostname is define with 127.0.0.1 and ::1 and fill in the hostname with the 10.X.Y.Z ip address, e.g.

	#127.0.0.1 cashost1.w251.mids cashost1
	10.54.41.184    cashost1.w251.mids cashost1
	#::1 cashost1.w251.mids cashost1

Edit the /etc/cassandra/conf/cassandra.yaml file and change the following:

		cluster_name: 'Test Cluster'
	to
		cluster_name: 'W251Twitter'

		- seeds: "127.0.0.1"
	to
		- seeds: "<10. ip address of server>"

		listen_address: localhost
	to
		listenaddress: <10. ip address of server>

		rpc_address: localhost
	to
		rpc_address: <10. ip address of server>

Enable and start the service:

	chkconfig cassandra on
	service cassandra start

Check for errors:

	egrep "ERR|WARN" /var/log/cassandra/system.log

Some warnings can be ignored

Verify it:

	nodetool status

should show something like:

	[root@cashost1 conf]# nodetool status
	Datacenter: W251Twitter
	=======================
	Status=Up/Down
	|/ State=Normal/Leaving/Joining/Moving
	--  Address       Load       Tokens       Owns (effective)  Host ID                               Rack
	UN  10.54.41.184  243.43 KiB  256          100.0%            3635de91-0ef4-4858-b7be-4fa4704da17e  rack1

and connecting into the database:

	[root@cashost1 conf]# cqlsh $(hostname) -u cassandra -p cassandra
	Connected to pdurkinC1 at cashost1.w251.mids:9042.
	[cqlsh 5.0.1 | Cassandra 3.11.2 | CQL spec 3.4.4 | Native protocol v4]
	Use HELP for help.
	cassandra@cqlsh>

Set up python on any server that needs access to the database.  The below assumes that the pip packages are in a directory /tmp/pip and then are installed locally (no internet required):

	yum -y install python36u python36u-pip.noarch
	pip3.6 install --upgrade --no-index --find-links file:///tmp/pip pip
	pip3 install --upgrade --no-index --find-links file:///tmp/pip cassandra-driver

Set up initial keyspace:

	create keyspace w251twitter with replication = {'class':'SimpleStrategy', 'replication_factor':1};
	use w251twitter;
	create table twitter_connections(username text, access_token text, access_token_secret text, consumer_key t
	ext, consumer_secret text, PRIMARY KEY(username));

After this there are utility functions (in this repo) to insert, retrieve and delete these keys

## Adding a second and third node

Follow the same procedure as above, however in the -seeds configuration in cassandra.yaml use the ip address of one of the existing servers.  Set the listen_address and the rpc_address to the localhosts 10.X.Y.Z address and the same cluster name.  Check the "nodetool status" and wait until the state changes to UN to be fully up.  Once the second node has been joined login to one of the nodes and update the replication factor for the keyspace:

	[root@cashost2 cassandra]# cqlsh $(hostname) -u cassandra -p cassandra
	Connected to W251Twitter at cashost2.w251.mids:9042.
	[cqlsh 5.0.1 | Cassandra 3.11.2 | CQL spec 3.4.4 | Native protocol v4]
	Use HELP for help.
	cassandra@cqlsh> alter keyspace w251twitter with replication = { 'class' : 'SimpleStrategy', 'replication_factor' :2};

and for the third node change the replication factor to 3 (that should be enough replication so further updates not required).

## Decommissioning
Login to the server and type:
	nodetool -h localhost decommission
then shutdown the service and remove it.  If there are aliases to it then remove or replace them

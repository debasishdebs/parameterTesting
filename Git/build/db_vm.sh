#!/bin/bash
#
# This script automates the following build steps:
#
# - Install expect
# - Install telnet
# - Install git
# - Install mysql
# - Edit the mysql conf, /etc/my.cnf, with the appropriate settings
# - Create symlinks for mysql socket (mysql.sock)
# - Start mysql
# - Complete the mysql_secure_installation (uses expect)
# - Grant all privs to mysql root user (uses expect to run query)
# - Create the pa mysql user
# - Grant priveliges to the pa mysql user
# - Create the repl mysql user (*used for replication)
# - Grant priveliges to the repl mysql user
# - Create the directories used for mysql logs
# - Create the directories used for mysql bin logging (*for replication)
# - Change the permissions and ownership for the directories used by mysql
# - chown the /etc/my.cnf to fsgapp:fsgsbl
# - Generate the ssh keys for fsgapp
# - Change the password for fsgapp to the standard value
#
# ! Tested on Red Hat Enterprise Linux Server release 6.6 
# ! author <mitch.seymour@macys.com>

echo "

Running Predictive Analytics - Database VM - Build Script ...
"

sleep 2
echo "
                     3
"
sleep 1
echo "
                     2
"
sleep 1
echo "
                     1
"
sleep 1


# install expect
yum -y install expect

# install telnet
yum -y install telnet

# install git
yum -y install git

# create yum repo for mysql
echo "[mysql-5.6.23]
name=mysql-5.6.23
baseurl=http://esu3v544.federated.fds:9080/repo/mysql-5.6/5.6.23/
gpgkey=http://esu3v544.federated.fds:9080/repo/RPM-GPG-KEY-mysql
gpgcheck=1
enabled=1" > /etc/yum.repos.d/mysql.repo

# install mysql
expect -c "

    set timeout 15
    spawn yum install mysql mysql-server mysql-devel

    expect {
        "]:"        { send y\r ; sleep 1 ; exp_continue  }
    }
"

# edit the mysql config
cp /etc/my.cnf /etc/my.cnf.bu
cat << CONFIG_END > /etc/my.cnf
[mysqld]
datadir=/data/mysql
socket=/data/mysql/mysql.sock

# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0

# Settings user and group are ignored when systemd is used (fedora >= 15).
# If you need to run mysqld under a different user or group,
# customize your systemd unit file for mysqld according to the
# instructions in http://fedoraproject.org/wiki/Systemd
user=mysql

# Semisynchronous Replication
# http://dev.mysql.com/doc/refman/5.5/en/replication-semisync.html
# uncomment next line on MASTER
;plugin-load=rpl_semi_sync_master=semisync_master.so
# uncomment next line on SLAVE
;plugin-load=rpl_semi_sync_slave=semisync_slave.so

# Others options for Semisynchronous Replication
;rpl_semi_sync_master_enabled=1
;rpl_semi_sync_master_timeout=10
;rpl_semi_sync_slave_enabled=1

# http://dev.mysql.com/doc/refman/5.5/en/performance-schema.html
performance_schema = ON
performance_schema_consumer_events_statements_history_long = ON

# SAFETY #
max_allowed_packet                      = 500M
max_connect_errors                      = 100000
sysdate_is_now                          = 1
innodb                                  = FORCE

# GENERAL #
default_storage_engine                  = InnoDB
event_scheduler                         = 1

# MyISAM #
key_buffer_size                         = 1G
myisam-recover-options                  = FORCE,BACKUP
concurrent_insert                       = 2

# CACHES AND LIMITS #
tmp_table_size                          = 100M
max_heap_table_size                     = 100M
query_cache_type                        = 1
query_cache_size                        = 100M
query_cache_limit                       = 100M
max_connections                         = 120
thread_cache_size                       = 50
open_files_limit                        = 65535
table_definition_cache                  = 20000
table_open_cache                        = 1024
sort_buffer_size                        = 150M
join_buffer_size                        = 150M

# INNODB #
innodb_flush_method                     = O_DSYNC
innodb_thread_concurrency               = 48
innodb_log_files_in_group               = 2
innodb_log_file_size                    = 1G
innodb_log_buffer_size                  = 2G
innodb_flush_log_at_trx_commit          = 2
innodb_file_per_table                   = 1
innodb_buffer_pool_size                 = 10G
innodb_buffer_pool_instances            = 4
innodb_stats_on_metadata                = 0

# LOGGING #
long_query_time                         = 30
log_warnings                            = 1
log_queries_not_using_indexes           = 0
slow_query_log                          = 1
slow_query_log_file                     = /var/log/mysql-slow.log

[mysqld_safe]
log-error                               = /var/log/mysqld.log
pid-file                                = /var/run/mysqld/mysqld.pid

[client]
socket                                  = /data/mysql/mysql.sock

#
# include all files from the config directory
#
!includedir /etc/my.cnf.d
CONFIG_END

# create symlink
echo "Creating symlink for mysql.sock"
sleep 1
ln -s /data/mysql/mysql.sock /var/lib/mysql/mysql.sock
sleep 1

#start mysql
/etc/rc.d/init.d/mysqld start # should say OK

# secure the mysql install
expect -c "

spawn /usr/bin/mysql_secure_installation

expect \"Enter current password for root (enter for none):\"
send \"\r\"

expect \"Set root password?\"
send \"y\r\"

expect \"New password:\"
send \"magic1858\r\"

expect \"Re-enter new password:\"
send \"magic1858\r\"

expect \"Remove anonymous users?\"
send \"y\r\"

expect \"Disallow root login remotely?\"
send \"n\r\"

expect \"Remove test database and access to it?\"
send \"y\r\"

expect \"Reload privilege tables now?\"
send \"y\r\"

"
# Grant all priveleges to mysql root user, and create the pa user
expect -c "

set timeout 20
spawn mysql -u root -p

expect \"password:\"
send \"magic1858\r\"

expect \"mysql>\"
send \"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY PASSWORD '*E8EAA723B938A8D4CC24BAAAB3946CA637DD90AE' WITH GRANT OPTION; FLUSH PRIVILEGES;\r\"

expect \"mysql>\"
send \"create database if not exists predictiveAnalytics character set utf8 collate utf8_general_ci;\r\"

expect \"mysql>\"
send \"create user 'pa'@'%' identified by password '*B1BD076E04CFF037D338541030762D64B999AFEF';\r\"

expect \"mysql>\"
send \"grant all privileges on predictiveAnalytics.* to 'pa'@'%';\r\"

expect \"mysql>\"
send \"create user 'repl'@'%' identified by password '*C3EB3068A84EA065BFFC1DE226EDC7D816A61B9F';\r\"

expect \"mysql>\"
send \"grant replication slave on *.* to 'repl'@'%';\r\"

expect \"mysql>\"
send \"quit;\r\"
"

#make sure the mysql user owns the mysql log files
touch /var/log/mysqld.log && touch /var/log/mysql-slow.log && chown mysql:mysql /var/log/mysql* && chmod +w /var/log/mysql*

# create the directory for logging
mkdir /data/mysqlrepl/ && chown -R mysql:mysql /data/mysqlrepl

# make sure fsgapp owns the my.cnf file
chown fsgapp:fsgsbl /etc/my.cnf


#change the password for the fsgapp user
expect -c "

spawn passwd fsgapp

expect \"New password: \"
send \"reset.1\r\"

expect \"Retype new password: \"
send \"reset.1\r\"

sleep 1
send \"\r\"
"

echo "

Changed password for fsgapp

"

# create ssh-keys for fsgapp
expect -c "

spawn runuser -l fsgapp -c \"ssh-keygen -t rsa\"

expect \"Enter file in which to save the key (/home/fsgapp/.ssh/id_rsa):\"
send \"\r\"

expect \"Enter passphrase (empty for no passphrase):\"
send \"\r\"

expect \"Enter same passphrase again:\"
send \"\r\"
"

printf "\n"

echo "
	
   What Now?
   
  - Configure the db replication as needed
  - Take a 15 minute break. You deserve it.

"
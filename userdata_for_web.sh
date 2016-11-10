#! /bin/bash
# update yum
set -x
yum -y update
yum -y install gcc
cd /opt

#install codedeploy
wget https://aws-codedeploy-ap-southeast-1.s3.amazonaws.com/latest/install
chmod +x install
./install auto

# Install Java
cd /opt
aws s3 cp --region=ap-southeast-1 s3://fabianlim-artifact/jdk-8u112-linux-x64.rpm /opt/jdk-8u112-linux-x64.rpm
rpm -i jdk-8u112-linux-x64.rpm

# install tomcat
cd /opt
wget http://mirror.atlanta.delimiter.com/pub/apache/tomcat/tomcat-6/v6.0.47/bin/apache-tomcat-6.0.47.tar.gz
tar -xzvf apache-tomcat-6.0.47.tar.gz
cd apache-tomcat-6.0.47/bin
tar -zvxf commons-daemon-native.tar.gz
cd commons-daemon-1.0.15-native-src/unix
export JAVA_HOME=/usr/java/latest
./configure
sleep(5)
/opt/apache-tomcat-6.0.47/bin/commons-daemon-1.0.15-native-src/unix/
make
cp jsvc ../..
cd ../..
cd /opt/apache-tomcat-6.0.47/bin
source ./startup.sh &
echo "exit userdata"

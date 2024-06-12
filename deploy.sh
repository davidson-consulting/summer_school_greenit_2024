SERVER=$(oarstat -j $1 -J | jq '.["258103"]["assigned_network_address"][0]')
kadeploy3 -m $SERVER ubuntu2204-nfs

ssh root@$SERVER apt update
ssh root@$SERVER apt install -y python3-pip cgroup-tools
ssh root@$SERVER wget https://github.com/hubblo-org/scaphandre/releases/download/v0.5.0/scaphandre-x86_64-unknown-linux-gnu -O /usr/bin/scaphandre 
ssh root@$SERVER chmod a+x /usr/bin/scaphandre

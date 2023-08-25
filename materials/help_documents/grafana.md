#[grafana](https://grafana.com/grafana/download)

# Install
```
wget https://dl.grafana.com/oss/release/grafana-7.4.3-1.x86_64.rpm
sudo yum install grafana-7.4.3-1.x86_64.rpm
```

Set up service
```
# reload
systemctl daemon-reload
# add to auto-set when starting the server
systemctl enable grafana-server.service 
# set up service
systemctl start grafana-server.service 
# check port
ss -lntp |grep grafana-server
# check process
ps -ef |grep grafana-server
```
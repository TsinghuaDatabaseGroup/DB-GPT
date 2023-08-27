# prometheus installation

### prometheus

Download
```
wget https://github.com/prometheus/prometheus/releases/download/v2.25.0/prometheus-2.25.0.linux-amd64.tar.gz -P /tmp

tar -zxpvf prometheus-2.25.0.linux-amd64.tar.gz
cd prometheus-2.25.0.linux-amd64/
cp prometheus  /usr/local/bin
cp promtool  /usr/local/bin
mkdir /etc/prometheus/
cp prometheus.yml /etc/prometheus/
```

Edit prometheus.yml

```
vim /etc/prometheus/prometheus.yml
# my global config
global:
  scrape_interval:     60s # Set the scrape interval to every 15 seconds. Default is every 1 minute.
  evaluation_interval: 60s # Evaluate rules every 15 seconds. The default is every 1 minute.
  # scrape_timeout is set to the global default (10s).

# Alertmanager configuration
alerting:
  alertmanagers:
  - static_configs:
    - targets:
      # - alertmanager:9093

# Load rules once and periodically evaluate them according to the global 'evaluation_interval'.
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

# A scrape configuration containing exactly one endpoint to scrape:
# Here it's Prometheus itself.
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']

# Collect node exporter monitoring data
  - job_name: 'node'
    scrape_interval: 60s
    static_configs:
    - targets: ["xxx.xx.xx.xxx:9100","xxx.xx.xx.xxx:9100"]

# Collect mysql exporter monitoring data
  - job_name: 'mysql'
    scrape_interval: 60s
    static_configs:
    - targets: ["xxx.xx.xx.xxx:9104"]
      
# Collect postgres exporter monitoring data
  - job_name: 'postgres'
    scrape_interval: 60s
    static_configs:
    - targets: ["xxx.xx.xx.xxx:9187"]
```

Create service
```
vim /usr/lib/systemd/system/prometheus.service

[Unit]
Description=prometheus-server
After=network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target
 
[Service]
Type=simple
ExecStart=/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --web.enable-lifecycle --storage.tsdb.path=/usr/local/prometheus/data --storage.tsdb.retention.time=7d --web.max-connections=512 --web.read-timeout=3m --query.max-concurrency=25 --query.timeout=2m
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
 
[Install]
WantedBy=multi-user.target
```

Run service
```
# Reload
systemctl daemon-reload
# Add to auto-set when starting the server
systemctl enable prometheus.service 
# Set up service
systemctl start prometheus.service 
# Check port
ss -lntp |grep prometheus
# Check process
ps -ef |grep prometheus
```


# exporter

## node_exporter

Download
```
wget https://github.com/prometheus/node_exporter/releases/download/v1.1.1/node_exporter-1.1.1.linux-amd64.tar.gz
tar -xvzf node_exporter-1.6.0.linux-amd64.tar.gz 
cd node_exporter-1.6.0.linux-amd64
cp -r node_exporter /usr/local/bin/
chmod +x /usr/local/bin/node_exporter
```

Set up service
```
vim /etc/systemd/system/node_exporter.service
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
```

Run service
```
# Reload
systemctl daemon-reload
# Add to auto-set when starting the server
systemctl enable node_exporter.service 
# Set up service
systemctl start node_exporter.service 
# Check process
ps -ef |grep node_exporter
```

## mysql

Download
```
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.12.1/mysqld_exporter-0.12.1.linux-amd64.tar.gz
tar -xvf mysqld_exporter-0.12.1.linux-amd64.tar.gz
cd mysqld_exporter-0.12.1.linux-amd64/
cp -r mysqld_exporter /usr/local/bin/
chmod +x /usr/local/bin/mysqld_exporter
```

Create service
```
vim /usr/lib/systemd/system/mysqld_exporter.service
[Unit]
Description=mysqld_exporter
After=network.target
[Service]
Type=simple
User=mysql
Environment=DATA_SOURCE_NAME=user:password@(localhost:3306)/
ExecStart=/usr/local/bin/mysqld_exporter --web.listen-address=0.0.0.0:9104
  --config.my-cnf /etc/my.cnf \
  --collect.slave_status \
  --collect.slave_hosts \
  --log.level=error \
  --collect.info_schema.processlist \
  --collect.info_schema.innodb_metrics \
  --collect.info_schema.innodb_tablespaces \
  --collect.info_schema.innodb_cmp \
  --collect.info_schema.innodb_cmpmem
Restart=on-failure
[Install]
WantedBy=multi-user.target
```

Run service
```
systemctl daemon-reload

systemctl enable mysqld_exporter.service 

systemctl start mysqld_exporter.service 

ps -ef |grep mysqld_exporter
```



## pgsql

Download
```
wget https://github.com/prometheus-community/postgres_exporter/releases/download/v0.11.1/postgres_exporter-0.11.1.linux-amd64.tar.gz

tar -xvzf postgres_exporter-0.11.1.linux-amd64.tar.gz 
cd postgres_exporter-0.11.1.linux-amd64/
cp -r postgres_exporter /usr/local/bin/
chmod +x /usr/local/bin/postgres_exporter
```

Create service
```
vim /usr/lib/systemd/system/postgres_exporter.service
[Unit]
Description=postgres_exporter
After=network.target

[Service]
Type=simple
User=postgres
Environment="DATA_SOURCE_NAME=postgresql://user:password@localhost:5432/postgres?sslmode=disable"
ExecStart=/usr/local/bin/postgres_exporter --log.level=error
#  --extend.query-path=quires.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Run service
```
systemctl daemon-reload

systemctl enable postgres_exporter.service 

systemctl start postgres_exporter.service 

ps -ef |grep postgres_exporter
```

## greenplum

Installation
```
[root@iZ2ze0ree1kf7ccu4p1vcyZ ~]# cd ~
[root@iZ2ze0ree1kf7ccu4p1vcyZ ~]# wget https://github.com/tangyibo/greenplum_exporter/releases/download/v1.1/greenplum_exporter-1.1-rhel7.x86_64.rpm
[root@iZ2ze0ree1kf7ccu4p1vcyZ ~]# rpm -ivh greenplum_exporter-1.1-rhel7.x86_64.rpm
```
Set database connection
```
[root@iZ2ze0ree1kf7ccu4p1vcyZ ~]# vim /usr/local/greenplum_exporter/etc/greenplum.conf
GPDB_DATA_SOURCE_URL=postgres://user:password@ip:54432/postgres?sslmode=disable
```

Run service
```
systemctl daemon-reload

systemctl enable greenplum_exporter

systemctl start greenplum_exporter

ps -ef |grep greenplum_exporter
```

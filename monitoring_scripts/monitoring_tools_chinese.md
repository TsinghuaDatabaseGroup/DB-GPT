# 优化工具

![Linux](https://pic1.zhimg.com/80/v2-9d70261114d9a29d55d152e265299108_720w.webp?source=1940ef5c)


[Linux Performance](https://www.brendangregg.com/linuxperf.html)



| 优化工具 | CPU优化 | IO优化 | 磁盘优化 |
| --- | --- | --- | --- |
| Nice和Renice | 控制进程优先级，提高CPU使用效率  | N/A | N/A |
| ionice | 调整磁盘I/O的优先级，减少对CPU的影响  | 提高磁盘I/O性能 | N/A |
| hdparm | 调整磁盘读写参数，提高磁盘I/O性能 | N/A | 提高磁盘读写性能 |
| iostat | 监控磁盘I/O性能，找出瓶颈 | 监控I/O性能，找出瓶颈 | N/A |
| sar | 监控系统负载、CPU、磁盘和网络等性能指标 | 监控I/O性能，找出瓶颈 | 监控磁盘I/O性能，找出瓶颈 |
| vmstat | 监控系统虚拟内存、CPU、磁盘和IO等性能指标 | 监控I/O性能，找出瓶颈 | 监控磁盘I/O性能，找出瓶颈 |

以上是常用的Linux系统优化工具，可以从CPU、IO、磁盘三个方面来分别进行优化。在CPU方面，可以利用Nice和Renice调整进程的优先级，提高CPU的使用效率；在IO方面，可以利用ionice和iostat监控I/O性能，并调整磁盘I/O的优先级，减少对CPU的影响。在磁盘方面，可以利用hdparm调整磁盘读写参数，提高磁盘I/O性能，并使用sar和vmstat来监控系统的磁盘I/O性能，找出瓶颈并进行优化。

### Nice使用方法
不需要安装，Linux自带
- `nice`命令用于启动一个新进程，并将其nice值设置为指定值。语法如下：

  ```
  nice [OPTION] [COMMAND [ARG]...]
  ```

  其中，`OPTION`参数可以用来指定nice值的具体数值、进程要使用的CPU核心数量等选项。

  示例：将`ls -l`命令以nice值19的优先级启动

  ```
  nice -n 19 ls -l
  ```

### Renice使用方法
不需要安装，Linux自带
- `renice`命令则是用于修改已经运行的进程的nice值。语法如下：
  ```
  renice [OPTION] PRIORITY [[-p] PID]...
  ```

  其中，`PRIORITY`参数是新的nice值，`PID`参数是要修改nice值的进程ID。如果没有指定`PID`参数，则renice会修改所有当前用户的进程的nice值。

  示例：将进程ID为1234的进程的nice值设置为5

  ```
  renice 5 1234
  ```


### ionice
ionice命令用于调整磁盘I/O的优先级，可以通过设置进程的I/O调度类别和优先级来影响进程所产生的磁盘I/O的行为。使用ionice可以避免磁盘I/O操作对CPU性能的影响。

ionice的基本语法如下：

```
ionice [OPTIONS] [COMMAND [ARG]...]
```

其中，`OPTIONS`参数可以指定I/O调度类别和优先级，常用的选项有：

- `-c, --class`: 指定I/O调度类别，可选值为`none`（不改变I/O调度类别）、`realtime`（实时）、`best-effort`（最佳尽力）和`idle`（空闲）。
- `-n, --priority`: 指定I/O优先级，取值范围为0~7，默认值为4。

示例：将`dd`命令以idie类别启动，并设置优先级为7：

```
ionice -c 3 -n 7 dd if=/dev/zero of=/tmp/test bs=1M count=1000
```

上述命令中，`-c 3`表示选择idle类别，`-n 7`表示设置优先级为7，`dd if=/dev/zero of=/tmp/test bs=1M count=1000`指定了要执行的命令及其参数。

注意：只有具有root权限的用户才能够使用ionice命令来修改其他用户的进程的I/O调度类别和优先级

### hdparm
[文档1](https://post.smzdm.com/p/a5d4orl7/)
[文档2](https://www.modb.pro/db/484676)
[文档3](http://www.manongjc.com/detail/60-ifohlihyzsxzggx.html)

hdparm命令是一个用于调整磁盘读写参数，提高磁盘I/O性能的工具。hdparm可以对磁盘驱动器进行各种操作，包括查看驱动器参数、测量磁盘I/O性能指标、启用或禁用硬件加速特性等。

hdparm的基本语法如下：

```
hdparm [OPTIONS] [DEVICE]
```

其中，`OPTIONS`参数是hdparm要执行的具体操作，`DEVICE`参数是要操作的设备名称（如/dev/sda）。常用的选项有：

- `-T, --direct`: 测量磁盘缓存读取速度。
- `-t, --totally`: 测量磁盘物理读写速度。
- `-c, --read-sector`: 读取指定扇区的数据并输出到标准输出。
- `-S, --standby`: 将磁盘设置为待机状态以节省电力消耗。
- `-A, --read-sector`: 查看或修改硬盘的高级功率管理设置。
- `-d, --dma`: 启用或禁用DMA模式。
- `-X, --set-xfer-mode`: 设置传输模式（PIO、Multiword DMA和Ultra DMA）。

示例：测量sda磁盘的缓存读取速度

```
hdparm -T /dev/sda
```

示例：将sda磁盘设置为Ultra DMA传输模式

```
hdparm -X udma6 /dev/sda
```

### iostat
[文档1](https://blog.csdn.net/m369880395/article/details/127789732)
iostat是一个用于监控磁盘I/O性能的工具，可以显示磁盘的实时读写速度、响应时间和I/O队列长度等信息，帮助用户找出系统中的瓶颈。iostat可以显示整个系统上所有磁盘的I/O指标，也可以分别显示单个设备的情况。

iostat的基本语法如下：

```
iostat [OPTIONS] [DEVICE [INTERVAL [COUNT]]]
```

其中，`OPTIONS`参数是iostat要执行的具体操作，`DEVICE`参数是要操作的磁盘设备名称（如/dev/sda），`INTERVAL`参数是每次采样的时间间隔（单位秒），`COUNT`参数是要采样的次数。

常用的选项有：

- `-c, --cpu`: 显示CPU使用率统计信息。
- `-d, --device`: 显示磁盘设备的I/O性能指标。
- `-k, --kilobytes`: 以KB为单位显示数据传输速度。
- `-m, --megabytes`: 以MB为单位显示数据传输速度。

示例：显示整个系统上所有磁盘的I/O指标

```
iostat -d
```

示例：每隔1秒钟输出一次sda设备的I/O指标，共输出10次

```
iostat -d /dev/sda 1 10
```

注意：在使用iostat监控磁盘I/O性能时，需要注意采样时间间隔和采样次数的设置，以免过于频繁地采样导致系统性能下降或过于稀疏的采样导致监控不到关键信息。


### sar

[文档1](https://blog.csdn.net/zyqash/article/details/128712108)
[文档2](https://www.jianshu.com/p/dd828da4fcdb)

sar是一个用于监控系统性能的工具，可以记录和显示CPU、内存、I/O等方面的性能指标。sar可以对系统资源的使用情况进行持续监控，并将结果输出到文件或屏幕上。sar命令需要root权限才能运行。

sar的基本语法如下：

```
sar [OPTIONS] [INTERVAL [COUNT]]
```

其中，`OPTIONS`参数是sar要执行的具体操作，`INTERVAL`参数是每次采样的时间间隔（单位秒），`COUNT`参数是要采样的次数。

常用的选项有：

- `-u, --cpu`: 显示CPU使用率统计信息。
- `-r, --mem`: 显示内存使用率统计信息。
- `-b, --io`: 显示磁盘I/O性能指标统计信息。
- `-n, --net`: 显示网络流量统计信息。
- `-q, --queue`: 显示负载均衡队列长度统计信息。

示例：每隔1秒钟输出一次CPU使用率，共输出10次

```
sar -u 1 10
```

示例：将磁盘I/O性能指标写入到文件中

```
sar -b -o iostat.log
```

注意：sar会在后台运行并记录系统性能指标，因此可能对系统产生一定的性能影响。如果需要长期运行sar来监控系统性能，请考虑调整采样时间间隔和采样次数，以减少对系统的影响。

### vmstat

[文档1](https://blog.csdn.net/weixin_64413763/article/details/128082083)

vmstat是一个用于监控系统资源的工具，可以显示CPU、内存、磁盘I/O等方面的性能指标。vmstat可以对系统资源的使用情况进行持续监控，并将结果输出到屏幕上。

vmstat的基本语法如下：

```
vmstat [OPTIONS] [INTERVAL [COUNT]]
```

其中，`OPTIONS`参数是vmstat要执行的具体操作，`INTERVAL`参数是每次采样的时间间隔（单位秒），`COUNT`参数是要采样的次数。

常用的选项有：

- `-n`: 隐藏第一行的统计信息。
- `-a`: 显示活跃和非活跃/缓存内存的统计信息。
- `-s`: 显示所有内存统计信息。
- `-d`: 显示磁盘读写统计信息。
- `-p`: 显示进程相关的统计信息。

示例：每隔1秒钟输出一次CPU和内存使用率，共输出10次

```
vmstat 1 10
```

示例：每隔2秒钟输出一次磁盘I/O性能指标，共输出5次

```
vmstat -d 2 5
```

注意：在使用vmstat监控系统资源时，需要考虑采样时间间隔和采样次数的设置，以免过于频繁地采样导致系统性能下降或过于稀疏的采样导致监控不到关键信息。此外，vmstat只提供了当前系统的性能指标，无法对历史数据进行回溯和分析。如果需要长期监控系统性能并进行更深入的分析，请考虑使用其他监控工具。
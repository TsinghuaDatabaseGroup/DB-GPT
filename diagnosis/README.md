

We demonstrate the following cases that are expertly crafted by AgentVerse.

#### [Database Administrator (DBA)]
In the database diagnosis scenario, the Chief DBA monitors the database system for anomalies. If detected, the memory and CPU agents are alerted to analyze root causes and suggest optimization solutions. The Chief DBA then provides a summarized diagnosis to the user, who can also contribute by giving instructions or evaluating the effectiveness of proposed solutions.

You should first configure the [database tool](https://github.com/OpenBMB/BMTools/blob/main/bmtools/tools/db_diag/readme.md) in BMTools, and launch the BMTools server according to the [guidance](https://github.com/OpenBMB/BMTools/tree/main#211-local-tools). Then use the following command to launch the Database Administrator example:
```bash
python main_demo.py --task db_diag
```

https://github.com/OpenBMB/AgentVerse/assets/11704492/c633419d-afbb-47d4-bb12-6bb512e7af3a
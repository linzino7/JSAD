# Log parsering 


1. Install Drain3

```
pip3 install drain3
```

2. Unzip ldap log file

```
unzip 80_01_paper.zip
```

3. Sorting log by conn to csv (note files path)

```
python3 preprocess_mui_pro.py
```

4. Merge all csv to one file.

```
python3 log80_30_tofile.py
```

5. remove date 

```
cat 2020_3mlogs.txt | python3 rm_date.py
```

6. convert log to log keys

```
cat 2020_log_3m_rmdate | python3 drain_ldap_l.py
```

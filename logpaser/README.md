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

# LDAP Dataset Description

The LDAP dataset was collected from the unified authentication system of National Yang Ming Chiao Tung University with OpenLDAP, which is an open-source implementation of the Lightweight Directory Access Protocol (LDAP). This is a de-identification dataset. All IP Addresses and user IDs were anonymized. The collection period of testing data was from November 10, 2020 to January 1, 2021.

## Definition of one event
An event comprises single or multiple logs as the following example:

```
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 fd=8 ACCEPT from IP=192.168.0.1:51601 (IP=0.0.0.0:389)
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 op=0 BIND dn="cn=portal,ou=other,o=nctu" method=128
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 op=0 BIND dn="cn=portal,ou=other,o=nctu" mech=SIMPLE ssf=0
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 op=0 RESULT tag=97 err=0 text=
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 op=1 SRCH base="o=nctu" scope=2 deref=0 filter="(&(cn=0000000)(objectClass=person))"
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 op=1 SRCH attr=cn dn ou idno mail sn givenname hit
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 op=1 SEARCH RESULT tag=101 err=0 nentries=1 text=
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 op=2 UNBIND
Nov 10 15:59:23 proxy1 slapd[81950]: conn=69242 fd=8 closed
```

A LDAP log typically starts with "conn=XXX fd=X ACCEPT ..." and ends with "conn=XXX fd=X closed", where the value of conn indicates the event ID. 
The log parser then can be applied to encode an event to a log vector as shown as follows:

```
73704 1 2 1 1 3 4 4 5 5	0.
```

A log vector consists of three components that are event ID, log keys, and lable, where the label is one or zero to represent normal or anomaly event. In the above example, the event ID is "73704", log keys are "1 2 1 1 3 4 4 5 5", and the label is zero.

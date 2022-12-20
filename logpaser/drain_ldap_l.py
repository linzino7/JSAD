"""
Description : Example of using Drain3 with Kafka persistence
Author      : David Ohana, Moshik Hershcovitch, Eran Raichstein
Author_email: david.ohana@ibm.com, moshikh@il.ibm.com, eranra@il.ibm.com
License     : MIT
"""
import json
import logging
import sys

from drain3 import TemplateMiner


def pro_str(string):
    if 'conn=' in string:
        strs = string.split(' ')
        conn = strs[5].split('=')[1]
        return conn
    else:
        return None

# persistence_type = "NONE"
# persistence_type = "REDIS"
# persistence_type = "KAFKA"
persistence_type = "FILE"

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')

if persistence_type == "KAFKA":
    from drain3.kafka_persistence import KafkaPersistence

    persistence = KafkaPersistence("drain3_state", bootstrap_servers="localhost:9092")

elif persistence_type == "FILE":
    from drain3.file_persistence import FilePersistence

    persistence = FilePersistence("drain3_oneday_te.bin")

elif persistence_type == "REDIS":
    from drain3.redis_persistence import RedisPersistence

    persistence = RedisPersistence(redis_host='',
                                   redis_port=25061,
                                   redis_db=0,
                                   redis_pass='',
                                   is_ssl=True,
                                   redis_key="drain3_state_key")
else:
    persistence = None

template_miner = TemplateMiner(persistence)
print(f"Drain3 started with '{persistence_type}' persistence, reading from std-in (input 'q' to finish)")
idflog = True # if True write conn to file
with open('keys/logkeys_oneday_202010_te', 'w') as f:
    while True:
        try:
           log_line = input()
        except EOFError as e:
           print('[INFO]',e)
           break
        
        if log_line == 'q':
            break
        
        if log_line == '--new_conn--':
            f.write('\n')
            idflog = True
            continue

        if idflog:
            f.write(pro_str(log_line)+' ')
            idflog = False

        result = template_miner.add_log_message(log_line)
        f.write(str(result["cluster_id"])+' ')
        result_json = json.dumps(result)
        #print(result_json)

f.close()

print("Clusters:")
for cluster in template_miner.drain.clusters:
    print(cluster)

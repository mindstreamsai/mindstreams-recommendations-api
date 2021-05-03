foo = """
kinesis = boto3.client('kinesis', region_name = 'us-east-2')

shard_iterator = None

info = kinesis.describe_stream(StreamName = 'mindstreams-ingestion')
shard_ids = []
stream_name = None 
if info and 'StreamDescription' in info:
    stream_name = info['StreamDescription']['StreamName']                   
    for shard_id in info['StreamDescription']['Shards']:
         shard_id = shard_id['ShardId']
         print(shard_id)
         shard_iterator = kinesis.get_shard_iterator(StreamName=stream_name, ShardId=shard_id, ShardIteratorType='TRIM_HORIZON')
         shard_ids.append({'shard_id' : shard_id ,'shard_iterator' : shard_iterator['ShardIterator'] })


def GetRecords(shard_iterator):
    tries = 0
    result = []
    while tries < 100:
        tries += 1
        response = kinesis.get_records(ShardIterator = shard_iterator, Limit = 10)
        shard_iterator = response['NextShardIterator']
        if len(response['Records'])> 0:
            for res in response['Records']: 
                result.append(res['Data'])
            print()
            return result, shard_iterator
            print(result)


while shard_iterator:
    result, shard_iterator = GetRecords(shard_iterator)
    exit()
"""

GET /_search
{
   "size": 0,
   "aggs": {
      "stocksight": {
         "terms": {
            "field": "message.keyword",
            "include": {
               "partition": 0,
               "num_partitions": 20
            },
            "size": 10000,
            "order": {
               "last_access": "asc"
            }
         },
         "aggs": {
            "last_access": {
               "max": {
                  "field": "access_date"
               }
            }
         }
      }
   }
}


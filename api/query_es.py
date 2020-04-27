query_most_retweeted = {
    "aggs": {
        "top_tags": {
            "terms": {
                "field": "message.keyword",
                "size": 2000
            },
            "aggs": {
                "terms": {
                    "top_hits": {
                        "sort": [
                            {
                                "date": {
                                    "order": "desc"
                                }
                            }
                        ],
                        "_source": {
                            "includes": ["date", "message"]
                        },
                        "size": 1
                    }
                }
            }
        }
    }
}

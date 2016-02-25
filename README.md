WSP
===

Data Structure
---

### Task

```
{
	id: ObjectId,
	create_time: DateTime,
	finish_time: DateTime,
	is_running: Bool,
	desc: String,
	start_urls: List<String>,
	follow: {
		starts_with: List<String>,
		ends_with: List<String>,
		contains: List<String>,
		regex_matches: List<String>
	},
	check: List<{
		url: String,
		succ: String,
		deny: String
	}>,
	max_retry: UInt,
	custom_fetcher: String
}
```

### Request

```
{
	id: ObjectId,
	father_id: ObjectId,
	task_id: ObjectId,
	url: String,
	level: UInt,
	retry: UInt,
	proxy: String,
	raw_req: Pickle
}
```

### Response

```
{
	id: ObjectId,
	req_id: ObjectId,	
	task_id: ObjectId,
	url: String,
	html: String,
	http_code: UInt,
	error: String,
	raw_resp: Pickle
}
```

### Result_{task_id}

```
{
	id: ObjectId,
	req: Request,
	resp: Response
}
```

### Global

```
{
	kafka: String,
	mongo: String,
	agent: String,
	fetchers: List<String>
}
```

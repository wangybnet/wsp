WSP
===

Google Style Guide
---
<http://zh-google-styleguide.readthedocs.org/en/latest/google-python-styleguide/python_language_rules/>

Data Structures
---

### Task

```
{
	id: ObjectId,
	create_time: DateTime,
	finish_time: DateTime,
	status: {
		0: CREATED,
		1: RUNNING,
		2: STOPPED,
		3: FINISHED,
		4: REMOVED
	},
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
	fetcher: String,
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

### Config

```
{
	kafka: String,
	mongo: String,
	agent: String,
	fetchers: List<String>
}
```

Interfaces
---

### Fetcher

```
// RPC server and client
start(task_id ObjectId) 
stop(task_id ObjectId)
start_all() 
stop_all()
list()
```

#### Kafka

```
push(task_id ObjectId, req Request)
poll(task_id ObjectId)(req Request)
```

#### Master

```
// Task
create(task Task)(task_id ObjectId) 
delete(task_id ObjectId)
start(task_id ObjectId) 
stop(task_id ObjectId)
status(task_id ObjectId)
status_all()

// Master
status(config Config)
```

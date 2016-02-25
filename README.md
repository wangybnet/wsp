WSP
===

Data Structure
---

### Task

| Field | Type | Default |
| --- | --- | --- |
| id | ObjectId | - |
| create_time | DateTime | - | 
| finish_time | DateTime | - |
| is_running | Bool | False |
| desc | String | "" |
| start_urls | List< String> | [ ] |
| follow | _Follow | - |
| check | List< _Check> | - |
| max_retry | UInt | 0 |
| custom_fetcher | String | "" |

### _Follow

| Field | Type | Default |
| --- | --- | --- |
| starts_with | List< String> | [ ] |
| ends_with | List< String> | [ ] |
| contains | List< String> | [ ] |
| regex_matches | List< String> | [ ] |

### _Check

| Field | Type | Default |
| --- | --- | --- |
| rule | List< _Url, List< _Succ, _Deny> > | [ ] |

### Result_{task_id}

| Field | Type | Default |
| --- | --- | --- |
| req_id | ObjectId | - |
| req_father_id | ObjectId | - |
| resp_id | ObjectId | - |
| url | String | "" |
| level | UInt | 0 |
| html | String | "" |
| retry | UInt | 0 |
| proxy | String | "" |
| http_code | UInt | - |
| internal_error | String | "" |
| raw_req | _Pickle | - |
| raw_resp | _Pickle | - |

### Global

| Field | Type | Default |
| --- | --- | --- |
| kafka | _Addr | - |
| mongo | _Addr | - |
| agent | _Addr | - |
| fetchers | List< _Addr> | [ ] |

### _Url / _Succ / _Deny / _Pickle / _Addr => String

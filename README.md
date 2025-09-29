# Setup

I had splunk collector running locally. Using OpenTelemetry collector emitted errors about metrics not being implemented.

I ran ollama locally with model ollama/llama3.2:latest listening on port 11434, and had a personal openai key for testing.

## Clone the repository

```sh
git clone git@github.com:keith-decker/litellm-example.git
```

## Install requirements

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Copy environment file

```sh
cp .env.example .env
```

## Run the script (with dotenv)

```sh
dotenv run -- opentelemetry-instrument python opentelemetry_poem.py
```

## Or, set environment variables manually

```sh
LITELLM_OTEL_INTEGRATION_ENABLE_EVENTS=true \
LITELLM_OTEL_INTEGRATION_ENABLE_METRICS=true \
OTEL_EXPORTER_OTLP_PROTOCOL=grpc \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
opentelemetry-instrument python opentelemetry_poem.py
```



# Output

## Metrics

```
2025-09-29T11:01:21.510-0600	info	Metrics	{"resource": {}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "metrics", "resource metrics": 1, "metrics": 2, "data points": 3}
2025-09-29T11:01:21.511-0600	info	ResourceMetrics #0
Resource SchemaURL:
Resource attributes:
     -> telemetry.sdk.language: Str(python)
     -> telemetry.sdk.name: Str(opentelemetry)
     -> telemetry.sdk.version: Str(1.37.0)
     -> service.name: Str(litellm)
     -> deployment.environment: Str(production)
     -> model_id: Str(litellm)
ScopeMetrics #0
ScopeMetrics SchemaURL:
InstrumentationScope litellm.integrations.opentelemetry
Metric #0
Descriptor:
     -> Name: gen_ai.client.operation.duration
     -> Description: GenAI operation duration
     -> Unit: s
     -> DataType: Histogram
     -> AggregationTemporality: Delta
HistogramDataPoints #0
Data point attributes:
     -> gen_ai.operation.name: Str(chat)
     -> gen_ai.system: Str(ollama)
     -> gen_ai.request.model: Str(llama3.2:latest)
     -> gen_ai.framework: Str(litellm)
     -> metadata.applied_guardrails: Str([])
StartTimestamp: 2025-09-29 17:01:21.298495 +0000 UTC
Timestamp: 2025-09-29 17:01:21.29937 +0000 UTC
Count: 1
Sum: 6.181012
Min: 6.181012
Max: 6.181012
ExplicitBounds #0: 0.000000
ExplicitBounds #1: 5.000000
ExplicitBounds #2: 10.000000
ExplicitBounds #3: 25.000000
ExplicitBounds #4: 50.000000
ExplicitBounds #5: 75.000000
ExplicitBounds #6: 100.000000
ExplicitBounds #7: 250.000000
ExplicitBounds #8: 500.000000
ExplicitBounds #9: 750.000000
ExplicitBounds #10: 1000.000000
ExplicitBounds #11: 2500.000000
ExplicitBounds #12: 5000.000000
ExplicitBounds #13: 7500.000000
ExplicitBounds #14: 10000.000000
Buckets #0, Count: 0
Buckets #1, Count: 0
Buckets #2, Count: 1
Buckets #3, Count: 0
Buckets #4, Count: 0
Buckets #5, Count: 0
Buckets #6, Count: 0
Buckets #7, Count: 0
Buckets #8, Count: 0
Buckets #9, Count: 0
Buckets #10, Count: 0
Buckets #11, Count: 0
Buckets #12, Count: 0
Buckets #13, Count: 0
Buckets #14, Count: 0
Buckets #15, Count: 0
Metric #1
Descriptor:
     -> Name: gen_ai.client.token.usage
     -> Description: GenAI token usage
     -> Unit: {token}
     -> DataType: Histogram
     -> AggregationTemporality: Delta
HistogramDataPoints #0
Data point attributes:
     -> gen_ai.operation.name: Str(chat)
     -> gen_ai.system: Str(ollama)
     -> gen_ai.request.model: Str(llama3.2:latest)
     -> gen_ai.framework: Str(litellm)
     -> metadata.applied_guardrails: Str([])
     -> gen_ai.token.type: Str(input)
StartTimestamp: 2025-09-29 17:01:21.298553 +0000 UTC
Timestamp: 2025-09-29 17:01:21.29937 +0000 UTC
Count: 1
Sum: 77.000000
Min: 77.000000
Max: 77.000000
ExplicitBounds #0: 0.000000
ExplicitBounds #1: 5.000000
ExplicitBounds #2: 10.000000
ExplicitBounds #3: 25.000000
ExplicitBounds #4: 50.000000
ExplicitBounds #5: 75.000000
ExplicitBounds #6: 100.000000
ExplicitBounds #7: 250.000000
ExplicitBounds #8: 500.000000
ExplicitBounds #9: 750.000000
ExplicitBounds #10: 1000.000000
ExplicitBounds #11: 2500.000000
ExplicitBounds #12: 5000.000000
ExplicitBounds #13: 7500.000000
ExplicitBounds #14: 10000.000000
Buckets #0, Count: 0
Buckets #1, Count: 0
Buckets #2, Count: 0
Buckets #3, Count: 0
Buckets #4, Count: 0
Buckets #5, Count: 0
Buckets #6, Count: 1
Buckets #7, Count: 0
Buckets #8, Count: 0
Buckets #9, Count: 0
Buckets #10, Count: 0
Buckets #11, Count: 0
Buckets #12, Count: 0
Buckets #13, Count: 0
Buckets #14, Count: 0
Buckets #15, Count: 0
HistogramDataPoints #1
Data point attributes:
     -> gen_ai.operation.name: Str(chat)
     -> gen_ai.system: Str(ollama)
     -> gen_ai.request.model: Str(llama3.2:latest)
     -> gen_ai.framework: Str(litellm)
     -> metadata.applied_guardrails: Str([])
     -> gen_ai.token.type: Str(completion)
StartTimestamp: 2025-09-29 17:01:21.298573 +0000 UTC
Timestamp: 2025-09-29 17:01:21.29937 +0000 UTC
Count: 1
Sum: 230.000000
Min: 230.000000
Max: 230.000000
ExplicitBounds #0: 0.000000
ExplicitBounds #1: 5.000000
ExplicitBounds #2: 10.000000
ExplicitBounds #3: 25.000000
ExplicitBounds #4: 50.000000
ExplicitBounds #5: 75.000000
ExplicitBounds #6: 100.000000
ExplicitBounds #7: 250.000000
ExplicitBounds #8: 500.000000
ExplicitBounds #9: 750.000000
ExplicitBounds #10: 1000.000000
ExplicitBounds #11: 2500.000000
ExplicitBounds #12: 5000.000000
ExplicitBounds #13: 7500.000000
ExplicitBounds #14: 10000.000000
Buckets #0, Count: 0
Buckets #1, Count: 0
Buckets #2, Count: 0
Buckets #3, Count: 0
Buckets #4, Count: 0
Buckets #5, Count: 0
Buckets #6, Count: 0
Buckets #7, Count: 1
Buckets #8, Count: 0
Buckets #9, Count: 0
Buckets #10, Count: 0
Buckets #11, Count: 0
Buckets #12, Count: 0
Buckets #13, Count: 0
Buckets #14, Count: 0
Buckets #15, Count: 0
	{"resource": {}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "metrics"}
```


## Logs
```
2025-09-29T11:01:21.514-0600	info	Logs	{"resource": {}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "logs", "resource logs": 1, "log records": 3}
2025-09-29T11:01:21.515-0600	info	ResourceLog #0
Resource SchemaURL:
Resource attributes:
     -> telemetry.sdk.language: Str(python)
     -> telemetry.sdk.name: Str(opentelemetry)
     -> telemetry.sdk.version: Str(1.37.0)
     -> telemetry.auto.version: Str(0.58b0)
     -> service.name: Str(unknown_service)
ScopeLogs #0
ScopeLogs SchemaURL:
InstrumentationScope litellm
LogRecord #0
ObservedTimestamp: 2025-09-29 17:01:21.298611 +0000 UTC
Timestamp: 1970-01-01 00:00:00 +0000 UTC
SeverityText:
SeverityNumber: Unspecified(0)
Body: Map({"content":"You are a poetic assistant, skilled in crafting beautiful poems about technical topics.","role":"system"})
Attributes:
     -> event_name: Str(gen_ai.content.prompt)
     -> gen_ai.system: Str(ollama)
     -> gen_ai.prompt: Str(You are a poetic assistant, skilled in crafting beautiful poems about technical topics.)
Trace ID: ff36ae636599d185ed769efa1f2bd55b
Span ID: c06d85e2146fec6e
Flags: 1
LogRecord #1
ObservedTimestamp: 2025-09-29 17:01:21.298686 +0000 UTC
Timestamp: 1970-01-01 00:00:00 +0000 UTC
SeverityText:
SeverityNumber: Unspecified(0)
Body: Map({"content":"Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems.","role":"user"})
Attributes:
     -> event_name: Str(gen_ai.content.prompt)
     -> gen_ai.system: Str(ollama)
     -> gen_ai.prompt: Str(Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems.)
     
Trace ID: ff36ae636599d185ed769efa1f2bd55b
Span ID: c06d85e2146fec6e
Flags: 1
LogRecord #2
ObservedTimestamp: 2025-09-29 17:01:21.298719 +0000 UTC
Timestamp: 1970-01-01 00:00:00 +0000 UTC
SeverityText:
SeverityNumber: Unspecified(0)
Body: Map({"finish_reason":"stop","index":0,"message":{"content":"In realms of code, where data streams flow,\nA hero emerges, few may know.\nOpenTelemetry, an open heart,\nBeats with insight, a work of art.\n\nIt watches, listens, and reports back,\nThe whispers of the system's track.\nA web of sensors, far and wide,\nCollecting signs, the distributed tide.\n\nWith spans and traces, it paints the map,\nOf functions called, and paths they take.\nThrough fault lines deep, it finds the way,\nTo shed light on errors, night and day.\n\nIn observability's realm, it stands tall,\nA champion of visibility, for one and all.\nIt helps us navigate, the system's maze,\nAnd gives us tools to debug, in haste.\n\nWith OpenTelemetry, our eyes are wide,\nSeeing patterns, we never could divide.\nThe blind spots fade, as clarity dawns,\nOur systems sing, with fewer moans.\n\nIn the dark of night, when errors creep,\nOpenTelemetry shines, a guiding light to keep.\nIt's an ally true, in times of woe,\nA trusted friend, that helps our code grow.","role":"assistant"}})
Attributes:
     -> event_name: Str(gen_ai.content.completion)
     -> gen_ai.system: Str(ollama)
     -> index: Int(0)
     -> finish_reason: Str(stop)
     -> message.content: Str(In realms of code, where data streams flow,
A hero emerges, few may know.
OpenTelemetry, an open heart,
Beats with insight, a work of art.

It watches, listens, and reports back,
The whispers of the system's track.
A web of sensors, far and wide,
Collecting signs, the distributed tide.

With spans and traces, it paints the map,
Of functions called, and paths they take.
Through fault lines deep, it finds the way,
To shed light on errors, night and day.

In observability's realm, it stands tall,
A champion of visibility, for one and all.
It helps us navigate, the system's maze,
And gives us tools to debug, in haste.

With OpenTelemetry, our eyes are wide,
Seeing patterns, we never could divide.
The blind spots fade, as clarity dawns,
Our systems sing, with fewer moans.

In the dark of night, when errors creep,
OpenTelemetry shines, a guiding light to keep.
It's an ally true, in times of woe,
A trusted friend, that helps our code grow.)
Trace ID: ff36ae636599d185ed769efa1f2bd55b
Span ID: c06d85e2146fec6e
Flags: 1
	{"resource": {}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "logs"}
```



## Span
```
025-09-29T11:01:21.518-0600	info	Traces	{"resource": {}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "traces", "resource spans": 1, "spans": 2}
2025-09-29T11:01:21.518-0600	info	ResourceSpans #0
Resource SchemaURL:
Resource attributes:
     -> telemetry.sdk.language: Str(python)
     -> telemetry.sdk.name: Str(opentelemetry)
     -> telemetry.sdk.version: Str(1.37.0)
     -> telemetry.auto.version: Str(0.58b0)
     -> service.name: Str(unknown_service)
ScopeSpans #0
ScopeSpans SchemaURL:
InstrumentationScope litellm
Span #0
    Trace ID       : ff36ae636599d185ed769efa1f2bd55b
    Parent ID      :
    ID             : c06d85e2146fec6e
    Name           : litellm_request
    Kind           : Internal
    Start time     : 2025-09-29 17:01:15.017127936 +0000 UTC
    End time       : 2025-09-29 17:01:21.198139904 +0000 UTC
    Status code    : Ok
    Status message :
Attributes:
     -> metadata.user_api_key_hash: Str()
     -> metadata.user_api_key_alias: Str()
     -> metadata.user_api_key_spend: Str()
     -> metadata.user_api_key_max_budget: Str()
     -> metadata.user_api_key_budget_reset_at: Str()
     -> metadata.user_api_key_team_id: Str()
     -> metadata.user_api_key_org_id: Str()
     -> metadata.user_api_key_user_id: Str()
     -> metadata.user_api_key_team_alias: Str()
     -> metadata.user_api_key_user_email: Str()
     -> metadata.user_api_key_end_user_id: Str()
     -> metadata.user_api_key_request_route: Str()
     -> metadata.spend_logs_metadata: Str()
     -> metadata.requester_ip_address: Str()
     -> metadata.requester_metadata: Str()
     -> metadata.prompt_management_metadata: Str()
     -> metadata.applied_guardrails: Str([])
     -> metadata.mcp_tool_call_metadata: Str()
     -> metadata.vector_store_request_metadata: Str()
     -> metadata.usage_object: Str({'completion_tokens': 230, 'prompt_tokens': 77, 'total_tokens': 307, 'completion_tokens_details': None, 'prompt_tokens_details': None})
     -> metadata.requester_custom_headers: Str()
     -> metadata.cold_storage_object_key: Str()
     -> gen_ai.request.model: Str(llama3.2:latest)
     -> llm.request.type: Str(completion)
     -> gen_ai.system: Str(ollama)
     -> llm.is_streaming: Str(False)
     -> gen_ai.response.id: Str(chatcmpl-25885f01-6b30-47d5-b7d9-12dc48dd5e1a)
     -> gen_ai.response.model: Str(ollama/llama3.2:latest)
     -> llm.usage.total_tokens: Int(307)
     -> gen_ai.usage.completion_tokens: Int(230)
     -> gen_ai.usage.prompt_tokens: Int(77)
     -> gen_ai.prompt.0.role: Str(system)
     -> gen_ai.prompt.0.content: Str(You are a poetic assistant, skilled in crafting beautiful poems about technical topics.)
     -> gen_ai.prompt.1.role: Str(user)
     -> gen_ai.prompt.1.content: Str(Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems.)
     -> gen_ai.completion.0.finish_reason: Str(stop)
     -> gen_ai.completion.0.role: Str(assistant)
     -> gen_ai.completion.0.content: Str(In realms of code, where data streams flow,
A hero emerges, few may know.
OpenTelemetry, an open heart,
Beats with insight, a work of art.

It watches, listens, and reports back,
The whispers of the system's track.
A web of sensors, far and wide,
Collecting signs, the distributed tide.

With spans and traces, it paints the map,
Of functions called, and paths they take.
Through fault lines deep, it finds the way,
To shed light on errors, night and day.

In observability's realm, it stands tall,
A champion of visibility, for one and all.
It helps us navigate, the system's maze,
And gives us tools to debug, in haste.

With OpenTelemetry, our eyes are wide,
Seeing patterns, we never could divide.
The blind spots fade, as clarity dawns,
Our systems sing, with fewer moans.

In the dark of night, when errors creep,
OpenTelemetry shines, a guiding light to keep.
It's an ally true, in times of woe,
A trusted friend, that helps our code grow.)
Span #1
    Trace ID       : ff36ae636599d185ed769efa1f2bd55b
    Parent ID      : c06d85e2146fec6e
    ID             : 0354fb8c7d42e130
    Name           : raw_gen_ai_request
    Kind           : Internal
    Start time     : 2025-09-29 17:01:15.017127936 +0000 UTC
    End time       : 2025-09-29 17:01:21.198139904 +0000 UTC
    Status code    : Ok
    Status message :
Attributes:
     -> llm.ollama.model: Str(llama3.2:latest)
     -> llm.ollama.prompt: Str(### System:
You are a poetic assistant, skilled in crafting beautiful poems about technical topics.

### User:
Write a short, creative poem about OpenTelemetry, the open-source observability framework. Focus on its ability to provide insights and visibility into distributed systems.

)
     -> llm.ollama.options: Str({})
     -> llm.ollama.stream: Bool(false)
     -> llm.ollama.images: Str([])
	{"resource": {}, "otelcol.component.id": "debug", "otelcol.component.kind": "exporter", "otelcol.signal": "traces"}
```

# FR-Script Documentation

The **Filtering & Ruling Script** facilitates advanced topic filtering based on user-defined conditions and enables the publishing of payloads on newly generated subtopics. It empowers users to selectively filter and process topics based on condition evaluations, allowing for the publication of modified or original payloads on the resulting subtopics when the conditions yield true.
Furthermore, the script empowers users to create rules by performing logical operations on defined conditions across multiple topics. This functionality allows for the combination of payloads from the aforementioned topics, enabling the publishing of new payloads or the merged payloads onto a freshly created topic, contingent upon the evaluation of the logical operations.
By leveraging the Filtering & Ruling Script, users gain granular control over topic filtering and payload publication, while the rule-based operations provide flexible processing capabilities across various topics, fostering efficient data management and topic-based decision-making.

In order for the fr_script to operate the user should provide relevant filters and rules corresponding to different use cases (scenarios). Please read carefully the instructions and examples below.

The filters and rules should be provided in json format. GET, POST, PATCH, DELETE HTTP Methods can be used to fetch, post, update and delete json objects via an API respectively. The APIs can get accessed on given nodePort. Use endpoint `/docs#/` for accessing swgger UI.

![Capture](/uploads/df4bbb09d3ffe8bce6691224f337d86e/Capture.PNG)

The _json_ consists of two parts.

```console
{
	“filters”: [],
	“rules”: []
}
```
Witch both contains an array of objects.

## Filters

For the filtering, the MQTT **topic** which the user wants to filter is required. It consists of one or more topic levels and can contain `“#”` and `“+”` wildcard as well.

A **subtopic** is also required. It will get appended to the topic that is being filtered and create the new topic in which the filtered messages will be published. This can also consist one or more topic levels.

After setting the topic and subtopic of the filter, **statements** also need to get defined. Statements is an array of objects. Every statement consists of two components, a **condition** and a **new_payload**.
A condition takes as value the same thing that an if statement expression would. Variables, values, comparison operators, logical operators and parenthesis, to set the priority of the operations. **NOTE**: Use spaces between every instance of the condition.

The variables should exist as key values in the json message sent to the topic that is being filtered. In the json file with the filters and rules that the user provides, those same variables should start with the `$` sign, followed by their name. If the filtered json message has nested objects, the parent variable comes after the `$` sign, followed by a dot `.` and then the child variable. **Example**: `$parent.child`

The **new_payload** takes as value a `string` value or `""`. The new_payload’s value is the new message that will be published at the newlly set filtered topic. If the new_payload’s value is `""` and the statements condition is met, the initial message of the filtered topic will be sent. 

### Example

Let’s say we have a number of houses in a smart city. There are sensors installed inside and outside of those houses that generate data like the json below.

```
{"h_id":1,"inside":{"temperature":35,"humidity":60},"temperature":43,"wind_speed":34}
```

The sensors of every house publish their data in a topic like `house/1`,`house/2`, etc.

The team that inspects and monitors the smart city wants to receive the sensor’s data only when those exceed some threshold and not all of them, so they subscribe on the topic `house/+/alert/` (`“+”` is a single-level wildcard that matches any name for a specific topic level.) and use the json below to set the rules for the filtering of the data being published on 
`house/#`.

```
{
    "filters": [
        {
            "topic": "house/#",
            "subtopic": "alert/",
            "statements": [
                {
                    "condition": "( $inside.temperature < 20 and $inside.humidity >= 60 ) or $temperature < 5",
                    "new_payload": ""
                },
                {
                    "condition": "$inside.temperature >= 45 and $inside.humidity <= 15",
                    "new_payload": "fire_danger"
                }
            ]
        }
    ],
    "rules": []
}
```

The messages below published by the sensors of houses 1,2 and 3 in topics `house/1`, `house/2` and `house/3` respectively.

```
{"h_id":1,"inside":{"temperature":50,"humidity":6},"temperature":8,"wind_speed":34}
{"h_id":2,"inside":{"temperature":15,"humidity":60},"temperature":8,"wind_speed":34}
{"h_id":3,"inside":{"temperature":22,"humidity":55},"temperature":8,"wind_speed":35}
```
And the monitoring team’s client that was subscribed to the topic `house/+/alert/` got the messages:
```
house/1/alert/--> b'fire_danger'
house/2/alert/--> b'{"h_id":2,"inside":{"temperature":15,"humidity":60},"temperature":8,"wind_speed":34}'
```

## Rules

In the rules part of fr_script, every rule consists of two parts.

```
{
	“filters”: [],
	“rules”: [
		“statements”: [],
		“logic”: []
    ]
}
```
**statements** and **logic** witch both contains an array of objects.

The **statements** are situated very similar to the filters.
Every statement consists of the MQTT **topic** that the user wants to apply rules against, the **condition** which work exactly like the conditions in filtering, an **id** unique for every statement and the **payload type** of the messages’ fields sent to the above defined topic and are used as variables in our condition. Those can be `int`, `float`, `str`, `bool`.

Every instance in logic array consist of the logical **operations** which constitute the essence of the ruling part of the script, the newly created topic **new_topic** and the **payload** that would be published in it only if the logical operations return true.

### Example

Let’s say we are managers in a mine. We have sensors inside the mine monitoring its environment as well as biometric sensors on every miner. The sensors monitoring mine’s environment produces messages like the json below:
```
{“temperature”: 25, “humidity”: 90}
```
and publish them in `mine/environment` topic.
The miners’ biometric sensors produce messages like:
```
{“m_id”:1, “body-temperature”: 36.6, “heart-rate”: 80}
```
And publish their data in a topic like `miner/1`, `miner/2`, etc.

So as managers we want to apply the following rules to monitor the miners’ wellbeing.

- If miner’s heart rate is between 100-120 and the mine’s temperature is above 35 or the humidity is above 85 the miner should rest.

- If miner’s body temperature is above 38 degrees and the mine’s temperature is above 30 the miner should leave.

- If miner’s heart rate is 0 the miner is dead.

The fr_script should be as follows:

```
{
	“filters”: [],
	“rules”: [
		{
            "statements": [
                {   
                    "id": 1,
                    "topic": "miner/#",
                    "payload_type": "float",
                    "condition": "$heart-rate >= 100 and $heart-rate <= 120"
                },
                {
                    "id": 2,
                    "topic": "mine/environment",
                    "payload_type": "int",
                    "condition": "$temperature > 35 or $humidity > 85"
                }
            ],
            "logic": [
                {
                    "operations": "( $1 ) and ( $2 )",
                    "new_topic": "action/rest",
                    "new_payload": ""
                }
            ]
        },
        {
            "statements": [
                {   
                    "id": 3,
                    "topic": "miner/#",
                    "payload_type": "float",
                    "condition": "$body-temperature > 38"
                },
                {
                    "id": 4,
                    "topic": "mine/environment",
                    "payload_type": "int",
                    "condition": "$temperature > 30"
                }
            ],
            "logic": [
                {
                    "operations": "$3 and $4",
                    "new_topic": "action/leave",
                    "new_payload": ""
                }
            ]
        },
        {
            "statements": [
                {   
                    "id": 5,
                    "topic": "miner/#",
                    "payload_type": "float",
                    "condition": "$heart-rate == 0"
                }
            ],
            "logic": [
                {
                    "operations": "$5",
                    "new_topic": "action/dead",
                    "new_payload": ""
                }
            ]
        }
    ]
}
```

The messages below published by the sensors on the workers’ 1 and workers’ 2 equipment as well as sensors on the mine itself. Our topics are `miner/1`, `miner/2` and `mine/environment` respectively and the messages are published in the order shown bellow.
```
{"m_id":1, "body-temperature": 36.6, "heart-rate": 105}
```
to topic `miner/1`
```
{"m_id":2, "body-temperature": 38.6, "heart-rate": 75}
```
to topic `miner/2`
```
{"temperature": 35, "humidity": 90}
```
to topic `mine/environment`

```
{"m_id":1, "body-temperature": 16.6, "heart-rate": 0}
```
to topic `miner/1`

The monitoring team’s client that was subscribed to the topic `!action` will get the messages:
```
!action/rest--> "{'miner/1': {'m_id': 1, 'body-temperature': 39.6, 'heart-rate': 105}, 'mine/environment': {'temperature': 35, 'humidity': 90}}"
```
```
!action/leave--> "{'miner/2': {'m_id': 2, 'body-temperature': 38.6, 'heart-rate': 75}, 'mine/environment': {'temperature': 35, 'humidity': 90}}"
```
*(Just after the message sent to topic mine/environment)*
```
!action/dead--> "{'miner/1': {'m_id': 1, 'body-temperature': 16.6, 'heart-rate': 0}}"
```
**NOTE**: If the messages were sent in a different order like bellow: 
```
{"m_id":1, "body-temperature": 36.6, "heart-rate": 105}
```
to topic `miner/1`
```
{"temperature": 35, "humidity": 90}
```
to topic `mine/environment`
```
{"m_id":2, "body-temperature": 38.6, "heart-rate": 75}
```
to topic `miner/2`
```
{"m_id":1, "body-temperature": 16.6, "heart-rate": 0}
```
to topic `miner/1`

And the monitoring team’s client that was subscribed to the topic `!action` will get the messages:
```
!action/rest--> "{'miner/1': {'m_id': 1, 'body-temperature': 39.6, 'heart-rate': 105}, 'mine/environment': {'temperature': 35, 'humidity': 90}}"
```
```
!action/dead--> "{'miner/1': {'m_id': 1, 'body-temperature': 16.6, 'heart-rate': 0}}"
```

This happens because when a logical operation comes True in fr_script’s rules and a new message is sent, the array holding the messages previously sent to fr_script, empty itself.

Lastly as we can see when `“new_payload”: “”` the new payload generated by fr_script is a json with the topic(s) used in the logic’s operations and their payload(s). Topics created by fr_script will always start with `“!”` as shown above.

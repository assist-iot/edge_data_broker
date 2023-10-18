# EDB

## Edge Data Broker (EDB) Enabler

### To install the chart with the release name `edbe`:

Clone the repository to your machine.

Install Edge Data Broker Enabler.

```console
$ helm install edbe ./edgedatabroker
```

The command deploys EDB on the Kubernetes cluster in the default configuration.

To check if the installation was successful run:

```console
$ kubectl get pods
```

The result should show something like:

```console
NAME                                               READY   STATUS    RESTARTS   AGE
edbe-edgedatabroker-frscript-6468497fbf-c72dt      1/1     Running   0          2m58s
edbe-edgedatabroker-mqttexplorer-69659d465-q6ff2   1/1     Running   0          2m58s
edbe-edgedatabroker-vernemq-0                      1/1     Running   0          2m58s
edbe-edgedatabroker-vernemq-1                      1/1     Running   0          2m56s
```

### Edge Data Broker works for both Ubuntu x64 and ARM architectures.

Use `gitlab.assist-iot.eu:5050/enablers-registry/public/edb/vernemq-arm` and `gitlab.assist-iot.eu:5050/enablers-registry/public/edb/frscript-arm` images for deploying EDBE in ARM architectures. 

**Note**: Disable mqttexplorer when deploying EDBE in ARM architectures.

Use `vernemq/vernemq` (official vernemq image) and `gitlab.assist-iot.eu:5050/enablers-registry/public/edb/frscript-ubuntu` images for deploying EDBE in Ubuntu x64 architectures. 

**Note**: Add `DOCKER_VERNEMQ_ACCEPT_EULA: "yes"` as an environmental variable when using the official vernemq image.

### SSL Configuration for secure communication (Enable MQTTS).

Accepting SSL connections on port 8883:

- Set the parameter service.ports.mqtts.enabled=true

- Create secret resource using existing certificates
Using the key and crt files, you can create a secret. Kubernetes stores these files as a base64 string, so the first step is to encode them.

```
$ cat ca.crt| base64
LS0tLS1CRUdJTiBDRVJUSUZJQ...CBDRVJUSUZJQ0FURS0tLS0t
$ cat tls.crt | base64
LS0tLS1CRUdJTiBDRVJUSUZJQ...gQ0VSVElGSUNBVEUtLS0tLQo=
$ cat tls.key | base64
LS0tLS1CRUdJTiBSU0EgUFJJV...gUFJJVkFURSBLRVktLS0tLQo=
```
- Use `vernemq-certificates-secret.yaml` to create the secret resource by updating the data values.
```
apiVersion: v1
kind: Secret
metadata:
  name: vernemq-certificates-secret
  namespace: default
type: kubernetes.io/tls
data:
  ca.crt:LS0tLS1CRUdJTiBDRVJUSUZJQ...CBDRVJUSUZJQ0FURS0tLS0t
  tls.crt:LS0tLS1CRUdJTiBDRVJUSUZJQ...gQ0VSVElGSUNBVEUtLS0tLQo=
  tls.key:LS0tLS1CRUdJTiBSU0EgUFJJV...gUFJJVkFURSBLRVktLS0tLQo=
```
```console
kubectl apply -f vernemq-certificates-secret.yaml
```
The result should show something like:
`secret "vernemq-certificates-secret" created`

- Mount the certificate secret inside the EDBE's Vernemq values.
```
...
secretMounts:
  - name: vernemq-certificates
    secretName: vernemq-certificates-secret
    path: /etc/ssl/vernemq
...
```

- Add as environmental variables the following:

```
DOCKER_VERNEMQ_LISTENER__SSL__CAFILE: "/etc/ssl/vernemq/tls.crt"
DOCKER_VERNEMQ_LISTENER__SSL__CERTFILE: "/etc/ssl/vernemq/tls.crt"
DOCKER_VERNEMQ_LISTENER__SSL__KEYFILE: "/etc/ssl/vernemq/tls.key"
DOCKER_VERNEMQ_LISTENER__SSL__DEFAULT: "0.0.0.0:8883"
```

For more info regarding self-signed certificates please check [self-signed-certificates.md](https://gitlab.assist-iot.eu/wp4/data-mgmt/edbe/-/blob/main/self-signed-certificates.md)

### To nable PostgreSQL authentication and authorization (integration with LTSE).

- Add as environmental variables the following:
```
DOCKER_VERNEMQ_PLUGINS__VMQ_DIVERSITY: "on"
DOCKER_VERNEMQ_PLUGINS__VMQ_PASSWD: "off"
DOCKER_VERNEMQ_PLUGINS__VMQ_ACL: "off"
DOCKER_VERNEMQ_VMQ_DIVERSITY__AUTH_POSTGRES__ENABLED: "on"
DOCKER_VERNEMQ_VMQ_DIVERSITY__POSTGRES__HOST: "<IP>"
DOCKER_VERNEMQ_VMQ_DIVERSITY__POSTGRES__PORT: "<PORT>"
DOCKER_VERNEMQ_VMQ_DIVERSITY__POSTGRES__USER: "<DATABASE_USER>"
DOCKER_VERNEMQ_VMQ_DIVERSITY__POSTGRES__PASSWORD: "<DATABASE_PASSWORD>"
DOCKER_VERNEMQ_VMQ_DIVERSITY__POSTGRES__DATABASE: "<DATABASE>"
DOCKER_VERNEMQ_VMQ_DIVERSITY__POSTGRES__PASSWORD_HASH_METHOD: "crypt"
```

- Create the Postgres tables
```
CREATE EXTENSION pgcrypto;
CREATE TABLE vmq_auth_acl
 (
   mountpoint character varying(10) NOT NULL,
   client_id character varying(128) NOT NULL,
   username character varying(128) NOT NULL,
   password character varying(128),
   publish_acl json,
   subscribe_acl json,
   CONSTRAINT vmq_auth_acl_primary_key PRIMARY KEY (mountpoint, client_id, username)
 );
```

- Enter new users and Access Control List entries using a query similar to the following
```
WITH x AS (
    SELECT
        ''::text AS mountpoint,
           'test-client'::text AS client_id,
           'test-user'::text AS username,
           '123'::text AS password,
           gen_salt('bf')::text AS salt,
           '[{"pattern": "a/b/c"}, {"pattern": "c/b/#"}]'::json AS publish_acl,
           '[{"pattern": "a/b/c"}, {"pattern": "c/b/#"}]'::json AS subscribe_acl
    )
INSERT INTO vmq_auth_acl (mountpoint, client_id, username, password, publish_acl, subscribe_acl)
    SELECT
        x.mountpoint,
        x.client_id,
        x.username,
        crypt(x.password, x.salt),
        publish_acl,
        subscribe_acl
    FROM x;
```
### To make the two VerneMQ nodes (edbe-0, edbe-1) run as a singular cluster, you'll need to join one node to the other like this:

- Connect to a shell of a running container within Kubernetes pod (edbe-0 or edbe-1).

```console
$ kubectl exec -it edbe-edgedatabroker-vernemq-0 -- /bin/bash
```

- Check the cluster state (you should see a 1 node cluster):

```console
$ vmq-admin cluster show
```

The result should show something like:

```console
+--------------------+---------+
| Node               | Running |
+--------------------+---------+
| VerneMQ@10.1.6.252 | true    |
+--------------------+---------+
```

- Join one node to the other with:

```console
$ vmq-admin cluster join discovery-node=<OtherClusterNode>
```

- Check the cluster state (you should see a 2 node cluster):

```console
$ vmq-admin cluster show
```

The result should show something like:

```console
+--------------------+---------+
| Node               | Running |
+--------------------+---------+
| VerneMQ@10.1.7.1   | true    |
+--------------------+---------+
| VerneMQ@10.1.6.252 | true    |
+--------------------+---------+
```
### To create an MQTT bridge so Edge Data Broker Enabler can interface with other brokers (and itself).

- Add as environmental variables the following:

```
DOCKER_VERNEMQ_PLUGINS__VMQ_BRIDGE: "on"
DOCKER_VERNEMQ_VMQ_BRIDGE__TCP__BR0: "<IP>:<PORT>"
DOCKER_VERNEMQ_VMQ_BRIDGE__TCP__BR0__TOPIC__1: "* in"
```

`DOCKER_VERNEMQ_VMQ_BRIDGE__TCP__BR0__TOPIC__#` Define the topics the bridge should incorporate in its local topic tree (by subscribing to the remote), or the topics it should export to the remote broker. The configuration syntax is:

```console
topic [[ out | in | both ] qos-level]
```
topic defines a topic pattern that is shared between the two brokers. Any topics matching the pattern (which may include wildcards) are shared. The second parameter defines the direction that the messages will be shared in, so it is possible to import messages from a remote broker using in, export messages to a remote broker using out or share messages in both directions. If this parameter is not defined, VerneMQ defaults to out. The QoS level defines the publish/subscribe QoS level used for this topic and defaults to 0.
**NOTE**: Currently the # wildcard is treated as a comment from the configuration parser, please use * instead.

- Check the bridge state

```console
$ vmq-admin bridge show
```
The result should show something like:

```console
+------+-----------------+-------------+------------+---------------------+--------------------------+
| name | endpoint        | buffer size | buffer max | buffer dropped msgs | MQTT process mailbox len |
+------+-----------------+-------------+------------+---------------------+--------------------------+
| br0  | 10.42.0.1:31094 | 0           | 0          | 0                   | 0                        |
+------+-----------------+-------------+------------+---------------------+--------------------------+
```

### To monitor Edge Data Broker Enabler, type to your browser:

`http://<IP>:<NodePort>/status` to get EDBE's status page.

`http://<IP>:<NodePort>/metrics` to get EDBE's metrics page made for Performance and Usage Diagnosis Enabler's consumption.

### To access Filtering and Ruling Script's API type to your browser:

`http://<IP>:<NodePort>/docs` and fr-script's Swagger page will open up, where you can fetch, post, update and delete filters and rules.

For more info regarding FR-Script please check [FR-Script's Documentation](https://gitlab.assist-iot.eu/wp4/data-mgmt/edbe/-/blob/main/FR-Script.md)
### To use fr-script over SSL: 

- Mount the certificate secret inside EDBE's FR-Script values.
```
...
secretMounts:
  - name: vernemq-certificates
    secretName: vernemq-certificates-secret
    path: /etc/ssl/frscript
...
```

- Add as environmental variables the following:

```
VERNEMQ_PORT: "8883"
FR_SCRIPT_SSL_ENABLED: "True"
```

### To enable `client-id`, `username` and `password` for fr-script add as environmental variables the following:

```
FR_SCRIPT_CLIENT_ID: "<client-id>"
FR_SCRIPT_USERNAME: "<username>"
FR_SCRIPT_PASSWORD: "<password>"
```

### To use MQTT-Explorer:

**NOTE**: MQTT-Explorer works for Ubuntu x64 architectures and not for ARM. When deploying EDBE in ARM architectures, set the parameter `mqttexplorer.enabled=false`.

- Set the parameter `service.ports.ws.enabled=true`

- Add as environmental variable the following:

```
DOCKER_VERNEMQ_LISTENER__WS__DEFAULT: "0.0.0.0:9001"
```

- Type to your browser `http://<IP>:<NodePort>/`

- Insert the correct `NodePort` in the Port field, `mqtt` in Basepath filed and press CONNECT.

- If `DOCKER_VERNEMQ_ALLOW_ANONYMOUS: "off"` in EDBE's Vernemq environmental variables, also insert `Username`, `Password` in the corresponding fields and change the `Client ID` in the ADVANCED options.

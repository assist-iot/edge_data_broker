## Using self-signed certificates with Edge Data Broker (EDB) Enabler.

### Step-by-step instructions

- Generate public and private RSA keypair for CA:

```console
openssl genrsa -out vernemq_ca.key 2048
```

- Create CA certificate:

```console
openssl req -new -x509 -days 3650 -key vernemq_ca.key -out vernemq_ca.crt
```

- Create VerneMQ keypair:

```console
openssl genrsa -out vernemq.key 2048
```

- Create certificate request from CA:

```console
openssl req -new -out vernemq.csr -key vernemq.key
```

- Verify and sign the certificate request: create cert.cnf, edit values (names, DNS and IPs) and run command:

```console
[ req ]
default_bits       = 2048
default_md         = sha512
default_keyfile    = vernemq.key
prompt             = no
encrypt_key        = no
distinguished_name = req_distinguished_name

[ req_distinguished_name ]
countryName                 = GR
stateOrProvinceName         = Attica
localityName               = Athens
organizationName           = iccs
commonName                 = isense

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1   = localhost
IP.1 = 127.0.0.1
```

```console
openssl x509 -req -in vernemq.csr -CA vernemq_ca.crt -CAkey vernemq_ca.key -CAcreateserial -extensions req_ext -extfile cert.cnf -out vernemq.crt -days 3650
```

- To check if values of alternative names are generated valid use:

```console
openssl x509 -text -noout -in vernemq.crt -certopt no_subject,no_header,no_version,no_serial,no_signame,no_validity,no_issuer,no_pubkey,no_sigdump,no_aux
```

- Kubernetes stores these files as a base64 string, so the first step is to encode them.

```console
cat vernemq_ca.crt| base64
LS0tLS1CRUdJTiBDRVJUSUZJQ...CBDRVJUSUZJQ0FURS0tLS0t
cat vernemq.crt | base64
LS0tLS1CRUdJTiBDRVJUSUZJQ...gQ0VSVElGSUNBVEUtLS0tLQo=
cat vernemq.key | base64
LS0tLS1CRUdJTiBSU0EgUFJJV...gUFJJVkFURSBLRVktLS0tLQo=
```

- Use `vernemq-certificates-secret.yaml` to create the secret resource by updating the data values.

```console
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

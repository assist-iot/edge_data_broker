FROM erlang:21.3.8.24-slim

RUN apt-get update && \
    apt-get -y install bash procps openssl iproute2 curl jq nano apt-utils && \
    apt-get -y install build-essential git gnupg2 libssl-dev net-tools && \
    addgroup --gid 10000 vernemq && \
    adduser --uid 10000 --system --ingroup vernemq --home /vernemq --disabled-password vernemq

# Defaults
ENV DOCKER_VERNEMQ_KUBERNETES_LABEL_SELECTOR="app=vernemq" \
    DOCKER_VERNEMQ_LOG__CONSOLE=console \
    PATH="/vernemq/bin:$PATH" \
    VERNEMQ_VERSION="1.11.0"

RUN git clone --depth 1 --branch $VERNEMQ_VERSION https://github.com/erlio/vernemq.git vernemq-src
WORKDIR /vernemq-src

# ugly hack
RUN make rpi32 || true
WORKDIR /vernemq-src/_build/rpi32/lib/eleveldb/c_src
RUN rm -rf snappy-1.0.4 && tar -xzf snappy-1.0.4.tar.gz
COPY files/config.guess snappy-1.0.4/config.guess
COPY files/config.sub snappy-1.0.4/config.sub
RUN tar cfvz snappy-1.0.4.tar.gz snappy-1.0.4 && rm -rf snappy-1.0.4
WORKDIR /vernemq-src

# ugly hack 2
RUN make rpi32 || true
WORKDIR /vernemq-src/_build/rpi32/lib/eleveldb/c_src/leveldb
RUN rm build_config.mk && \
    sed -i'' -e 's/cstdatomic/atomic/' build_detect_platform port/atomic_pointer.h && \
    sed -i'' -e 's/.*moved below/#include <atomic>/' port/atomic_pointer.h
WORKDIR /vernemq-src

RUN make rpi32 && \
    mv -v _build/rpi32/rel/vernemq/* /vernemq/

WORKDIR /vernemq
RUN rm -rf /vernemq-src /root/.cache/rebar3

COPY --chown=10000:10000 bin/vernemq.sh /usr/sbin/start_vernemq
COPY --chown=10000:10000 files/vm.args /vernemq/etc/vm.args

RUN chown -R 10000:10000 /vernemq && \
    ln -s /vernemq/etc /etc/vernemq && \
    ln -s /vernemq/data /var/lib/vernemq && \
    ln -s /vernemq/log /var/log/vernemq

RUN chmod a+x /usr/sbin/start_vernemq

# Ports
# 1883  MQTT
# 8883  MQTT/SSL
# 8080  MQTT WebSockets
# 44053 VerneMQ Message Distribution
# 4369  EPMD - Erlang Port Mapper Daemon
# 8888  Prometheus Metrics
# 9100 9101 9102 9103 9104 9105 9106 9107 9108 9109  Specific Distributed Erlang Port Range

EXPOSE 1883 8883 8080 44053 4369 8888 \
       9100 9101 9102 9103 9104 9105 9106 9107 9108 9109

VOLUME ["/vernemq/log", "/vernemq/data", "/vernemq/etc"]

HEALTHCHECK CMD vernemq ping | grep -q pong

USER vernemq

CMD ["start_vernemq"]


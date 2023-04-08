FROM python:3.9.0-slim

ARG PACKAGE_NAME
ARG FORWARD_PACKAGE_NANME

COPY $FORWARD_PACKAGE_NANME /usr/share/kubevision
COPY $PACKAGE_NAME /tmp
COPY pip.conf /tmp
COPY requirements.txt /tmp

RUN mkdir -p ~/.pip/ \
    && mv /tmp/pip.conf ~/.pip \
    && python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/requirements.txt \
    && python -m pip install /tmp/$PACKAGE_NAME \
    && rm -rf /tmp/$PACKAGE_NAME /tmp/requirements.txt \
    && python -m pip cache purge
RUN mkdir -p /etc/vstackboard && touch /etc/vstackboard/vstackboard.conf

EXPOSE 8091

ENTRYPOINT [ "kubevision", "serve", "--container", "--static", "/usr/share/kubevision/static", "--template", "/usr/share/kubevision"]

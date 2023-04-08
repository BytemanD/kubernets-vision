FROM registry.centos.org/centos:8

ARG PACKAGE_NAME

COPY ${PACKAGE_NAME} /tmp/${PACKAGE_NAME}
COPY pip.conf /tmp/pip.conf
COPY CentOS-8-ali.repo /tmp/
COPY requirements.txt /tmp/requirements.txt

RUN mkdir -p ~/.pip/ && mv /tmp/pip.conf ~/.pip \
    && mkdir -p /etc/yum.repos.d/backup \
    && mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/backup \
    && mv /tmp/CentOS-8-ali.repo /etc/yum.repos.d
RUN yum install -y python39 python39-pip \
    && pip3 install pip --upgrade \
    && pip3 install -r /tmp/requirements.txt \
    && pip3 install /tmp/$PACKAGE_NAME && rm -rf /tmp/$PACKAGE_NAME
RUN mkdir -p /etc/kubevision \
    && touch /etc/kubevision/kubevision.conf /etc/kubevision/hosts
RUN pip3 cache purge || true \
    && yum clean all

EXPOSE 80

ENTRYPOINT [ "kubevision", "serve", "--container"]

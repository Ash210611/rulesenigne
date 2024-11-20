
#===============================================================================
FROM registry.cigna.com/redhat/python-39-ubi8:latest

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

USER 0

WORKDIR /tmp

ARG UNAME=jenkins
ARG USER=jenkins
ARG GROUP=jenkins
ARG UID=42531
ARG GID=3231

ENV HOME="/home/${USER}"
#ENV PATH="${HOME}/.local/bin:${HOME}/.bin:${HOME}/.please:${PATH}"
RUN mkdir -p "${HOME}/.jenkins" "${HOME}/.bin" "${HOME}/agent" "${HOME}/.local/bin" "/run/containers" "/run/user/${UID}"
RUN mkdir -p "${HOME}/.cache" "${HOME}/rules_engine"

# Add certificates
COPY build_image/certs/*pem /etc/pki/ca-trust/source/anchors/
COPY build_image/certs/*crt /etc/pki/ca-trust/source/anchors/
RUN update-ca-trust && rm -rf certfix
RUN yum -y install yum-utils

COPY scripts/adhoc-perms /usr/local/bin/adhoc-perms
RUN chmod +x /usr/local/bin/adhoc-perms
RUN chmod 777 /usr/local/bin /etc/passwd

# steve start
RUN sed -i 's/gpgcheck=1/gpgcheck=0/g' /etc/yum.conf 				\
    && ls -la /etc/yum.repos.d 							\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && cat /etc/yum.repos.d/ubi.repo						\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum repolist 								\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && touch /var/lib/rpm/* 							\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum -y remove httpd							\
    && yum -y update 								\
    && yum -y install which gzip tar unzip 					\
    		git bzip2-devel dos2unix unix2dos openssl-devel libgcc 		\
		libstdc++ unixODBC-devel pkgconfig bc 				\
    && printf "%80s\n" " " | tr ' ' '-'

RUN yum -y install 								\
		https://vault.centos.org/8-stream/AppStream/x86_64/os/Packages/java-11-openjdk-headless-11.0.17.0.8-2.el8.x86_64.rpm \
		https://vault.centos.org/8-stream/AppStream/x86_64/os/Packages/java-11-openjdk-11.0.17.0.8-2.el8.x86_64.rpm \
		https://vault.centos.org/8-stream/AppStream/x86_64/os/Packages/java-11-openjdk-devel-11.0.17.0.8-2.el8.x86_64.rpm \
    && update-alternatives --set java /usr/lib/jvm/java-11-openjdk-11.0.17.0.8-2.el8.x86_64/bin/java \
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum -y install								\
		https://vault.centos.org/8-stream/AppStream/x86_64/os/Packages/jq-1.6-6.el8.x86_64.rpm \
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum -y install 								\
		https://vault.centos.org/8-stream/AppStream/x86_64/os/Packages/libpng15-1.5.30-7.el8.x86_64.rpm \
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum -y install diffutils							\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && ls -la /usr/lib64/libpng*						\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum -y install 								\
		https://vault.centos.org/8-stream/AppStream/x86_64/os/Packages/libXext-devel-1.3.4-1.el8.x86_64.rpm \
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum -y install libffi-devel						\
    && yum -y install sqlite sqlite-devel					\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum clean all 								\
    && rm -rf /var/cache/yum 							\
    && git config --global user.name "maa-dataops-rules-engine-build" 		\
    && git config --global user.email "noreply@cigna.com" 			\
    && git config --global --list						\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum list available | grep cairo						\
    && printf "%80s\n" " " | tr ' ' '-'						\
    && yum list available | grep python						\
    && printf "%80s\n" " " | tr ' ' '-'


# Create and switch to non-root user; set props
RUN groupadd ${GROUP} -g ${GID} && \
    useradd -c "Jenkins user" -d "${HOME}" -u "${UID}" -g "${GID}" -m "${USER}"

RUN echo "jenkins:x:${UID}:${GID}:Jenkins user:/home/jenkins:" >> /etc/passwd

# Python3.9
COPY build_image/configs/pip.conf /etc/
RUN yum -y install gcc gcc-c++ python39 python39-devel \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && chmod -R 644 /etc/pip.conf \
    && python3.9 -m ensurepip \
    && pip3.9 install --upgrade pip setuptools

# Install Please Build
# See https://please.build/quickstart.html
RUN curl https://get.please.build | bash
RUN cp ~/.please/bin/* /usr/local/bin

WORKDIR /opt/devops/jenkins/workspace/dit/

# copy poetry config & un_re to /home/jenkins/rules_engine
COPY --chown=${UNAME}:${GROUP} ["poetry.lock", "pyproject.toml", "README.md", "bin/run_rules_engine.sh","bin/test_output_parse.sh", "${HOME}/rules_engine/"]
COPY --chown=${UNAME}:${GROUP} un_re ${HOME}/rules_engine/un_re/
COPY --chown=${UNAME}:${GROUP} dummy_solutions ${HOME}/rules_engine/dummy_solutions/

RUN chown -R ${UNAME}:${GROUP} /opt/app-root
RUN chown -R ${UNAME}:${GROUP} /opt/devops/jenkins/workspace
RUN chown -R ${UNAME}:${GROUP} ${HOME}

USER ${UNAME}

RUN pip3.9 install --upgrade pip setuptools \
    && pip3.9 install poetry


WORKDIR ${HOME}/rules_engine
RUN poetry install

RUN chmod 777 -R ${HOME}/.cache
RUN chmod 777 -R ${HOME}/rules_engine
RUN chmod +x ${HOME}/rules_engine/run_rules_engine.sh

CMD /bin/bash

VOLUME ${HOME}/.jenkins
VOLUME ${HOME}/agent
WORKDIR ${HOME}
ENTRYPOINT ["adhoc-perms"]

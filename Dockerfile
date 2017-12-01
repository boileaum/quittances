FROM jupyter/scipy-notebook:cf6258237ff9

USER root

RUN apt-get update --fix-missing && \
    apt-get install -y \
    latexmk \
    texlive-latex-extra \
    texlive-lang-french \
    locales

RUN sed -i 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen
RUN locale-gen fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR
ENV LC_ALL fr_FR.UTF-8
RUN dpkg-reconfigure -f noninteractive locales

RUN pip install --no-cache-dir notebook==5.*
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

ENV NB_USER jovyan
ENV NB_UID 1000
ENV HOME /home/${NB_USER}

# Make sure the contents of our repo are in ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

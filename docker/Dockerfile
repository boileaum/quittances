FROM boileaum/latex:fr
LABEL maintainer="Matthieu Boileau <matthieu.boileau@math.unistra.fr>"

RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD /bin/bash

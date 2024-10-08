FROM python:buster
WORKDIR /app

#RUN sed -i s@/archive.debian.org/@/mirrors.huaweicloud.com/@g /etc/apt/sources.list  && \
#    sed -i s@/security.debian.org/@/mirrors.huaweicloud.com/@g /etc/apt/sources.list && \
#    sed -i s@/deb.debian.org/@/mirrors.huaweicloud.com/@g /etc/apt/sources.list

#RUN apt-get update && apt-get install -y vim \
#    curl \
#    ffmpeg \
#    imagemagick \
#    build-essential \
#    libssl-dev  \
#    libasound2 \
#    wget \
#    libgstreamer1.0-0 \
#    gstreamer1.0-plugins-base \
#    gstreamer1.0-plugins-good \
#    gstreamer1.0-plugins-bad \
#    gstreamer1.0-plugins-ugly \
#    && apt-get clean
RUN /usr/local/bin/python -m pip install --upgrade pip
#RUN sed -i s@<policy domain="path" rights="none" pattern="@*"/>@<!--<policy domain="path" rights="none" pattern="@*"/>-->@g /etc/ImageMagick-6/policy.xml
COPY . /app/

RUN /usr/local/bin/pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENV TZ=Asia/Shanghai
ENV PYTHONPATH=$PYTHONPATH:/app

CMD ["python", "coin/run.py"]
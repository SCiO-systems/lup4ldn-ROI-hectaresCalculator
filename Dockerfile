FROM public.ecr.aws/lambda/python:3.7

ENV PROJ_VERSION=6.1.1
ENV GEOS_VERSION=3.6.0
ENV GDAL_VERSION=3.0.4

ARG AWS_KEY
ARG AWS_SECRET

ENV AWS_KEY ${AWS_KEY}
ENV AWS_SECRET ${AWS_SECRET}

RUN yum install -y gcc-c++.x86_64 \
	cpp.x86_64 \
	sqlite-devel.x86_64 \
	libtiff.x86_64 \
	cmake3.x86_64 \
    wget \
	gcc \
	glibc \
	glibc-common \
	gd \
	gd-devel \
	gcc-c++ \
	tar


# PROJ Installation
RUN cd /tmp
RUN wget https://download.osgeo.org/proj/proj-${PROJ_VERSION}.tar.gz
RUN tar -xvf proj-${PROJ_VERSION}.tar.gz
RUN cd proj-${PROJ_VERSION} \
    && ./configure \
    && make -j4 \
    && make install

# GEOS Installation
RUN cd /tmp
RUN wget http://download.osgeo.org/geos/geos-${GEOS_VERSION}.tar.bz2
RUN bunzip2 geos-${GEOS_VERSION}.tar.bz2 && tar -xvf geos-${GEOS_VERSION}.tar
RUN cd geos-${GEOS_VERSION} \
    && ./configure \
    && make -j4 \
    && make install

# GDAL Installation
RUN cd /tmp
RUN wget https://github.com/OSGeo/gdal/releases/download/v${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz
RUN tar -xvf gdal-${GDAL_VERSION}.tar.gz
RUN cd gdal-${GDAL_VERSION} \
    && ./configure \
    && make -j4 \
    && make install

# install AWS CLI
RUN yum install aws-cli -y

RUN aws configure set aws_access_key_id ${AWS_KEY}
RUN aws configure set aws_secret_access_key ${AWS_SECRET}

COPY . ./

RUN pip3 install -r requirements.txt

RUN cp /usr/local/lib/libgdal.so.26* /usr/lib64/

CMD ["ROI_hectares_calcualtor.lambda_handler"]

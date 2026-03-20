FROM python:3.9-slim

# Install Java (required for Spark)
RUN apt-get update && \
    apt-get install -y default-jre && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Install PySpark
RUN pip install pyspark

# Set working directory
WORKDIR /app

# Default to bash for interactive use
CMD ["/bin/bash"]

FROM python:3.12

# Create a non-root user and switch to it
RUN useradd -ms /bin/bash vscode
USER vscode

# Set the container user
ENV USER=vscode

WORKDIR .

COPY . /src



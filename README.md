# an API implementation to serve Hash runs/events via API

This repository provides a tool to expose
[WordPress Event Manager Plugin](https://wordpress.org/plugins/wp-event-manager/) events via API.
This is aimed at Hash Kennels to announce runs which then can be consumed
by [Harrier Central](https://www.harriercentral.com)

## Requirements
### Software
* python >= 3.6
* starlette
* fastapi
* pydantic
* uvicorn
* pytz
* phpserialize
* mysql-connector

### WP Event Manager Plugin
* WP Event Manager >= 3.1.21

# Installing
* here we assume we install in ```/opt```

## RedHat based OS
* on RedHat/CentOS 7 you need to install python3.6 and pip from EPEL first
* on RedHat/CentOS 8 systems the package name changed to `python3-pip`
```
yum install python36-pip
```

## Ubuntu 18.04 & 20.04
```
apt-get update && apt-get install python3-venv
```

## Clone repo and install dependencies
* download and setup of virtual environment
```
cd /opt
git clone https://github.com/bb-Ricardo/wordpress-hash-event-api.git
cd wordpress-hash-event-api
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt || pip install -r requirements.txt
```

## Docker

Run the application in docker container

* The application working directory is ```/app```
* Required to mount your ```config.ini```

```
docker build -t wordpress-hash-event-api .
docker run --rm -it -v $(pwd)/config.ini:/app/settings.ini wordpress-hash-event-api
```

## Setup
Copy the [config-example.ini](config-example.ini) sample settings file to `config.ini`.
All options are described in the example file.


## ToDo
- [x] fix and test db connection timeout
- [ ] fill README with useful information
- [x] describe config
- [ ] function and class doc strings
- [x] add filters for most run attributes
- [x] add API auth
- [x] clean up code / linting
- [x] describe setup and installation
- [x] add docker file
- [x] try to add "auto-install", this should set up the WordPress Event Manager to add all available fields to all events
- [x] requirements.ini
- [ ] add OpenRC init script and config to server API via uvicorn
- [ ] add nginx config example
  - [ ] add CORS Headers to nginx config




## License
>You can check out the full license [here](LICENSE.txt)

This project is licensed under the terms of the **MIT** license.

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
* psutil

### WP Event Manager Plugin
* WP Event Manager >= 3.1.21

# Installing
* here we assume we install in ```/opt```

## RedHat based OS
* on RedHat/CentOS 7 you need to install python3.6 and pip from EPEL first
* on RHEL/Rocky Linux 8 systems the package name changed to `python3-pip`
```shell
yum install python36-pip
```

## Ubuntu 18.04 & 20.04
```shell
apt-get update && apt-get install python3-venv
```

## Clone repo and install dependencies
* download and setup of virtual environment
```shell
cd /opt
git clone https://github.com/bb-Ricardo/wordpress-hash-event-api.git
cd wordpress-hash-event-api
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt || pip install -r requirements.txt
```

## Install as systemd service
If files have been installed in a different directory then the systemd service file
needs to be edited.

Ubuntu
```shell
cp /opt/wordpress-hash-event-api/contrib/wordpress-hash-event-api.service /etc/systemd/system
```
RHEL/Rocky Linux
```shell
sed -e 's/nogroup/nobody/g' /opt/wordpress-hash-event-api/contrib/wordpress-hash-event-api.service > /etc/systemd/system/wordpress-hash-event-api.service
```

Enable and start service
```shell
systemctl daemon-reload
systemctl start wordpress-hash-event-api
systemctl enable wordpress-hash-event-api
```

## Install as OpenRC service
The [uvicorn.confd](contrib/uvicorn.confd) config file needs to be copied to `/etc/conf.d/`.
Let's assume the API is called `nerd-h3`.
```shell
cp contrib/uvicorn.confd /etc/conf.d/uvicorn.nerd-h3
chmod 644 /etc/conf.d/uvicorn.nerd-h3
```

The init script [uvicorn.openrc](contrib/uvicorn.openrc) needs to be copied to `etc/init.d/`
and symlinked.
```shell
cp contrib/uvicorn.openrc /etc/init.d/uvicorn
chmod 755 /etc/init.d/uvicorn
cd /etc/init.d
ln -s uvicorn uvicorn.nerd-h3
```

Then the correct values need to be set in `/etc/conf.d/uvicorn.nerd-h3`. After the configuration
is finished the service can be started.
```shell
/etc/init.d/uvicorn.nerd-h3 start
rc-update add uvicorn.nerd-h3 default
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
- [x] add OpenRC init script and config to server API via uvicorn
- [ ] add nginx config example
  - [ ] add CORS Headers to nginx config




## License
>You can check out the full license [here](LICENSE.txt)

This project is licensed under the terms of the **MIT** license.

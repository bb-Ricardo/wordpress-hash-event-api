# an API implementation to serve Hash runs/events via API

This repository provides a tool to expose
[WordPress Event Manager Plugin](https://wordpress.org/plugins/wp-event-manager/) events via API.
This is aimed at Hash Kennels to announce runs which then can be consumed
by [Harrier Central](https://www.harriercentral.com)

## Requirements
You need to have a running Wordpress site with 'WP Event Manager' Plugin installed.

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
* icalendar
* beautifulsoup4

### WP Event Manager Plugin
* WP Event Manager >= 3.1.21

## Installing
* here we assume we install in ```/opt```

### RedHat based OS
* on RedHat/CentOS 7 you need to install python3.6 and pip from EPEL first
* on RHEL/Rocky Linux 8 systems the package name changed to `python3-pip`
```shell
yum install python36-pip
```

### Ubuntu 18.04 & 20.04
```shell
apt-get update && apt-get install python3-venv
```

### Clone repo and install dependencies
* download and setup of virtual environment
```shell
cd /opt
git clone https://github.com/bb-Ricardo/wordpress-hash-event-api.git
cd wordpress-hash-event-api
python3 -m venv .venv
. .venv/bin/activate
pip3 install -r requirements.txt || pip install -r requirements.txt
```

### Install as systemd service
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

### Install as OpenRC service
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

### Docker

Run the application in docker container

* The application working directory is ```/app```
* Required to mount your ```config.ini```

```
docker build -t wordpress-hash-event-api .
docker run --rm -it -v $(pwd)/config.ini:/app/config.ini wordpress-hash-event-api
```

### Nginx as reverse proxy
In case you want to use Nginx as a reverse proxy you can add following lines
to your server block configuration. Make sure to adjust your IP and port accordingly.
```nginx
        location /api {
                return 307 /api/v1;
        }
        location /api/v1/ {
                rewrite /api/v1/(.*) /$1  break;
                proxy_pass http://127.0.0.1:8000;
                proxy_redirect     off;
                proxy_set_header   Host              $host;
                proxy_set_header   X-Real-IP         $remote_addr;
                # activate to see the actual remote IP and not just your reverse proxy
                # attention: in Europe this has implications on your GDPR statements on your page
                #            as you log IP addresses.
                #proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
                #proxy_set_header   X-Forwarded-Proto $scheme;
        }
        # expose icalender evets
        location /events.ics {
                proxy_pass http://127.0.0.1:8000/runs/calendar;
                proxy_set_header   Host              $host;
                proxy_set_header   X-Real-IP         $remote_addr;
                # activate to see the actual remote IP and not just your reverse proxy
                # attention: in Europe this has implications on your GDPR statements on your page
                #            as you log IP addresses.
                #proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
                #proxy_set_header   X-Forwarded-Proto $scheme;
        }
```

## Setup
Copy the [config-example.ini](config-example.ini) sample settings file to `config.ini`.
All options are described in the example file.

### Order
1. Install WordPress
2. Install [WordPress Event Manager Plugin](https://wordpress.org/plugins/wp-event-manager/)
3. Edit event form fields at least once
4. Start API
5. Define event types which will be exposed as "event_type" for a run, like "Regular Run" or "Christmas Run"

After starting the API the first time it will add additional fields to each event.
Such as a choice for the hosting Kennel or amount of Hash Cash.

## Listmonk support to post event
It is possible to post an event directly to via [Listmonk](https://github.com/knadh/listmonk) to a mailing list.

### Requirements
* a running listmonk instance
* WordPress Advanced Custom Fields plugin
* Wordpress WPCode Plugin

First both WordPress plugins should be installed.

Using the `Advanced Custom Fields` we add a new Field Group `Run Announcement`. There we add a new field `Mailing List`.
* Type: Message
* Label: Mailing List
* Name: mailing_list
* Message:
```
<div>
<button
    id="send-to-mailing-list-button"
    type="button"
    class="button-secondary send-to-mailing-list-button"
    id="refresh-cache">Send/Update Event to Mailing List
</button>
</div>
  ```

In the bottom we can find `Settings`.
* Rules:
  1. Post Typ
  2. is equal to
  3. Event
* Representation:
  1. Style: Standard
  2. Position: Side
  3. Label Placement: Top
  4. Instruction placement: Below
  5. Order No: 2

* Now press `Save Changes`

After that we switch to the `WPCode` plugin and a Javascript function to this button we just created.
Here we add a new `Send Mailinglist` code snippet of type `PHP Snipet` with this content:
```php
/* Inline script printed out in the header */
add_action('admin_footer', 'tutsplus_add_script_wp_head');
function tutsplus_add_script_wp_head() {
    ?>
		<script id="updateMailingList" type="text/javascript">
			document.querySelector( '.send-to-mailing-list-button' ).addEventListener( 'click', function( e ) {
				var xhttp = new XMLHttpRequest();
				var params = {
					user: "<?php echo get_current_user_id(); ?>",
					token: "<?php echo wp_get_session_token(); ?>"
				}

				xhttp.onreadystatechange = function() {
					if (this.readyState == 4 && this.status == 200) {
					    console.log(this.responseText);
					}
				};

			    xhttp.open("POST", "/api/v1/send-newsletter/<?php echo get_the_ID(); ?>" , true);
				xhttp.setRequestHeader('Content-type', 'application/json')

			    xhttp.send(JSON.stringify(params));
				xhttp.onload = function() {
                    // Do whatever with response
                        alert("Mailing List request status: " + xhttp.responseText)
                }

			} );
		</script>
    <?php
}
```
With Listmonk running on the same hos, sending an event via Mailing list is just a button press away.

## License
>You can check out the full license [here](LICENSE.txt)

This project is licensed under the terms of the **MIT** license.

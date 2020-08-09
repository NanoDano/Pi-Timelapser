# Pi-Timelapser

Scripts for creating timelapse videos on a Raspberry Pi.

## Setup

Basic setup steps:

```bash
sudo apt install -y mencoder
git clone https://github.com/NanoDano/Pi-Timelapser /home/pi/Pi-Timelapser
/usr/bin/python3 -m venv /home/pi/Pi-Timelapser/venv
/home/pi/Pi-Timelapser/venv/bin/python -m pip install -r /home/pi/Pi-Timelapser/requirements.txt
cp /home/pi/Pi-Timelapser/app/app/app{.example,}.env
vim /home/pi/Pi-Timelapser/app/app/app.env
/home/pi/Pi-Timelapser/venv/bin/python /home/pi/Pi-Timelapser/app/manage.py migrate
/home/pi/Pi-Timelapser/venv/bin/python /home/pi/Pi-Timelapser/app/manage.py collectstatic
```

### Setup cron jobs

There are two cron jobs to setup:

1. Taking a picture ever X minutes
2. Nightly "build" which creates the timelapse video and uploads over FTP

Run:

```bash
crontab -e
```

And add the lines:

```text
*/5 * * * * /home/pi/Pi-Timelapser/venv/bin/python /home/pi/Pi-Timelapser/app/manage.py take_picture
0 0 * * * /home/pi/Pi-Timelapser/venv/bin/python /home/pi/Pi-Timelapser/app/manage.py nightly_build
```

The `merge_videos` script is not on a cron timer, but
is a utility script provided to assist with stitching multiple
videos together to create a longer video.

## Map media dir with nginx

If you want the media dir with all images to be browsable
via nginx, update the nginx config with the location alias:

```
# http ...
  # server ...

    location /timelapser-images {
        autoindex on;
        alias /home/pi/Pi-Timelapser/app/media/;
    }
```


### Setup gunicorn or waitress? I don't need the front end even do I? What about waitress?

1. Create a systemd service file for the gunicorn/django app.

```
# /etc/systemd/system/Timelapser.service
[Unit]
Description=Pi Timelapser
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/var/www/Pi-Timelapser/app
ExecStart=/usr/local/bin/gunicorn app.wsgi -b 127.0.0.1:8001
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service

```bash
sudo systemctl enable Timelapser
sudo systemctl start Timelapser
```

### Setup Nginx

1. Generate SSL cert and key


```bash
# TODO put this ssl cert in the timelapser dir instead?
sudo openssl \
  req \
  -newkey rsa:2048 -nodes \
  -keyout /etc/ssl/private/pi-timelapster.key \
  -x509 -days 36500 -out /etc/ssl/private/pi-timelapser.cert \
  -subj "/C=US/ST=NRW/L=Earth/O=CompanyName/OU=IT/CN=www.example.com/emailAddress=email@example.com"
```

2. Create a config file for nginx in `/etc/nginx/sites-available/`.

```
# /etc/nginx/sites-available/pi-timelapser.conf
server { 
    listen 0.0.0.0:443 ssl;
    server_name cammy.attlocal.net;

    ssl_certificate /etc/ssl/private/pi-timelapser.cert;
    ssl_certificate_key /etc/ssl/private/pi-timelapster.key;
    ssl_ciphers  HIGH:!aNULL:!MD5;

    location /static/ {
        alias /var/www/Pi-Timelapser/app/static/;
    }
    location /media/ {
        alias /var/www/Pi-Timelapser/app/media/;
    }
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8001;
    }
}
```

3. Symlink config from sites-available to sites-enabled.

```bash
sudo ln -s \
  /etc/nginx/sites-available/Pi-Timelapser.conf \
  /etc/nginx/sites-enabled/Pi-Timelapser.conf
```

4. Enable and start the service

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```












## Camera resolution

Pi Cam v1 - 2592x1944
Pi Cam v2 - 3280x2464

## References

- https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
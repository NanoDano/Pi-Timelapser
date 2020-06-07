# Pi-Timelapser

Scripts for creating timelapse videos on a Raspberry Pi.

```text
crontab -e
*/5 * * * * /home/pi/Pi-Timelapser/take_picture 2>&1
0 0 * * * /home/pi/Pi-Timelapser/timelapse_nightly_build 2>&1
```

The `merge_videos` script is not on a cron timer, but
is a utility script provided to assist with stitching multiple
videos together to create a longer video.

## References

- https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
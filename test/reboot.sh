
#! /bin/bash

set count = 1
while true
do
    adb wait-for-device
    adb reboot
    ((count++))
    echo $count
done

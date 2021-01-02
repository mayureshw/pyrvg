#!/bin/sh

# If you want to capture full usbmon trace right from inserting the cable, you
# won't know the bus and device id up front to pass it to usbmon, so you might
# end up gathering trace for all devices. Once you get to know the bus and
# device id, this script helps you filter the trace for that. (It's not just a
# matter of grep due to the lines that contain data)

usage() {
    echo "`basename $0` <tracefile> <bus.devide in n.nnn form>"
    exit 1
    }

if [ $# -lt 2 ]
then
    usage
fi

TRACE=$1
BUSDEV=$2

if [ ! -f "$TRACE" ]
then
    echo "No such file: " $TRACE
    usage
fi

awk -v BUSDEV=$BUSDEV '
    /^ / && CURBUSDEV==BUSDEV { print; next }
    $0 ~ "^"BUSDEV { CURBUSDEV = BUSDEV; print; next }
    { CURBUSDEV="" }
    ' $TRACE

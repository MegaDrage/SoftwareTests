#!/bin/bash

JENKINS_BUILD_URL="https://jenkins.openbmc.org/job/ci-openbmc/lastSuccessfulBuild/distro=ubuntu,label=docker-builder,target=romulus/artifact/openbmc/build/tmp/deploy/images/romulus/*zip*/romulus.zip"
QEMU_IMAGE_DIR="romulus"
QEMU_IMAGE_PATTERN="obmc-phosphor-image-romulus-*.static.mtd"

mkdir -p "$QEMU_IMAGE_DIR"

if [ ! -f "$QEMU_IMAGE_DIR/$QEMU_IMAGE_PATTERN" ]; then
  echo "Downloading latest image from Jenkins..."
  wget "$JENKINS_BUILD_URL" -O romulus.zip
  
  echo "Unpacking image..."
  unzip -o romulus.zip -d "$QEMU_IMAGE_DIR"
  rm romulus.zip
fi

QEMU_IMAGE=$(find "$QEMU_IMAGE_DIR" -name "$QEMU_IMAGE_PATTERN" | head -n 1)

if [ -z "$QEMU_IMAGE" ]; then
  echo "Error: QEMU image not found!"
  exit 1
fi

echo "Using QEMU image: $QEMU_IMAGE"

qemu-system-arm -m 256 -M romulus-bmc -nographic -drive file=$QEMU_IMAGE,format=raw,if=mtd \ 
-net nic -net user,hostfwd=tcp::2222-:22,hostfwd=tcp::2443-:443,hostfwd=udp::2623-:623,hostname=qemu
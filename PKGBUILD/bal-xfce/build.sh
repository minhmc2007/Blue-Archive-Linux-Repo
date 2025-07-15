#!/bin/bash
set -e
dpkg-deb --build "$(dirname "$0")"

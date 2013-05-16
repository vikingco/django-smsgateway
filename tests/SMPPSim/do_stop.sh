#! /bin/bash
rm *.log.*
kill -TERM `cat service.pid`
rm service.pid

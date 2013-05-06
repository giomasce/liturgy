#!/bin/bash

sqlite3 liturgy.sqlite ".dump" > backups/liturgy-$(date '+%Y%m%d-%H%M%S').sql

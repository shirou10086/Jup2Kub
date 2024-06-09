#!/bin/bash
input=("$@")
echo -e "${#input[@]}\n${input[@]}" | ./example3


#!/bin/bash
input1=$1
input2=$2
output=$(echo -e "$input1\n$input2" | ./example2)
echo "$output"

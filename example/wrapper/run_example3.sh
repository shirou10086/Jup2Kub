
#!/bin/bash
input=("$@")
echo -e "${#input[@]}
${input[@]}" | ./example3

#/bin/bash
#--------------------------------------------------------------------------------
# Search a directory tree from START upwards until END to locate a specified path.
#--------------------------------------------------------------------------------
_locate(){
    START=$1; END=$2; PATTERN=$3

    path="${START}"
    while [[ $path != ${END} ]];
    do
        #find "$path" -maxdepth 1 -mindepth 1 -path "*/${PATTERN}" | egrep '.*'
        find "$path" -path "*/${PATTERN}" | egrep '.*'
        if [ $? -eq 0 ]; then
            return 0
        else
            path="$(realpath "$path"/..)"
        fi
    done
    return 1
}
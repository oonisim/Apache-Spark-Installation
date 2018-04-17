for i in $(find . -type f) 
do
	echo "========================================================================================================"
	echo $i
	diff $i /Users/maonishi/home/projects/BTSM/platform/git/operations/monitoring/ansible/$i
done


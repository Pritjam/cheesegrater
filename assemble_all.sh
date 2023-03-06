echo "Assembling files in $1 to output directory $2"

for FILENAME in $(ls $1 | grep '.sws')
do 
    echo "Assembling $FILENAME now"
    python3 grater.py $1/$FILENAME $2
done
file=$1

users=$(cat $file | cut -d ":" -f1 | sort -u)
for user in ${users[@]}; do
    hashes=(${hashes[@]} $(grep -a "$user:" -m1 $file))
done

for hash in ${hashes[@]}; do
    echo $hash >> "${file}_parsed"
done

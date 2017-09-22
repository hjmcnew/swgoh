#!/bin/sh

set -e
set -u

debug=0
now=$(date -u +"%s%N")
guild="guild-name"
count=0

hacky=$(mktemp)
ships=$(mktemp)
toons=$(mktemp)
if [ $debug -eq 1 ]; then
    curl="/bin/echo -- curl"
else
    curl="/usr/bin/curl"
fi

wget -q -O- 'guild-swgoh.gg-url' | \
    egrep -o 'href="/u/.+"' | \
    sed -e 's#href="#https://swgoh.gg#' -e 's#"##g' | \
while read url; do
    sleep 1
    user=$(echo $url | awk -F/ '{print $5}')
    /path/to/swgoh.py ${user}
    sleep 1
    wget -q -O- "${url}" | \
        grep 'class="pull-right"' | \
        awk -F\> '{print $2 "#" $3}' | \
        awk -F\< '{print $1 "#" $2}' | \
        awk -F\# '{print $1 " " $3}' | \
        sed 's/,//g' | \
        egrep -v '^Guild  $|^Joined|^Ally' | \
    while read stat; do
        case $stat in
            Galactic?Power??Characters?*)
                stat_name="character-gp"
                stat_value=$(echo $stat | awk '{print $4}')
                measure="galactic-power"
		echo ${stat_value} > ${toons}
                ;;
            Galactic?Power??Ships?*)
                stat_name="ship-gp"
                stat_value=$(echo $stat | awk '{print $4}')
                measure="galactic-power"
		echo ${stat_value} > ${ships}
                ;;
            PVE?Battles?Won*)
                stat_name="pve"
                stat_value=$(echo $stat | awk '{print $4}')
                measure="battles"
                ;;
            PVE?Hard?Battles?Won*)
                stat_name="pve-hard"
                stat_value=$(echo $stat | awk '{print $5}')
                measure="battles"
                ;;
            Galactic?War?Battles?Won?*)
                stat_name="gw"
                stat_value=$(echo $stat | awk '{print $5}')
                measure="battles"
                ;;
            Arena?Battles?Won*)
                stat_name="arena"
                stat_value=$(echo $stat | awk '{print $4}')
                measure="battles"
                ;;
            Ship?Battles?Won*)
                stat_name="ship-battles"
                stat_value=$(echo $stat | awk '{print $4}')
                measure="battles"
                ;;
            *)
                continue
                ;;
        esac
        ${curl} -s -XPOST 'http://localhost:8086/write?db=swgoh' --data-binary "${measure},guild=${guild},user=${user} ${stat_name}=${stat_value} ${now}"
    done
    tot_gp=$(($(awk '{print $1}' ${ships})+$(awk '{print $1}' ${toons})))
    ${curl} -s -XPOST 'http://localhost:8086/write?db=swgoh' --data-binary "galactic-power,guild=${guild},user=${user} total_gp=${tot_gp} ${now}"
    count=$((${count}+1))
    echo "count ${count}" > ${hacky}
done
count=$(grep ^count ${hacky} | awk '{print $2}')
${curl} -s -XPOST 'http://localhost:8086/write?db=swgoh' --data-binary "users,guild=${guild} count=${count} ${now}"
rm -f ${hacky}
rm -f ${ships}
rm -f ${toons}

exit 0

#!/bin/bash

folder_c="$HOME/moving-out/configs"
folder_b="$HOME/moving-out/backups"
procedures=$1
# old - preparation for moving to new OS 
# new - unpacking files on new OS

# Application,old_location,new_location,permissions
data_config=(
    "Remmina,$HOME/.config/remmina/,${folder_c}/remmina-pref/,user"
    "Remmina,$HOME/.local/share/remmina/,${folder_c}/remmina-conn/,user"
    "Vim,$HOME/.vim/spell/,${folder_c}/vim-spell/,user"
    "Vim,$HOME/.vimrc,${folder_c}/vim-config/,user"
    "Joplin,$HOME/.config/joplin-desktop/settings.json,${folder_c}/joplin/,user"
    "Joplin,$HOME/.config/joplin-desktop/userstyle.css,${folder_c}/joplin/,user"
    "Joplin,$HOME/.config/joplin-desktop/database.sqlite,${folder_c}/joplin/,user"
    "Joplin,$HOME/.config/joplin-desktop/resources/,${folder_c}/joplin-resources/,user"
    "Joplin,$HOME/.config/joplin-desktop/plugins/,${folder_c}/joplin-plugins/,user"
    "Terminator,$HOME/.config/terminator/,${folder_c}/terminator/,user"
    "Bash,$HOME/.bashrc,${folder_c}/bash/,user"
    "NetworkManager,/etc/NetworkManager/system-connections/,${folder_c}/net-manager/,root"
    "NetworkManager,$HOME/.cert/nm-openvpn/,${folder_c}/net-manager-openvpn/,user"
    "Wireguard,/etc/wireguard/,${folder_c}/wireguard/,root"
    "SSL,/usr/local/share/ca-certificates/,${folder_c}/ssl-certs/,root"
    "SSH,$HOME/.ssh/,${folder_c}/ssh/,user"
    "Socks-wrapper,/etc/systemd/system/socks-wrapper.service,${folder_c}/socks-wrapper/,root"
    "Host-file,/etc/hosts,${folder_c}/hosts/,root"
    "HTML,/var/www/html/,${folder_c}/html,root"
)

data_backup=(
    "Joplin,$HOME/.config/joplin-desktop/JoplinBackup/,${folder_b}/joplinbackup/,user"
    "Anki,$HOME/.local/share/Anki2/User 1/backups/,${folder_b}/ankibackup/,user"
    "Documents,$HOME/Documents/,${folder_b}/Documents/,user"
    "Templates,$HOME/Templates/,${folder_b}/Templates/,user"
)

packages=(
    "hashcat" "redsocks" "ffuf" "curl" "wfuzz" "hydra" "wireshark" "terminator" "vim"
    "simplenote" "snap"
)

manual_procedures=(
    "Mozilla Firefox saved passwords"
    "RemoteConn VirtualBox VM export"
    "Acestreamplayer instalation"
)

f_old_os (){
    input="$1"
    src=$(echo "$input" | cut -d ',' -f2)
    dst=$(echo "$input" | cut -d ',' -f3)
    priv=$(echo "$input" | cut -d ',' -f4)
    
    mkdir "$dst" 2>/dev/null
    
    if [[ "$priv" == "root" ]]; then
        sudo cp -a "$src"* "$dst"
    else
        cp -a "$src"* "$dst"
    fi
}

f_new_os (){
    input="$1"
    src="$(echo $input | cut -d ',' -f3)"
    dst="$(echo $input | cut -d ',' -f2)"
    priv="$(echo $input | cut -d ',' -f4)"
    
    if [[ "$priv" == "root" ]]; then
        sudo cp -a "$src"* "$dst"
    else
        cp -a "$src"* "$dst"
    fi

    cp -a "$src"* "$dst"
}

f_pkg_install () {
    for package in ${packages[@]}; do
        line="$line $package"
    done
    sudo apt install $line
}

if [[ $procedures == "old" ]]; then
    rm -r "$folder_c" 2>/dev/null
    mkdir --parents "$folder_c"
    rm -r "$folder_b" 2>/dev/null
    mkdir --parents "$folder_b"
fi

if [[ $procedures == "old" ]]; then
    for config_entry in "${data_config[@]}"; do
        f_old_os "$config_entry"
    done
    for backup_entry in "${data_backup[@]}"; do
        f_old_os "$backup_entry"
    done
elif [[ $procedures == "new" ]]; then
    for config_entry in "${data_config[@]}"; do
        f_new_os "$config_entry"

    done
    f_new_os "$data_entry"
    f_pkg_install
    echo 
else
    echo "Wrong argument. Accept 'old' or 'new'"
    exit 1
fi

echo "Do not forget about following manual procedures:"
for procedure in "${manual_procedures[@]}"; do
    echo -e "\t- $procedure"
done

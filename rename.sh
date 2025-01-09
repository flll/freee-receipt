#!/bin/sh -eu

echo "imagesディレクトリ内のjpgファイルを最適なファイル名にリネームします"
echo "Enterで開始します"
read dummy
cd images
for file in *.jpg; do
    if [ ! "$(echo "$file" | grep -E "^[0-9]{8}(_[0-9]{6}[a-z]{2})?\.jpg$")" ]; then
        random_suffix=$(cat /dev/urandom | tr -dc 'a-z' | fold -w 2 | head -n 1)
        new_name=$(date -r "$file" +%Y%m%d_%H%M%S${random_suffix}.jpg)
        
        echo "$file" "$new_name"
        mv "$file" "$new_name"
    fi
done

echo "完了しました"
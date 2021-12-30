#!/bin/bash

OUTPUT_PATH=$1

for name in $(curl -s localhost:8080/studies?count=1000 | jq '.[].name'| sed 's/"//g'); do
  echo $name
  mkdir -p "${OUTPUT_PATH}/${name}";
  wget -q -O "${OUTPUT_PATH}/${name}/studies.json" "localhost:8080/studies?name=${name}";
  wget -q -O "${OUTPUT_PATH}/${name}/viewer.html" "localhost:8080/reports?as=HTML&type=HTML_VIEWER&Studies.name=${name}&sort=-creation_datetime";
  wget -q -O "${OUTPUT_PATH}/${name}/report.pdf" "localhost:8080/reports?as=PDF&type=PDF_SIMPLE&Studies.name=${name}&sort=-creation_datetime";
  wget -q -O "${OUTPUT_PATH}/${name}/report.json" "localhost:8080/reports?as=JSON&type=JSON&Studies.name=${name}&sort=-creation_datetime";
  wget -q -O "${OUTPUT_PATH}/${name}/report.csv" "localhost:8080/reports?as=CSV&type=JSON&Studies.name=${name}&sort=-creation_datetime";
done;
wget -q -O "${OUTPUT_PATH}/summary.csv" "localhost:8080/reports?as=SUMMARYCSV&type=JSON&count=1000";

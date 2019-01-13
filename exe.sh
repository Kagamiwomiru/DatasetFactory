function last(){
  echo '強制終了'
  rm -rf /home/kagamiwomiru/datasets/Load_set_sep/imgs/
  rm /home/kagamiwomiru/datasets/Load_set_sep/Load_set_sep_annotation.csv
  exit 2

}

trap 'last' {1,2,3,15}
echo "label,minX,minY,maxX,maxY,path,file,name" > /home/kagamiwomiru/datasets/Load_set_sep/Load_set_sep_annotation.csv
for label in `seq 44`
  do
  python DatasetFactory.py --Background_dir=/home/kagamiwomiru/datasets/haikeigazou/ \
                         --Output_dir=/home/kagamiwomiru/datasets/Load_set_sep/imgs/ \
                         --Target_dir=/home/kagamiwomiru/datasets/hyousiki/$label/ \
                         --annotation_file=/home/kagamiwomiru/datasets/Load_set_sep/Load_set_sep_annotation.csv \
                         --init=true \
                         --label=$label \
                         --name=$label \
                         --recipe_file=./GetPoint.csv
  done

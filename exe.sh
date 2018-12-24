

for label in seq 1 48
  do
  python DatasetFactory.py --Background_dir=/home/kagamiwomiru/datasets/haikeigazou/ \
                         --Output_dir=/home/kagamiwomiru/datasets/Load_set/ \
                         --Target_dir=/home/kagamiwomiru/datasets/hyousiki/ \
                         --annotation_file=/home/kagamiwomiru/datasets/Load_set_annotation.csv \
                         --init=true \
                         --label=? \
                         --name=test \
                         --recipe_file=./Getpoint.csv
  done


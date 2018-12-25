for label in `seq 45`
  do
  python DatasetFactory.py --Background_dir=/home/kagamiwomiru/datasets/haikeigazou/ \
                         --Output_dir=/home/kagamiwomiru/datasets/Load_set/ \
                         --Target_dir=/home/kagamiwomiru/datasets/hyousiki/$label/ \
                         --annotation_file=/home/kagamiwomiru/datasets/Load_set_annotation.csv \
                         --init=true \
                         --label=$label \
                         --name=$label \
                         --recipe_file=./Getpoint.csv
  done
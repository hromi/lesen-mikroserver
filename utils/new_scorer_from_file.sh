#!/bin/bash
source /data/deepspeech-train-jetson-venv/bin/activate
mkdir /data/lms/$1
python3 /data/DeepSpeech/data/lm/generate_lm.py --input_txt $1 --output_dir /data/lms/$1 --top_k 500000 --kenlm_bins ./kenlm_bins --arpa_order 4 --max_arpa_memory "1%" --arpa_prune "0|0|1" --binary_a_bits 255 --binary_q_bits 8 --binary_type trie --discount_fallback
/data/utils/generate_scorer_package --lm /data/lms/$1/lm.binary --vocab /data/lms/$1/vocab-500000.txt  --checkpoint /data/alphabets/deepspeech/de --package /data/scorers/$1.scorer --default_alpha 0.931289039105002 --default_beta 1.1834137581510284

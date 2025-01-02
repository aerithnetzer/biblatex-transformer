#!/bin/bash
#SBATCH -A p32234
#SBATCH -p gengpu
#SBATCH -t 24:00:00
#SBATCH --gres=gpu:a100:2
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=128G
#SBATCH --job-name=biblatex-transformer

module load singularity

# Use a temporary directory when pulling container image
export SINGULARITY_CACHEDIR=$TMPDIR

eval "$(conda shell.bash hook)"
# Run the container
singularity exec --nv -B /projects/p32234:/projects/p32234/ /projects/p32234/projects/aerith/biblatex-transformer/ollama_latest.sif ollama serve &
conda activate /projects/p32234/projects/aerith/biblatex-transformer/biblatex-conda
python /projects/p32234/projects/aerith/biblatex-transformer/test-ollama.py

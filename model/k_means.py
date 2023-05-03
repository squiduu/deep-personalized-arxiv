from dataclasses import dataclass, field
from typing import Optional

import torch


@dataclass
class ClusteringArguments:
    max_seq_len: Optional[int] = field(
        default=128,
        metadata={
            "help": "The maximum total input sequence length after tokenization. Sequences longer "
            "than this will be truncated, sequences shorter will be padded."
        },
    )
    overwrite_cache: Optional[bool] = field(
        default=False,
        metadata={"help": "Overwrite the cached preprocessed datasets or not."},
    )
    pad_to_max_len: Optional[bool] = field(
        default=True,
        metadata={
            "help": "Whether to pad all samples to `max_seq_length`. "
            "If False, will pad the samples dynamically when batching to the maximum length in the batch."
        },
    )
    num_target_words: Optional[int] = field(default=0, metadata={"help": "The number of gender words."})
    num_wiki_words: Optional[int] = field(default=0, metadata={"help": "The number of wiki words."})
    bias_type: Optional[str] = field(default="gender", metadata={"help": "The type of bias attributes."})
    model_id: Optional[str] = field(
        default="bert-base-uncased",
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"},
    )
    model_name: Optional[str] = field(
        default=None,
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"},
    )

def run_k_means():
    pass

if __name__ == "__main__":
    run_k_means()
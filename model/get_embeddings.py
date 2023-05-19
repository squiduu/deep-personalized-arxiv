import pickle
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

import pandas as pd
import torch

# from pandas.core import frame
from pymongo.mongo_client import MongoClient
from tqdm import tqdm
from transformers.hf_argparser import HfArgumentParser
from transformers.models.roberta.modeling_roberta import RobertaModel
from transformers.models.roberta.tokenization_roberta import RobertaTokenizer


@dataclass
class EmbeddingArguments:
    model_id: Optional[str] = field(
        default="johngiorgi/declutr-base",
        metadata={
            "help": "Path to pretrained model or model identifier from huggingface.co/models"
        },
    )


def load_from_mongodb(
    db_name: str = "arxiv", collection_name: str = "papers"
) -> pd.DataFrame:
    client = MongoClient("mongodb://root:cvpr0372@arxivdb:27017/")
    db = client[db_name]
    collection = db[collection_name]

    cursor = collection.find()
    df = pd.DataFrame(list(cursor))

    client.close()

    return df


def prepare_data(
    df: pd.DataFrame, tokenizer: RobertaTokenizer
) -> List[Dict[str, Union[str, torch.Tensor]]]:
    data = []
    for row in tqdm(iterable=df.itertuples(), desc="Preparing data", total=len(df)):
        encoding = tokenizer.__call__(
            text=row.title + tokenizer.sep_token + row.abstract,
            max_length=tokenizer.model_max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
        )
        datum = {"_id": row._1, "encoding": encoding}
        data.append(datum)

    return data


def get_embeddings(args: EmbeddingArguments) -> Dict[str, Union[str, torch.Tensor]]:
    tokenizer = RobertaTokenizer.from_pretrained(args.model_id)
    model = RobertaModel.from_pretrained(args.model_id)
    model.cuda("cuda").eval()

    df = load_from_mongodb(db_name="arxiv", collection_name="papers")

    data = prepare_data(df=df, tokenizer=tokenizer)

    embeddings: list = []
    for datum in tqdm(iterable=data, desc="Getting embeddings", total=len(data)):
        _id = datum["_id"]
        encoding = datum["encoding"]
        input_ids = torch.Tensor.cuda(encoding["input_ids"], device="cuda")
        attention_mask = torch.Tensor.cuda(encoding["attention_mask"], device="cuda")

        with torch.autograd.grad_mode.no_grad():
            sequence_output = model.forward(
                input_ids=input_ids, attention_mask=attention_mask
            ).last_hidden_state
            embedding: torch.Tensor = torch.sum(
                sequence_output * torch.unsqueeze(attention_mask, dim=-1), dim=1
            ) / torch.clamp(torch.sum(attention_mask, dim=1, keepdims=True), min=1e-9)
            embeddings.append({"_id": _id, "embedding": embedding.squeeze(0).cpu()})

    return embeddings


def save_embeddings(args: EmbeddingArguments):
    with open(file="../data/embeddings.pkl", mode="wb") as fp:
        pickle.dump(obj=get_embeddings(args), file=fp)
    print("Embeddings are saved.")


if __name__ == "__main__":
    parser = HfArgumentParser(EmbeddingArguments)
    args = parser.parse_args_into_dataclasses()[0]

    save_embeddings(args)

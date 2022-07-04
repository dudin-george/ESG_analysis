import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, BertTokenizerFast


class MyTextDataset(Dataset):
    def __init__(self, sentence_list):
        self.sentences = sentence_list

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        return idx, self.sentences[idx]


class MyCollateBatch:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, batch):
        sentences = [b[1] for b in batch]
        idx = [b[0] for b in batch]

        text = self.tokenizer(sentences, max_length=512, padding="max_length", truncation=True, return_tensors="pt")
        text["idx"] = idx
        return text


class ModelSentiment:
    def __init__(self, model_folder, device):
        print("Impo")
        self.device = device
        self.model_folder = model_folder

        self.tokenizer = BertTokenizerFast.from_pretrained(model_folder)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_folder, return_dict=True)
        self.collate_fn = MyCollateBatch(self.tokenizer)

        # self.model = torch.nn.DataParallel(self.model)
        # To GPU (or CPU)
        self.model.to(device)
        # No training
        self.model.eval()

    def __call__(self, sentence_list):
        data_ds = MyTextDataset(sentence_list)
        loader = DataLoader(data_ds, batch_size=128, collate_fn=self.collate_fn)
        result = np.zeros((len(sentence_list), len(self.class_names())))
        for batch in loader:
            idx = batch["idx"]
            batch = {k: v.to(self.device) for k, v in batch.items() if k != "idx"}
            with torch.no_grad():
                outputs = self.model(**batch)
                logits = outputs.logits
                predictions = torch.softmax(logits, dim=-1)

                result[idx, :] = predictions.to("cpu").numpy()

        return result

    def class_names(self):
        # return self.model.module.config.id2label
        return self.model.config.id2label

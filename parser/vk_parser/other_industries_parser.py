import os

import numpy as np

from utils import relative_path
from vk_parser.base_parser import VKBaseParser
from vk_parser.database import VkOtherIndustries
from vk_parser.queries import create_banks
from vk_parser.schemes import VKType


class VKOtherIndustriesParser(VKBaseParser):
    file = "vk_other_industries.npy"
    type = VKType.other

    def load_bank_list(self) -> None:
        params = {
            "access_token": self.settings.vk_token,
            "v": self.VERSION,
        }
        path = relative_path(os.path.dirname(__file__), self.file)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{self.file} not found")
        bank_arr = np.load(path, allow_pickle=True)
        params["group_ids"] = ",".join(bank_arr[:, 2])
        response = self.get_json_from_url("https://api.vk.com/method/groups.getById", params=params)
        if response is None or "response" not in response:
            return None
        if bank_arr.shape[0] != len(response["response"]):
            self.logger.error("bank array and response have different length")
            raise Exception("bank array and response have different length")
        db_banks = []
        for bank, vk_group in zip(bank_arr, response["response"]):
            db_banks.append(VkOtherIndustries(id=bank[0], name=bank[1], vk_id=-vk_group['id'], domain=bank[2]))
        create_banks(db_banks)
        self.logger.info("bank list loaded")

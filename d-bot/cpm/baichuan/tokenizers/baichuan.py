import io
import json
from typing import Dict
from typing import IO
from typing import List

import pkg_resources
from pytrie import StringTrie


def load_vocab(fp: IO[bytes]) -> Dict[str, int]:
    """
    Loads a vocabulary file into a dictionary.
    Note: Since there is an '\n' in Baichuan vocab, we use the json file
    """
    tokens = json.load(fp)
    vocab: Dict[str, int] = {token: idx for idx, token in enumerate(tokens)}
    return vocab


class BaichuanTokenizer(object):
    def __init__(self, path: str = None):
        self.unk_token = "<unk>"
        self.bos_token = "<s>"
        self.eos_token = "</s>"
        self.byte_list = [f"<0x{i:02X}>" for i in range(0x100)]
        self.reserve_list = [f"<reserved_{i}>" for i in range(300)]

        self._special_token_set = set(
            [self.unk_token, self.bos_token, self.eos_token] + self.byte_list + self.reserve_list
        )

        if path:
            all_tokens = load_vocab(io.FileIO(path, "rb"))
        else:
            all_tokens = load_vocab(pkg_resources.resource_stream("cpm", "/baichuan/vocabs/baichuan.json"))

        self.encoder: Dict[str, int] = {}
        self._special_encoder: Dict[str, int] = {}
        for token, token_id in all_tokens.items():
            if token in self._special_token_set:
                self._special_encoder[token] = token_id
            else:
                self.encoder[token] = token_id

        self.decoder = {v: k for k, v in self.encoder.items()}
        self._byte_decoder = {self._special_encoder[token]: i for i, token in enumerate(self.byte_list)}

        self._max_word_len = max([len(x) for x in self.encoder.keys()])
        self.tencoder = StringTrie(self.encoder)

    def get_piece(self, text: str) -> str:
        text = text[: self._max_word_len]
        len_text = len(text)
        for i in range(len(text)):
            sub = text[: len_text - i]
            if sub in self.encoder:
                return sub
        return text[0]

    @property
    def vocab_size(self):
        return len(self)

    @property
    def eos_id(self):
        return self._special_encoder[self.eos_token]

    @property
    def bos_id(self):
        return self._special_encoder[self.bos_token]

    @property
    def unk_id(self):
        return self._special_encoder[self.unk_token]

    def __len__(self):
        return len(self.encoder) + len(self._special_encoder)

    def tokenize(self, text: str) -> List[str]:
        output_tokens: List[str] = []
        st, text = 0, " " + text.replace("▁", " ")
        while st < len(text):
            piece = self.get_piece(text[st:])
            output_tokens.append(piece)
            st += len(piece)
        return output_tokens

    @staticmethod
    def escape(text: str) -> str:
        return text

    @staticmethod
    def unescape(text: str) -> str:
        return text

    def encode(self, text: str) -> List[int]:
        ret = []
        for x in self.tokenize(text):
            if x in self.encoder:
                ret.append(self.encoder[x])
            else:
                ret.extend(self._encode_unicode(x))
        return ret

    def decode(self, tokens: List[int]):
        """Decode ids into a string."""
        ret = []
        st = 0

        while st < len(tokens):
            if tokens[st] in self.decoder:
                ret.append(self.decoder[tokens[st]])
                st += 1
            elif tokens[st] in self._byte_decoder:
                if (
                    st + 2 < len(tokens)
                    and tokens[st + 1] in self._byte_decoder
                    and tokens[st + 2] in self._byte_decoder
                ):
                    plane_id = self._byte_decoder[tokens[st]]
                    row_id = self._byte_decoder[tokens[st + 1]]
                    cell_id = self._byte_decoder[tokens[st + 2]]
                    ret.append(int.to_bytes(plane_id << 16 | row_id << 8 | cell_id, 3, "big").decode("utf-8"))
                    st += 3
                elif st + 1 < len(tokens) and tokens[st + 1] in self._byte_decoder:
                    row_id = self._byte_decoder[tokens[st]]
                    cell_id = self._byte_decoder[tokens[st + 1]]
                    ret.append(int.to_bytes(row_id << 8 | cell_id, 2, "big").decode("utf-8"))
                    st += 2
                else:
                    cell_id = self._byte_decoder[tokens[st]]
                    ret.append(int.to_bytes(cell_id, 1, "big").decode("utf-8"))
                    st += 1
            elif tokens[st] == self.eos_id:
                ret.append(self.eos_token)
                st += 1
            elif tokens[st] == self.bos_id:
                ret.append(self.bos_token)
                st += 1
            else:
                ret.append(self.unk_token)
                st += 1
        if len(ret) > 0 and ret[0] == " ":  # lstrip "▁"
            ret = ret[1:]
        return "".join(ret)

    def _encode_unicode(self, token):
        # wrap unicode encoding into a helper function
        ids = []
        utf8_id = token.encode("utf-8")
        plane_id = utf8_id[-3] if len(utf8_id) >= 3 else 0
        row_id = utf8_id[-2] if len(utf8_id) >= 2 else 0
        cell_id = utf8_id[-1] if len(utf8_id) >= 1 else 0
        if plane_id > 0:
            ids.append(self._special_encoder[self.byte_list[plane_id]])
        if row_id > 0:
            ids.append(self._special_encoder[self.byte_list[row_id]])
        ids.append(self._special_encoder[self.byte_list[cell_id]])
        return ids

    def next_token(self, text):
        # fast next token matching
        token, token_id = self.tencoder.longest_prefix_item(text, (None, None))
        if token is None:
            token = text[0]
            token_ids = self._encode_unicode(token)
        else:
            token_ids = [token_id]
        return token, token_ids

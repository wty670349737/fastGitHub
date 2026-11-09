from adapters.base import BaseAdapter
from adapters.jd import JdAdapter
from adapters.taobao import TaobaoAdapter

ADAPTERS = {"jd": JdAdapter, "taobao": TaobaoAdapter}

__all__ = ["BaseAdapter", "JdAdapter", "TaobaoAdapter", "ADAPTERS"]

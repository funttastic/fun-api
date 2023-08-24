from dotmap import DotMap

from utils import safe_deep_get

setattr(DotMap, 'safe_deep_get', safe_deep_get)

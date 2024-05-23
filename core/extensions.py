from dotmap import DotMap
from core.utils import safe_deep_get, safe_deep_set

# original_init = DotMap.__init__
#
# def new_init(self, *args, **kwargs):
# 	kwargs['_dynamic'] = False
# 	original_init(self, *args, **kwargs)
#
#
# DotMap.__init__ = new_init

setattr(DotMap, 'safe_deep_get', safe_deep_get)
setattr(DotMap, 'safe_deep_set', safe_deep_set)

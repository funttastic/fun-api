from _decimal import Decimal

from dotmap import DotMap

INT_ZERO = int(0)
FLOAT_ZERO = float(0)
FLOAT_INFINITY = float('inf')
FLOAT_NAN = float('nan')
DECIMAL_ZERO = Decimal(0)
DECIMAL_INFINITY = Decimal("Infinity")
DECIMAL_NAN = Decimal('NaN')

KUJIRA_NATIVE_TOKEN = DotMap({
	"id": "ukuji",
	"name": "Kuji",
	"symbol": "KUJI",
	"decimals": "6",
}, _dynamic=False)

NUMBER_OF_RETRIES = 3
DELAY_BETWEEN_RETRIES = 3
TIMEOUT = 60

VWAP_THRESHOLD = 50

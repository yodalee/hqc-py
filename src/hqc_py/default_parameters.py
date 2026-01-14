from .hqc import Hqc

# Default parameters for three HQC variants
DEFAULT_PARAMETERS = {
	"HQC-1": {
		"n1": 46,
		"n2": 384,
		"n": 17669,
		"k": 128,
		"w": 66,
		"we": 75,
	},
	"HQC-3": {
		"n1": 56,
		"n2": 640,
		"n": 35851,
		"k": 192,
		"w": 100,
		"we": 114,
	},
	"HQC-5": {
		"n1": 90,
		"n2": 640,
		"n": 57637,
		"k": 256,
		"w": 131,
		"we": 149,
	},
}

# Create Hqc objects for each variant

# HQC-1 parameter set instance
Hqc1 = Hqc(DEFAULT_PARAMETERS["HQC-1"])
# HQC-3 parameter set instance
Hqc3 = Hqc(DEFAULT_PARAMETERS["HQC-3"])
# HQC-5 parameter set instance
Hqc5 = Hqc(DEFAULT_PARAMETERS["HQC-5"])
from .hqc import Hqc

# Default parameters for three HQC variants
DEFAULT_PARAMETERS = {
	"HQC-1": {
		"n1": 46,
		"n2": 384,
		"n": 17669,
		"k": 16,
		"w": 66,
		"we": 75,
        "len_sigma": 16,
        "generator_polynomial": [
            89,  69, 153, 116, 176, 117, 111, 75,  73, 233,
            242, 233, 65,  210, 21, 139, 103, 173, 67, 118,
            105, 210, 174, 110, 74,  69, 228, 82,  255, 181,
            1
        ],
	},
	"HQC-3": {
		"n1": 56,
		"n2": 640,
		"n": 35851,
		"k": 24,
		"w": 100,
		"we": 114,
        "len_sigma": 24,
        "generator_polynomial": [
            45, 216, 239, 24, 253, 104, 27, 40, 107, 50,
            163, 210, 227, 134, 224, 158, 119, 13, 158,
            1, 238, 164, 82, 43, 15, 232, 246, 142, 50,
            189, 29, 232, 1
        ],
	},
	"HQC-5": {
		"n1": 90,
		"n2": 640,
		"n": 57637,
		"k": 32,
		"w": 131,
		"we": 149,
        "len_sigma": 32,
        "generator_polynomial": [
            49, 167, 49, 39, 200, 121, 124, 91, 240, 63,
            148, 71, 150, 123, 87, 101, 32, 215, 159, 71,
            201, 115, 97, 210, 186, 183, 141, 217, 123, 12,
            31, 243, 180, 219, 152, 239, 99, 141, 4, 246,
            191, 144, 8, 232, 47, 27, 141, 178, 130, 64,
            124, 47, 39, 188, 216, 48, 199, 187, 1
        ],
	},
}

# Create Hqc objects for each variant

# HQC-1 parameter set instance
Hqc1 = Hqc(DEFAULT_PARAMETERS["HQC-1"])
# HQC-3 parameter set instance
Hqc3 = Hqc(DEFAULT_PARAMETERS["HQC-3"])
# HQC-5 parameter set instance
Hqc5 = Hqc(DEFAULT_PARAMETERS["HQC-5"])
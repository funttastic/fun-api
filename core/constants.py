from dotmap import DotMap

from core.types import SystemStatus

constants = DotMap({
	"configuration": {
		"main": "main.yml",
		"common": "common.yml",
		"environment": {
			"development": "development.yml",
			"staging": "staging.yml",
			"production": "production.yml"
		},
		"relative_folder": "resources/configuration",
	},
	"environments": {
		"development": "development",
		"staging": "staging",
		"production": "production"
	},
	"system": {
		"commands": {
			"status": "status",
			"start": {
				"fun_client": "start_fun_client",
				"hb_client": "start_hb_client",
				"hb_gateway": "start_hb_gateway",
			},
			"stop": {
				"fun_client": "stop_fun_client",
				"hb_client": "stop_hb_client",
				"hb_gateway": "stop_hb_gateway",
			}
		}
	},
	"status": {
		"delay": 500,  # in ms
		"default": {
			"fun-client": {
				"status": SystemStatus.UNKNOWN,
				"message": f"{str(SystemStatus.UNKNOWN).capitalize()}."
			},
			"hb-client": {
				"status": SystemStatus.UNKNOWN,
				"message": f"{str(SystemStatus.UNKNOWN).capitalize()}."
			},
			"hb-gateway": {
				"status": SystemStatus.UNKNOWN,
				"message": f"{str(SystemStatus.UNKNOWN).capitalize()}."
			}
		}
	}
})

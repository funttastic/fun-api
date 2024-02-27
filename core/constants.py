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
	"authentication": {
		"jwt": {
			"algorithm": "HS256",
			"token": {
				"expiration": 30  # in minutes
			}
		}
	},
	"system": {
		"commands": {
			"authenticate": """source ~/.bashrc && authenticate "{username}" "{password}" """,
			"status": "status",
			"start": {
				"fun_client": "source ~/.bashrc && start_fun_client",
				"hb_client": "source ~/.bashrc && start_hb_client",
				"hb_gateway": "source ~/.bashrc && start_hb_gateway",
			},
			"stop": {
				"fun_client": "source ~/.bashrc && stop_fun_client",
				"hb_client": "source ~/.bashrc && stop_hb_client",
				"hb_gateway": "source ~/.bashrc && stop_hb_gateway",
			}
		}
	},
	"services": {
		"status": {
			"task": "services.status",
			"delay": 500,  # in ms
			"current": None,
			"default": {
				"fun-frontend": SystemStatus.UNKNOWN,
				"filebrowser": SystemStatus.UNKNOWN,
				"fun-client": SystemStatus.UNKNOWN,
				"hb-client": SystemStatus.UNKNOWN,
				"hb-gateway": SystemStatus.UNKNOWN
			}
		}
	}
}, _dynamic=False)

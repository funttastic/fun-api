from dotmap import DotMap

constants = DotMap({
	'configuration': {
		'main': 'main.yml',
		'common': 'common.yml',
		'environment': {
			'development': 'development.yml',
			'staging': 'staging.yml',
			'production': 'production.yml'
		},
		'relative_folder': 'resources/configuration',
	},
	'environments': {
		'development': 'development',
		'staging': 'staging',
		'production': 'production'
	},
})

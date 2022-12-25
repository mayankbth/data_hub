# Data Base Schemas
SCHEMA_PUBLIC = 'public'
SCHEMA_DATA_HUB = 'data_hub'
SCHEMA_DATA_HUB_META = 'data_hub_meta'


# save point and rollback commands for atomic transaction
_save_point = 'mysavepoint'
_save_point_command = "SAVEPOINT " + _save_point
_rollback_save_point = "ROLLBACK TO SAVEPOINT " + _save_point


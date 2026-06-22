class AuditMonitoringRouter:
    """
    🎛️ AUTOMATED CONTROL MATRIX: Routes log trails and audit entities 
    straight to the monitoring_logs cluster, keeping primary operational tables lean.
    """
    route_app_labels = {'audit_logs', 'violations', 'reports', 'deleted_records'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'monitoring_logs'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'monitoring_logs'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow database references if neither model is trapped inside the audit silo
        if obj1._meta.app_label in self.route_app_labels or obj2._meta.app_label in self.route_app_labels:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'monitoring_logs'
        return db == 'default'
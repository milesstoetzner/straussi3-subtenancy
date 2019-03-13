from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import User, MainTenant, SubTenant, ResidentialHome, BlockedTenantID, BlockedStudentID, Feedback, Blacklist


admin.site.register(User, SimpleHistoryAdmin)
admin.site.register(MainTenant, SimpleHistoryAdmin)
admin.site.register(SubTenant, SimpleHistoryAdmin)
admin.site.register(ResidentialHome, SimpleHistoryAdmin)
admin.site.register(BlockedTenantID, SimpleHistoryAdmin)
admin.site.register(BlockedStudentID, SimpleHistoryAdmin)
admin.site.register(Blacklist, SimpleHistoryAdmin)
admin.site.register(Feedback, SimpleHistoryAdmin)

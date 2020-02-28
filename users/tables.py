import django_tables2 as tables
from .models import AuditLog, User


class AuditTable(tables.Table):
	date = tables.DateTimeColumn(format='d-m-Y H:i:s')

	class Meta:
		model = AuditLog
		fields = ('date', 'user', 'action', 'screen','object', 'object_attribute',
		          'object_instance', 'changed_attribute',
				  'old_value','new_value', 'ip',
				#    'other'
				   )
		attrs = {
			# 'class': 'paleblue',
			# 'width':'100%',
			'_ordering': {
				'orderable': 'sortable',  # Instead of `orderable`
				'ascending': 'ascend',   # Instead of `asc`
				'descending': 'descend'  # Instead of `desc`
				}
            }

class AuditListView(tables.SingleTableView):
	table = AuditTable



class UserTable(tables.Table):
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','profile.partner')
        row_attrs = {
            'data-id': lambda record: record.pk,
            'class': 'clickable-row'
        }
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from api_user.decorators import staff_required, super_admin_required


class StaffRequiredMixin(LoginRequiredMixin):
    @method_decorator(staff_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperAdminRequiredMixin(LoginRequiredMixin):
    @method_decorator(super_admin_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SuperAdminRequiredMixin, self).dispatch(request, *args, **kwargs)

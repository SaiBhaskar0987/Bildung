import time
from django.utils.deprecation import MiddlewareMixin


class ReminderMiddleware(MiddlewareMixin):
    """
    Runs on every request (every 3 minutes per user).
    Works for both student & instructor reminders.
    """

    CHECK_INTERVAL_SECONDS = 180  

    def process_request(self, request):
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return

        now_ts = time.time()
        last_ts = request.session.get("reminder_last_check_ts", 0)

        if now_ts - last_ts < self.CHECK_INTERVAL_SECONDS:
            return

        from courses.utils import check_and_send_reminders

        check_and_send_reminders(user)

        request.session["reminder_last_check_ts"] = now_ts

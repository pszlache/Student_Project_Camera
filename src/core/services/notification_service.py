class NotificationService:

    def __init__(self, user_repository):

        self.user_repository = user_repository

        # CACHE
        self._email_cache = {}
        self._sms_cache = {}

    # EMAIL RECIPIENTS
    def get_recipients_for_camera(self, cam_id):

        if cam_id not in self._email_cache:

            recipients = self.user_repository.get_notification_emails(cam_id)

            self._email_cache[cam_id] = recipients

        return self._email_cache[cam_id]

    # SMS RECIPIENTS
    def get_sms_recipients_for_camera(self, cam_id):

        if cam_id not in self._sms_cache:

            recipients = self.user_repository.get_notification_phones(cam_id)

            self._sms_cache[cam_id] = recipients

        return self._sms_cache[cam_id]

    # CACHE RESET
    def refresh_cache(self):

        self._email_cache.clear()
        self._sms_cache.clear()
class NotificationService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_recipients_for_camera(self, cam_id):
        return self.user_repository.get_notification_emails(cam_id)
    
    def get_sms_recipients_for_camera(self, cam_id):
        return self.user_repository.get_notification_phones(cam_id)
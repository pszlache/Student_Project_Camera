class SMSService:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_numbers_for_camera(self, camera_id):

        numbers = self.user_repository.get_notification_phones(camera_id)
        
        print(f"[SMS] Numbers for camera {camera_id}: {numbers}")
        
        return numbers
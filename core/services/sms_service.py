class SMSService:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_numbers_for_camera(self, cam_id):

        print(f"[SMS] Fetching numbers for camera {cam_id}")

        numbers = self.user_repository.get_notification_phones(cam_id)

        print(f"[SMS] Numbers from DB: {numbers}")

        if not numbers:
            print("[SMS] No phone numbers eligible for notifications")

        return numbers
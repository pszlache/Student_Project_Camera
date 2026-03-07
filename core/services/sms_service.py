class SMSService:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_numbers_for_camera(self, camera_id):

        users = self.user_repository.get_users_for_camera(camera_id)

        numbers = []

        for user in users:
            if user.phone_number:
                numbers.append(user.phone_number)

        return numbers
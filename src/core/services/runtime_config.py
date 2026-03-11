class RuntimeConfig:

    smtp_host = None
    smtp_port = None
    smtp_username = None
    smtp_password = None


    @classmethod
    def update_mail(cls, host, port, username, password):

        cls.smtp_host = host
        cls.smtp_port = int(port) if port else None
        cls.smtp_username = username
        cls.smtp_password = password


    @classmethod
    def get_mail_config(cls):

        return {
            "host": cls.smtp_host,
            "port": cls.smtp_port,
            "username": cls.smtp_username,
            "password": cls.smtp_password
        }
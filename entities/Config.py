class Config:
    api_token = None

    profiles_number = 0
    offset = 0

    proxy_type = None

    metamask_file = ''
    proxy_file = ''

    thread_number = ''

    tag_name = ''

    metamask_password = ''

    def __init__(self, api_token, profiles_number, offset, proxy_type, metamask_file, proxy_file, thread_number, tag_name, metamask_password):
        self.api_token = api_token
        self.profiles_number = int(profiles_number)
        self.offset = int(offset)
        self.proxy_type = proxy_type
        self.metamask_file = metamask_file
        self.proxy_file = proxy_file
        self.thread_number = int(thread_number)
        self.tag_name = tag_name
        self.metamask_password = metamask_password
